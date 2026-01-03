from typing import Any

from .client import ZoApiClient
from .exceptions import ZoAPIError, ZoProfileError, ZoValidationError
from .types import ZoProfileResponse
from .utils import logger


class ZoProfile:
    """Profile management module for ZoPassport SDK."""

    def __init__(self, client: ZoApiClient) -> None:
        """
        Initialize profile module.

        Args:
            client: ZoApiClient instance for making API requests
        """
        self.client = client

    async def get_profile(self, access_token: str) -> dict[str, Any]:
        """
        Get user profile information.

        Args:
            access_token: Valid access token

        Returns:
            Dictionary with success status and profile data

        Raises:
            ZoProfileError: If profile fetch fails
            ZoAPIError: If API returns an error
        """
        try:
            response = await self.client.request(
                "GET",
                "/api/v1/profile/me/",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code >= 400:
                data = response.json()
                error_msg = data.get("detail") or data.get("message") or "Failed to fetch profile"
                raise ZoAPIError(
                    error_msg,
                    status_code=response.status_code,
                    details=data,
                )

            data = response.json()

            # Validate with Pydantic
            try:
                profile = ZoProfileResponse(**data)
            except Exception as e:
                raise ZoValidationError(
                    f"Failed to parse profile response: {str(e)}",
                    details={"data": data},
                ) from e

            return {"success": True, "profile": profile}

        except (ZoAPIError, ZoValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching profile: {e}")
            raise ZoProfileError(
                f"Failed to fetch profile: {str(e)}",
                details={"error_type": type(e).__name__},
            ) from e

    async def update_profile(self, access_token: str, updates: dict[str, Any]) -> dict[str, Any]:
        """
        Update user profile information.

        Args:
            access_token: Valid access token
            updates: Dictionary of fields to update

        Returns:
            Dictionary with success status and updated profile data

        Raises:
            ZoProfileError: If profile update fails
            ZoAPIError: If API returns an error
            ZoValidationError: If update data is invalid
        """
        if not updates:
            raise ZoValidationError("Update data cannot be empty")

        try:
            response = await self.client.request(
                "POST",
                "/api/v1/profile/me/",
                json=updates,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code >= 400:
                data = response.json()
                error_msg = data.get("detail") or data.get("message") or "Failed to update profile"
                raise ZoAPIError(
                    error_msg,
                    status_code=response.status_code,
                    details=data,
                )

            data = response.json()

            # Validate with Pydantic
            try:
                profile = ZoProfileResponse(**data)
            except Exception as e:
                raise ZoValidationError(
                    f"Failed to parse updated profile response: {str(e)}",
                    details={"data": data},
                ) from e

            return {"success": True, "profile": profile}

        except (ZoAPIError, ZoValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating profile: {e}")
            raise ZoProfileError(
                f"Failed to update profile: {str(e)}",
                details={"error_type": type(e).__name__, "updates": updates},
            ) from e
