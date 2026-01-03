"""Integration tests for authentication flows."""

from unittest.mock import MagicMock

import pytest

from zopassport import ZoPassportSDK
from zopassport.storage import MemoryStorageAdapter


class TestAuthIntegration:
    """Integration tests for authentication."""

    @pytest.mark.asyncio
    async def test_full_login_flow(self, mock_httpx_response, mock_auth_response):
        """Test complete login flow with mock API."""
        storage = MemoryStorageAdapter()
        sdk = ZoPassportSDK(client_key="test_key", storage_adapter=storage, auto_refresh=False)
        await sdk.initialize()

        # Mock API responses
        otp_response = mock_httpx_response(json_data={"message": "OTP sent successfully"})
        verify_response = mock_httpx_response(json_data=mock_auth_response)

        # We need to mock the client.request to return different responses
        # based on the URL being called
        async def mock_request(method, url, **kwargs):
            if "otp" in url and method == "POST":
                return otp_response
            if "login/mobile" in url and method == "POST":
                return verify_response
            return mock_httpx_response(status_code=404)

        # Patch the client request method
        sdk.client.request = MagicMock(side_effect=mock_request)  # type: ignore[method-assign]

        # Step 1: Send OTP
        otp_result = await sdk.auth.send_otp("91", "9876543210")
        assert otp_result["success"] is True

        # Step 2: Verify OTP
        login_result = await sdk.login_with_phone("91", "9876543210", "123456")
        assert login_result["success"] is True

        # Verify state
        assert sdk.is_authenticated is True
        assert sdk.user is not None
        assert sdk.user.first_name == "John"

        # Verify storage
        token = await storage.get_item("zo_access_token")
        assert token == "mock_access_token"

        await sdk.close()
