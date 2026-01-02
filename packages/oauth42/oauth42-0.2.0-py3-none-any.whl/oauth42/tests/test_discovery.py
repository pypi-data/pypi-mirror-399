"""Tests for OAuth42 discovery utilities."""

import pytest
from unittest.mock import Mock, patch

import httpx

from oauth42.utils.discovery import discover_oidc_config, discover_oidc_config_sync
from oauth42.types_.models import OIDCDiscovery
from oauth42.types_.exceptions import NetworkError, ConfigError


@pytest.fixture
def discovery_response_data():
    """Mock OIDC discovery response data."""
    return {
        "issuer": "https://oauth42.example.com",
        "authorization_endpoint": "https://oauth42.example.com/auth",
        "token_endpoint": "https://oauth42.example.com/token",
        "userinfo_endpoint": "https://oauth42.example.com/userinfo",
        "jwks_uri": "https://oauth42.example.com/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"]
    }


class TestDiscoverOIDCConfigSync:
    """Test synchronous OIDC discovery."""
    
    @patch('httpx.Client')
    def test_discover_oidc_config_sync_success(self, mock_client_class, discovery_response_data):
        """Test successful OIDC discovery."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = discovery_response_data
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        result = discover_oidc_config_sync("https://oauth42.example.com")
        
        assert isinstance(result, OIDCDiscovery)
        assert result.issuer == "https://oauth42.example.com"
        assert result.authorization_endpoint == "https://oauth42.example.com/auth"
        assert result.token_endpoint == "https://oauth42.example.com/token"
        assert result.userinfo_endpoint == "https://oauth42.example.com/userinfo"
        
        # Verify HTTP call
        mock_client.get.assert_called_once_with(
            "https://oauth42.example.com/.well-known/openid-configuration"
        )
        mock_client_class.assert_called_once_with(timeout=30, verify=False)
    
    @patch('httpx.Client')
    def test_discover_oidc_config_sync_with_trailing_slash(self, mock_client_class, discovery_response_data):
        """Test OIDC discovery with trailing slash in issuer."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = discovery_response_data
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        result = discover_oidc_config_sync("https://oauth42.example.com/")
        
        assert isinstance(result, OIDCDiscovery)
        
        # Should strip trailing slash
        mock_client.get.assert_called_once_with(
            "https://oauth42.example.com/.well-known/openid-configuration"
        )
    
    @patch('httpx.Client')
    def test_discover_oidc_config_sync_custom_timeout(self, mock_client_class, discovery_response_data):
        """Test OIDC discovery with custom timeout."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = discovery_response_data
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        result = discover_oidc_config_sync("https://oauth42.example.com", timeout=60)
        
        assert isinstance(result, OIDCDiscovery)
        mock_client_class.assert_called_once_with(timeout=60, verify=False)
    
    @patch('httpx.Client')
    def test_discover_oidc_config_sync_http_error(self, mock_client_class):
        """Test OIDC discovery with HTTP error."""
        mock_client = Mock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            message="Not found",
            request=Mock(),
            response=Mock(status_code=404)
        )
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        with pytest.raises(NetworkError, match="Failed to discover OIDC configuration"):
            discover_oidc_config_sync("https://oauth42.example.com")
    
    @patch('httpx.Client')
    def test_discover_oidc_config_sync_invalid_json(self, mock_client_class):
        """Test OIDC discovery with invalid JSON response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        with pytest.raises(ConfigError, match="Invalid OIDC discovery document"):
            discover_oidc_config_sync("https://oauth42.example.com")
    
    @patch('httpx.Client')
    def test_discover_oidc_config_sync_missing_required_fields(self, mock_client_class):
        """Test OIDC discovery with missing required fields."""
        invalid_data = {
            "issuer": "https://oauth42.example.com"
            # Missing required fields
        }
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = invalid_data
        
        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        with pytest.raises(ConfigError, match="Invalid OIDC discovery document"):
            discover_oidc_config_sync("https://oauth42.example.com")


class TestDiscoverOIDCConfigAsync:
    """Test asynchronous OIDC discovery."""
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_discover_oidc_config_async_success(self, mock_client_class, discovery_response_data):
        """Test successful async OIDC discovery."""
        from unittest.mock import AsyncMock
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = discovery_response_data
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await discover_oidc_config("https://oauth42.example.com")
        
        assert isinstance(result, OIDCDiscovery)
        assert result.issuer == "https://oauth42.example.com"
        assert result.authorization_endpoint == "https://oauth42.example.com/auth"
        
        # Verify HTTP call
        mock_client.get.assert_called_once_with(
            "https://oauth42.example.com/.well-known/openid-configuration"
        )
        mock_client_class.assert_called_once_with(timeout=30, verify=False)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_discover_oidc_config_async_with_timeout(self, mock_client_class, discovery_response_data):
        """Test async OIDC discovery with custom timeout."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = discovery_response_data
        
        from unittest.mock import AsyncMock
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await discover_oidc_config("https://oauth42.example.com", timeout=45)
        
        assert isinstance(result, OIDCDiscovery)
        mock_client_class.assert_called_once_with(timeout=45, verify=False)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_discover_oidc_config_async_http_error(self, mock_client_class):
        """Test async OIDC discovery with HTTP error."""
        mock_client = Mock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(NetworkError, match="Failed to discover OIDC configuration"):
            await discover_oidc_config("https://oauth42.example.com")
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_discover_oidc_config_async_parse_error(self, mock_client_class):
        """Test async OIDC discovery with parsing error."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"invalid": "data"}
        
        from unittest.mock import AsyncMock
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(ConfigError, match="Invalid OIDC discovery document"):
            await discover_oidc_config("https://oauth42.example.com")
