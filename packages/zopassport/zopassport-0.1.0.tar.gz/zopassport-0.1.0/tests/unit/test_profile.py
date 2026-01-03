"""Tests for profile module."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from zopassport.exceptions import ZoAPIError, ZoValidationError
from zopassport.profile import ZoProfile
from zopassport.types import ZoProfileResponse


class TestZoProfile:
    """Tests for ZoProfile class."""

    @pytest.fixture
    def profile(self):
        client = AsyncMock()
        client.request = AsyncMock()
        return ZoProfile(client)

    @pytest.mark.asyncio
    async def test_get_profile_success(self, profile):
        """Test successful profile fetch."""
        mock_data = {"id": "user_123", "first_name": "Test", "last_name": "User"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        profile.client.request.return_value = mock_response

        result = await profile.get_profile("token")

        assert result["success"] is True
        assert isinstance(result["profile"], ZoProfileResponse)
        assert result["profile"].first_name == "Test"

    @pytest.mark.asyncio
    async def test_get_profile_failure(self, profile):
        """Test failed profile fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        profile.client.request.return_value = mock_response

        with pytest.raises(ZoAPIError):
            await profile.get_profile("token")

    @pytest.mark.asyncio
    async def test_update_profile_success(self, profile):
        """Test successful profile update."""
        mock_data = {"id": "user_123", "bio": "Updated bio"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        profile.client.request.return_value = mock_response

        result = await profile.update_profile("token", {"bio": "Updated bio"})

        assert result["success"] is True
        assert result["profile"].bio == "Updated bio"

    @pytest.mark.asyncio
    async def test_update_profile_empty(self, profile):
        """Test update with empty data raises error."""
        with pytest.raises(ZoValidationError):
            await profile.update_profile("token", {})
