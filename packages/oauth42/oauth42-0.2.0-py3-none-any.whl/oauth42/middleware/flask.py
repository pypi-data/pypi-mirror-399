"""Flask extension for OAuth42."""

from typing import Optional, Callable, Any
from functools import wraps
from flask import Flask, request, session, redirect, url_for, g, jsonify
from werkzeug.exceptions import Unauthorized
import logging

from ..client import OAuth42Client
from ..types.models import OAuth42User, UserInfo, TokenResponse
from ..types.exceptions import OAuth42Error, TokenExpiredError

logger = logging.getLogger(__name__)


class OAuth42Flask:
    """Flask extension for OAuth42 authentication."""
    
    def __init__(self, app: Optional[Flask] = None, client: Optional[OAuth42Client] = None):
        """Initialize OAuth42 Flask extension.
        
        Args:
            app: Flask application
            client: OAuth42 client
        """
        self.app = app
        self.client = client
        self._state_storage = {}  # Simple in-memory state storage
        self._pkce_storage = {}   # Simple in-memory PKCE storage
        
        if app is not None and client is not None:
            self.init_app(app, client)
    
    def init_app(self, app: Flask, client: OAuth42Client):
        """Initialize the Flask application.
        
        Args:
            app: Flask application
            client: OAuth42 client
        """
        self.app = app
        self.client = client
        
        # Register before_request handler
        app.before_request(self._before_request)
        
        # Store extension in app extensions
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["oauth42"] = self
    
    def _before_request(self):
        """Before request handler to load user."""
        g.oauth42_user = None
        
        # Check if user is in session
        if "oauth42_user_id" in session and "oauth42_access_token" in session:
            try:
                # Validate token is still valid (simplified check)
                g.oauth42_user = OAuth42User(
                    id=session["oauth42_user_id"],
                    email=session.get("oauth42_user_email", ""),
                    username=session.get("oauth42_username"),
                    first_name=session.get("oauth42_first_name"),
                    last_name=session.get("oauth42_last_name"),
                    company_id=session.get("oauth42_company_id"),
                    company_name=session.get("oauth42_company_name"),
                    access_token=session["oauth42_access_token"],
                    refresh_token=session.get("oauth42_refresh_token"),
                )
            except Exception as e:
                logger.error(f"Failed to load OAuth42 user: {e}")
                g.oauth42_user = None
    
    def require_auth(self, f: Callable) -> Callable:
        """Decorator to require authentication.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.oauth42_user is None:
                # Store the URL to redirect to after login
                session["oauth42_next_url"] = request.url
                return redirect(url_for("oauth42_login"))
            return f(*args, **kwargs)
        return decorated_function
    
    def get_current_user(self) -> Optional[OAuth42User]:
        """Get current authenticated user.
        
        Returns:
            Current user or None
        """
        return g.get("oauth42_user")
    
    def authorize_redirect(
        self,
        redirect_uri: Optional[str] = None,
        scopes: Optional[list] = None,
        use_pkce: bool = True,
    ) -> Any:
        """Redirect to OAuth2 authorization.
        
        Args:
            redirect_uri: Override redirect URI
            scopes: Override scopes
            use_pkce: Whether to use PKCE
            
        Returns:
            Redirect response
        """
        auth_url, state, code_verifier = self.client.create_authorization_url(
            redirect_uri=redirect_uri,
            scopes=scopes,
            use_pkce=use_pkce,
        )
        
        # Store state and PKCE verifier in session
        session["oauth42_state"] = state
        if code_verifier:
            session["oauth42_code_verifier"] = code_verifier
        
        return redirect(auth_url)
    
    def authorize_access_token(
        self,
        redirect_uri: Optional[str] = None,
    ) -> TokenResponse:
        """Handle OAuth2 callback and get tokens.
        
        Args:
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Token response
        """
        # Get code and state from request
        code = request.args.get("code")
        state = request.args.get("state")
        
        if not code or not state:
            raise Unauthorized("Missing code or state parameter")
        
        # Get expected state from session
        expected_state = session.pop("oauth42_state", None)
        if not expected_state:
            raise Unauthorized("Missing state in session")
        
        # Get PKCE verifier if used
        code_verifier = session.pop("oauth42_code_verifier", None)
        
        # Exchange code for tokens
        tokens = self.client.exchange_code(
            code=code,
            state=state,
            expected_state=expected_state,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
        
        # Get user info
        user_info = self.client.get_user_info(tokens.access_token)
        
        # Store in session
        session["oauth42_user_id"] = user_info.sub
        session["oauth42_user_email"] = user_info.email
        session["oauth42_username"] = user_info.preferred_username
        session["oauth42_first_name"] = user_info.given_name
        session["oauth42_last_name"] = user_info.family_name
        session["oauth42_company_id"] = user_info.company_id
        session["oauth42_company_name"] = user_info.company_name
        session["oauth42_access_token"] = tokens.access_token
        if tokens.refresh_token:
            session["oauth42_refresh_token"] = tokens.refresh_token
        
        return tokens
    
    def refresh_token(self) -> Optional[TokenResponse]:
        """Refresh the access token.
        
        Returns:
            New token response or None
        """
        refresh_token = session.get("oauth42_refresh_token")
        if not refresh_token:
            return None
        
        try:
            tokens = self.client.refresh_token(refresh_token)
            
            # Update session
            session["oauth42_access_token"] = tokens.access_token
            if tokens.refresh_token:
                session["oauth42_refresh_token"] = tokens.refresh_token
            
            return tokens
            
        except OAuth42Error as e:
            logger.error(f"Token refresh failed: {e}")
            self.logout()
            return None
    
    def logout(self):
        """Clear OAuth42 session."""
        keys_to_remove = [
            "oauth42_user_id",
            "oauth42_user_email",
            "oauth42_username",
            "oauth42_first_name",
            "oauth42_last_name",
            "oauth42_company_id",
            "oauth42_company_name",
            "oauth42_access_token",
            "oauth42_refresh_token",
            "oauth42_state",
            "oauth42_code_verifier",
            "oauth42_next_url",
        ]
        for key in keys_to_remove:
            session.pop(key, None)
        
        g.oauth42_user = None


def oauth42_login_required(f: Callable) -> Callable:
    """Standalone decorator for requiring OAuth42 authentication.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, "oauth42_user") or g.oauth42_user is None:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function
