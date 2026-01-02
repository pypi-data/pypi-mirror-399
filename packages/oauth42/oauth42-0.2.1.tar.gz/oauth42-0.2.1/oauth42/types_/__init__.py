"""Type definitions for OAuth42 SDK (root package)."""

from .models import Config, TokenResponse, UserInfo, OAuth42User
from .exceptions import OAuth42Error, AuthenticationError, TokenError

__all__ = [
    "Config",
    "TokenResponse", 
    "UserInfo",
    "OAuth42User",
    "OAuth42Error",
    "AuthenticationError", 
    "TokenError",
]
