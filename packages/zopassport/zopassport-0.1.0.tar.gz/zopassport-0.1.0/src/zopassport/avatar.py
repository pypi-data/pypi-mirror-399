import asyncio
from collections.abc import Callable
from typing import Any

from .client import ZoApiClient
from .exceptions import ZoAPIError, ZoAvatarError, ZoValidationError
from .utils import logger


class ZoAvatar:
    """Avatar generation module for ZoPassport SDK."""

    def __init__(self, client: ZoApiClient) -> None:
        """
        Initialize avatar module.

        Args:
            client: ZoApiClient instance for making API requests
        """
        self.client = client

    async def generate_avatar(self, access_token: str, body_type: str) -> dict[str, Any]:
        """
        Start avatar generation task.

        Args:
            access_token: Valid access token
            body_type: Avatar body type ('bro' or 'bae')

        Returns:
            Dictionary with success status, task_id, and status

        Raises:
            ZoValidationError: If body_type is invalid
            ZoAvatarError: If avatar generation fails to start
            ZoAPIError: If API returns an error
        """
        if body_type not in ["bro", "bae"]:
            raise ZoValidationError(
                f"Invalid body_type: {body_type}. Must be 'bro' or 'bae'",
                details={"body_type": body_type},
            )

        try:
            response = await self.client.request(
                "POST",
                "/api/v1/avatar/generate/",
                json={"body_type": body_type},
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code >= 400:
                data = response.json()
                error_msg = data.get("detail") or data.get("message") or "Failed to generate avatar"
                raise ZoAPIError(
                    error_msg,
                    status_code=response.status_code,
                    details=data,
                )

            data = response.json()
            return {
                "success": True,
                "task_id": data.get("task_id"),
                "status": data.get("status"),
            }

        except (ZoAPIError, ZoValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating avatar: {e}")
            raise ZoAvatarError(
                f"Failed to generate avatar: {str(e)}",
                details={"error_type": type(e).__name__, "body_type": body_type},
            ) from e

    async def get_avatar_status(self, access_token: str, task_id: str) -> dict[str, Any]:
        """
        Get status of avatar generation task.

        Args:
            access_token: Valid access token
            task_id: Task ID from generate_avatar

        Returns:
            Dictionary with success status, generation status, and avatar_url if ready

        Raises:
            ZoValidationError: If task_id is missing
            ZoAvatarError: If status check fails
            ZoAPIError: If API returns an error
        """
        if not task_id:
            raise ZoValidationError("task_id is required")

        try:
            response = await self.client.request(
                "GET",
                f"/api/v1/avatar/status/{task_id}/",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code >= 400:
                data = response.json()
                error_msg = (
                    data.get("detail") or data.get("message") or "Failed to get avatar status"
                )
                raise ZoAPIError(
                    error_msg,
                    status_code=response.status_code,
                    details=data,
                )

            data = response.json()
            result_data = data.get("result", {})
            return {
                "success": True,
                "status": data.get("status"),
                "avatar_url": result_data.get("avatar_url") if result_data else None,
            }

        except (ZoAPIError, ZoValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting avatar status: {e}")
            raise ZoAvatarError(
                f"Failed to get avatar status: {str(e)}",
                details={"error_type": type(e).__name__, "task_id": task_id},
            ) from e

    async def poll_avatar_status(
        self,
        access_token: str,
        task_id: str,
        on_progress: Callable[[str], None] | None = None,
        on_complete: Callable[[str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        max_attempts: int = 30,
        interval_seconds: float = 2.0,
    ) -> None:
        """
        Poll avatar generation status until completion or timeout.

        Args:
            access_token: Valid access token
            task_id: Task ID from generate_avatar
            on_progress: Callback for status updates (can be async)
            on_complete: Callback when avatar is ready with URL (can be async)
            on_error: Callback on error with error message (can be async)
            max_attempts: Maximum polling attempts (default: 30)
            interval_seconds: Seconds between polls (default: 2.0)

        Raises:
            ZoAvatarError: If polling times out or fails
        """
        attempts = 0
        while attempts < max_attempts:
            attempts += 1

            try:
                result = await self.get_avatar_status(access_token, task_id)
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Avatar status check failed: {error_msg}")
                if on_error:
                    if asyncio.iscoroutinefunction(on_error):
                        await on_error(error_msg)
                    else:
                        on_error(error_msg)
                raise ZoAvatarError(
                    f"Avatar status polling failed: {error_msg}",
                    details={"task_id": task_id, "attempts": attempts},
                ) from e

            if not result["success"]:
                error_msg = result.get("error", "Unknown error")
                if on_error:
                    if asyncio.iscoroutinefunction(on_error):
                        await on_error(error_msg)
                    else:
                        on_error(error_msg)
                return

            status = result.get("status", "unknown")

            if on_progress:
                if asyncio.iscoroutinefunction(on_progress):
                    await on_progress(status)
                else:
                    on_progress(status)

            if status == "completed" and result.get("avatar_url"):
                if on_complete:
                    if asyncio.iscoroutinefunction(on_complete):
                        await on_complete(result["avatar_url"])
                    else:
                        on_complete(result["avatar_url"])
                return

            if status == "failed":
                error_msg = "Avatar generation failed"
                if on_error:
                    if asyncio.iscoroutinefunction(on_error):
                        await on_error(error_msg)
                    else:
                        on_error(error_msg)
                raise ZoAvatarError(error_msg, details={"task_id": task_id})

            await asyncio.sleep(interval_seconds)

        # Timeout
        error_msg = "Avatar generation timed out"
        if on_error:
            if asyncio.iscoroutinefunction(on_error):
                await on_error(error_msg)
            else:
                on_error(error_msg)
        raise ZoAvatarError(
            error_msg,
            details={"task_id": task_id, "max_attempts": max_attempts},
        )
