from typing import Any

from pydantic import BaseModel


class ZoAvatar(BaseModel):
    """User avatar information."""

    status: str
    image: str | None = None


class ZoUser(BaseModel):
    """Zo World user profile."""

    id: str
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    date_of_birth: str | None = None
    place_name: str | None = None
    body_type: str | None = None
    pfp_image: str | None = None
    email_address: str | None = None
    mobile_country_code: str | None = None
    mobile_number: str | None = None
    wallet_address: str | None = None
    membership: str | None = None
    cultures: list[str] | None = None
    avatar: ZoAvatar | None = None
    role: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ZoProfileResponse(BaseModel):
    """User profile API response."""

    id: str
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    date_of_birth: str | None = None
    location: dict[str, Any] | None = None
    body_type: str | None = None
    pfp_image: str | None = None
    email_address: str | None = None
    mobile_country_code: str | None = None
    mobile_number: str | None = None
    wallet_address: str | None = None
    zo_membership: str | None = None
    cultures: list[str] | None = None
    avatar: ZoAvatar | None = None
    founder_nfts: list[Any] | None = None
    founder_nfts_count: int | None = None
    role: str | None = None


class ZoAuthResponse(BaseModel):
    """Authentication API response."""

    user: ZoUser
    access_token: str
    refresh_token: str
    access_token_expiry: str
    refresh_token_expiry: str
    device_id: str | None = None
    device_secret: str | None = None


class ZoTokenRefreshResponse(BaseModel):
    """Token refresh API response."""

    access: str
    refresh: str
    access_expiry: str
    refresh_expiry: str


class ZoErrorResponse(BaseModel):
    """Standard API error response."""

    success: bool | None = False
    error: str | None = None
    message: str | None = None
    detail: str | None = None
    errors: list[str] | None = None


class ZoAvatarGenerateResponse(BaseModel):
    """Avatar generation initiation response."""

    task_id: str
    status: str


class ZoAvatarStatusResponse(BaseModel):
    """Avatar generation status response."""

    task_id: str
    status: str
    result: dict[str, Any] | None = None
