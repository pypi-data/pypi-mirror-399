"""Tests for OAuth42 Pydantic models."""

import pytest
from pydantic import ValidationError

from oauth42.types_.models import (
    Config, TokenResponse, UserInfo, OAuth42User,
    AuthorizationRequest, TokenRequest, OIDCDiscovery
)


class TestTokenResponse:
    """Test TokenResponse model."""
    
    def test_token_response_minimal(self):
        """Test TokenResponse with minimal required fields."""
        token = TokenResponse(access_token="test_token")
        
        assert token.access_token == "test_token"
        assert token.token_type == "Bearer"
        assert token.expires_in is None
        assert token.refresh_token is None
        assert token.scope is None
        assert token.id_token is None
    
    def test_token_response_full(self):
        """Test TokenResponse with all fields."""
        token = TokenResponse(
            access_token="access_token_value",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh_token_value",
            scope="openid profile email",
            id_token="id_token_value"
        )
        
        assert token.access_token == "access_token_value"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600
        assert token.refresh_token == "refresh_token_value"
        assert token.scope == "openid profile email"
        assert token.id_token == "id_token_value"
    
    def test_token_response_missing_access_token(self):
        """Test TokenResponse fails without access token."""
        with pytest.raises(ValidationError):
            TokenResponse()


class TestUserInfo:
    """Test UserInfo model."""
    
    def test_user_info_minimal(self):
        """Test UserInfo with minimal required fields."""
        user_info = UserInfo(sub="user123")
        
        assert user_info.sub == "user123"
        assert user_info.email is None
        assert user_info.email_verified is None
        assert user_info.name is None
        assert user_info.given_name is None
        assert user_info.family_name is None
        assert user_info.picture is None
        assert user_info.username is None
    
    def test_user_info_full(self):
        """Test UserInfo with all fields."""
        user_info = UserInfo(
            sub="user123",
            email="user@example.com",
            email_verified=True,
            name="John Doe",
            given_name="John",
            family_name="Doe",
            picture="https://example.com/avatar.jpg",
            username="johndoe"
        )
        
        assert user_info.sub == "user123"
        assert user_info.email == "user@example.com"
        assert user_info.email_verified is True
        assert user_info.name == "John Doe"
        assert user_info.given_name == "John"
        assert user_info.family_name == "Doe"
        assert user_info.picture == "https://example.com/avatar.jpg"
        assert user_info.username == "johndoe"
    
    def test_user_info_extra_fields_allowed(self):
        """Test that UserInfo allows extra fields."""
        user_info = UserInfo(
            sub="user123",
            custom_field="custom_value",
            another_field=42
        )
        
        assert user_info.sub == "user123"
        # Extra fields should be accessible via model_dump
        data = user_info.model_dump()
        assert data["custom_field"] == "custom_value"
        assert data["another_field"] == 42


class TestOAuth42User:
    """Test OAuth42User model."""
    
    def test_oauth42_user_minimal(self):
        """Test OAuth42User with minimal required fields."""
        user = OAuth42User(
            id="user123",
            access_token="token123"
        )
        
        assert user.id == "user123"
        assert user.access_token == "token123"
        assert user.email is None
        assert user.email_verified is None
        assert user.username is None
        assert user.name is None
        assert user.picture is None
        assert user.expires_at is None
        assert user.scopes == []
    
    def test_oauth42_user_full(self):
        """Test OAuth42User with all fields."""
        user = OAuth42User(
            id="user123",
            email="user@example.com",
            email_verified=True,
            username="johndoe",
            name="John Doe",
            picture="https://example.com/avatar.jpg",
            access_token="token123",
            expires_at=1640995200,
            scopes=["openid", "profile", "email"]
        )
        
        assert user.id == "user123"
        assert user.email == "user@example.com"
        assert user.email_verified is True
        assert user.username == "johndoe"
        assert user.name == "John Doe"
        assert user.picture == "https://example.com/avatar.jpg"
        assert user.access_token == "token123"
        assert user.expires_at == 1640995200
        assert user.scopes == ["openid", "profile", "email"]
    
    def test_oauth42_user_is_authenticated(self):
        """Test is_authenticated property."""
        user_with_token = OAuth42User(id="user123", access_token="token123")
        user_without_token = OAuth42User(id="user123", access_token="")
        
        assert user_with_token.is_authenticated is True
        assert user_without_token.is_authenticated is False
    
    def test_oauth42_user_display_name(self):
        """Test display_name property."""
        user_with_name = OAuth42User(
            id="user123", 
            access_token="token123", 
            name="John Doe"
        )
        user_with_username = OAuth42User(
            id="user123", 
            access_token="token123", 
            username="johndoe"
        )
        user_with_email = OAuth42User(
            id="user123", 
            access_token="token123", 
            email="user@example.com"
        )
        user_with_id_only = OAuth42User(id="user123", access_token="token123")
        
        assert user_with_name.display_name == "John Doe"
        assert user_with_username.display_name == "johndoe"
        assert user_with_email.display_name == "user@example.com"
        assert user_with_id_only.display_name == "user123"


