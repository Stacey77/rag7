"""
Custom exceptions for the Ragamuffin SDK.
"""


class RagamuffinError(Exception):
    """Base exception for Ragamuffin SDK errors."""

    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(RagamuffinError):
    """Raised when authentication fails."""

    pass


class APIError(RagamuffinError):
    """Raised when an API request fails."""

    pass


class ValidationError(RagamuffinError):
    """Raised when input validation fails."""

    pass


class NotFoundError(RagamuffinError):
    """Raised when a resource is not found."""

    pass


class RateLimitError(RagamuffinError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
