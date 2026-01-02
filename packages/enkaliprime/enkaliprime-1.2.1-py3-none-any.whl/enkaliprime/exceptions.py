"""
Custom exceptions for the EnkaliPrime Python SDK.
"""

from typing import Any, Dict, Optional


class EnkaliPrimeError(Exception):
    """Base exception for all EnkaliPrime SDK errors."""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class ConnectionError(EnkaliPrimeError):
    """Raised when there's an issue connecting to the API."""
    
    def __init__(
        self,
        message: str = "Failed to connect to EnkaliPrime API",
        code: Optional[str] = "CONNECTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class AuthenticationError(EnkaliPrimeError):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        code: Optional[str] = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class APIError(EnkaliPrimeError):
    """Raised when the API returns an error response."""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        super().__init__(message, code or f"HTTP_{status_code}", details)
    
    def __str__(self) -> str:
        return f"[HTTP {self.status_code}] {self.message}"


class StreamingError(EnkaliPrimeError):
    """Raised when there's an error during streaming response handling."""
    
    def __init__(
        self,
        message: str = "Error processing streaming response",
        code: Optional[str] = "STREAMING_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class ValidationError(EnkaliPrimeError):
    """Raised when request validation fails."""
    
    def __init__(
        self,
        message: str = "Validation error",
        code: Optional[str] = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)


class SessionError(EnkaliPrimeError):
    """Raised when there's an issue with session management."""
    
    def __init__(
        self,
        message: str = "Session error",
        code: Optional[str] = "SESSION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, details)

