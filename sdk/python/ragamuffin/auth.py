"""
Authentication client for Ragamuffin SDK.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import RagamuffinClient


class AuthClient:
    """
    Authentication operations for Ragamuffin API.
    
    Example:
        >>> client.auth.login("user@example.com", "password")
        >>> user = client.auth.me()
        >>> client.auth.logout()
    """

    def __init__(self, client: "RagamuffinClient"):
        self._client = client

    def login(self, email: str, password: str) -> dict:
        """
        Login with email and password.
        
        Args:
            email: User email address
            password: User password
        
        Returns:
            Token response containing access_token and refresh_token
        """
        response = self._client.request(
            "POST",
            "/auth/login",
            authenticated=False,
            json={"email": email, "password": password},
        )
        
        # Store tokens
        if "access_token" in response:
            self._client._access_token = response["access_token"]
        if "refresh_token" in response:
            self._client._refresh_token = response["refresh_token"]
        
        return response

    def register(self, name: str, email: str, password: str) -> dict:
        """
        Register a new user account.
        
        Args:
            name: Full name
            email: Email address
            password: Password (minimum 8 characters)
        
        Returns:
            Registration response
        """
        return self._client.request(
            "POST",
            "/auth/register",
            authenticated=False,
            json={"name": name, "email": email, "password": password},
        )

    def logout(self) -> None:
        """Clear stored authentication tokens."""
        self._client._access_token = None
        self._client._refresh_token = None

    def refresh(self) -> dict:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            New token response
        """
        if not self._client._refresh_token:
            from .exceptions import AuthenticationError
            raise AuthenticationError("No refresh token available")
        
        response = self._client.request(
            "POST",
            "/auth/refresh",
            authenticated=False,
            json={"refresh_token": self._client._refresh_token},
        )
        
        if "access_token" in response:
            self._client._access_token = response["access_token"]
        if "refresh_token" in response:
            self._client._refresh_token = response["refresh_token"]
        
        return response

    def me(self) -> dict:
        """
        Get current authenticated user information.
        
        Returns:
            User information dictionary
        """
        return self._client.request("GET", "/auth/me")

    def update_profile(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        """
        Update user profile.
        
        Args:
            name: New name (optional)
            email: New email (optional)
        
        Returns:
            Updated user information
        """
        data = {}
        if name is not None:
            data["name"] = name
        if email is not None:
            data["email"] = email
        
        return self._client.request("PATCH", "/auth/me", json=data)

    def change_password(
        self,
        current_password: str,
        new_password: str,
    ) -> dict:
        """
        Change user password.
        
        Args:
            current_password: Current password
            new_password: New password (minimum 8 characters)
        
        Returns:
            Success response
        """
        return self._client.request(
            "POST",
            "/auth/change-password",
            json={
                "current_password": current_password,
                "new_password": new_password,
            },
        )

    @property
    def is_authenticated(self) -> bool:
        """Check if client has authentication tokens."""
        return self._client._access_token is not None
