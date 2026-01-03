"""Tests for NewsMesh SDK exceptions."""

import pytest

from newsmesh.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NewsMeshError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    raise_for_error,
)


class TestExceptions:
    """Tests for exception classes."""

    def test_newsmesh_error_str(self):
        """Test NewsMeshError string representation."""
        error = NewsMeshError("Test error", code="testCode", status_code=400)
        assert "Test error" in str(error)
        assert "(code: testCode)" in str(error)
        assert "[HTTP 400]" in str(error)

    def test_newsmesh_error_minimal(self):
        """Test NewsMeshError with minimal args."""
        error = NewsMeshError("Simple error")
        assert str(error) == "Simple error"
        assert error.code is None
        assert error.status_code is None

    def test_rate_limit_error_retry_after(self):
        """Test RateLimitError with retry_after."""
        error = RateLimitError(
            "Rate limited",
            code="dailyLimitExceeded",
            status_code=429,
            retry_after=60,
        )
        assert error.retry_after == 60


class TestRaiseForError:
    """Tests for raise_for_error function."""

    def test_authentication_error_api_key_missing(self):
        """Test raising AuthenticationError for missing API key."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_error(
                {"status": "error", "code": "apiKeyMissing", "message": "API key is missing"},
                401,
            )
        assert exc_info.value.code == "apiKeyMissing"

    def test_authentication_error_invalid_key(self):
        """Test raising AuthenticationError for invalid API key."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_error(
                {"status": "error", "code": "invalidApiKey", "message": "Invalid API key"},
                401,
            )
        assert exc_info.value.code == "invalidApiKey"

    def test_forbidden_error(self):
        """Test raising ForbiddenError."""
        with pytest.raises(ForbiddenError):
            raise_for_error(
                {"status": "error", "code": "forbidden", "message": "Access forbidden"},
                403,
            )

    def test_not_found_error(self):
        """Test raising NotFoundError."""
        with pytest.raises(NotFoundError):
            raise_for_error(
                {"status": "error", "code": "articleNotFound", "message": "Not found"},
                404,
            )

    def test_validation_error(self):
        """Test raising ValidationError."""
        for code in ["invalidFromDate", "invalidToDate", "queryMissing", "queryTooLong"]:
            with pytest.raises(ValidationError) as exc_info:
                raise_for_error(
                    {"status": "error", "code": code, "message": "Validation error"},
                    400,
                )
            assert exc_info.value.code == code

    def test_rate_limit_error(self):
        """Test raising RateLimitError."""
        with pytest.raises(RateLimitError):
            raise_for_error(
                {"status": "error", "code": "dailyLimitExceeded", "message": "Limit exceeded"},
                429,
            )

    def test_server_error(self):
        """Test raising ServerError."""
        with pytest.raises(ServerError):
            raise_for_error(
                {"status": "error", "code": "searchError", "message": "Search failed"},
                500,
            )

    def test_unknown_error_code(self):
        """Test raising base NewsMeshError for unknown codes."""
        with pytest.raises(NewsMeshError) as exc_info:
            raise_for_error(
                {"status": "error", "code": "unknownCode", "message": "Unknown error"},
                500,
            )
        assert type(exc_info.value) is NewsMeshError

    def test_no_error(self):
        """Test that no error is raised for success response."""
        # Should not raise
        raise_for_error({"status": "success", "data": []}, 200)
