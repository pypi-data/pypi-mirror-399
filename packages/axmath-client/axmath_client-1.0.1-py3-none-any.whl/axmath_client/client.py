"""
AxMath API client - connects to private AxMath service.
"""

import os
import httpx
from typing import Optional, List
from contextlib import asynccontextmanager

from .models import ProveResult, SearchResult, SolveResult
from .exceptions import (
    AuthenticationError,
    RateLimitError,
    ServerError,
    NetworkError,
    ValidationError,
)


class AxMath:
    """
    Client for AxMath theorem proving API.

    Requires API key for authentication. Get your API key at:
    https://axmath.yourdomain.com/auth/register

    Example:
        >>> from axmath_client import AxMath
        >>>
        >>> # Option 1: Pass API key directly
        >>> client = AxMath(api_key="axm_abc123...")
        >>>
        >>> # Option 2: Use environment variable
        >>> # export AXMATH_API_KEY="axm_abc123..."
        >>> client = AxMath()
        >>>
        >>> # Prove a theorem
        >>> result = client.prove("∀ n : ℕ, n + 0 = n")
        >>> if result.verified:
        ...     print("Proof verified!")
        ...     print(result.lean_code)
        >>>
        >>> # Search for premises
        >>> search_result = client.search("Cauchy-Schwarz inequality", k=5)
        >>> for premise in search_result.premises:
        ...     print(f"{premise.full_name}: {premise.similarity:.3f}")
        >>>
        >>> # Multi-agent problem solving
        >>> solve_result = client.solve(
        ...     "Prove sqrt(2) is irrational and verify numerically"
        ... )
        >>> print(solve_result.synthesis)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: float = 120.0,
    ):
        """
        Initialize AxMath client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                    AXMATH_API_KEY environment variable.
            api_url: Base URL for AxMath API. Defaults to production server.
                    Can also be set via AXMATH_API_URL environment variable.
            timeout: Default timeout for API requests in seconds.

        Raises:
            AuthenticationError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("AXMATH_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key parameter or set AXMATH_API_KEY environment variable.\n"
                "Get your API key at: https://axmath.yourdomain.com/auth/register"
            )

        self.api_url = (
            api_url or
            os.getenv("AXMATH_API_URL") or
            "https://axmath.dirkenglund.org"
        )

        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[httpx.Client] = None

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"axmath-client/1.0.0",
        }

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid API key. Get a new key at: https://axmath.yourdomain.com/auth/register"
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded. Upgrade your plan or try again later.",
                retry_after=int(retry_after) if retry_after else None
            )
        elif response.status_code == 422:
            raise ValidationError(f"Request validation failed: {response.text}")
        elif response.status_code >= 500:
            raise ServerError(f"Server error: {response.text}")
        elif response.status_code >= 400:
            raise ServerError(f"Request failed: {response.text}")

        response.raise_for_status()
        return response.json()

    def prove(
        self,
        statement: str,
        search_premises: bool = True,
        max_iterations: int = 10,
        timeout: Optional[float] = None,
    ) -> ProveResult:
        """
        Prove a theorem in LEAN 4.

        Args:
            statement: Theorem statement to prove (natural language or LEAN syntax)
            search_premises: Whether to search for relevant premises in mathlib4
            max_iterations: Maximum proving iterations
            timeout: Timeout in seconds (overrides default)

        Returns:
            ProveResult with verified status, LEAN code, and verification details

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            ServerError: If server returns an error
            NetworkError: If network request fails

        Example:
            >>> result = client.prove("Sum of two even numbers is even")
            >>> if result.verified:
            ...     print(result.lean_code)
        """
        if not self._sync_client:
            self._sync_client = httpx.Client(
                timeout=timeout or self.timeout,
                headers=self._get_headers()
            )

        try:
            response = self._sync_client.post(
                f"{self.api_url}/api/prove",
                json={
                    "statement": statement,
                    "search_premises": search_premises,
                    "max_iterations": max_iterations,
                    "timeout": timeout or self.timeout,
                }
            )

            data = self._handle_response(response)
            return ProveResult(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    def search(
        self,
        query: str,
        k: int = 10,
        use_tfidf_fallback: bool = True,
    ) -> SearchResult:
        """
        Search for relevant premises in mathlib4.

        Args:
            query: Search query (natural language or mathematical concept)
            k: Number of results to return
            use_tfidf_fallback: Use TF-IDF if FAISS fails

        Returns:
            SearchResult with matching premises and similarity scores

        Example:
            >>> result = client.search("Cauchy-Schwarz inequality", k=5)
            >>> for premise in result.premises:
            ...     print(f"{premise.full_name}: {premise.similarity:.3f}")
        """
        if not self._sync_client:
            self._sync_client = httpx.Client(
                timeout=self.timeout,
                headers=self._get_headers()
            )

        try:
            response = self._sync_client.post(
                f"{self.api_url}/api/search",
                json={
                    "query": query,
                    "k": k,
                    "use_tfidf_fallback": use_tfidf_fallback,
                }
            )

            data = self._handle_response(response)
            return SearchResult(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    def verify(self, lean_code: str) -> dict:
        """
        Verify LEAN 4 code compilation.

        Args:
            lean_code: LEAN 4 code to verify

        Returns:
            Verification result with errors, warnings, and exit code

        Example:
            >>> code = "theorem test : 2 + 2 = 4 := by rfl"
            >>> result = client.verify(code)
            >>> print(result)
        """
        if not self._sync_client:
            self._sync_client = httpx.Client(
                timeout=self.timeout,
                headers=self._get_headers()
            )

        try:
            response = self._sync_client.post(
                f"{self.api_url}/api/verify",
                json={"lean_code": lean_code}
            )

            return self._handle_response(response)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    def solve(
        self,
        query: str,
        timeout: Optional[float] = None,
    ) -> SolveResult:
        """
        Solve complex problem using multi-agent orchestration.

        Automatically routes to specialized agents (reasoning, proving, computation)
        and synthesizes results.

        Args:
            query: Problem description
            timeout: Timeout in seconds (default: 300)

        Returns:
            SolveResult with synthesis and task execution details

        Example:
            >>> result = client.solve(
            ...     "Prove that sqrt(2) is irrational and verify numerically"
            ... )
            >>> print(result.synthesis)
        """
        if not self._sync_client:
            self._sync_client = httpx.Client(
                timeout=timeout or 300.0,
                headers=self._get_headers()
            )

        try:
            response = self._sync_client.post(
                f"{self.api_url}/api/solve",
                json={
                    "query": query,
                    "timeout": timeout or 300.0,
                }
            )

            data = self._handle_response(response)
            return SolveResult(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    def get_usage(self) -> dict:
        """
        Get usage statistics for your API key.

        Returns:
            Usage statistics including request counts, success rates, and quotas

        Example:
            >>> usage = client.get_usage()
            >>> print(f"Requests today: {usage['daily_requests']}")
            >>> print(f"Remaining: {usage['daily_limit'] - usage['daily_requests']}")
        """
        if not self._sync_client:
            self._sync_client = httpx.Client(
                timeout=self.timeout,
                headers=self._get_headers()
            )

        try:
            response = self._sync_client.get(f"{self.api_url}/auth/usage")
            return self._handle_response(response)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    def close(self):
        """Close HTTP clients and clean up resources."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # Async API methods

    async def aprove(
        self,
        statement: str,
        search_premises: bool = True,
        max_iterations: int = 10,
        timeout: Optional[float] = None,
    ) -> ProveResult:
        """Async version of prove()."""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=timeout or self.timeout,
                headers=self._get_headers()
            )

        try:
            response = await self._client.post(
                f"{self.api_url}/api/prove",
                json={
                    "statement": statement,
                    "search_premises": search_premises,
                    "max_iterations": max_iterations,
                    "timeout": timeout or self.timeout,
                }
            )

            data = self._handle_response(response)
            return ProveResult(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    async def asearch(
        self,
        query: str,
        k: int = 10,
        use_tfidf_fallback: bool = True,
    ) -> SearchResult:
        """Async version of search()."""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._get_headers()
            )

        try:
            response = await self._client.post(
                f"{self.api_url}/api/search",
                json={
                    "query": query,
                    "k": k,
                    "use_tfidf_fallback": use_tfidf_fallback,
                }
            )

            data = self._handle_response(response)
            return SearchResult(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    async def asolve(
        self,
        query: str,
        timeout: Optional[float] = None,
    ) -> SolveResult:
        """Async version of solve()."""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=timeout or 300.0,
                headers=self._get_headers()
            )

        try:
            response = await self._client.post(
                f"{self.api_url}/api/solve",
                json={
                    "query": query,
                    "timeout": timeout or 300.0,
                }
            )

            data = self._handle_response(response)
            return SolveResult(**data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network request failed: {e}")

    async def aclose(self):
        """Close async HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
