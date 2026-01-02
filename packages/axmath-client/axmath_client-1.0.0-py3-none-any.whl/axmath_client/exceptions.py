"""
Exception classes for AxMath client.
"""


class AxMathError(Exception):
    """Base exception for AxMath client errors."""
    pass


class AuthenticationError(AxMathError):
    """Raised when API key authentication fails."""
    pass


class RateLimitError(AxMathError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class ServerError(AxMathError):
    """Raised when server returns an error."""
    pass


class NetworkError(AxMathError):
    """Raised when network request fails."""
    pass


class ValidationError(AxMathError):
    """Raised when request validation fails."""
    pass
