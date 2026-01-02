"""Tests for OAuth42 client implementation."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from urllib.parse import urlparse, parse_qs

import httpx
import jwt

from oauth42 import OAuth42Client, OAuth42AsyncClient, Config
from oauth42.types_.models import TokenResponse, UserInfo, OIDCDiscovery
from oauth42.types_.exceptions import OAuth42Error, TokenError, AuthenticationError


@pytest.fixture
def config():
    """Test configuration."""
    return Config(
        client_id="test_client",
        client_secret="test_secret",
        issuer="https://oauth42.example.com",
        redirect_uri="http://localhost:3000/callback"
    )


@pytest.fixture
def discovery_doc():
    """Mock OIDC discovery document."""
    return OIDCDiscovery(
        issuer="https://oauth42.example.com",
        authorization_endpoint="https://oauth42.example.com/auth",
        token_endpoint="https://oauth42.example.com/token",
        userinfo_endpoint="https://oauth42.example.com/userinfo",
        jwks_uri="https://oauth42.example.com/.well-known/jwks.json"
    )


@pytest.fixture
def token_response_data():
    """Mock token response data."""
    return {
        "access_token": "test_access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "test_refresh_token",
        "scope": "openid profile email",
        "id_token": "test_id_token"
    }


@pytest.fixture
def user_info_data():
    """Mock user info data."""
    return {
        "sub": "user123",
        "email": "user@example.com",
        "email_verified": True,
        "name": "Test User",
        "username": "testuser",
        "picture": "https://example.com/avatar.jpg"
    }


class TestOAuth42Client:
    """Test synchronous OAuth42Client."""
    
    def test_client_initialization(self, config):
        """Test client initialization with config."""
        client = OAuth42Client(config)
        
        assert client.config == config
        assert client._discovery is None
    
    def test_client_initialization_missing_credentials(self):
        """Test client initialization fails with missing credentials."""
        config = Config(
            client_id="",
            client_secret="test_secret",
            issuer="https://oauth42.example.com",
            redirect_uri="http://localhost:3000/callback"
        )
        
        with pytest.raises(OAuth42Error, match="client_id and client_secret are required"):
            OAuth42Client(config)
    
    @patch.dict('os.environ', {
        'OAUTH42_CLIENT_ID': 'env_client',
        'OAUTH42_CLIENT_SECRET': 'env_secret',
        'OAUTH42_ISSUER': 'https://env.oauth42.com',
        'OAUTH42_REDIRECT_URI': 'http://localhost:8000/callback'
    })
    def test_client_from_env(self):
        """Test creating client from environment variables."""
        client = OAuth42Client.from_env()
        
        assert client.config.client_id == "env_client"
        assert client.config.client_secret == "env_secret"
        assert str(client.config.issuer) == "https://env.oauth42.com/"
        assert client.config.redirect_uri == "http://localhost:8000/callback"
    
    def test_get_discovery(self, config, discovery_doc):
        """Test OIDC discovery fetching."""
        with patch('oauth42.client.discover_oidc_config_sync') as mock_discover:
            mock_discover.return_value = discovery_doc
            client = OAuth42Client(config)
            
            # First call should fetch discovery
            result = client._get_discovery()
            assert result == discovery_doc
            mock_discover.assert_called_once_with("https://oauth42.example.com/", 30)
            
            # Second call should use cached result
            result2 = client._get_discovery()
            assert result2 == discovery_doc
            assert mock_discover.call_count == 1  # Still only called once
    
    @patch('oauth42.client.OAuth42Client._get_discovery')
    def test_create_authorization_url_minimal(self, mock_get_discovery, config, discovery_doc):
        """Test creating authorization URL with minimal parameters."""
        mock_get_discovery.return_value = discovery_doc
        client = OAuth42Client(config)
        
        auth_url, state, code_verifier = client.create_authorization_url()
        
        # Parse the URL
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        assert parsed.scheme == "https"
        assert parsed.netloc == "oauth42.example.com"
        assert parsed.path == "/auth"
        
        assert params["response_type"][0] == "code"
        assert params["client_id"][0] == "test_client"
        assert params["redirect_uri"][0] == "http://localhost:3000/callback"
        assert params["scope"][0] == "openid profile email"
        assert "state" in params
        assert state is not None
        assert len(state) > 0
        
        # Should use PKCE by default
        assert "code_challenge" in params
        assert "code_challenge_method" in params
        assert params["code_challenge_method"][0] == "S256"
        assert code_verifier is not None
        assert len(code_verifier) > 0
    
    @patch('oauth42.client.OAuth42Client._get_discovery')
    def test_create_authorization_url_custom_params(self, mock_get_discovery, config, discovery_doc):
        """Test creating authorization URL with custom parameters."""
        mock_get_discovery.return_value = discovery_doc
        client = OAuth42Client(config)
        
        auth_url, state, code_verifier = client.create_authorization_url(
            scopes=["openid", "profile"],
            state="custom_state",
            nonce="custom_nonce",
            use_pkce=False
        )
        
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        assert params["scope"][0] == "openid profile"
        assert params["state"][0] == "custom_state"
        assert params["nonce"][0] == "custom_nonce"
        assert state == "custom_state"
        
        # PKCE should be disabled
        assert "code_challenge" not in params
        assert "code_challenge_method" not in params
        assert code_verifier is None
    
    @patch('oauth42.client.OAuth42Client._get_discovery')
    @patch('httpx.Client')
    def test_exchange_code_success(self, mock_client_class, mock_get_discovery, 
                                 config, discovery_doc, token_response_data):
        """Test successful code exchange."""
        mock_get_discovery.return_value = discovery_doc
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = token_response_data
        
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        client = OAuth42Client(config)
        result = client.exchange_code("test_code", "test_state", "test_verifier")
        
        assert isinstance(result, TokenResponse)
        assert result.access_token == "test_access_token"
        assert result.token_type == "Bearer"
        assert result.expires_in == 3600
        
        # Verify HTTP call
        mock_client.post.assert_called_once_with(
            "https://oauth42.example.com/token",
            data={
                "grant_type": "authorization_code",
                "code": "test_code",
                "redirect_uri": "http://localhost:3000/callback",
                "client_id": "test_client",
                "client_secret": "test_secret",
                "code_verifier": "test_verifier"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    @patch('oauth42.client.OAuth42Client._get_discovery')
    @patch('httpx.Client')
    def test_exchange_code_http_error(self, mock_client_class, mock_get_discovery, 
                                    config, discovery_doc):
        """Test code exchange with HTTP error."""
        mock_get_discovery.return_value = discovery_doc
        
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            message="Token endpoint error",
            request=Mock(),
            response=Mock(status_code=400)
        )
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        client = OAuth42Client(config)
        
        with pytest.raises(TokenError, match="Token exchange failed"):
            client.exchange_code("test_code", "test_state", "test_verifier")
    
    @patch('oauth42.client.OAuth42Client._get_discovery')
    @patch('httpx.Client')
    def test_get_user_info_success(self, mock_client_class, mock_get_discovery, 
                                 config, discovery_doc, user_info_data):
        """Test successful user info retrieval."""
        mock_get_discovery.return_value = discovery_doc
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = user_info_data
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        client = OAuth42Client(config)
        result = client.get_user_info("test_access_token")
        
        assert isinstance(result, UserInfo)
        assert result.sub == "user123"
        assert result.email == "user@example.com"
        assert result.name == "Test User"
        
        # Verify HTTP call
        mock_client.get.assert_called_once_with(
            "https://oauth42.example.com/userinfo",
            headers={"Authorization": "Bearer test_access_token"}
        )
    
    @patch('oauth42.client.OAuth42Client._get_discovery')
    def test_get_user_info_no_endpoint(self, mock_get_discovery, config):
        """Test user info retrieval with no userinfo endpoint."""
        discovery_doc = OIDCDiscovery(
            issuer="https://oauth42.example.com",
            authorization_endpoint="https://oauth42.example.com/auth",
            token_endpoint="https://oauth42.example.com/token",
            jwks_uri="https://oauth42.example.com/.well-known/jwks.json"
            # userinfo_endpoint is None
        )
        mock_get_discovery.return_value = discovery_doc
        
        client = OAuth42Client(config)
        
        with pytest.raises(OAuth42Error, match="UserInfo endpoint not available"):
            client.get_user_info("test_access_token")
    
    @patch('jwt.decode')
    def test_validate_token_success(self, mock_jwt_decode, config):
        """Test successful token validation."""
        mock_claims = {"sub": "user123", "iss": "https://oauth42.example.com"}
        mock_jwt_decode.return_value = mock_claims
        
        client = OAuth42Client(config)
        result = client.validate_token("test_token")
        
        assert result == mock_claims
        mock_jwt_decode.assert_called_once_with(
            "test_token", 
            options={"verify_signature": False}
        )
    
    def test_validate_token_with_signature_verification_not_implemented(self, config):
        """Test token validation with signature verification (not implemented)."""
        client = OAuth42Client(config)
        
        with pytest.raises(NotImplementedError):
            client.validate_token("test_token", verify_signature=True)
    
    @patch('jwt.decode')
    def test_validate_token_invalid_jwt(self, mock_jwt_decode, config):
        """Test token validation with invalid JWT."""
        mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid token")
        
        client = OAuth42Client(config)
        
        with pytest.raises(TokenError, match="Invalid JWT token"):
            client.validate_token("invalid_token")


class TestOAuth42AsyncClient:
    """Test asynchronous OAuth42AsyncClient."""
    
    def test_async_client_initialization(self, config):
        """Test async client initialization."""
        client = OAuth42AsyncClient(config)
        
        assert client.config == config
        assert client._discovery is None
    
    @patch.dict('os.environ', {
        'OAUTH42_CLIENT_ID': 'env_client',
        'OAUTH42_CLIENT_SECRET': 'env_secret'
    })
    def test_async_client_from_env(self):
        """Test creating async client from environment."""
        client = OAuth42AsyncClient.from_env()
        
        assert client.config.client_id == "env_client"
        assert client.config.client_secret == "env_secret"
    
    @pytest.mark.asyncio
    async def test_async_get_discovery(self, config, discovery_doc):
        """Test async OIDC discovery fetching."""
        from unittest.mock import AsyncMock
        with patch('oauth42.client.discover_oidc_config', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = discovery_doc
            client = OAuth42AsyncClient(config)
            
            result = await client._get_discovery()
            assert result == discovery_doc
            mock_discover.assert_called_once_with("https://oauth42.example.com/", 30)
    
    def test_async_create_authorization_url(self, config):
        """Test async authorization URL creation (should use sync version)."""
        client = OAuth42AsyncClient(config)
        
        with patch.object(OAuth42Client, 'create_authorization_url') as mock_sync:
            mock_sync.return_value = ("url", "state", "verifier")
            
            result = client.create_authorization_url(["openid"])
            
            assert result == ("url", "state", "verifier")
            mock_sync.assert_called_once_with(["openid"], None, None, None)
    
    @pytest.mark.asyncio
    @patch('oauth42.client.OAuth42AsyncClient._get_discovery')
    @patch('httpx.AsyncClient')
    async def test_async_exchange_code_success(self, mock_client_class, mock_get_discovery, 
                                             config, discovery_doc, token_response_data):
        """Test successful async code exchange."""
        mock_get_discovery.return_value = discovery_doc
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = token_response_data
        
        from unittest.mock import AsyncMock
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        client = OAuth42AsyncClient(config)
        result = await client.exchange_code("test_code", "test_state", "test_verifier")
        
        assert isinstance(result, TokenResponse)
        assert result.access_token == "test_access_token"
    
    def test_async_validate_token(self, config):
        """Test async token validation (should use sync version)."""
        client = OAuth42AsyncClient(config)
        
        with patch.object(OAuth42Client, 'validate_token') as mock_sync:
            mock_sync.return_value = {"sub": "user123"}
            
            result = client.validate_token("test_token")
            
            assert result == {"sub": "user123"}
            mock_sync.assert_called_once_with("test_token", False)
