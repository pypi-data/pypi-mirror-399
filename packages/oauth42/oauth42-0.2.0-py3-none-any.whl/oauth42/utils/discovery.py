"""OpenID Connect discovery utilities."""

import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin

import httpx

from ..types.models import OIDCDiscovery


async def discover_oidc_config(issuer: str, timeout: float = 30.0) -> OIDCDiscovery:
    """Discover OpenID Connect configuration asynchronously.
    
    Args:
        issuer: The OAuth2/OIDC issuer URL
        timeout: Request timeout in seconds
        
    Returns:
        OIDCDiscovery object
        
    Raises:
        httpx.HTTPError: If discovery fails
        ValueError: If configuration is invalid
    """
    from ..types.exceptions import ConfigError, NetworkError
    
    # Ensure issuer URL ends with /
    if not issuer.endswith('/'):
        issuer = issuer + '/'
    
    discovery_url = urljoin(issuer, '.well-known/openid-configuration')
    
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            response = await client.get(discovery_url)
            response.raise_for_status()
            
            config_data = response.json()
            try:
                return OIDCDiscovery(**config_data)
            except Exception as e:
                raise ConfigError(f"Invalid OIDC discovery document: {e}")
    except (httpx.ConnectError, httpx.HTTPError) as e:
        raise NetworkError(f"Failed to discover OIDC configuration: {e}")


def discover_oidc_config_sync(issuer: str, timeout: float = 30.0) -> OIDCDiscovery:
    """Discover OpenID Connect configuration synchronously.
    
    Args:
        issuer: The OAuth2/OIDC issuer URL
        timeout: Request timeout in seconds
        
    Returns:
        OIDCDiscovery object
        
    Raises:
        httpx.HTTPError: If discovery fails
        ValueError: If configuration is invalid
    """
    from ..types_.exceptions import ConfigError, NetworkError
    
    # Ensure issuer URL ends with /
    if not issuer.endswith('/'):
        issuer = issuer + '/'
    
    discovery_url = urljoin(issuer, '.well-known/openid-configuration')
    
    try:
        with httpx.Client(timeout=timeout, verify=False) as client:
            response = client.get(discovery_url)
            response.raise_for_status()
            
            try:
                config_data = response.json()
            except ValueError as e:
                raise ConfigError(f"Invalid OIDC discovery document: {e}")
            
            try:
                return OIDCDiscovery(**config_data)
            except Exception as e:
                raise ConfigError(f"Invalid OIDC discovery document: {e}")
    except (httpx.ConnectError, httpx.HTTPError) as e:
        raise NetworkError(f"Failed to discover OIDC configuration: {e}")


async def discover_jwks(issuer: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Discover JSON Web Key Set asynchronously.
    
    Args:
        issuer: The OAuth2/OIDC issuer URL
        timeout: Request timeout in seconds
        
    Returns:
        JWKS dictionary
        
    Raises:
        httpx.HTTPError: If discovery fails
    """
    config = await discover_oidc_config(issuer, timeout)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(config.jwks_uri, timeout=timeout)
        response.raise_for_status()
        return response.json()


def discover_jwks_sync(issuer: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Discover JSON Web Key Set synchronously.
    
    Args:
        issuer: The OAuth2/OIDC issuer URL
        timeout: Request timeout in seconds
        
    Returns:
        JWKS dictionary
        
    Raises:
        httpx.HTTPError: If discovery fails
    """
    config = discover_oidc_config_sync(issuer, timeout)
    
    with httpx.Client() as client:
        response = client.get(config.jwks_uri, timeout=timeout)
        response.raise_for_status()
        return response.json()


def validate_issuer(issuer: str, config: OIDCDiscovery) -> bool:
    """Validate that the issuer matches the discovered configuration.
    
    Args:
        issuer: Expected issuer URL
        config: Discovered configuration
        
    Returns:
        True if issuer matches
    """
    # Remove trailing slash for comparison
    expected = issuer.rstrip('/')
    actual = config.issuer.rstrip('/')
    return expected == actual
