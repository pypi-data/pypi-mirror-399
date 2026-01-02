"""OAuth42 SDK exceptions."""

from typing import Any, Dict, Optional


class OAuth42Error(Exception):
    """Base exception for OAuth42 SDK errors."""
    
    def __init__(
        self, 
        message: str = "", 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(OAuth42Error):
    """Raised when authentication fails."""
    pass


class TokenError(OAuth42Error):
    """Raised when token operations fail."""
    pass


class ConfigError(OAuth42Error):
    """Raised when configuration is invalid."""
    pass


class NetworkError(OAuth42Error):
    """Raised when network requests fail."""
    pass


class TokenExpiredError(OAuth42Error):
    """Raised when a token has expired."""
    pass


class ConfigurationError(OAuth42Error):
    """Raised for invalid client configuration or parameters."""
    pass


class TokenRefreshError(OAuth42Error):
    """Raised when refresh token flow fails."""
    pass
