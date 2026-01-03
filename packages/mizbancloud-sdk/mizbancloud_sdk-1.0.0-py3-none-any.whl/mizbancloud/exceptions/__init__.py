"""MizbanCloud SDK Exceptions."""

from typing import Any, Dict, List, Optional


class MizbanCloudException(Exception):
    """Exception raised for MizbanCloud API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        fields: Optional[Dict[str, str]] = None,
        invalid_fields: Optional[List[str]] = None,
        missing_fields: Optional[List[str]] = None,
        response: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.fields = fields or {}
        self.invalid_fields = invalid_fields or []
        self.missing_fields = missing_fields or []
        self.response = response

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"MizbanCloudException(message={self.message!r}, status_code={self.status_code})"
