"""
Main Ragamuffin client for Python SDK.
"""

import httpx
from typing import Optional

from .auth import AuthClient
from .rag import RAGClient
from .flows import FlowsClient
from .voice import VoiceClient
from .exceptions import APIError, AuthenticationError, RateLimitError, NotFoundError


class RagamuffinClient:
    """
    Main client for interacting with the Ragamuffin API.
    
    Example:
        >>> client = RagamuffinClient("http://localhost:8000")
        >>> client.login("user@example.com", "password")
        >>> result = client.rag.search("machine learning", top_k=5)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Ragamuffin client.
        
        Args:
            base_url: Base URL of the Ragamuffin API server
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._api_key = api_key
        
        # Initialize HTTP client
        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_default_headers(),
        )
        
        # Initialize sub-clients
        self._auth = AuthClient(self)
        self._rag = RAGClient(self)
        self._flows = FlowsClient(self)
        self._voice = VoiceClient(self)

    def _get_default_headers(self) -> dict:
        """Get default headers for requests."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "Ragamuffin-Python-SDK/1.0.0",
        }
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        return headers

    def _get_auth_headers(self) -> dict:
        """Get headers with authentication token."""
        headers = self._get_default_headers()
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication required or token expired",
                status_code=401,
            )
        elif response.status_code == 403:
            raise AuthenticationError(
                "Access forbidden",
                status_code=403,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                "Resource not found",
                status_code=404,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 60)
            raise RateLimitError(
                "Rate limit exceeded",
                status_code=429,
                retry_after=int(retry_after),
            )
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("detail", str(error_data))
            except Exception:
                message = response.text or "Unknown error"
            raise APIError(message, status_code=response.status_code)
        
        if response.status_code == 204:
            return {}
        
        try:
            return response.json()
        except Exception:
            return {"text": response.text}

    def request(
        self,
        method: str,
        path: str,
        authenticated: bool = True,
        **kwargs,
    ) -> dict:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            authenticated: Whether to include auth token
            **kwargs: Additional arguments for httpx request
        
        Returns:
            Response data as dictionary
        """
        headers = kwargs.pop("headers", {})
        if authenticated:
            headers.update(self._get_auth_headers())
        else:
            headers.update(self._get_default_headers())
        
        response = self._http.request(method, path, headers=headers, **kwargs)
        return self._handle_response(response)

    def login(self, email: str, password: str) -> dict:
        """
        Login with email and password.
        
        Args:
            email: User email
            password: User password
        
        Returns:
            Token response with access and refresh tokens
        """
        return self._auth.login(email, password)

    def register(self, name: str, email: str, password: str) -> dict:
        """
        Register a new user account.
        
        Args:
            name: Full name
            email: Email address
            password: Password (min 8 chars)
        
        Returns:
            Registration response
        """
        return self._auth.register(name, email, password)

    def logout(self) -> None:
        """Clear authentication tokens."""
        self._auth.logout()

    def set_tokens(self, access_token: str, refresh_token: str = None) -> None:
        """
        Set authentication tokens directly.
        
        Args:
            access_token: JWT access token
            refresh_token: Optional refresh token
        """
        self._access_token = access_token
        self._refresh_token = refresh_token

    @property
    def auth(self) -> "AuthClient":
        """Authentication operations."""
        return self._auth

    @property
    def rag(self) -> "RAGClient":
        """RAG operations (embed, search, query)."""
        return self._rag

    @property
    def flows(self) -> "FlowsClient":
        """Flow management operations."""
        return self._flows

    @property
    def voice(self) -> "VoiceClient":
        """Voice/Retell.ai operations."""
        return self._voice

    def health(self) -> dict:
        """Check API health status."""
        return self.request("GET", "/health", authenticated=False)

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
