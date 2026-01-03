"""Tests for exception hierarchy."""

import pytest

from march_history.exceptions import (
    APIError,
    BadRequestError,
    ConflictError,
    MarchHistoryError,
    NetworkError,
    NotFoundError,
    RetryError,
    ServerError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test exception inheritance and hierarchy."""

    def test_base_exception(self):
        """Test base MarchHistoryError."""
        exc = MarchHistoryError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_api_error(self):
        """Test APIError with status code and response body."""
        response_body = {
            "error": "test_error",
            "message": "Test message",
            "details": [{"field": "test", "message": "Invalid"}],
        }
        exc = APIError("Test error", status_code=400, response_body=response_body)

        assert exc.message == "Test error"
        assert exc.status_code == 400
        assert exc.error_code == "test_error"
        assert len(exc.details) == 1
        assert str(exc) == "[400] Test error"

    def test_api_error_without_status(self):
        """Test APIError without status code."""
        exc = APIError("Test error")
        assert str(exc) == "Test error"
        assert exc.status_code is None

    def test_validation_error(self):
        """Test ValidationError (422)."""
        exc = ValidationError("Validation failed", 422, {})
        assert isinstance(exc, APIError)
        assert exc.status_code == 422

    def test_not_found_error(self):
        """Test NotFoundError (404)."""
        exc = NotFoundError("Resource not found", 404, {})
        assert isinstance(exc, APIError)
        assert exc.status_code == 404

    def test_conflict_error(self):
        """Test ConflictError (409)."""
        exc = ConflictError("Duplicate resource", 409, {})
        assert isinstance(exc, APIError)
        assert exc.status_code == 409

    def test_bad_request_error(self):
        """Test BadRequestError (400)."""
        exc = BadRequestError("Bad request", 400, {})
        assert isinstance(exc, APIError)
        assert exc.status_code == 400

    def test_server_error(self):
        """Test ServerError (500+)."""
        exc = ServerError("Internal server error", 500, {})
        assert isinstance(exc, APIError)
        assert exc.status_code == 500

    def test_network_error(self):
        """Test NetworkError."""
        exc = NetworkError("Connection failed")
        assert isinstance(exc, MarchHistoryError)
        assert str(exc) == "Connection failed"

    def test_retry_error(self):
        """Test RetryError with last exception."""
        last_exc = NetworkError("Connection failed")
        exc = RetryError("Max retries exceeded", last_exc)

        assert isinstance(exc, MarchHistoryError)
        assert exc.last_exception == last_exc
        assert "Connection failed" in str(exc)
        assert "Max retries exceeded" in str(exc)

    def test_api_error_with_details(self):
        """Test APIError detail extraction."""
        response_body = {
            "error": "validation_error",
            "message": "Validation failed",
            "details": [
                {"field": "name", "message": "Required field", "code": "required"},
                {"field": "email", "message": "Invalid email", "code": "invalid"},
            ],
        }
        exc = APIError("Validation failed", 422, response_body)

        assert exc.error_code == "validation_error"
        assert len(exc.details) == 2
        assert exc.details[0]["field"] == "name"
        assert exc.details[1]["field"] == "email"

    def test_exception_catching(self):
        """Test catching exceptions by type."""
        # Can catch specific type
        with pytest.raises(NotFoundError):
            raise NotFoundError("Not found", 404, {})

        # Can catch as APIError
        with pytest.raises(APIError):
            raise NotFoundError("Not found", 404, {})

        # Can catch as base exception
        with pytest.raises(MarchHistoryError):
            raise NotFoundError("Not found", 404, {})
