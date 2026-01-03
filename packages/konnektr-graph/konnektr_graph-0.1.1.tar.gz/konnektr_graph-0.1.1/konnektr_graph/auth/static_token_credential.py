# konnektr_graph/auth/static_token_credential.py
"""
StaticTokenCredential for using a pre-obtained access token.
"""
import time
from typing import Dict, Optional


class StaticTokenCredential:
    """
    Uses a pre-obtained access token directly.

    This credential is useful when you already have a valid token from
    another source (e.g., a different auth flow, token exchange, etc.).

    :param token: The access token to use
    :param expires_on: Optional Unix timestamp when the token expires.
        If not provided, the token is assumed to never expire.
    """

    def __init__(self, token: str, *, expires_on: Optional[float] = None):
        self._token = token
        self._expires_on = expires_on

    def get_token(self) -> str:
        """
        Get the access token.

        :return: The access token.
        :raises Exception: If the token has expired.
        """
        if self._expires_on is not None and time.time() >= self._expires_on:
            raise Exception("Token has expired.")
        return self._token

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers including the Authorization header.

        :return: Dictionary with Authorization header.
        """
        return {"Authorization": f"Bearer {self.get_token()}"}

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if self._expires_on is None:
            return False
        return time.time() >= self._expires_on
