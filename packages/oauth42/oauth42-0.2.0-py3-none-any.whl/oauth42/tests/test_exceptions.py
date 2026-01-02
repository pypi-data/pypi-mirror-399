"""Tests for OAuth42 exceptions."""

import pytest

from oauth42.types_.exceptions import (
    OAuth42Error, AuthenticationError, TokenError, 
    ConfigError, NetworkError
)


class TestOAuth42Exceptions:
    """Test OAuth42 exception hierarchy."""
    
    def test_oauth42_error_base_exception(self):
        """Test OAuth42Error is the base exception."""
        error = OAuth42Error("Test error")
        
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inherits from OAuth42Error."""
        error = AuthenticationError("Authentication failed")
        
        assert str(error) == "Authentication failed"
        assert isinstance(error, OAuth42Error)
        assert isinstance(error, Exception)
    
    def test_token_error_inheritance(self):
        """Test TokenError inherits from OAuth42Error."""
        error = TokenError("Token error")
        
        assert str(error) == "Token error"
        assert isinstance(error, OAuth42Error)
        assert isinstance(error, Exception)
    
    def test_config_error_inheritance(self):
        """Test ConfigError inherits from OAuth42Error."""
        error = ConfigError("Configuration error")
        
        assert str(error) == "Configuration error"
        assert isinstance(error, OAuth42Error)
        assert isinstance(error, Exception)
    
    def test_network_error_inheritance(self):
        """Test NetworkError inherits from OAuth42Error."""
        error = NetworkError("Network error")
        
        assert str(error) == "Network error"
        assert isinstance(error, OAuth42Error)
        assert isinstance(error, Exception)
    
    def test_exception_catching(self):
        """Test that specific exceptions can be caught as OAuth42Error."""
        exceptions = [
            AuthenticationError("Auth error"),
            TokenError("Token error"),
            ConfigError("Config error"),
            NetworkError("Network error")
        ]
        
        for exc in exceptions:
            try:
                raise exc
            except OAuth42Error as caught:
                assert caught is exc
                assert isinstance(caught, OAuth42Error)
            except Exception:
                pytest.fail(f"Should have caught {type(exc).__name__} as OAuth42Error")
    
    def test_exception_with_no_message(self):
        """Test exceptions with no message."""
        error = OAuth42Error()
        # Exception with no args should have empty or default string representation
        assert str(error) in ["", "()"]
        
        error = AuthenticationError()
        assert str(error) in ["", "()"]
    
    def test_exception_repr(self):
        """Test exception string representation."""
        error = OAuth42Error("Test message")
        assert repr(error) == "OAuth42Error('Test message')"
        
        error = TokenError("Token invalid")
        assert repr(error) == "TokenError('Token invalid')"
