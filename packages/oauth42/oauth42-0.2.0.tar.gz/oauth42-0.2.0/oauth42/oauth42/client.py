"""OAuth42 client implementation."""

import httpx
import jwt
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlencode, urlparse, parse_qs

from .types_.models import (
    Config, TokenResponse, UserInfo, OAuth42User, 
    AuthorizationRequest, TokenRequest, OIDCDiscovery
)
from .types_.exceptions import OAuth42Error, AuthenticationError, TokenError, NetworkError
from .utils.crypto import generate_pkce_pair, generate_state, generate_nonce
from .utils.discovery import discover_oidc_config, discover_oidc_config_sync


class OAuth42Client:
    """Synchronous OAuth42 client."""
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize OAuth42 client.
        
        Args:
            config: OAuth42 configuration. If None, will load from environment.
        """
        self.config = config or Config.from_env()
        self._discovery: Optional[OIDCDiscovery] = None
        
        # Validate configuration
        if not self.config.client_id or not self.config.client_secret:
            raise OAuth42Error("client_id and client_secret are required")
    
    @classmethod
    def from_env(cls) -> "OAuth42Client":
        """Create client from environment variables."""
        return cls(Config.from_env())
    
    def _get_discovery(self) -> OIDCDiscovery:
        """Get or fetch OIDC discovery configuration."""
        if self._discovery is None:
            self._discovery = discover_oidc_config_sync(
                str(self.config.issuer), 
                self.config.timeout
            )
        return self._discovery
    
    def create_authorization_url(
        self, 
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
        use_pkce: Optional[bool] = None
    ) -> Tuple[str, str, Optional[str]]:
        """Create OAuth2 authorization URL.
        
        Args:
            scopes: OAuth2 scopes to request
            state: OAuth2 state parameter (generated if not provided)
            nonce: OpenID Connect nonce (generated if not provided)
            use_pkce: Whether to use PKCE (defaults to config setting)
            
        Returns:
            Tuple of (authorization_url, state, code_verifier)
            code_verifier is None if PKCE is not used
        """
        discovery = self._get_discovery()
        
        # Use provided values or defaults
        scopes = scopes or self.config.scopes
        state = state or generate_state()
        nonce = nonce or generate_nonce()
        use_pkce = use_pkce if use_pkce is not None else self.config.use_pkce
        
        # Build authorization request
        auth_request = AuthorizationRequest(
            client_id=self.config.client_id,
            redirect_uri=self.config.redirect_uri,
            scope=" ".join(scopes),
            state=state,
            nonce=nonce
        )
        
        code_verifier = None
        if use_pkce:
            code_verifier, code_challenge = generate_pkce_pair()
            auth_request.code_challenge = code_challenge
            auth_request.code_challenge_method = "S256"
        
        # Build URL
        params = auth_request.model_dump(exclude_none=True)
        auth_url = f"{discovery.authorization_endpoint}?{urlencode(params)}"
        
        return auth_url, state, code_verifier
    
    def exchange_code(
        self,
        code: str,
        state: Optional[str] = None,
        code_verifier: Optional[str] = None
    ) -> TokenResponse:
        """Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from callback
            state: OAuth2 state parameter for validation
            code_verifier: PKCE code verifier if PKCE was used
            
        Returns:
            Token response with access token and optional refresh token
            
        Raises:
            TokenError: If token exchange fails
        """
        discovery = self._get_discovery()
        
        # Build token request
        token_request = TokenRequest(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self.config.redirect_uri,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            code_verifier=code_verifier
        )
        
        try:
            with httpx.Client(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = client.post(
                    discovery.token_endpoint,
                    data=token_request.model_dump(exclude_none=True),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_data = response.json()
                return TokenResponse.model_validate(token_data)
                
        except httpx.HTTPError as e:
            raise TokenError(f"Token exchange failed: {e}")
        except Exception as e:
            raise TokenError(f"Failed to parse token response: {e}")
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
            
        Raises:
            TokenError: If token refresh fails
        """
        discovery = self._get_discovery()
        
        token_request = TokenRequest(
            grant_type="refresh_token",
            refresh_token=refresh_token,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )
        
        try:
            with httpx.Client(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = client.post(
                    discovery.token_endpoint,
                    data=token_request.model_dump(exclude_none=True),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_data = response.json()
                return TokenResponse.model_validate(token_data)
                
        except httpx.HTTPError as e:
            raise TokenError(f"Token refresh failed: {e}")
        except Exception as e:
            raise TokenError(f"Failed to parse token response: {e}")
    
    def get_user_info(self, access_token: str) -> UserInfo:
        """Get user information using access token.
        
        Args:
            access_token: Access token
            
        Returns:
            User information from UserInfo endpoint
            
        Raises:
            AuthenticationError: If UserInfo request fails
        """
        discovery = self._get_discovery()
        
        if not discovery.userinfo_endpoint:
            raise OAuth42Error("UserInfo endpoint not available")
        
        try:
            with httpx.Client(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = client.get(
                    discovery.userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                
                user_data = response.json()
                return UserInfo.model_validate(user_data)
                
        except httpx.HTTPError as e:
            raise AuthenticationError(f"UserInfo request failed: {e}")
        except Exception as e:
            raise AuthenticationError(f"Failed to parse UserInfo response: {e}")
    
    def validate_token(self, access_token: str, verify_signature: bool = False) -> Dict[str, Any]:
        """Validate and decode JWT access token.
        
        Args:
            access_token: JWT access token to validate
            verify_signature: Whether to verify JWT signature (requires JWKS)
            
        Returns:
            Decoded token claims
            
        Raises:
            TokenError: If token validation fails
        """
        try:
            # For now, just decode without verification
            # TODO: Add proper JWT signature verification with JWKS
            if verify_signature:
                raise NotImplementedError("JWT signature verification not yet implemented")
            
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            return decoded
            
        except jwt.InvalidTokenError as e:
            raise TokenError(f"Invalid JWT token: {e}")


class OAuth42AsyncClient:
    """Asynchronous OAuth42 client."""
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize async OAuth42 client."""
        self.config = config or Config.from_env()
        self._discovery: Optional[OIDCDiscovery] = None
        
        if not self.config.client_id or not self.config.client_secret:
            raise OAuth42Error("client_id and client_secret are required")
    
    @classmethod
    def from_env(cls) -> "OAuth42AsyncClient":
        """Create async client from environment variables."""
        return cls(Config.from_env())
    
    async def _get_discovery(self) -> OIDCDiscovery:
        """Get or fetch OIDC discovery configuration."""
        if self._discovery is None:
            self._discovery = await discover_oidc_config(
                str(self.config.issuer), 
                self.config.timeout
            )
        return self._discovery
    
    def create_authorization_url(
        self, 
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
        use_pkce: Optional[bool] = None
    ) -> Tuple[str, str, Optional[str]]:
        """Create OAuth2 authorization URL (same as sync version)."""
        # This method is the same as sync version since it doesn't make HTTP requests
        client = OAuth42Client(self.config)
        return client.create_authorization_url(scopes, state, nonce, use_pkce)
    
    async def exchange_code(
        self,
        code: str,
        state: Optional[str] = None,
        code_verifier: Optional[str] = None
    ) -> TokenResponse:
        """Async version of exchange_code."""
        discovery = await self._get_discovery()
        
        token_request = TokenRequest(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self.config.redirect_uri,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            code_verifier=code_verifier
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = await client.post(
                    discovery.token_endpoint,
                    data=token_request.model_dump(exclude_none=True),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_data = response.json()
                return TokenResponse.model_validate(token_data)
                
        except httpx.HTTPError as e:
            raise TokenError(f"Token exchange failed: {e}")
        except Exception as e:
            raise TokenError(f"Failed to parse token response: {e}")
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Async version of refresh_token."""
        discovery = await self._get_discovery()
        
        token_request = TokenRequest(
            grant_type="refresh_token",
            refresh_token=refresh_token,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = await client.post(
                    discovery.token_endpoint,
                    data=token_request.model_dump(exclude_none=True),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                token_data = response.json()
                return TokenResponse.model_validate(token_data)
                
        except httpx.HTTPError as e:
            raise TokenError(f"Token refresh failed: {e}")
        except Exception as e:
            raise TokenError(f"Failed to parse token response: {e}")
    
    async def get_user_info(self, access_token: str) -> UserInfo:
        """Async version of get_user_info."""
        discovery = await self._get_discovery()
        
        if not discovery.userinfo_endpoint:
            raise OAuth42Error("UserInfo endpoint not available")
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout, verify=self.config.verify_ssl) as client:
                response = await client.get(
                    discovery.userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                
                user_data = response.json()
                return UserInfo.model_validate(user_data)
                
        except httpx.HTTPError as e:
            raise AuthenticationError(f"UserInfo request failed: {e}")
        except Exception as e:
            raise AuthenticationError(f"Failed to parse UserInfo response: {e}")
    
    def validate_token(self, access_token: str, verify_signature: bool = False) -> Dict[str, Any]:
        """Validate JWT token (same as sync version)."""
        client = OAuth42Client(self.config)
        return client.validate_token(access_token, verify_signature)
