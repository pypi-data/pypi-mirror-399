# konnektr_graph/auth/device_code_credential.py
"""
DeviceCodeCredential for OAuth 2.0 device authorization flow.
"""
import time
import webbrowser
from typing import Callable, Dict, Optional

import requests


class DeviceCodeCredential:
    """
    Authenticates users through the device code flow.

    This credential is intended for interactive authentication in environments
    where a browser may not be available (e.g., SSH sessions, CLI tools).

    :param domain: The OAuth provider domain (e.g., 'auth.konnektr.io')
    :param audience: The API audience/resource identifier
    :param client_id: The application client ID (public client)
    :param scope: OAuth scopes to request (default: 'openid profile email')
    :param prompt_callback: Optional callback for displaying auth instructions.
        If not provided, instructions are printed and browser is opened.
    :param timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        domain: str,
        audience: str,
        client_id: str,
        *,
        scope: str = "openid profile email",
        prompt_callback: Optional[Callable[[str, str, str], None]] = None,
        timeout: int = 30,
    ):
        self.domain = domain
        self.audience = audience
        self.client_id = client_id
        self.scope = scope
        self.prompt_callback = prompt_callback
        self.timeout = timeout
        self._token: Optional[str] = None
        self._expires_on: float = 0

    def get_token(self) -> str:
        """
        Get the current access token, initiating device code flow if needed.

        :return: A valid access token.
        :raises Exception: If authentication fails or times out.
        """
        # Return cached token if still valid (with 300s buffer)
        if self._token and time.time() < self._expires_on - 300:
            return self._token

        # Step 1: Request device code
        device_url = f"https://{self.domain}/oauth/device/code"
        device_data = {
            "client_id": self.client_id,
            "scope": self.scope,
            "audience": self.audience,
        }
        device_response = requests.post(
            device_url, json=device_data, timeout=self.timeout
        )
        device_response.raise_for_status()
        device_info = device_response.json()

        verification_uri = device_info["verification_uri"]
        verification_uri_complete = device_info["verification_uri_complete"]
        user_code = device_info["user_code"]

        # Step 2: Prompt user
        if self.prompt_callback:
            self.prompt_callback(verification_uri, verification_uri_complete, user_code)
        else:
            print(f"Please visit: {verification_uri_complete}")
            print(f"Or go to {verification_uri} and enter: {user_code}")
            webbrowser.open(verification_uri_complete)

        # Step 3: Poll for token
        token_url = f"https://{self.domain}/oauth/token"
        token_data = {
            "client_id": self.client_id,
            "device_code": device_info["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
        interval = device_info.get("interval", 5)
        expires_in = device_info.get("expires_in", 900)
        deadline = time.time() + expires_in

        while time.time() < deadline:
            token_response = requests.post(
                token_url, json=token_data, timeout=self.timeout
            )
            token_result = token_response.json()

            if "error" in token_result:
                error = token_result["error"]
                if error == "authorization_pending":
                    time.sleep(interval)
                    continue
                elif error == "slow_down":
                    interval += 5
                    time.sleep(interval)
                    continue
                elif error == "expired_token":
                    raise Exception("Device code expired. Please try again.")
                elif error == "access_denied":
                    raise Exception("User denied the authorization request.")
                else:
                    raise Exception(
                        f"Authentication error: {error} - {token_result.get('error_description', '')}"
                    )
            else:
                self._expires_on = time.time() + token_result["expires_in"]
                self._token = token_result["access_token"]
                print("Authentication successful!")
                return self._token

        raise Exception("Device code flow timed out.")

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers including the Authorization header.

        :return: Dictionary with Authorization header.
        """
        return {"Authorization": f"Bearer {self.get_token()}"}
