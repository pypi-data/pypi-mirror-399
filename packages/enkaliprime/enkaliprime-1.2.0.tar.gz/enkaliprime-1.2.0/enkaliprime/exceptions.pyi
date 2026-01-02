"""
Type stubs for EnkaliPrime exceptions.
Provides comprehensive type information for error handling.
"""

from typing import Any, Dict, Optional

class EnkaliPrimeError(Exception):
    """Base exception for all EnkaliPrime SDK errors."""
    message: str
    code: Optional[str]
    details: Optional[Dict[str, Any]]

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None: ...

class ConnectionError(EnkaliPrimeError):
    """Raised when unable to connect to EnkaliPrime services.""" ...

class AuthenticationError(EnkaliPrimeError):
    """Raised when API key is invalid or expired.""" ...

class APIError(EnkaliPrimeError):
    """Raised when the API returns an error response."""
    status_code: Optional[int]

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None: ...

class StreamingError(EnkaliPrimeError):
    """Raised when there's an error during streaming.""" ...

class ValidationError(EnkaliPrimeError):
    """Raised when request parameters are invalid.""" ...

__all__ = [
    'EnkaliPrimeError',
    'ConnectionError',
    'AuthenticationError',
    'APIError',
    'StreamingError',
    'ValidationError',
]
