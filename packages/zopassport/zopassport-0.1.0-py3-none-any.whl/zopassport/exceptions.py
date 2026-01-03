"""
Custom exceptions for ZoPassport SDK.

This module defines the exception hierarchy for the SDK, providing
specific error types for different failure scenarios.
"""

from typing import Any


class ZoPassportError(Exception):
    """
    Base exception for all ZoPassport SDK errors.

    All custom exceptions in the SDK inherit from this base class,
    allowing users to catch all SDK-specific errors with a single except clause.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary containing additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ZoAuthenticationError(ZoPassportError):
    """
    Raised when authentication fails.

    This includes OTP send failures, OTP verification failures,
    invalid credentials, and authentication state issues.
    """

    pass


class ZoTokenError(ZoAuthenticationError):
    """
    Raised when there are issues with authentication tokens.

    This includes missing tokens, invalid tokens, and token format errors.
    """

    pass


class ZoTokenExpiredError(ZoTokenError):
    """
    Raised when an authentication token has expired.

    This typically triggers an automatic token refresh attempt.
    """

    pass


class ZoTokenRefreshError(ZoTokenError):
    """
    Raised when token refresh fails.

    This usually means the user needs to re-authenticate.
    """

    pass


class ZoNetworkError(ZoPassportError):
    """
    Raised when network-related errors occur.

    This includes connection failures, timeouts, and HTTP errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the network error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if applicable
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, details)
        self.status_code = status_code

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.status_code:
            return f"{base_msg} | Status: {self.status_code}"
        return base_msg


class ZoAPIError(ZoNetworkError):
    """
    Raised when the API returns an error response.

    This includes 4xx and 5xx HTTP status codes.
    """

    pass


class ZoRateLimitError(ZoNetworkError):
    """
    Raised when API rate limits are exceeded.

    Contains information about when the request can be retried.
    """

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the rate limit error.

        Args:
            message: Human-readable error message
            retry_after: Seconds to wait before retrying (from Retry-After header)
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} | Retry after: {self.retry_after}s"
        return base_msg


class ZoConnectionError(ZoNetworkError):
    """
    Raised when a connection to the API cannot be established.

    This includes DNS failures, connection timeouts, and refused connections.
    """

    pass


class ZoTimeoutError(ZoNetworkError):
    """
    Raised when a request times out.

    The request took longer than the configured timeout period.
    """

    pass


class ZoValidationError(ZoPassportError):
    """
    Raised when data validation fails.

    This includes Pydantic validation errors and custom validation failures.
    """

    pass


class ZoStorageError(ZoPassportError):
    """
    Raised when storage operations fail.

    This includes file I/O errors, encryption/decryption errors,
    and keyring access failures.
    """

    pass


class ZoEncryptionError(ZoStorageError):
    """
    Raised when encryption or decryption operations fail.

    This could be due to invalid keys, corrupted data, or algorithm errors.
    """

    pass


class ZoConfigurationError(ZoPassportError):
    """
    Raised when there are configuration issues.

    This includes missing required configuration, invalid configuration values,
    or incompatible settings.
    """

    pass


class ZoWalletError(ZoPassportError):
    """
    Raised when wallet operations fail.

    This includes balance fetching failures, transaction errors,
    and blockchain RPC errors.
    """

    pass


class ZoProfileError(ZoPassportError):
    """
    Raised when profile operations fail.

    This includes profile fetch failures and update errors.
    """

    pass


class ZoAvatarError(ZoPassportError):
    """
    Raised when avatar operations fail.

    This includes avatar generation failures and status check errors.
    """

    pass


class ZoRetryExhaustedError(ZoNetworkError):
    """
    Raised when all retry attempts have been exhausted.

    The operation failed after the maximum number of retry attempts.
    """

    def __init__(
        self,
        message: str,
        attempts: int,
        last_error: Exception | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the retry exhausted error.

        Args:
            message: Human-readable error message
            attempts: Number of attempts made
            last_error: The exception from the last failed attempt
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, details=details)
        self.attempts = attempts
        self.last_error = last_error

    def __str__(self) -> str:
        base_msg = super().__str__()
        error_info = f" | Attempts: {self.attempts}"
        if self.last_error:
            error_info += f" | Last error: {str(self.last_error)}"
        return base_msg + error_info
