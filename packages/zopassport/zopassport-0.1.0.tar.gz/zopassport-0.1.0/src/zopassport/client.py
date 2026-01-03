import asyncio
import secrets
import string
import time
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import (
    ZoConnectionError,
    ZoNetworkError,
    ZoRateLimitError,
    ZoRetryExhaustedError,
    ZoTimeoutError,
    ZoTokenRefreshError,
)
from .storage import STORAGE_KEYS, MemoryStorageAdapter, StorageAdapter
from .utils import logger


class ZoPassportConfig:
    """Configuration for ZoPassport SDK."""

    def __init__(
        self,
        client_key: str,
        base_url: str = "https://api.io.zo.xyz",
        timeout: int = 10,
        storage_adapter: StorageAdapter | None = None,
        max_retries: int = 3,
        retry_backoff_factor: float = 1.5,
    ) -> None:
        """
        Initialize the configuration.

        Args:
            client_key: API client key for authentication
            base_url: Base URL for the API (default: https://api.io.zo.xyz)
            timeout: Request timeout in seconds (default: 10)
            storage_adapter: Storage adapter for session persistence (default: MemoryStorageAdapter)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_backoff_factor: Multiplier for exponential backoff (default: 1.5)
        """
        self.client_key = client_key
        self.base_url = base_url
        self.timeout = timeout
        self.storage_adapter = storage_adapter or MemoryStorageAdapter()
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor


def generate_device_credentials() -> dict[str, str]:
    """
    Generate unique device credentials.

    Returns:
        Dictionary with device_id and device_secret
    """
    timestamp = str(int(time.time() * 1000))
    random_str = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(7))
    device_id = f"web-{timestamp}-{random_str}"

    secret_part1 = "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(13)
    )
    secret_part2 = "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(13)
    )
    device_secret = secret_part1 + secret_part2

    return {"device_id": device_id, "device_secret": device_secret}


