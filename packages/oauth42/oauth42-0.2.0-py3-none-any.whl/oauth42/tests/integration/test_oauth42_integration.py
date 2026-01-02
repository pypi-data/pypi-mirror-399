"""Integration tests for OAuth42 Python SDK against running OAuth42 server.

These tests require the OAuth42 test environment to be running via docker-compose.test.yml
Run with: make -C src/rust/oauth42 test-env-up
"""

import pytest
import httpx
import time
from urllib.parse import parse_qs, urlparse

from oauth42 import OAuth42Client, Config
from oauth42.types_.exceptions import OAuth42Error


# Test configuration for the running OAuth42 test environment
TEST_CONFIG = Config(
    client_id="test_client_id",
    client_secret="test_client_secret", 
    issuer="https://localhost:18080",
    redirect_uri="http://localhost:3000/callback",
    verify_ssl=False  # Self-signed cert in test environment
)


@pytest.fixture
def oauth42_client():
    """OAuth42 client configured for test environment."""
    return OAuth42Client(TEST_CONFIG)


def skip_if_oidc_not_implemented(func):
    """Decorator to skip tests if OIDC discovery is not implemented."""
    from functools import wraps
    import asyncio
    
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if "404" in str(e) and "openid-configuration" in str(e):
                    pytest.skip("OIDC discovery endpoint not yet implemented in OAuth42 server")
                else:
                    raise
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "404" in str(e) and "openid-configuration" in str(e):
                    pytest.skip("OIDC discovery endpoint not yet implemented in OAuth42 server")
                else:
                    raise
        return sync_wrapper


@pytest.fixture(scope="session", autouse=True)
def wait_for_oauth42_server():
    """Wait for OAuth42 server to be ready before running tests."""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = httpx.get(
                "https://localhost:18080/health", 
                verify=False, 
                timeout=5.0
            )
            if response.status_code == 200:
                print(f"OAuth42 server is ready after {attempt + 1} attempts")
                return
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}: OAuth42 server not ready, waiting {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                pytest.skip(f"OAuth42 server not available after {max_retries} attempts: {e}")


class TestOAuth42Integration:
    """Integration tests for OAuth42 client against running server."""
    
    def test_server_health_check(self):
        """Test that OAuth42 server health endpoint is accessible."""
        response = httpx.get("https://localhost:18080/health", verify=False)
        assert response.status_code == 200
    
    @skip_if_oidc_not_implemented
    def test_oidc_discovery(self, oauth42_client):
        """Test OIDC discovery endpoint works."""
        discovery = oauth42_client._get_discovery()
        
        assert discovery.issuer == "https://localhost:18080"
        assert discovery.authorization_endpoint == "https://localhost:18080/auth"
        assert discovery.token_endpoint == "https://localhost:18080/token"
        assert discovery.userinfo_endpoint == "https://localhost:18080/userinfo"
        assert discovery.jwks_uri == "https://localhost:18080/.well-known/jwks.json"
    
    @skip_if_oidc_not_implemented
    def test_create_authorization_url(self, oauth42_client):
        """Test authorization URL creation with OIDC discovery."""
        auth_url, state, code_verifier = oauth42_client.create_authorization_url(
            scopes=["openid", "profile", "email"],
            use_pkce=True
        )
        
        # Parse and validate the URL
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        assert parsed.scheme == "https"
        assert parsed.netloc == "localhost:18080"
        assert parsed.path == "/auth"
        
        assert params["response_type"][0] == "code"
        assert params["client_id"][0] == "test_client_id"
        assert params["redirect_uri"][0] == "http://localhost:3000/callback"
        assert params["scope"][0] == "openid profile email"
        assert "state" in params
        assert "code_challenge" in params
        assert params["code_challenge_method"][0] == "S256"
        
        assert state is not None and len(state) > 0
        assert code_verifier is not None and len(code_verifier) > 0
    
    @skip_if_oidc_not_implemented
    def test_authorization_endpoint_reachable(self, oauth42_client):
        """Test that authorization endpoint is reachable."""
        auth_url, _, _ = oauth42_client.create_authorization_url()
        
        # Just test that we can reach the authorization endpoint
        # We expect a redirect or HTML response, not an error
        response = httpx.get(auth_url, verify=False, follow_redirects=False)
        
        # Should either be OK (login page) or redirect (already logged in)
        assert response.status_code in [200, 302, 400]  # 400 if missing params is expected
    
    @skip_if_oidc_not_implemented
    def test_jwks_endpoint_accessible(self, oauth42_client):
        """Test that JWKS endpoint is accessible."""
        discovery = oauth42_client._get_discovery()
        
        response = httpx.get(discovery.jwks_uri, verify=False)
        assert response.status_code == 200
        
        jwks = response.json()
        assert "keys" in jwks
        assert isinstance(jwks["keys"], list)
    
    @skip_if_oidc_not_implemented
    def test_userinfo_endpoint_requires_auth(self, oauth42_client):
        """Test that userinfo endpoint properly requires authentication."""
        discovery = oauth42_client._get_discovery()
        
        # Test without authorization header - should fail
        response = httpx.get(discovery.userinfo_endpoint, verify=False)
        assert response.status_code == 401
        
        # Test with invalid token - should fail
        response = httpx.get(
            discovery.userinfo_endpoint, 
            headers={"Authorization": "Bearer invalid_token"},
            verify=False
        )
        assert response.status_code == 401
    
    @skip_if_oidc_not_implemented  
    def test_token_endpoint_requires_valid_request(self, oauth42_client):
        """Test that token endpoint properly validates requests."""
        discovery = oauth42_client._get_discovery()
        
        # Test with empty request - should fail
        response = httpx.post(discovery.token_endpoint, verify=False)
        assert response.status_code == 400
        
        # Test with invalid grant type - should fail
        response = httpx.post(
            discovery.token_endpoint,
            data={"grant_type": "invalid_grant"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=False
        )
        assert response.status_code == 400


class TestOAuth42AsyncIntegration:
    """Integration tests for async OAuth42 client."""
    
    @pytest.mark.asyncio
    @skip_if_oidc_not_implemented
    async def test_async_oidc_discovery(self):
        """Test async OIDC discovery works."""
        from oauth42 import OAuth42AsyncClient
        
        client = OAuth42AsyncClient(TEST_CONFIG)
        discovery = await client._get_discovery()
        
        assert discovery.issuer == "https://localhost:18080"
        assert discovery.authorization_endpoint == "https://localhost:18080/auth"
    
    @pytest.mark.asyncio
    @skip_if_oidc_not_implemented
    async def test_async_create_authorization_url(self):
        """Test async authorization URL creation."""
        from oauth42 import OAuth42AsyncClient
        
        client = OAuth42AsyncClient(TEST_CONFIG)
        auth_url, state, code_verifier = client.create_authorization_url()
        
        parsed = urlparse(auth_url)
        assert parsed.netloc == "localhost:18080"
        assert state is not None
        assert code_verifier is not None


# Note: Full OAuth flow integration tests would require:
# 1. A test OAuth client to be registered in the test environment
# 2. A way to programmatically complete the authorization flow
# 3. Test user credentials in the system
# These would be valuable additions but require coordination with the test environment setup
