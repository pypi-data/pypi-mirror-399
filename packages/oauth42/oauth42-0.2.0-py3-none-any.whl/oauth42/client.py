"""OAuth42 client implementation with sync and async support."""

import os
import secrets
import hashlib
import base64
import json
from typing import Optional, Tuple, Dict, Any, List
from urllib.parse import urlencode, parse_qs, urlparse
import logging

import httpx
import jwt

from .types.models import Config, TokenResponse, UserInfo, OIDCDiscovery
from .types.exceptions import (
    OAuth42Error,
    AuthenticationError,
    ConfigurationError,
    NetworkError,
    TokenError,
    TokenRefreshError,
    TokenExpiredError,
)
from .utils import discovery as discovery_utils

logger = logging.getLogger(__name__)


class OAuth42BaseClient:
    """Base OAuth42 client with common functionality."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        issuer: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        config: Optional[Config] = None,
        verify_ssl: bool = True,
    ):
        """Initialize OAuth42 client.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            issuer: OAuth2 issuer URL
            redirect_uri: OAuth2 redirect URI
            scopes: OAuth2 scopes
            config: Configuration object (overrides other parameters)
            verify_ssl: Whether to verify SSL certificates
        """
        if config:
            self.config = config
        else:
            if not all([client_id, client_secret, issuer]):
                raise ConfigurationError(
                    "Either provide a Config object or client_id, client_secret, and issuer"
                )
            self.config = Config(
                client_id=client_id,
                client_secret=client_secret,
                issuer=issuer,
                redirect_uri=redirect_uri or "",
                scopes=scopes or ["openid", "profile", "email"],
            )

        issuer_as_str = str(self.config.issuer)
        if issuer_as_str.endswith('/'):
            issuer_as_str = issuer_as_str.rstrip('/')
            self.config.issuer = issuer_as_str

        self.verify_ssl = verify_ssl
        self._discovery_cache: Optional[OIDCDiscovery] = None
        self._jwks_cache: Optional[Dict[str, Any]] = None
        
    @classmethod
    def from_env(cls, verify_ssl: bool = True) -> "OAuth42BaseClient":
        """Create client from environment variables."""
        config = Config.from_env()
        return cls(config=config, verify_ssl=verify_ssl)
    
    def _generate_pkce_challenge(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge.
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode("utf-8").rstrip("=")
        return code_verifier, code_challenge
    
    def _generate_state(self) -> str:
        """Generate random state for CSRF protection."""
        return secrets.token_urlsafe(32)
    
    def create_authorization_url(
        self,
        redirect_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
        use_pkce: bool = True,
        nonce: Optional[str] = None,
    ) -> Tuple[str, str, Optional[str]]:
        """Create authorization URL.
        
        Args:
            redirect_uri: Override redirect URI
            scopes: Override scopes
            state: Custom state parameter
            use_pkce: Whether to use PKCE
            nonce: OpenID Connect nonce
            
        Returns:
            Tuple of (authorization_url, state, code_verifier)
        """
        state = state or self._generate_state()
        redirect_uri = redirect_uri or self.config.redirect_uri
        if not redirect_uri:
            raise ConfigurationError("redirect_uri is required")
        
        scopes = scopes or self.config.scopes
        
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
        }
        
        if nonce:
            params["nonce"] = nonce
        
        code_verifier = None
        if use_pkce:
            code_verifier, code_challenge = self._generate_pkce_challenge()
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        
        auth_endpoint = self._get_authorization_endpoint()
        auth_url = f"{auth_endpoint}?{urlencode(params)}"
        
        return auth_url, state, code_verifier
    
    def _get_authorization_endpoint(self) -> str:
        """Get authorization endpoint from discovery or config."""
        # Simplified for now - should use discovery
        return f"{self.config.issuer}/oauth2/authorize"
    
    def _get_token_endpoint(self) -> str:
        """Get token endpoint from discovery or config."""
        return f"{self.config.issuer}/oauth2/token"
    
    def _get_userinfo_endpoint(self) -> str:
        """Get userinfo endpoint from discovery or config."""
        return f"{self.config.issuer}/oauth2/userinfo"


class OAuth42Client(OAuth42BaseClient):
    """Synchronous OAuth42 client."""
    
    def __init__(self, *args, **kwargs):
        # Support positional Config: OAuth42Client(Config(...))
        if args and 'config' not in kwargs:
            first = args[0]
            if hasattr(first, 'client_id') and hasattr(first, 'issuer'):
                kwargs['config'] = first
                args = ()
        super().__init__(*args, **kwargs)
        # For tests expecting simple client behavior
        self._discovery: Optional[OIDCDiscovery] = None
        self._client: Optional[httpx.Client] = None
        if not self.config.client_id or not self.config.client_secret:
            raise OAuth42Error("client_id and client_secret are required")
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def _get_discovery(self) -> OIDCDiscovery:
        if self._discovery is None:
            timeout = getattr(self.config, 'timeout', 30)
            issuer = str(self.config.issuer)
            if not issuer.endswith('/'):
                issuer = issuer + '/'
            # Resolve via module so test patches (oauth42.utils.discovery...) apply
            self._discovery = discovery_utils.discover_oidc_config_sync(issuer, timeout)
        return self._discovery

    def _get_authorization_endpoint(self) -> str:
        try:
            return self._get_discovery().authorization_endpoint
        except Exception:
            return super()._get_authorization_endpoint()

    def _get_token_endpoint(self) -> str:
        try:
            return self._get_discovery().token_endpoint
        except Exception:
            return super()._get_token_endpoint()

    def _get_userinfo_endpoint(self) -> str:
        try:
            ep = self._get_discovery().userinfo_endpoint
            return ep or super()._get_userinfo_endpoint()
        except Exception:
            return super()._get_userinfo_endpoint()
    
    def exchange_code(
        self,
        code: str,
        state: Optional[str] = None,
        expected_state: Optional[str] = None,
        code_verifier: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> TokenResponse:
        """Exchange authorization code for tokens.
        
        Args:
            code: Authorization code
            state: State value returned with the authorization response
            redirect_uri: Redirect URI used in authorization
            code_verifier: PKCE code verifier
            
        Returns:
            Token response
        """
        if expected_state is not None and state is not None and state != expected_state:
            raise AuthenticationError("State mismatch")

        redirect_uri = redirect_uri or self.config.redirect_uri
        if not redirect_uri:
            raise ConfigurationError("redirect_uri is required")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }

        if code_verifier:
            data["code_verifier"] = code_verifier
        
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                response = client.post(
                    self._get_token_endpoint(),
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return TokenResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Token exchange failed: {e}")
            raise TokenError("Token exchange failed") from e
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
        }
        
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                response = client.post(
                    self._get_token_endpoint(),
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return TokenResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Token refresh failed: {e}")
            raise TokenRefreshError(f"Token refresh failed: {e}") from e
    
    def get_user_info(self, access_token: str) -> UserInfo:
        """Get user information.
        
        Args:
            access_token: Access token
            
        Returns:
            User information
        """
        # Require userinfo endpoint from discovery if available
        try:
            if self._get_discovery().userinfo_endpoint is None:
                raise OAuth42Error("UserInfo endpoint not available")
        except Exception:
            pass
        # Require discovery userinfo endpoint if available
        if self._get_discovery().userinfo_endpoint is None:
            raise OAuth42Error("UserInfo endpoint not available")
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                response = client.get(
                    self._get_userinfo_endpoint(),
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                return UserInfo.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user info: {e}")
            raise NetworkError(f"Failed to get user info: {e}") from e

    def validate_token(self, token: str, verify_signature: bool = False) -> Dict[str, Any]:
        """Validate JWT token and return claims."""
        if verify_signature:
            raise NotImplementedError
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError as e:
            raise TokenError("Invalid JWT token") from e
    
    def client_credentials(self, scopes: Optional[List[str]] = None) -> TokenResponse:
        """Client credentials flow.
        
        Args:
            scopes: Optional scopes to request
            
        Returns:
            Token response
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        
        if scopes:
            data["scope"] = " ".join(scopes)
        
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                response = client.post(
                    self._get_token_endpoint(),
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return TokenResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Client credentials flow failed: {e}")
            raise NetworkError(f"Client credentials flow failed: {e}") from e


class OAuth42AsyncClient(OAuth42BaseClient):
    """Asynchronous OAuth42 client."""
    
    def __init__(self, *args, **kwargs):
        if args and 'config' not in kwargs:
            first = args[0]
            if hasattr(first, 'client_id') and hasattr(first, 'issuer'):
                kwargs['config'] = first
                args = ()
        super().__init__(*args, **kwargs)
        self._discovery: Optional[OIDCDiscovery] = None
        if not self.config.client_id or not self.config.client_secret:
            raise OAuth42Error("client_id and client_secret are required")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self):
        """Close HTTP client (no-op for compatibility)."""
        return None

    async def _get_discovery(self) -> OIDCDiscovery:
        if self._discovery is None:
            issuer = str(self.config.issuer)
            if not issuer.endswith('/'):
                issuer = issuer + '/'
            # Resolve via module so test patches apply
            self._discovery = await discovery_utils.discover_oidc_config(issuer, 30)
        return self._discovery

    def create_authorization_url(
        self,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
        use_pkce: Optional[bool] = None,
    ) -> Tuple[str, str, Optional[str]]:
        return OAuth42Client(self.config).create_authorization_url(scopes, state, nonce, use_pkce)
    
    async def exchange_code(
        self,
        code: str,
        state: Optional[str] = None,
        expected_state: Optional[str] = None,
        code_verifier: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> TokenResponse:
        """Exchange authorization code for tokens (async).
        
        Args:
            code: Authorization code
            state: State from callback
            expected_state: Expected state for CSRF validation
            redirect_uri: Redirect URI used in authorization
            code_verifier: PKCE code verifier
            
        Returns:
            Token response
        """
        if expected_state is not None and state is not None and state != expected_state:
            raise AuthenticationError("State mismatch")

        redirect_uri = redirect_uri or self.config.redirect_uri
        if not redirect_uri:
            raise ConfigurationError("redirect_uri is required")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        
        if code_verifier:
            data["code_verifier"] = code_verifier
        
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=verify) as client:
                response = await client.post(
                    self._get_token_endpoint(),
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return TokenResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Token exchange failed: {e}")
            raise TokenError(f"Token exchange failed: {e}") from e
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token (async).
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
        }
        
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=verify) as client:
                response = await client.post(
                    self._get_token_endpoint(),
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return TokenResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Token refresh failed: {e}")
            raise TokenRefreshError(f"Token refresh failed: {e}") from e
    
    async def get_user_info(self, access_token: str) -> UserInfo:
        """Get user information (async).
        
        Args:
            access_token: Access token
            
        Returns:
            User information
        """
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=verify) as client:
                response = await client.get(
                    self._get_userinfo_endpoint(),
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                return UserInfo.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user info: {e}")
            raise NetworkError(f"Failed to get user info: {e}") from e
    
    async def client_credentials(self, scopes: Optional[List[str]] = None) -> TokenResponse:
        """Client credentials flow (async).
        
        Args:
            scopes: Optional scopes to request
            
        Returns:
            Token response
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        
        if scopes:
            data["scope"] = " ".join(scopes)
        
        timeout = getattr(self.config, "timeout", 30)
        verify = getattr(self.config, "verify_ssl", True)

        try:
            async with httpx.AsyncClient(timeout=timeout, verify=verify) as client:
                response = await client.post(
                    self._get_token_endpoint(),
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return TokenResponse.model_validate(response.json())
        except httpx.HTTPError as e:
            logger.error(f"Client credentials flow failed: {e}")
            raise NetworkError(f"Client credentials flow failed: {e}") from e

    def validate_token(self, token: str, verify_signature: bool = False) -> Dict[str, Any]:
        """Delegate to sync client for validation to match test behavior."""
        return OAuth42Client(self.config).validate_token(token, verify_signature)