class ZoApiClient:
    """HTTP client for ZoPassport API with authentication and retry logic."""

    def __init__(self, config: ZoPassportConfig) -> None:
        """
        Initialize the API client.

        Args:
            config: ZoPassport configuration object
        """
        self.config = config
        self.storage = self.config.storage_adapter
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        self._refresh_lock = asyncio.Lock()

    async def _get_auth_headers(self) -> dict[str, str]:
        """
        Build authentication headers for requests.

        Returns:
            Dictionary of authentication headers

        Raises:
            ZoStorageError: If storage operations fail
        """
        headers = {"client-key": self.config.client_key}

        # Device Credentials
        creds = await self._get_or_create_device_credentials()
        headers["client-device-id"] = creds["device_id"]
        headers["client-device-secret"] = creds["device_secret"]

        # Auth Token
        token = await self.storage.get_item(STORAGE_KEYS["ACCESS_TOKEN"])
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    async def _get_or_create_device_credentials(self) -> dict[str, str]:
        """
        Get existing device credentials or create new ones.

        Returns:
            Dictionary with device_id and device_secret

        Raises:
            ZoStorageError: If storage operations fail
        """
        stored_id = await self.storage.get_item(STORAGE_KEYS["CLIENT_DEVICE_ID"])
        stored_secret = await self.storage.get_item(STORAGE_KEYS["CLIENT_DEVICE_SECRET"])

        if stored_id and stored_secret:
            return {"device_id": stored_id, "device_secret": stored_secret}

        creds = generate_device_credentials()
        await self.storage.set_item(STORAGE_KEYS["CLIENT_DEVICE_ID"], creds["device_id"])
        await self.storage.set_item(STORAGE_KEYS["CLIENT_DEVICE_SECRET"], creds["device_secret"])

        return creds

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make an HTTP request with authentication, retry logic, and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL path
            **kwargs: Additional arguments to pass to httpx

        Returns:
            HTTP response object

        Raises:
            ZoConnectionError: If connection fails
            ZoTimeoutError: If request times out
            ZoRateLimitError: If rate limit is exceeded
            ZoNetworkError: For other network-related errors
            ZoTokenRefreshError: If token refresh fails after 401
            ZoRetryExhaustedError: If all retry attempts fail
        """
        # Create retry handler for this request
        retry_handler = AsyncRetrying(
            retry=retry_if_exception_type((ZoConnectionError, ZoTimeoutError)),
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=self.config.retry_backoff_factor,
                max=10,
            ),
            reraise=True,
        )

        attempt_num = 0
        last_error = None

        async for attempt in retry_handler:
            with attempt:
                attempt_num += 1
                try:
                    response = await self._make_request(method, url, **kwargs)
                    return response
                except (ZoConnectionError, ZoTimeoutError) as e:
                    last_error = e
                    logger.warning(f"Request attempt {attempt_num} failed: {e}")
                    raise

        # This should not be reached due to reraise=True, but just in case
        raise ZoRetryExhaustedError(
            f"Request to {url} failed after {attempt_num} attempts",
            attempts=attempt_num,
            last_error=last_error,
        )

    async def _make_request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """
        Make a single HTTP request attempt.

        Args:
            method: HTTP method
            url: Request URL path
            **kwargs: Additional arguments

        Returns:
            HTTP response object

        Raises:
            Various ZoPassport exceptions based on error type
        """
        headers = await self._get_auth_headers()
        # Merge with any provided headers
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
            del kwargs["headers"]

        try:
            response = await self.client.request(method, url, headers=headers, **kwargs)

            # Handle 401 Unauthorized (Token Refresh)
            if response.status_code == 401:
                logger.info("Received 401, attempting token refresh")
                refresh_success = await self._refresh_token()
                if refresh_success:
                    # Retry request with new token
                    new_headers = await self._get_auth_headers()
                    return await self.client.request(method, url, headers=new_headers, **kwargs)
                else:
                    # Refresh failed, clear session
                    await self._clear_session()
                    raise ZoTokenRefreshError(
                        "Token refresh failed, session cleared. Please re-authenticate."
                    )

            # Handle 429 Rate Limiting
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
                raise ZoRateLimitError(
                    "API rate limit exceeded",
                    retry_after=retry_seconds,
                    details={"url": url, "method": method},
                )

            # Handle 5xx server errors (retryable)
            if response.status_code >= 500:
                raise ZoNetworkError(
                    f"Server error: HTTP {response.status_code}",
                    status_code=response.status_code,
                    details={"url": url, "method": method},
                )

            return response

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise ZoTimeoutError(
                f"Request to {url} timed out after {self.config.timeout}s",
                details={"method": method, "url": url},
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise ZoConnectionError(
                f"Failed to connect to {self.config.base_url}",
                details={"method": method, "url": url},
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise ZoNetworkError(
                f"Network error during request to {url}",
                details={"method": method, "url": url, "error": str(e)},
            ) from e

    async def _refresh_token(self) -> bool:
        """
        Refresh the access token using the refresh token.

        Uses a lock to prevent concurrent refresh attempts.

        Returns:
            True if refresh succeeded, False otherwise
        """
        async with self._refresh_lock:
            refresh_token = await self.storage.get_item(STORAGE_KEYS["REFRESH_TOKEN"])
            if not refresh_token:
                logger.warning("No refresh token available")
                return False

            try:
                # Build headers for refresh request
                headers = {
                    "client-key": self.config.client_key,
                    "Content-Type": "application/json",
                }
                creds = await self._get_or_create_device_credentials()
                headers["client-device-id"] = creds["device_id"]
                headers["client-device-secret"] = creds["device_secret"]

                response = await self.client.post(
                    "/api/v1/auth/token/refresh/",
                    json={"refresh_token": refresh_token},
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("access")
                    new_refresh_token = data.get("refresh")

                    if access_token:
                        await self.storage.set_item(STORAGE_KEYS["ACCESS_TOKEN"], access_token)
                        if new_refresh_token:
                            await self.storage.set_item(
                                STORAGE_KEYS["REFRESH_TOKEN"], new_refresh_token
                            )

                        # Save expiry times if available
                        if "access_expiry" in data:
                            await self.storage.set_item(
                                STORAGE_KEYS["TOKEN_EXPIRY"], data["access_expiry"]
                            )
                        if "refresh_expiry" in data:
                            await self.storage.set_item(
                                STORAGE_KEYS["REFRESH_EXPIRY"], data["refresh_expiry"]
                            )

                        logger.info("Token refresh successful")
                        return True

                logger.warning(f"Token refresh failed with status {response.status_code}")
                return False
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                return False

    async def _clear_session(self) -> None:
        """Clear stored session data."""
        await self.storage.remove_item(STORAGE_KEYS["ACCESS_TOKEN"])
        await self.storage.remove_item(STORAGE_KEYS["REFRESH_TOKEN"])
        await self.storage.remove_item(STORAGE_KEYS["USER"])
        logger.info("Session cleared")

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        await self.client.aclose()
        logger.debug("HTTP client closed")
