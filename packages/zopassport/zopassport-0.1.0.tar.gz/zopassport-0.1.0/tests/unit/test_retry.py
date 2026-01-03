"""Tests for retry utilities."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from zopassport.exceptions import (
    ZoConnectionError,
    ZoNetworkError,
    ZoRateLimitError,
    ZoRetryExhaustedError,
    ZoTimeoutError,
)
from zopassport.retry import handle_rate_limit, retry_with_backoff, with_retry


class TestRetryUtilities:
    """Tests for retry module functions."""

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self):
        """Test successful execution without retries."""
        mock_func = AsyncMock(return_value="success")

        result = await retry_with_backoff(mock_func)

        assert result == "success"
        assert mock_func.await_count == 1

    @pytest.mark.asyncio
    async def test_retry_with_backoff_retries(self):
        """Test retrying on failure."""
        # Fail twice, then succeed
        mock_func = AsyncMock(
            side_effect=[ZoConnectionError("Fail 1"), ZoTimeoutError("Fail 2"), "success"]
        )

        result = await retry_with_backoff(
            mock_func,
            max_attempts=3,
            backoff_factor=0.1,  # Fast backoff for test
        )

        assert result == "success"
        assert mock_func.await_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test exhausting retries raises ZoRetryExhaustedError."""
        mock_func = AsyncMock(side_effect=ZoNetworkError("Fail"))

        with pytest.raises(ZoRetryExhaustedError) as excinfo:
            await retry_with_backoff(mock_func, max_attempts=2, backoff_factor=0.1)

        assert excinfo.value.attempts == 2
        assert isinstance(excinfo.value.last_error, ZoNetworkError)

    @pytest.mark.asyncio
    async def test_no_retry_on_rate_limit(self):
        """Test rate limit error is not retried."""
        mock_func = AsyncMock(side_effect=ZoRateLimitError("Rate limit"))

        with pytest.raises(ZoRateLimitError):
            await retry_with_backoff(mock_func)

        assert mock_func.await_count == 1

    @pytest.mark.asyncio
    async def test_with_retry_decorator(self):
        """Test decorator usage."""
        call_count = 0

        @with_retry(max_attempts=2, backoff_factor=0.1)
        async def flaky_func():
            nonlocal call_count
            await asyncio.sleep(0.01)  # Simulate work
            if call_count == 0:
                call_count += 1
                raise ZoNetworkError("Fail once")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_handle_rate_limit(self):
        """Test handling rate limit waiting."""
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await handle_rate_limit(10)
            mock_sleep.assert_awaited_with(10)

            await handle_rate_limit(0)
            mock_sleep.assert_awaited_with(60)  # Default
