"""Exception classes for SiloWorker SDK."""

from typing import Any, Dict, Optional


class SiloWorkerError(Exception):
    """Base exception for SiloWorker SDK errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.details = details


class ValidationError(SiloWorkerError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class AuthenticationError(SiloWorkerError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Invalid API key") -> None:
        super().__init__(message, 401, "AUTHENTICATION_ERROR")


class RateLimitError(SiloWorkerError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, 429, "RATE_LIMIT_ERROR")
