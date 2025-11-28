"""
Ragamuffin Python SDK

Official Python client library for the Ragamuffin AI platform.
"""

from .client import RagamuffinClient
from .exceptions import (
    RagamuffinError,
    AuthenticationError,
    APIError,
    ValidationError,
    NotFoundError,
    RateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "RagamuffinClient",
    "RagamuffinError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
]
