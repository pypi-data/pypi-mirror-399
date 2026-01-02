"""Tests for OAuth42 cryptographic utilities."""

import base64
import hashlib
import re

from oauth42.utils.crypto import generate_state, generate_nonce, generate_pkce_pair


class TestCryptoUtils:
    """Test cryptographic utility functions."""
    
    def test_generate_state(self):
        """Test state generation."""
        state1 = generate_state()
        state2 = generate_state()
        
        # States should be different
        assert state1 != state2
        
        # State should be URL-safe base64 encoded string
        assert isinstance(state1, str)
        assert len(state1) > 0
        
        # Should be valid base64 (with padding added back)
        padded = state1 + '=' * (4 - len(state1) % 4)
        try:
            base64.urlsafe_b64decode(padded)
        except Exception:
            pytest.fail("Generated state is not valid base64")
    
    def test_generate_nonce(self):
        """Test nonce generation."""
        nonce1 = generate_nonce()
        nonce2 = generate_nonce()
        
        # Nonces should be different
        assert nonce1 != nonce2
        
        # Nonce should be URL-safe base64 encoded string
        assert isinstance(nonce1, str)
        assert len(nonce1) > 0
        
        # Should be valid base64 (with padding added back)
        padded = nonce1 + '=' * (4 - len(nonce1) % 4)
        try:
            base64.urlsafe_b64decode(padded)
        except Exception:
            pytest.fail("Generated nonce is not valid base64")
    
    def test_generate_pkce_pair(self):
        """Test PKCE code verifier and challenge generation."""
        verifier1, challenge1 = generate_pkce_pair()
        verifier2, challenge2 = generate_pkce_pair()
        
        # Pairs should be different
        assert verifier1 != verifier2
        assert challenge1 != challenge2
        
        # Both should be strings
        assert isinstance(verifier1, str)
        assert isinstance(challenge1, str)
        
        # Code verifier should be 43-128 characters (base64url without padding)
        assert 43 <= len(verifier1) <= 128
        
        # Code challenge should be valid base64url
        assert len(challenge1) > 0
        
        # Verify that challenge is correctly computed from verifier
        expected_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier1.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        assert challenge1 == expected_challenge
    
    def test_pkce_pair_uses_s256_method(self):
        """Test that PKCE challenge is computed using S256 method."""
        verifier, challenge = generate_pkce_pair()
        
        # Manually compute S256 challenge
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        expected_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        
        assert challenge == expected_challenge
    
    def test_generated_values_are_url_safe(self):
        """Test that all generated values are URL-safe."""
        state = generate_state()
        nonce = generate_nonce()
        verifier, challenge = generate_pkce_pair()
        
        # URL-safe base64 should only contain these characters
        url_safe_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
        
        assert url_safe_pattern.match(state), "State contains non-URL-safe characters"
        assert url_safe_pattern.match(nonce), "Nonce contains non-URL-safe characters"
        assert url_safe_pattern.match(verifier), "Verifier contains non-URL-safe characters"
        assert url_safe_pattern.match(challenge), "Challenge contains non-URL-safe characters"
    
    def test_no_padding_in_generated_values(self):
        """Test that generated values don't include base64 padding."""
        state = generate_state()
        nonce = generate_nonce()
        verifier, challenge = generate_pkce_pair()
        
        assert '=' not in state, "State should not contain padding"
        assert '=' not in nonce, "Nonce should not contain padding"
        assert '=' not in verifier, "Verifier should not contain padding"
        assert '=' not in challenge, "Challenge should not contain padding"