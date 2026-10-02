"""Authentication module for SCM OAuth2 token management."""

import time
from typing import Optional

import requests
from requests.exceptions import RequestException

from scm_device_register.config import settings


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class TokenManager:
    """Manages OAuth2 bearer tokens for SCM API access."""

    def __init__(self) -> None:
        """Initialize the token manager."""
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0

    def get_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            str: Valid bearer token

        Raises:
            AuthenticationError: If token acquisition fails
        """
        # Check if we have a valid token
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        # Get a new token
        return self._refresh_token()

    def _refresh_token(self) -> str:
        """
        Obtain a new access token from the SCM OAuth2 endpoint.

        Returns:
            str: New bearer token

        Raises:
            AuthenticationError: If token acquisition fails
        """
        payload = {
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "grant_type": "client_credentials",
            "scope": f"tsg_id:{settings.tsg_id}",
        }

        try:
            response = requests.post(
                settings.auth_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                verify=settings.verify_ssl,
                timeout=30,
            )
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data["access_token"]

            # Set expiry time (subtract 60 seconds as buffer)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expiry = time.time() + expires_in - 60

            return self._access_token

        except RequestException as e:
            raise AuthenticationError(f"Failed to obtain access token: {e}") from e
        except KeyError as e:
            raise AuthenticationError(f"Invalid token response format: {e}") from e

    def clear_token(self) -> None:
        """Clear the cached token, forcing a refresh on next request."""
        self._access_token = None
        self._token_expiry = 0.0


# Global token manager instance
token_manager = TokenManager()
