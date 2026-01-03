# konnektr_graph/auth/async_client_secret_credential.py
"""
AsyncClientSecretCredential for OAuth 2.0 client credentials flow.
"""
import time
from typing import Dict, Optional

import aiohttp

from .protocol import AsyncTokenProvider


class AsyncClientSecretCredential:
    """
    Authenticates using OAuth 2.0 client credentials flow asynchronously.

    :param domain: The OAuth provider domain (e.g., 'auth.konnektr.io')
    :param audience: The API audience/resource identifier
    :param client_id: The application client ID
    :param client_secret: The application client secret
    :param timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        domain: str,
        audience: str,
        client_id: str,
        client_secret: str,
        *,
        timeout: int = 30,
    ):
        self.domain = domain
        self.audience = audience
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self._token: Optional[str] = None
        self._expires_on: float = 0

    async def get_token(self) -> str:
        """
        Get the current access token, refreshing if expired or about to expire.

        :return: A valid access token.
        :raises Exception: If token acquisition fails.
        """
        # Return cached token if still valid (with 300s buffer)
        if self._token and time.time() < self._expires_on - 300:
            return self._token

        url = f"https://{self.domain}/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.audience,
            "grant_type": "client_credentials",
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                token_data = await response.json()

        self._expires_on = time.time() + token_data["expires_in"]
        self._token = token_data["access_token"]
        return self._token

    async def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers including the Authorization header.

        :return: Dictionary with Authorization header.
        """
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}
