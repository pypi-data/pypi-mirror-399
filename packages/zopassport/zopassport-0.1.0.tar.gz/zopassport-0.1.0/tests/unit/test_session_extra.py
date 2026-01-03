"""Extra tests for session module coverage."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from zopassport.exceptions import ZoStorageError
from zopassport.session import STORAGE_KEYS, ZoPassportSDK
from zopassport.types import ZoAuthResponse, ZoUser


class TestZoSessionExtra:
    """Extra tests for ZoPassportSDK."""

    @pytest.fixture
    def sdk(self, mock_storage):
        return ZoPassportSDK(
            client_key="test_key", storage_adapter=mock_storage, auto_refresh=False
        )

    @pytest.mark.asyncio
    async def test_load_session_storage_error(self, sdk, mock_storage):
        """Test load_session handles storage error."""
        # Mock get_item to raise ZoStorageError
        mock_storage.get_item = AsyncMock(side_effect=ZoStorageError("Read failed"))

        with pytest.raises(ZoStorageError):
            await sdk._load_session()

    @pytest.mark.asyncio
    async def test_load_session_missing_data(self, sdk, mock_storage):
        """Test load_session with partial data."""
        # Only user, no token
        await mock_storage.set_item(STORAGE_KEYS["USER"], "{}")

        await sdk._load_session()
        assert sdk.is_authenticated is False

    @pytest.mark.asyncio
    async def test_load_session_corrupt_json(self, sdk, mock_storage):
        """Test load_session with invalid JSON."""
        await mock_storage.set_item(STORAGE_KEYS["USER"], "{bad_json}")
        await mock_storage.set_item(STORAGE_KEYS["ACCESS_TOKEN"], "token")

        # Should catch JSONDecodeError and clear session
        sdk._clear_session_data = AsyncMock()
        await sdk._load_session()

        assert sdk.is_authenticated is False
        sdk._clear_session_data.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_session(self, sdk, mock_storage):
        """Test save_session stores all fields."""
        user = ZoUser(id="123", first_name="Test")
        auth_response = ZoAuthResponse(
            user=user,
            access_token="acc",
            refresh_token="ref",
            access_token_expiry="exp1",
            refresh_token_expiry="exp2",
            device_id="dev1",
            device_secret="sec1",
        )

        await sdk._save_session(auth_response)

        assert await mock_storage.get_item(STORAGE_KEYS["ACCESS_TOKEN"]) == "acc"
        assert await mock_storage.get_item(STORAGE_KEYS["REFRESH_TOKEN"]) == "ref"
        assert await mock_storage.get_item(STORAGE_KEYS["CLIENT_DEVICE_ID"]) == "dev1"
        assert sdk.is_authenticated is True

    @pytest.mark.asyncio
    async def test_should_refresh_token_no_expiry(self, sdk, mock_storage):
        """Test _should_refresh_token returns False if no expiry stored."""
        await mock_storage.remove_item(STORAGE_KEYS["TOKEN_EXPIRY"])
        assert await sdk._should_refresh_token() is False

    @pytest.mark.asyncio
    async def test_refresh_loop_cancelled(self, sdk):
        """Test refresh loop handles cancellation gracefully."""
        # Mock sleep to raise CancelledError immediately
        # It should catch it and exit cleanly without raising
        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            await sdk._refresh_loop()

    @pytest.mark.asyncio
    async def test_refresh_loop_error_handling(self, sdk):
        """Test refresh loop continues after error."""
        sdk._refresh_interval_ms = 1  # Run fast
        sdk._shutdown = False

        # 1. First iteration raises Exception
        # 2. Second iteration we cancel it to stop test
        side_effects = [Exception("Loop Error"), asyncio.CancelledError()]

        with patch("asyncio.sleep", side_effect=side_effects):
            try:
                await sdk._refresh_loop()
            except asyncio.CancelledError:
                pass  # Expected end of test

    @pytest.mark.asyncio
    async def test_refresh_loop_success(self, sdk):
        """Test successful token refresh in loop."""
        sdk._is_authenticated = True
        sdk._should_refresh_token = AsyncMock(return_value=True)
        sdk.client._refresh_token = AsyncMock(return_value=True)

        # Run once then stop
        sdk._shutdown = False

        async def stop_loop(*args):
            sdk._shutdown = True

        with patch("asyncio.sleep", side_effect=stop_loop):
            await sdk._refresh_loop()

        sdk.client._refresh_token.assert_awaited()

    @pytest.mark.asyncio
    async def test_refresh_loop_failed_refresh(self, sdk):
        """Test failed token refresh stops authentication."""
        sdk._is_authenticated = True
        sdk._should_refresh_token = AsyncMock(return_value=True)
        sdk.client._refresh_token = AsyncMock(return_value=False)

        sdk._shutdown = False

        async def stop_loop(*args):
            # Should have set authenticated to False
            if not sdk._is_authenticated:
                sdk._shutdown = True

        with patch("asyncio.sleep", side_effect=stop_loop):
            await sdk._refresh_loop()

        assert sdk.is_authenticated is False
