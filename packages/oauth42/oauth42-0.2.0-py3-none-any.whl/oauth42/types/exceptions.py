"""OAuth42 SDK exceptions."""

from typing import Optional, Dict, Any


class OAuth42Error(Exception):
    """Base exception for OAuth42 SDK errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(OAuth42Error):
    """Authentication failed."""

    pass


class TokenExpiredError(OAuth42Error):
    """Token has expired."""

    pass


class TokenError(OAuth42Error):
    """Generic token handling error."""

    pass


class ConfigurationError(OAuth42Error):
    """Configuration error."""

    pass


class NetworkError(OAuth42Error):
    """Network request failed."""

    pass


class TokenRefreshError(OAuth42Error):
    """Token refresh failed."""

    pass


class InvalidGrantError(OAuth42Error):
    """Invalid grant error from OAuth2 server."""

    pass


class InvalidClientError(OAuth42Error):
    """Invalid client credentials."""

    pass
