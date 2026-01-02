"""Tests for OAuth42 configuration."""

import os
import pytest
from unittest.mock import patch

from oauth42.types_.models import Config
from oauth42.types_.exceptions import OAuth42Error


class TestConfig:
    """Test OAuth42 configuration."""
    
    def test_config_creation_with_all_fields(self):
        """Test creating config with all required fields."""
        config = Config(
            client_id="test_client",
            client_secret="test_secret",
            issuer="https://oauth42.example.com",
            redirect_uri="http://localhost:3000/callback"
        )
        
        assert config.client_id == "test_client"
        assert config.client_secret == "test_secret"
        assert str(config.issuer) == "https://oauth42.example.com/"
        assert config.redirect_uri == "http://localhost:3000/callback"
        assert config.scopes == ["openid", "profile", "email"]
        assert config.timeout == 30
        assert config.verify_ssl is True
        assert config.use_pkce is True
    
    def test_config_custom_scopes(self):
        """Test config with custom scopes."""
        config = Config(
            client_id="test_client",
            client_secret="test_secret",
            issuer="https://oauth42.example.com",
            redirect_uri="http://localhost:3000/callback",
            scopes=["openid", "profile"]
        )
        
        assert config.scopes == ["openid", "profile"]
    
    def test_config_scopes_validation_adds_openid(self):
        """Test that openid scope is automatically added if missing."""
        config = Config(
            client_id="test_client",
            client_secret="test_secret",
            issuer="https://oauth42.example.com",
            redirect_uri="http://localhost:3000/callback",
            scopes=["profile", "email"]
        )
        
        assert "openid" in config.scopes
        assert config.scopes == ["profile", "email", "openid"]
    
    def test_config_optional_fields(self):
        """Test config with custom optional fields."""
        config = Config(
            client_id="test_client",
            client_secret="test_secret",
            issuer="https://oauth42.example.com",
            redirect_uri="http://localhost:3000/callback",
            timeout=60,
            verify_ssl=False,
            use_pkce=False
        )
        
        assert config.timeout == 60
        assert config.verify_ssl is False
        assert config.use_pkce is False
    
    @patch.dict(os.environ, {
        'OAUTH42_CLIENT_ID': 'env_client',
        'OAUTH42_CLIENT_SECRET': 'env_secret',
        'OAUTH42_ISSUER': 'https://env.oauth42.com',
        'OAUTH42_REDIRECT_URI': 'http://localhost:8000/callback',
        'OAUTH42_SCOPES': 'openid,profile,email,custom'
    })
    def test_config_from_env(self):
        """Test creating config from environment variables."""
        config = Config.from_env()
        
        assert config.client_id == "env_client"
        assert config.client_secret == "env_secret"
        assert str(config.issuer) == "https://env.oauth42.com/"
        assert config.redirect_uri == "http://localhost:8000/callback"
        assert config.scopes == ["openid", "profile", "email", "custom"]
    
    @patch.dict(os.environ, {
        'OAUTH42_CLIENT_ID': 'env_client',
        'OAUTH42_CLIENT_SECRET': 'env_secret'
    }, clear=True)
    def test_config_from_env_with_defaults(self):
        """Test config from env uses defaults for missing values."""
        config = Config.from_env()
        
        assert config.client_id == "env_client"
        assert config.client_secret == "env_secret"
        assert str(config.issuer) == "https://api.oauth42.com/"
        assert config.redirect_uri == ""
        assert config.scopes == ["openid", "profile", "email"]
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_from_env_missing_required(self):
        """Test config from env with missing required fields."""
        config = Config.from_env()
        
        assert config.client_id == ""
        assert config.client_secret == ""
    
    def test_config_invalid_issuer_url(self):
        """Test config with invalid issuer URL."""
        with pytest.raises(Exception):  # Pydantic validation error
            Config(
                client_id="test_client",
                client_secret="test_secret",
                issuer="not-a-valid-url",
                redirect_uri="http://localhost:3000/callback"
            )
