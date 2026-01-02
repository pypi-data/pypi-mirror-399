"""Cryptographic utilities for OAuth42 SDK."""

import base64
import hashlib
import secrets
import string
from typing import Tuple


def generate_state(length: int = 32) -> str:
    """Generate a random state parameter for OAuth2 flow.
    
    Args:
        length: Length of the state string
        
    Returns:
        Random state string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_nonce(length: int = 32) -> str:
    """Generate a random nonce for OpenID Connect.
    
    Args:
        length: Length of the nonce string
        
    Returns:
        Random nonce string
    """
    return generate_state(length)  # Same implementation as state


def generate_pkce_pair() -> Tuple[str, str]:
    """Generate PKCE code verifier and challenge pair.
    
    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    # Generate code verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    # Generate code challenge using SHA256
    challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge


def generate_client_secret(length: int = 48) -> str:
    """Generate a secure client secret.
    
    Args:
        length: Length of the secret
        
    Returns:
        Secure random secret string
    """
    alphabet = string.ascii_letters + string.digits + '-._~'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_client_secret(secret: str) -> str:
    """Hash a client secret using SHA256.
    
    Args:
        secret: Plain text secret
        
    Returns:
        Hex-encoded hash of the secret
    """
    return hashlib.sha256(secret.encode('utf-8')).hexdigest()