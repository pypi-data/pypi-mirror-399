"""
Retry logic utilities for ZoPassport SDK.

Provides decorators and helpers for implementing retry logic with
exponential backoff for network requests.
"""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import (
    ZoConnectionError,
    ZoNetworkError,
    ZoRateLimitError,
    ZoRetryExhaustedError,
    ZoTimeoutError,
)
from .utils import logger

T = TypeVar("T")


def should_retry(exception: BaseException) -> bool:
    """
    Check if exception should be retried.

    Don't retry ZoRateLimitError even though it inherits from ZoNetworkError.
    """
    if isinstance(exception, ZoRateLimitError):
        return False
    return isinstance(exception, (ZoConnectionError, ZoTimeoutError, ZoNetworkError))


def create_retry_handler(
    max_attempts: int = 3,
    backoff_factor: float = 1.5,
    max_wait: int = 10,
) -> AsyncRetrying:
    """
    Create a retry handler with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        max_wait: Maximum wait time between retries in seconds

    Returns:
        AsyncRetrying instance configured with retry logic
    """
    return AsyncRetrying(
        # Retry on valid exception types, excluding rate limits
        retry=retry_if_exception(should_retry),
        # Stop after max attempts
        stop=stop_after_attempt(max_attempts),
        # Exponential backoff: wait = backoff_factor * (2 ** attempt_number)
        wait=wait_exponential(multiplier=backoff_factor, max=max_wait),
        # Don't reraise the original exception immediately - allow catching RetryError
        reraise=False,
    )


async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    backoff_factor: float = 1.5,
    **kwargs: Any,
) -> Any:
    """
    Execute a function with retry logic and exponential backoff.

    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the function

    Raises:
        ZoRetryExhaustedError: If all retry attempts fail
        ZoRateLimitError: If rate limit is hit (not retried)
        Other exceptions: Propagated as-is if not retryable
    """
    retry_handler = create_retry_handler(max_attempts=max_attempts, backoff_factor=backoff_factor)

    try:
        async for attempt in retry_handler:
            with attempt:
                try:
                    result = await func(*args, **kwargs)
                    return result
                except ZoRateLimitError:
                    # Don't retry rate limit errors
                    raise
                except (ZoConnectionError, ZoTimeoutError, ZoNetworkError) as e:
                    logger.warning(f"Attempt {attempt.retry_state.attempt_number} failed: {e}")
                    raise

    except RetryError as e:
        # All retries exhausted
        last_exception = e.last_attempt.exception()
        if last_exception and not isinstance(last_exception, Exception):
            raise last_exception from e  # Re-raise BaseExceptions like KeyboardInterrupt

        raise ZoRetryExhaustedError(
            "All retry attempts exhausted",
            attempts=max_attempts,
            last_error=cast(Exception | None, last_exception),
        ) from last_exception


def with_retry(
    max_attempts: int = 3, backoff_factor: float = 1.5
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to add retry logic to async functions.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, backoff_factor=2.0)
        async def fetch_data():
            # This will be retried up to 3 times with exponential backoff
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_with_backoff(
                func, *args, max_attempts=max_attempts, backoff_factor=backoff_factor, **kwargs
            )

        return wrapper

    return decorator


async def handle_rate_limit(retry_after: int) -> None:
    """
    Handle rate limit by waiting for the specified duration.

    Args:
        retry_after: Seconds to wait before retrying

    Raises:
        ZoRateLimitError: After waiting, to signal caller to retry
    """
    if retry_after and retry_after > 0:
        logger.warning(f"Rate limited, waiting {retry_after} seconds")
        await asyncio.sleep(retry_after)
    else:
        # Default wait time if retry_after not specified
        logger.warning("Rate limited, waiting 60 seconds (default)")
        await asyncio.sleep(60)
