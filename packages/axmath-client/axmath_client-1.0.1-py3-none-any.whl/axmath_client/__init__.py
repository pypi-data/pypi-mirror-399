"""
AxMath Client - Python client for AxMath theorem proving API.

This is a thin client that connects to the private AxMath service.
Requires API key for authentication.

Example:
    >>> from axmath_client import AxMath
    >>> client = AxMath(api_key="axm_abc123...")
    >>> result = client.prove("∀ n : ℕ, n + 0 = n")
    >>> if result.verified:
    ...     print(result.lean_code)
"""

from .client import AxMath
from .models import (
    ProveResult,
    SearchResult,
    SolveResult,
    Premise,
    VerificationDetails,
)
from .exceptions import (
    AxMathError,
    AuthenticationError,
    RateLimitError,
    ServerError,
)

__version__ = "1.0.1"
__author__ = "Dirk Englund"
__all__ = [
    "AxMath",
    "ProveResult",
    "SearchResult",
    "SolveResult",
    "Premise",
    "VerificationDetails",
    "AxMathError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
]
