"""Tests for MizbanCloudException."""

import pytest
from mizbancloud import MizbanCloudException


class TestMizbanCloudException:
    """Tests for the exception class."""

    def test_exception_creation(self):
        """Test basic exception creation."""
        exc = MizbanCloudException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.status_code is None

    def test_exception_with_status_code(self):
        """Test exception with status code."""
        exc = MizbanCloudException("Not found", status_code=404)
        assert exc.status_code == 404
        assert exc.message == "Not found"

    def test_exception_with_fields(self):
        """Test exception with field errors."""
        exc = MizbanCloudException(
            "Validation failed",
            status_code=422,
            fields={"email": "Invalid email format"},
        )
        assert exc.fields == {"email": "Invalid email format"}

    def test_exception_with_invalid_fields(self):
        """Test exception with invalid fields list."""
        exc = MizbanCloudException(
            "Validation failed",
            status_code=422,
            invalid_fields=["email", "name"],
        )
        assert exc.invalid_fields == ["email", "name"]

    def test_exception_with_missing_fields(self):
        """Test exception with missing fields list."""
        exc = MizbanCloudException(
            "Missing required fields",
            status_code=422,
            missing_fields=["password"],
        )
        assert exc.missing_fields == ["password"]

    def test_exception_with_response(self):
        """Test exception with full response."""
        response_data = {"error": True, "code": "AUTH_FAILED"}
        exc = MizbanCloudException(
            "Authentication failed",
            status_code=401,
            response=response_data,
        )
        assert exc.response == response_data

    def test_exception_repr(self):
        """Test exception repr."""
        exc = MizbanCloudException("Test", status_code=500)
        assert "MizbanCloudException" in repr(exc)
        assert "500" in repr(exc)

    def test_exception_defaults(self):
        """Test exception default values."""
        exc = MizbanCloudException("Error")
        assert exc.fields == {}
        assert exc.invalid_fields == []
        assert exc.missing_fields == []
        assert exc.response is None
