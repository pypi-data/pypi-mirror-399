"""OpenID Connect Discovery utilities."""

import httpx
from typing import Optional
from ..types_.models import OIDCDiscovery
from ..types_.exceptions import NetworkError, ConfigError


async def discover_oidc_config(issuer: str, timeout: int = 30) -> OIDCDiscovery:
    """Discover OpenID Connect configuration.
    
    Args:
        issuer: The OAuth2 issuer URL
        timeout: HTTP request timeout in seconds
        
    Returns:
        OIDC discovery configuration
        
    Raises:
        NetworkError: If discovery request fails
        ConfigError: If discovery document is invalid
    """
    discovery_url = f"{issuer.rstrip('/')}/.well-known/openid-configuration"
    
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            response = await client.get(discovery_url)
            response.raise_for_status()
            
            discovery_data = response.json()
            return OIDCDiscovery.model_validate(discovery_data)
            
    except httpx.HTTPError as e:
        raise NetworkError(f"Failed to discover OIDC configuration: {e}")
    except Exception as e:
        raise ConfigError(f"Invalid OIDC discovery document: {e}")


def discover_oidc_config_sync(issuer: str, timeout: int = 30) -> OIDCDiscovery:
    """Synchronous version of discover_oidc_config."""
    discovery_url = f"{issuer.rstrip('/')}/.well-known/openid-configuration"
    
    try:
        with httpx.Client(timeout=timeout, verify=False) as client:
            response = client.get(discovery_url)
            response.raise_for_status()
            
            discovery_data = response.json()
            return OIDCDiscovery.model_validate(discovery_data)
            
    except httpx.HTTPError as e:
        raise NetworkError(f"Failed to discover OIDC configuration: {e}")
    except Exception as e:
        raise ConfigError(f"Invalid OIDC discovery document: {e}")
