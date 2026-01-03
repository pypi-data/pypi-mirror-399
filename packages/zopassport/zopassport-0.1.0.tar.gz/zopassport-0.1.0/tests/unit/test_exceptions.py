"""Tests for exception classes."""

from zopassport.exceptions import (
    ZoAPIError,
    ZoAuthenticationError,
    ZoAvatarError,
    ZoEncryptionError,
    ZoNetworkError,
    ZoPassportError,
    ZoProfileError,
    ZoRateLimitError,
    ZoRetryExhaustedError,
    ZoStorageError,
    ZoTokenError,
    ZoTokenExpiredError,
    ZoValidationError,
    ZoWalletError,
)


class TestExceptions:
    """Test exception classes and hierarchy."""

    def test_base_exception(self):
        """Test base ZoPassportError."""
        error = ZoPassportError("Test error", details={"key": "value"})
        assert str(error) == "Test error | Details: {'key': 'value'}"
        assert error.message == "Test error"
        assert error.details == {"key": "value"}

    def test_base_exception_without_details(self):
        """Test base exception without details."""
        error = ZoPassportError("Test error")
        assert str(error) == "Test error"
        assert error.details == {}

    def test_authentication_error_inheritance(self):
        """Test authentication error inherits from base."""
        error = ZoAuthenticationError("Auth failed")
        assert isinstance(error, ZoPassportError)
        assert isinstance(error, Exception)

    def test_token_error_inheritance(self):
        """Test token error hierarchy."""
        error = ZoTokenExpiredError("Token expired")
        assert isinstance(error, ZoTokenError)
        assert isinstance(error, ZoAuthenticationError)
        assert isinstance(error, ZoPassportError)

    def test_network_error_with_status_code(self):
        """Test network error with status code."""
        error = ZoNetworkError("Network error", status_code=500)
        assert error.status_code == 500
        assert "Status: 500" in str(error)

    def test_api_error_inherits_network_error(self):
        """Test API error inheritance."""
        error = ZoAPIError("API error", status_code=404)
        assert isinstance(error, ZoNetworkError)
        assert error.status_code == 404

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry after."""
        error = ZoRateLimitError("Rate limited", retry_after=60)
        assert error.retry_after == 60
        assert error.status_code == 429
        assert "Retry after: 60s" in str(error)

    def test_rate_limit_error_without_retry_after(self):
        """Test rate limit error without retry after."""
        error = ZoRateLimitError("Rate limited")
        assert error.retry_after is None
        assert error.status_code == 429

    def test_retry_exhausted_error(self):
        """Test retry exhausted error."""
        last_error = ConnectionError("Connection failed")
        error = ZoRetryExhaustedError(
            "All retries failed",
            attempts=3,
            last_error=last_error,
        )
        assert error.attempts == 3
        assert error.last_error == last_error
        assert "Attempts: 3" in str(error)
        assert "Connection failed" in str(error)

    def test_storage_error_types(self):
        """Test storage error types."""
        storage_error = ZoStorageError("Storage failed")
        encryption_error = ZoEncryptionError("Encryption failed")

        assert isinstance(storage_error, ZoPassportError)
        assert isinstance(encryption_error, ZoStorageError)
        assert isinstance(encryption_error, ZoPassportError)

    def test_service_specific_errors(self):
        """Test service-specific errors."""
        wallet_error = ZoWalletError("Wallet error")
        profile_error = ZoProfileError("Profile error")
        avatar_error = ZoAvatarError("Avatar error")

        assert isinstance(wallet_error, ZoPassportError)
        assert isinstance(profile_error, ZoPassportError)
        assert isinstance(avatar_error, ZoPassportError)

    def test_exception_catch_all(self):
        """Test catching all SDK exceptions."""
        exceptions = [
            ZoAuthenticationError("Auth"),
            ZoNetworkError("Network"),
            ZoValidationError("Validation"),
            ZoStorageError("Storage"),
            ZoWalletError("Wallet"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except ZoPassportError as e:
                assert isinstance(e, ZoPassportError)
