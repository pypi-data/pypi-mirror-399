"""Tests for type definitions and Pydantic models."""

from zopassport.types import ZoAuthResponse, ZoProfileResponse, ZoUser


class TestTypes:
    """Tests for Pydantic models."""

    def test_zo_user_validation(self):
        """Test ZoUser model validation."""
        user_data = {"id": "123", "first_name": "Test", "email_address": "test@example.com"}
        user = ZoUser(**user_data)  # type: ignore[arg-type]
        assert user.id == "123"
        assert user.first_name == "Test"
        assert user.last_name is None

    def test_zo_auth_response_validation(self):
        """Test ZoAuthResponse validation."""
        user = ZoUser(id="123")
        data = {
            "user": user,
            "access_token": "access",
            "refresh_token": "refresh",
            "access_token_expiry": "expiry",
            "refresh_token_expiry": "expiry",
        }
        response = ZoAuthResponse(**data)  # type: ignore[arg-type]
        assert response.user.id == "123"
        assert response.access_token == "access"

    def test_zo_profile_response_validation(self):
        """Test ZoProfileResponse validation."""
        data = {"id": "123", "first_name": "Test", "bio": "Bio"}
        profile = ZoProfileResponse(**data)  # type: ignore[arg-type]
        assert profile.id == "123"
        assert profile.bio == "Bio"
