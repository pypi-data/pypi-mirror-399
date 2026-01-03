"""Tests for authentication module."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from zopassport.auth import ZoAuth
from zopassport.exceptions import ZoAuthenticationError, ZoValidationError
from zopassport.types import ZoAuthResponse


class TestZoAuth:
    """Tests for ZoAuth class."""

    @pytest.fixture
    def mock_client(self):
        client = AsyncMock()
        client.request = AsyncMock()
        return client

    @pytest.fixture
    def auth(self, mock_client):
        return ZoAuth(mock_client)

    @pytest.mark.asyncio
    async def test_send_otp_success(self, auth, mock_client):
        """Test successful OTP sending."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "OTP sent successfully"}
        mock_client.request.return_value = mock_response

        result = await auth.send_otp("91", "9876543210")

        assert result["success"] is True
        assert result["message"] == "OTP sent successfully"
        mock_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_otp_validation_error(self, auth):
        """Test validation error for missing inputs."""
        with pytest.raises(ZoValidationError):
            await auth.send_otp("", "9876543210")

    @pytest.mark.asyncio
    async def test_verify_otp_success(self, auth, mock_client, mock_auth_response):
        """Test successful OTP verification."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_auth_response
        mock_client.request.return_value = mock_response

        result = await auth.verify_otp("91", "9876543210", "123456")

        assert result["success"] is True
        assert isinstance(result["data"], ZoAuthResponse)
        assert result["data"].access_token == "mock_access_token"

    @pytest.mark.asyncio
    async def test_verify_otp_failure(self, auth, mock_client):
        """Test failed OTP verification."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"errors": ["Invalid OTP"]}
        mock_client.request.return_value = mock_response

        with pytest.raises(ZoAuthenticationError) as excinfo:
            await auth.verify_otp("91", "9876543210", "000000")

        assert "Invalid OTP" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_check_login_status(self, auth, mock_client):
        """Test checking login status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"authenticated": True}
        mock_client.request.return_value = mock_response

        result = await auth.check_login_status("token")
        assert result["success"] is True
        assert result["is_authenticated"] is True
