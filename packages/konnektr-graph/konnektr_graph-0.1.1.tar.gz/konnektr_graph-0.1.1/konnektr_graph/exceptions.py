# konnektr_graph/exceptions.py
"""
Custom exceptions for Konnektr Graph SDK.
"""
from typing import Optional


class KonnektrGraphError(Exception):
    """Base exception for all Konnektr Graph errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class HttpResponseError(KonnektrGraphError):
    """Raised when an HTTP response is not successful."""

    pass


class ResourceNotFoundError(HttpResponseError):
    """Raised when a resource is not found (404)."""

    pass


class ResourceExistsError(HttpResponseError):
    """Raised when a resource already exists (409)."""

    pass


class AuthenticationError(HttpResponseError):
    """Raised when authentication fails (401/403)."""

    pass


class ValidationError(KonnektrGraphError):
    """Raised when input validation fails."""

    pass
