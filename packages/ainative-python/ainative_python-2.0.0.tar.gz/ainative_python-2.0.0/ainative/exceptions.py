"""
AINative SDK Exception Classes

Custom exceptions for better error handling and debugging.
"""

from typing import Optional, Dict, Any


class AINativeException(Exception):
    """Base exception for all AINative SDK errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(AINativeException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, error_code="AUTH_ERROR")


class APIError(AINativeException):
    """Raised when API returns an error response."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message, error_code="API_ERROR")
        self.status_code = status_code
        self.response_body = response_body


class NetworkError(AINativeException):
    """Raised when network-related errors occur."""
    
    def __init__(self, message: str = "Network error occurred"):
        super().__init__(message, error_code="NETWORK_ERROR")


class ValidationError(AINativeException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field


class RateLimitError(AINativeException):
    """Raised when API rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, error_code="RATE_LIMIT")
        self.retry_after = retry_after


class ResourceNotFoundError(AINativeException):
    """Raised when requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message, error_code="NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class TimeoutError(AINativeException):
    """Raised when operation times out."""
    
    def __init__(self, message: str = "Operation timed out"):
        super().__init__(message, error_code="TIMEOUT")