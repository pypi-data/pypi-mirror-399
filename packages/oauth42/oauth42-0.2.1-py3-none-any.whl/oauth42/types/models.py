"""OAuth42 SDK data models using Pydantic."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class Config(BaseModel):
    """OAuth42 client configuration."""

    model_config = ConfigDict(validate_assignment=True)

    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    issuer: str = Field(..., description="OAuth2 issuer URL")
    redirect_uri: Optional[str] = Field(None, description="OAuth2 redirect URI")
    scopes: List[str] = Field(
        default_factory=lambda: ["openid", "profile", "email"],
        description="OAuth2 scopes",
    )
    discovery_url: Optional[str] = Field(None, description="OIDC discovery URL")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        return cls(
            client_id=os.environ["OAUTH42_CLIENT_ID"],
            client_secret=os.environ["OAUTH42_CLIENT_SECRET"],
            issuer=os.environ.get("OAUTH42_ISSUER", "https://localhost:8443"),
            redirect_uri=os.environ.get("OAUTH42_REDIRECT_URI"),
            scopes=os.environ.get("OAUTH42_SCOPES", "openid profile email").split(),
        )


class TokenResponse(BaseModel):
    """OAuth2 token response."""

    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token lifetime in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    id_token: Optional[str] = Field(None, description="OpenID Connect ID token")
    scope: Optional[str] = Field(None, description="Granted scopes")
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired (simplified)."""
        # This would need proper implementation with token introspection
        return False


class UserInfo(BaseModel):
    """OpenID Connect UserInfo response."""

    sub: str = Field(..., description="Subject identifier")
    email: str = Field(..., description="User email")
    email_verified: Optional[bool] = Field(None, description="Email verification status")
    name: Optional[str] = Field(None, description="Full name")
    given_name: Optional[str] = Field(None, description="First name")
    family_name: Optional[str] = Field(None, description="Last name")
    preferred_username: Optional[str] = Field(None, description="Username")
    company_id: Optional[str] = Field(None, description="Company ID")
    company_name: Optional[str] = Field(None, description="Company name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    locale: Optional[str] = Field(None, description="User locale")
    updated_at: Optional[int] = Field(None, description="Last update timestamp")
    groups: Optional[List[str]] = Field(None, description="User groups")


class OAuth42User(BaseModel):
    """Authenticated OAuth42 user."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    company_id: Optional[str] = Field(None, description="Company ID")
    company_name: Optional[str] = Field(None, description="Company name")
    groups: Optional[List[str]] = Field(None, description="User groups")
    access_token: str = Field(..., description="Current access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration")
    
    @classmethod
    def from_userinfo(cls, userinfo: UserInfo, tokens: TokenResponse) -> "OAuth42User":
        """Create user from userinfo and tokens."""
        return cls(
            id=userinfo.sub,
            email=userinfo.email,
            username=userinfo.preferred_username,
            first_name=userinfo.given_name,
            last_name=userinfo.family_name,
            company_id=userinfo.company_id,
            company_name=userinfo.company_name,
            groups=userinfo.groups,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )


class OIDCDiscovery(BaseModel):
    """OpenID Connect Discovery document."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: Optional[str] = None
    jwks_uri: str
    registration_endpoint: Optional[str] = None
    scopes_supported: Optional[List[str]] = None
    response_types_supported: List[str]
    grant_types_supported: Optional[List[str]] = None
    subject_types_supported: List[str]
    id_token_signing_alg_values_supported: List[str]
    token_endpoint_auth_methods_supported: Optional[List[str]] = None
    claims_supported: Optional[List[str]] = None
    code_challenge_methods_supported: Optional[List[str]] = None
    introspection_endpoint: Optional[str] = None
    revocation_endpoint: Optional[str] = None
    
    
class AuthorizationRequest(BaseModel):
    """OAuth2 authorization request parameters."""
    
    response_type: str = Field(default="code", description="OAuth2 response type")
    client_id: str = Field(..., description="Client ID")
    redirect_uri: str = Field(..., description="Redirect URI")
    scope: str = Field(default="openid profile email", description="Requested scopes")
    state: str = Field(..., description="CSRF protection state")
    nonce: Optional[str] = Field(None, description="OIDC nonce")
    code_challenge: Optional[str] = Field(None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field(None, description="PKCE challenge method")