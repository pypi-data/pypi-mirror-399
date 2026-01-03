"""Tests for avatar module."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from zopassport.avatar import ZoAvatar
from zopassport.exceptions import ZoAvatarError, ZoValidationError


class TestZoAvatar:
    """Tests for ZoAvatar class."""

    @pytest.fixture
    def avatar(self):
        client = AsyncMock()
        client.request = AsyncMock()
        return ZoAvatar(client)

    @pytest.mark.asyncio
    async def test_generate_avatar_success(self, avatar):
        """Test successful avatar generation start."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "task_123", "status": "pending"}
        avatar.client.request.return_value = mock_response

        result = await avatar.generate_avatar("token", "bro")

        assert result["success"] is True
        assert result["task_id"] == "task_123"

    @pytest.mark.asyncio
    async def test_generate_avatar_invalid_body(self, avatar):
        """Test invalid body type raises error."""
        with pytest.raises(ZoValidationError):
            await avatar.generate_avatar("token", "invalid")

    @pytest.mark.asyncio
    async def test_get_avatar_status(self, avatar):
        """Test getting avatar status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "result": {"avatar_url": "http://example.com/avatar.png"},
        }
        avatar.client.request.return_value = mock_response

        result = await avatar.get_avatar_status("token", "task_123")

        assert result["success"] is True
        assert result["status"] == "completed"
        assert result["avatar_url"] == "http://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_poll_avatar_status_success(self, avatar):
        """Test polling avatar status until completion."""
        # Setup responses: pending -> completed
        avatar.get_avatar_status = AsyncMock(
            side_effect=[
                {"success": True, "status": "pending"},
                {"success": True, "status": "completed", "avatar_url": "url"},
            ]
        )

        on_complete = AsyncMock()

        await avatar.poll_avatar_status(
            "token", "task_123", on_complete=on_complete, interval_seconds=0.1
        )

        on_complete.assert_awaited_with("url")
        assert avatar.get_avatar_status.await_count == 2

    @pytest.mark.asyncio
    async def test_poll_avatar_status_timeout(self, avatar):
        """Test polling avatar status timeout."""
        avatar.get_avatar_status = AsyncMock(return_value={"success": True, "status": "pending"})

        on_error = AsyncMock()

        with pytest.raises(ZoAvatarError) as excinfo:
            await avatar.poll_avatar_status(
                "token", "task_123", on_error=on_error, max_attempts=2, interval_seconds=0.01
            )

        assert "timed out" in str(excinfo.value)
        on_error.assert_awaited_with("Avatar generation timed out")

    @pytest.mark.asyncio
    async def test_poll_avatar_status_failed(self, avatar):
        """Test polling avatar status generation failure."""
        avatar.get_avatar_status = AsyncMock(return_value={"success": True, "status": "failed"})

        on_error = AsyncMock()

        with pytest.raises(ZoAvatarError) as excinfo:
            await avatar.poll_avatar_status(
                "token", "task_123", on_error=on_error, interval_seconds=0.01
            )

        assert "generation failed" in str(excinfo.value)
        on_error.assert_awaited_with("Avatar generation failed")

    @pytest.mark.asyncio
    async def test_poll_avatar_status_error(self, avatar):
        """Test polling avatar status network error."""
        avatar.get_avatar_status = AsyncMock(side_effect=Exception("Network error"))

        on_error = AsyncMock()

        with pytest.raises(ZoAvatarError) as excinfo:
            await avatar.poll_avatar_status(
                "token", "task_123", on_error=on_error, interval_seconds=0.01
            )

        assert "Network error" in str(excinfo.value)
