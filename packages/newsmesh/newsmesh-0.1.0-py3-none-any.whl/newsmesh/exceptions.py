"""Exception classes for the NewsMesh SDK."""

from typing import Optional


class NewsMeshError(Exception):
    """Base exception for all NewsMesh SDK errors.

    Attributes:
        message: Human-readable error message.
        code: API error code (e.g., "apiKeyMissing", "rateLimitExceeded").
        status_code: HTTP status code from the API response.
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.append(f"(code: {self.code})")
        if self.status_code:
            parts.append(f"[HTTP {self.status_code}]")
        return " ".join(parts)


class AuthenticationError(NewsMeshError):
    """Raised when API key is missing or invalid (HTTP 401)."""

    pass


class ForbiddenError(NewsMeshError):
    """Raised when access is forbidden, e.g., inactive API key (HTTP 403)."""

    pass


class NotFoundError(NewsMeshError):
    """Raised when a requested resource is not found (HTTP 404)."""

    pass


class ValidationError(NewsMeshError):
    """Raised when request parameters are invalid (HTTP 400)."""

    pass


class RateLimitError(NewsMeshError):
    """Raised when rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying, if provided by the API.
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, code, status_code)
        self.retry_after = retry_after


class ServerError(NewsMeshError):
    """Raised when the API returns a server error (HTTP 5xx)."""

    pass


# Mapping of API error codes to exception classes
ERROR_CODE_MAP = {
    # 401 - Authentication errors
    "apiKeyMissing": AuthenticationError,
    "invalidApiKey": AuthenticationError,
    # 403 - Forbidden
    "forbidden": ForbiddenError,
    # 404 - Not found
    "articleNotFound": NotFoundError,
    # 400 - Validation errors
    "invalidFromDate": ValidationError,
    "invalidToDate": ValidationError,
    "invalidCursor": ValidationError,
    "queryMissing": ValidationError,
    "queryTooLong": ValidationError,
    # 429 - Rate limit
    "dailyLimitExceeded": RateLimitError,
    "monthlyLimitExceeded": RateLimitError,
    # 5xx - Server errors
    "trendingUnavailable": ServerError,
    "trendingError": ServerError,
    "searchError": ServerError,
}


def raise_for_error(response_data: dict, status_code: int) -> None:
    """Raise an appropriate exception based on the API error response.

    Args:
        response_data: The JSON response from the API containing error details.
        status_code: The HTTP status code.

    Raises:
        NewsMeshError: An appropriate subclass based on the error code.
    """
    if response_data.get("status") != "error":
        return

    code = response_data.get("code", "")
    message = response_data.get("message", "An unknown error occurred")

    # Get the appropriate exception class
    exception_class = ERROR_CODE_MAP.get(code, NewsMeshError)

    # Handle rate limit errors specially to include retry_after
    if exception_class == RateLimitError:
        raise RateLimitError(
            message=message,
            code=code,
            status_code=status_code,
            retry_after=None,  # API doesn't currently provide this
        )

    raise exception_class(message=message, code=code, status_code=status_code)
