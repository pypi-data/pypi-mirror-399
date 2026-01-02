"""Pytest configuration and shared fixtures for OAuth42 SDK tests."""

import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear OAuth42 environment variables before each test."""
    env_vars_to_clear = [
        'OAUTH42_CLIENT_ID',
        'OAUTH42_CLIENT_SECRET',
        'OAUTH42_ISSUER',
        'OAUTH42_REDIRECT_URI',
        'OAUTH42_SCOPES'
    ]
    
    # Store original values
    original_values = {}
    for var in env_vars_to_clear:
        original_values[var] = os.environ.get(var)
    
    # Clear the variables
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def sample_jwt_token():
    """Sample JWT token for testing (not cryptographically signed)."""
    # This is a sample JWT token with basic claims
    # Header: {"alg": "none", "typ": "JWT"}
    # Payload: {"sub": "user123", "iss": "https://oauth42.example.com", "aud": "test_client", "exp": 9999999999}
    return "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyMTIzIiwiaXNzIjoiaHR0cHM6Ly9vYXV0aDQyLmV4YW1wbGUuY29tIiwiYXVkIjoidGVzdF9jbGllbnQiLCJleHAiOjk5OTk5OTk5OTl9."


@pytest.fixture
def mock_http_response():
    """Mock HTTP response factory."""
    def _mock_response(status_code=200, json_data=None, text="", headers=None):
        from unittest.mock import Mock
        
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = headers or {}
        mock_response.text = text
        
        if json_data is not None:
            mock_response.json.return_value = json_data
        else:
            mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        
        if status_code >= 400:
            mock_response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
        else:
            mock_response.raise_for_status.return_value = None
            
        return mock_response
    
    return _mock_response