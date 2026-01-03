import asyncio
import json
from datetime import datetime, timedelta
from typing import Any

from dateutil import parser as dateparser

from .auth import ZoAuth
from .avatar import ZoAvatar
from .client import ZoApiClient, ZoPassportConfig
from .exceptions import ZoStorageError
from .profile import ZoProfile
from .storage import STORAGE_KEYS, FileStorageAdapter, StorageAdapter
from .types import ZoAuthResponse, ZoUser
from .utils import logger, set_log_level
from .wallet import ZoWallet


class ZoPassportSDK:
    """
    Main SDK class for ZoPassport authentication and services.

    This class provides access to all ZoPassport features including
    authentication, profile management, avatar generation, and wallet operations.
    """

    def __init__(
        self,
        client_key: str,
        base_url: str = "https://api.io.zo.xyz",
        storage_adapter: StorageAdapter | None = None,
        auto_refresh: bool = True,
        refresh_interval: int = 60000,  # ms
        debug: bool = False,
        max_retries: int = 3,
        timeout: int = 10,
    ) -> None:
        """
        Initialize the ZoPassport SDK.

        Args:
            client_key: API client key for authentication
            base_url: Base URL for the API (default: https://api.io.zo.xyz)
            storage_adapter: Storage adapter for session persistence (default: FileStorageAdapter)
            auto_refresh: Enable automatic token refresh (default: True)
            refresh_interval: Token refresh check interval in milliseconds (default: 60000)
            debug: Enable debug logging (default: False)
            max_retries: Maximum retry attempts for failed requests (default: 3)
            timeout: Request timeout in seconds (default: 10)
        """
        # Set logging level
        if debug:
            set_log_level("DEBUG")

        # Initialize configuration
        self.config = ZoPassportConfig(
            client_key=client_key,
            base_url=base_url,
            storage_adapter=storage_adapter or FileStorageAdapter(),
            max_retries=max_retries,
            retry_backoff_factor=1.5,
        )

        # Initialize API client
        self.client = ZoApiClient(self.config)
        self.storage = self.client.storage

        # Initialize service modules
        self.auth = ZoAuth(self.client)
        self.profile = ZoProfile(self.client)
        self.avatar = ZoAvatar(self.client)
        self.wallet = ZoWallet(self.client)

        # Session state
        self._user: ZoUser | None = None
        self._is_authenticated: bool = False

        # Auto-refresh configuration
        self._refresh_task: asyncio.Task | None = None
        self._auto_refresh = auto_refresh
        self._refresh_interval_ms = refresh_interval
        self._shutdown = False

    async def initialize(self) -> None:
        """
        Initialize the SDK by loading existing session and starting auto-refresh.

        This must be called after instantiation before using the SDK.

        Raises:
            ZoStorageError: If session loading fails
        """
        await self._load_session()
        if self._auto_refresh and self._is_authenticated:
            self._start_auto_refresh()
            logger.debug("Auto-refresh enabled")

    async def _load_session(self) -> None:
        """
        Load existing session from storage.

        Raises:
            ZoStorageError: If storage operations fail
        """
        try:
            user_json = await self.storage.get_item(STORAGE_KEYS["USER"])
            access_token = await self.storage.get_item(STORAGE_KEYS["ACCESS_TOKEN"])

            if user_json and access_token:
                try:
                    user_data = json.loads(user_json)
                    self._user = ZoUser(**user_data)
                    self._is_authenticated = True

                    if self._user.wallet_address:
                        self.wallet.set_wallet_address(self._user.wallet_address)

                    logger.info(f"Session loaded for user: {self._user.first_name}")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse stored session data: {e}")
                    await self._clear_session_data()
        except ZoStorageError:
            raise
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")

    async def login_with_phone(
        self, country_code: str, phone_number: str, otp: str
    ) -> dict[str, Any]:
        """
        Authenticate user with phone number and OTP.

        Args:
            country_code: Mobile country code (e.g., "91" for India)
            phone_number: Phone number without country code
            otp: One-time password received via SMS

        Returns:
            Dictionary with success status and user data

        Raises:
            ZoAuthenticationError: If authentication fails
            ZoValidationError: If inputs are invalid
            ZoNetworkError: If network request fails
        """
        result = await self.auth.verify_otp(country_code, phone_number, otp)

        if result["success"] and result.get("data"):
            auth_data: ZoAuthResponse = result["data"]
            await self._save_session(auth_data)

            if auth_data.user.wallet_address:
                self.wallet.set_wallet_address(auth_data.user.wallet_address)

            # Start auto-refresh if enabled
            if self._auto_refresh:
                self._start_auto_refresh()

            return {"success": True, "user": auth_data.user}

        return {"success": False, "error": result.get("error")}

    async def _save_session(self, auth_data: ZoAuthResponse) -> None:
        """
        Save authentication data to storage.

        Args:
            auth_data: Authentication response data

        Raises:
            ZoStorageError: If storage operations fail
        """
        await self.storage.set_item(STORAGE_KEYS["ACCESS_TOKEN"], auth_data.access_token)
        await self.storage.set_item(STORAGE_KEYS["REFRESH_TOKEN"], auth_data.refresh_token)
        await self.storage.set_item(STORAGE_KEYS["TOKEN_EXPIRY"], auth_data.access_token_expiry)
        await self.storage.set_item(STORAGE_KEYS["REFRESH_EXPIRY"], auth_data.refresh_token_expiry)
        await self.storage.set_item(STORAGE_KEYS["USER"], auth_data.user.model_dump_json())

        if auth_data.device_id:
            await self.storage.set_item(STORAGE_KEYS["CLIENT_DEVICE_ID"], auth_data.device_id)
        if auth_data.device_secret:
            await self.storage.set_item(
                STORAGE_KEYS["CLIENT_DEVICE_SECRET"], auth_data.device_secret
            )

        self._user = auth_data.user
        self._is_authenticated = True
        logger.info("Session saved successfully")

    async def logout(self) -> None:
        """
        Logout user and clear session data.

        Raises:
            ZoStorageError: If storage operations fail
        """
        await self._clear_session_data()
        self._user = None
        self._is_authenticated = False
        self._stop_auto_refresh()
        logger.info("User logged out")

    async def _clear_session_data(self) -> None:
        """
        Clear stored session data.

        Raises:
            ZoStorageError: If storage operations fail
        """
        await self.client._clear_session()

    def _start_auto_refresh(self) -> None:
        """Start the automatic token refresh loop."""
        if self._refresh_task and not self._refresh_task.done():
            logger.debug("Auto-refresh already running")
            return
        self._shutdown = False
        self._refresh_task = asyncio.create_task(self._refresh_loop())
        logger.debug("Auto-refresh loop started")

    def _stop_auto_refresh(self) -> None:
        """Stop the automatic token refresh loop."""
        self._shutdown = True
        if self._refresh_task and not self._refresh_task.done():
            self._refresh_task.cancel()
            self._refresh_task = None
            logger.debug("Auto-refresh loop stopped")

    async def _should_refresh_token(self) -> bool:
        """
        Check if token should be refreshed.

        Returns:
            True if token should be refreshed, False otherwise
        """
        try:
            expiry_str = await self.storage.get_item(STORAGE_KEYS["TOKEN_EXPIRY"])
            if not expiry_str:
                return False

            # Parse expiry time
            expiry_time = dateparser.parse(expiry_str)
            if not expiry_time:
                logger.warning(f"Failed to parse token expiry: {expiry_str}")
                return False

            # Refresh if less than 5 minutes until expiry
            time_until_expiry = expiry_time - datetime.now(expiry_time.tzinfo)
            should_refresh = time_until_expiry < timedelta(minutes=5)

            if should_refresh:
                logger.debug(f"Token expires in {time_until_expiry}, will refresh")

            return should_refresh

        except Exception as e:
            logger.warning(f"Error checking token expiry: {e}")
            return False

    async def _refresh_loop(self) -> None:
        """
        Automatic token refresh loop.

        Periodically checks if token needs refresh and refreshes if necessary.
        """
        interval_seconds = self._refresh_interval_ms / 1000

        while not self._shutdown:
            try:
                await asyncio.sleep(interval_seconds)

                if not self._is_authenticated:
                    logger.debug("Not authenticated, skipping refresh check")
                    continue

                should_refresh = await self._should_refresh_token()
                if should_refresh:
                    logger.info("Proactively refreshing token")
                    success = await self.client._refresh_token()
                    if success:
                        logger.info("Token refreshed successfully")
                    else:
                        logger.warning("Token refresh failed")
                        # On refresh failure, mark as unauthenticated
                        self._is_authenticated = False
                        break

            except asyncio.CancelledError:
                logger.debug("Refresh loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in refresh loop: {e}")
                # Continue loop despite errors
                await asyncio.sleep(interval_seconds)

    @property
    def user(self) -> ZoUser | None:
        """
        Get the current authenticated user.

        Returns:
            User object or None if not authenticated
        """
        return self._user

    @property
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._is_authenticated

    async def close(self) -> None:
        """
        Cleanup resources and close connections.

        Should be called when done using the SDK.
        """
        self._stop_auto_refresh()
        await self.client.close()
        logger.debug("SDK closed")
