"""Cryptographic utilities for OAuth42 SDK."""

import base64
import hashlib
import secrets
from typing import Tuple


def generate_state() -> str:
    """Generate a random OAuth2 state parameter."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')


def generate_nonce() -> str:
    """Generate a random OpenID Connect nonce."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')


def generate_pkce_pair() -> Tuple[str, str]:
    """Generate PKCE code verifier and challenge pair.
    
    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    # Generate code verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    # Generate code challenge using S256 method
    challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge