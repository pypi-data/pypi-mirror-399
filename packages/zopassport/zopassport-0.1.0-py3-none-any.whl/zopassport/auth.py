from typing import Any

from .client import ZoApiClient
from .exceptions import ZoAPIError, ZoAuthenticationError, ZoNetworkError, ZoValidationError
from .types import ZoAuthResponse
from .utils import logger


class ZoAuth:
    """Authentication module for ZoPassport SDK."""

    def __init__(self, client: ZoApiClient) -> None:
        """
        Initialize authentication module.

        Args:
            client: ZoApiClient instance for making API requests
        """
        self.client = client

    async def send_otp(self, country_code: str, phone_number: str) -> dict[str, Any]:
        """
        Send OTP to phone number (Step 1 of authentication).

        Args:
            country_code: Mobile country code (e.g., "91" for India)
            phone_number: Phone number without country code

        Returns:
            Dictionary with success status and message

        Raises:
            ZoValidationError: If inputs are invalid
            ZoNetworkError: If network request fails
            ZoAPIError: If API returns an error
        """
        if not country_code or not phone_number:
            raise ZoValidationError(
                "Country code and phone number are required",
                details={"country_code": country_code, "phone_number": phone_number},
            )

        try:
            payload = {
                "mobile_country_code": country_code,
                "mobile_number": phone_number,
                "message_channel": "",  # Empty string as per ZO API spec
            }

            response = await self.client.request(
                "POST", "/api/v1/auth/login/mobile/otp/", json=payload
            )

            data = response.json()
            if 200 <= response.status_code < 300:
                return {"success": True, "message": data.get("message", "OTP sent successfully")}

            raise ZoAPIError(
                data.get("message", "Failed to send OTP"),
                status_code=response.status_code,
                details=data,
            )

        except (ZoNetworkError, ZoAPIError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in send_otp: {e}")
            raise ZoAuthenticationError(
                f"Failed to send OTP: {str(e)}", details={"error_type": type(e).__name__}
            ) from e

    async def verify_otp(self, country_code: str, phone_number: str, otp: str) -> dict[str, Any]:
        """
        Verify OTP and authenticate user (Step 2 of authentication).

        Args:
            country_code: Mobile country code (e.g., "91" for India)
            phone_number: Phone number without country code
            otp: One-time password received via SMS

        Returns:
            Dictionary with success status and authentication data

        Raises:
            ZoValidationError: If inputs are invalid
            ZoAuthenticationError: If OTP verification fails
            ZoNetworkError: If network request fails
            ZoAPIError: If API returns an error
        """
        if not country_code or not phone_number or not otp:
            raise ZoValidationError(
                "Country code, phone number, and OTP are required",
                details={"country_code": country_code, "phone_number": phone_number},
            )

        try:
            payload = {
                "mobile_country_code": country_code,
                "mobile_number": phone_number,
                "otp": otp,
            }

            response = await self.client.request("POST", "/api/v1/auth/login/mobile/", json=payload)

            if response.status_code >= 400:
                error_msg = self._extract_error_message(response)
                raise ZoAuthenticationError(
                    error_msg,
                    details={"status_code": response.status_code, "response": response.json()},
                )

            data = response.json()

            # Handle double-encoded JSON (rare but possible)
            if isinstance(data, str):
                import json

                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    raise ZoValidationError("Invalid response format from API") from e

            # Validate response structure
            if not data or "user" not in data or "access_token" not in data:
                raise ZoValidationError(
                    "Invalid response structure from API",
                    details={"response_keys": list(data.keys()) if data else []},
                )

            # Parse and validate with Pydantic
            try:
                auth_response = ZoAuthResponse(**data)
            except Exception as e:
                raise ZoValidationError(
                    f"Failed to parse authentication response: {str(e)}", details={"data": data}
                ) from e

            return {"success": True, "data": auth_response}

        except (ZoNetworkError, ZoAPIError, ZoAuthenticationError, ZoValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in verify_otp: {e}")
            raise ZoAuthenticationError(
                f"Failed to verify OTP: {str(e)}", details={"error_type": type(e).__name__}
            ) from e

    async def check_login_status(self, access_token: str) -> dict[str, Any]:
        """
        Check if the access token is still valid.

        Args:
            access_token: Access token to check

        Returns:
            Dictionary with success status and authentication state

        Raises:
            ZoNetworkError: If network request fails
        """
        try:
            response = await self.client.request(
                "GET",
                "/api/v1/auth/login/check/",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            data = response.json()
            return {"success": True, "is_authenticated": data.get("authenticated") is True}
        except Exception as e:
            logger.warning(f"Login status check failed: {e}")
            return {"success": False, "is_authenticated": False}

    def _extract_error_message(self, response: Any) -> str:
        """
        Extract error message from API response.

        Args:
            response: HTTP response object

        Returns:
            Human-readable error message
        """
        try:
            data = response.json()
            if "errors" in data and isinstance(data["errors"], list) and data["errors"]:
                return str(data["errors"][0])
            if "detail" in data:
                return str(data["detail"])
            if "message" in data:
                return str(data["message"])
            if "error" in data:
                return str(data["error"])
        except Exception:
            pass
        return "Authentication failed"
