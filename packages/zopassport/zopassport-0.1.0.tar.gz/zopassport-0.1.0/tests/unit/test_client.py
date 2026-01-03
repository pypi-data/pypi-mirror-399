"""Tests for API client."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from zopassport.client import ZoApiClient, ZoPassportConfig
from zopassport.exceptions import ZoRateLimitError
from zopassport.storage import STORAGE_KEYS


class TestZoApiClient:
    """Tests for ZoApiClient."""

    @pytest.fixture
    def config(self, mock_storage):
        return ZoPassportConfig(client_key="test_key", storage_adapter=mock_storage)

    @pytest.fixture
    def client(self, config):
        return ZoApiClient(config)

    @pytest.mark.asyncio
    async def test_auth_headers(self, client):
        """Test auth headers generation."""
        await client.storage.set_item(STORAGE_KEYS["ACCESS_TOKEN"], "test_token")

        headers = await client._get_auth_headers()

        assert headers["client-key"] == "test_key"
        assert headers["Authorization"] == "Bearer test_token"
        assert "client-device-id" in headers
        assert "client-device-secret" in headers

    @pytest.mark.asyncio
    async def test_request_success(self, client):
        """Test successful request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        client.client.request = AsyncMock(return_value=mock_response)

        response = await client.request("GET", "/test")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, client):
        """Test automatic token refresh on 401."""
        # Setup initial 401 response
        response_401 = MagicMock()
        response_401.status_code = 401

        # Setup success response after refresh
        response_200 = MagicMock()
        response_200.status_code = 200

        # Mock refresh token method
        client._refresh_token = AsyncMock(return_value=True)

        # Mock client.request to return 401 then 200
        client.client.request = AsyncMock(side_effect=[response_401, response_200])

        response = await client.request("GET", "/test")

        assert response.status_code == 200
        client._refresh_token.assert_awaited_once()
        assert client.client.request.await_count == 2

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client):
        """Test rate limit handling."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        client.client.request = AsyncMock(return_value=mock_response)

        with pytest.raises(ZoRateLimitError) as excinfo:
            await client.request("GET", "/test")

        assert excinfo.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        await client.storage.set_item(STORAGE_KEYS["REFRESH_TOKEN"], "old_refresh")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access": "new_access", "refresh": "new_refresh"}
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client._refresh_token()

        assert result is True
        assert await client.storage.get_item(STORAGE_KEYS["ACCESS_TOKEN"]) == "new_access"
        assert await client.storage.get_item(STORAGE_KEYS["REFRESH_TOKEN"]) == "new_refresh"
