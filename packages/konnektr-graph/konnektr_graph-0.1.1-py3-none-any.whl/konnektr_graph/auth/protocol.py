# konnektr_graph/auth/protocol.py
"""
TokenProvider protocol for Konnektr Graph authentication.
"""
from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class TokenProvider(Protocol):
    """Protocol that all credential classes must implement."""

    def get_token(self) -> str:
        """Get the current access token, refreshing if necessary."""
        ...

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers including the Authorization header."""
        ...


@runtime_checkable
class AsyncTokenProvider(Protocol):
    """Protocol for async credential classes."""

    async def get_token(self) -> str:
        """Get the current access token, refreshing if necessary."""
        ...

    async def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers including the Authorization header."""
        ...