class TestAuthorizationRequest:
    """Test AuthorizationRequest model."""
    
    def test_authorization_request_minimal(self):
        """Test AuthorizationRequest with minimal required fields."""
        auth_req = AuthorizationRequest(
            client_id="client123",
            redirect_uri="http://localhost:3000/callback",
            scope="openid profile",
            state="state123"
        )
        
        assert auth_req.response_type == "code"
        assert auth_req.client_id == "client123"
        assert auth_req.redirect_uri == "http://localhost:3000/callback"
        assert auth_req.scope == "openid profile"
        assert auth_req.state == "state123"
        assert auth_req.code_challenge is None
        assert auth_req.code_challenge_method is None
        assert auth_req.nonce is None
    
    def test_authorization_request_with_pkce(self):
        """Test AuthorizationRequest with PKCE parameters."""
        auth_req = AuthorizationRequest(
            client_id="client123",
            redirect_uri="http://localhost:3000/callback",
            scope="openid profile",
            state="state123",
            code_challenge="challenge123",
            code_challenge_method="S256",
            nonce="nonce123"
        )
        
        assert auth_req.code_challenge == "challenge123"
        assert auth_req.code_challenge_method == "S256"
        assert auth_req.nonce == "nonce123"


class TestTokenRequest:
    """Test TokenRequest model."""
    
    def test_token_request_authorization_code(self):
        """Test TokenRequest for authorization code flow."""
        token_req = TokenRequest(
            grant_type="authorization_code",
            code="auth_code_123",
            redirect_uri="http://localhost:3000/callback",
            client_id="client123",
            client_secret="secret123",
            code_verifier="verifier123"
        )
        
        assert token_req.grant_type == "authorization_code"
        assert token_req.code == "auth_code_123"
        assert token_req.redirect_uri == "http://localhost:3000/callback"
        assert token_req.client_id == "client123"
        assert token_req.client_secret == "secret123"
        assert token_req.code_verifier == "verifier123"
        assert token_req.refresh_token is None
    
    def test_token_request_refresh_token(self):
        """Test TokenRequest for refresh token flow."""
        token_req = TokenRequest(
            grant_type="refresh_token",
            client_id="client123",
            client_secret="secret123",
            refresh_token="refresh123"
        )
        
        assert token_req.grant_type == "refresh_token"
        assert token_req.refresh_token == "refresh123"
        assert token_req.code is None
        assert token_req.redirect_uri is None


class TestOIDCDiscovery:
    """Test OIDCDiscovery model."""
    
    def test_oidc_discovery_minimal(self):
        """Test OIDCDiscovery with minimal required fields."""
        discovery = OIDCDiscovery(
            issuer="https://oauth42.example.com",
            authorization_endpoint="https://oauth42.example.com/auth",
            token_endpoint="https://oauth42.example.com/token",
            jwks_uri="https://oauth42.example.com/.well-known/jwks.json"
        )
        
        assert discovery.issuer == "https://oauth42.example.com"
        assert discovery.authorization_endpoint == "https://oauth42.example.com/auth"
        assert discovery.token_endpoint == "https://oauth42.example.com/token"
        assert discovery.jwks_uri == "https://oauth42.example.com/.well-known/jwks.json"
        assert discovery.userinfo_endpoint is None
        assert discovery.response_types_supported == []
        assert discovery.subject_types_supported == []
        assert discovery.id_token_signing_alg_values_supported == []
        assert discovery.scopes_supported is None
    
    def test_oidc_discovery_full(self):
        """Test OIDCDiscovery with all fields."""
        discovery = OIDCDiscovery(
            issuer="https://oauth42.example.com",
            authorization_endpoint="https://oauth42.example.com/auth",
            token_endpoint="https://oauth42.example.com/token",
            userinfo_endpoint="https://oauth42.example.com/userinfo",
            jwks_uri="https://oauth42.example.com/.well-known/jwks.json",
            response_types_supported=["code"],
            subject_types_supported=["public"],
            id_token_signing_alg_values_supported=["RS256"],
            scopes_supported=["openid", "profile", "email"]
        )
        
        assert discovery.userinfo_endpoint == "https://oauth42.example.com/userinfo"
        assert discovery.response_types_supported == ["code"]
        assert discovery.subject_types_supported == ["public"]
        assert discovery.id_token_signing_alg_values_supported == ["RS256"]
        assert discovery.scopes_supported == ["openid", "profile", "email"]
