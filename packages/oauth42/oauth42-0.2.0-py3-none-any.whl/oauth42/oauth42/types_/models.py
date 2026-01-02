"""Pydantic models for OAuth42 SDK."""

import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class Config(BaseModel):
    """OAuth42 client configuration."""
    
    client_id: str = Field(..., description="OAuth42 client ID")
    client_secret: str = Field(..., description="OAuth42 client secret")
    issuer: HttpUrl = Field(..., description="OAuth42 issuer URL")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    scopes: List[str] = Field(default=["openid", "profile", "email"], description="OAuth2 scopes")
    
    # Optional configuration
    timeout: int = Field(default=30, description="HTTP request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    use_pkce: bool = Field(default=True, description="Use PKCE for auth code flow")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        verify_ssl = os.environ.get("OAUTH42_VERIFY_SSL", "true").lower() == "true"
        
        return cls(
            client_id=os.environ.get("OAUTH42_CLIENT_ID", ""),
            client_secret=os.environ.get("OAUTH42_CLIENT_SECRET", ""),
            issuer=os.environ.get("OAUTH42_ISSUER", "https://api.oauth42.com"),
            redirect_uri=os.environ.get("OAUTH42_REDIRECT_URI", ""),
            scopes=os.environ.get("OAUTH42_SCOPES", "openid,profile,email").split(","),
            verify_ssl=verify_ssl,
        )
    
    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, v: List[str]) -> List[str]:
        """Ensure openid scope is included."""
        if "openid" not in v:
            v.append("openid")
        return v


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    scope: Optional[str] = Field(None, description="Granted scopes")
    id_token: Optional[str] = Field(None, description="OpenID Connect ID token")


class UserInfo(BaseModel):
    """OpenID Connect UserInfo response."""
    
    sub: str = Field(..., description="Subject identifier")
    email: Optional[str] = Field(None, description="Email address")
    email_verified: Optional[bool] = Field(None, description="Email verification status")
    name: Optional[str] = Field(None, description="Full name")
    given_name: Optional[str] = Field(None, description="Given name")
    family_name: Optional[str] = Field(None, description="Family name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    username: Optional[str] = Field(None, description="Username")
    
    model_config = ConfigDict(extra="allow")


class OAuth42User(BaseModel):
    """Represents an authenticated OAuth42 user."""
    
    id: str = Field(..., description="User ID")
    email: Optional[str] = Field(None, description="Email address")
    email_verified: Optional[bool] = Field(None, description="Email verification status")
    username: Optional[str] = Field(None, description="Username")
    name: Optional[str] = Field(None, description="Full name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    
    # Token information
    access_token: str = Field(..., description="Access token")
    expires_at: Optional[int] = Field(None, description="Token expiration timestamp")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return bool(self.access_token)
    
    @property
    def display_name(self) -> str:
        """Get display name for user."""
        return self.name or self.username or self.email or self.id


class AuthorizationRequest(BaseModel):
    """OAuth2 authorization request parameters."""
    
    response_type: str = Field(default="code", description="OAuth2 response type")
    client_id: str = Field(..., description="OAuth2 client ID")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    scope: str = Field(..., description="Requested scopes")
    state: str = Field(..., description="OAuth2 state parameter")
    code_challenge: Optional[str] = Field(None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field(None, description="PKCE code challenge method")
    nonce: Optional[str] = Field(None, description="OpenID Connect nonce")


class TokenRequest(BaseModel):
    """OAuth2 token request parameters."""
    
    grant_type: str = Field(..., description="OAuth2 grant type")
    code: Optional[str] = Field(None, description="Authorization code")
    redirect_uri: Optional[str] = Field(None, description="OAuth2 redirect URI")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    code_verifier: Optional[str] = Field(None, description="PKCE code verifier")
    refresh_token: Optional[str] = Field(None, description="Refresh token")


class OIDCDiscovery(BaseModel):
    """OpenID Connect Discovery document."""
    
    issuer: str = Field(..., description="Issuer identifier")
    authorization_endpoint: str = Field(..., description="Authorization endpoint URL")
    token_endpoint: str = Field(..., description="Token endpoint URL")
    userinfo_endpoint: Optional[str] = Field(None, description="UserInfo endpoint URL")
    jwks_uri: str = Field(..., description="JSON Web Key Set URL")
    
    # Supported features
    response_types_supported: List[str] = Field(default_factory=list)
    subject_types_supported: List[str] = Field(default_factory=list)
    id_token_signing_alg_values_supported: List[str] = Field(default_factory=list)
    scopes_supported: Optional[List[str]] = Field(None)
    
    model_config = ConfigDict(extra="allow")

