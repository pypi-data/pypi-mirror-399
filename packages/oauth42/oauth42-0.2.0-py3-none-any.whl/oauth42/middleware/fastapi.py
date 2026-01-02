"""FastAPI middleware and dependencies for OAuth42."""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from ..client import OAuth42AsyncClient
from ..types.models import OAuth42User, UserInfo, TokenResponse
from ..types.exceptions import OAuth42Error, TokenExpiredError

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class OAuth42Middleware(BaseHTTPMiddleware):
    """FastAPI middleware for OAuth42 authentication."""
    
    def __init__(self, app, client: OAuth42AsyncClient):
        super().__init__(app)
        self.client = client
    
    async def dispatch(self, request: Request, call_next):
        """Process requests and add OAuth42 context."""
        # Store client in request state for access in dependencies
        request.state.oauth42_client = self.client
        response = await call_next(request)
        return response


async def get_oauth42_client(request: Request) -> OAuth42AsyncClient:
    """Get OAuth42 client from request state."""
    if not hasattr(request.state, "oauth42_client"):
        raise HTTPException(status_code=500, detail="OAuth42 client not configured")
    return request.state.oauth42_client


async def get_current_user(
    request: Request,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    client: Annotated[OAuth42AsyncClient, Depends(get_oauth42_client)],
) -> OAuth42User:
    """Get current authenticated user from access token.
    
    Args:
        request: FastAPI request
        credentials: Bearer token from Authorization header
        client: OAuth42 client
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check for token in Authorization header
    if not credentials:
        # Check for token in session/cookies (if using session-based auth)
        access_token = request.session.get("access_token") if hasattr(request, "session") else None
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        access_token = credentials.credentials
    
    try:
        # Get user info from OAuth42
        user_info = await client.get_user_info(access_token)
        
        # Create OAuth42User object
        user = OAuth42User(
            id=user_info.sub,
            email=user_info.email,
            username=user_info.preferred_username,
            first_name=user_info.given_name,
            last_name=user_info.family_name,
            company_id=user_info.company_id,
            company_name=user_info.company_name,
            access_token=access_token,
        )
        
        return user
        
    except TokenExpiredError:
        # Try to refresh token if we have a refresh token
        if hasattr(request, "session") and "refresh_token" in request.session:
            try:
                tokens = await client.refresh_token(request.session["refresh_token"])
                request.session["access_token"] = tokens.access_token
                if tokens.refresh_token:
                    request.session["refresh_token"] = tokens.refresh_token
                
                # Retry with new token
                user_info = await client.get_user_info(tokens.access_token)
                user = OAuth42User(
                    id=user_info.sub,
                    email=user_info.email,
                    username=user_info.preferred_username,
                    first_name=user_info.given_name,
                    last_name=user_info.family_name,
                    company_id=user_info.company_id,
                    company_name=user_info.company_name,
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token,
                )
                return user
            except OAuth42Error:
                raise HTTPException(status_code=401, detail="Token refresh failed")
        else:
            raise HTTPException(status_code=401, detail="Token expired")
            
    except OAuth42Error as e:
        logger.error(f"OAuth42 authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_user(
    request: Request,
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    client: Annotated[OAuth42AsyncClient, Depends(get_oauth42_client)],
) -> Optional[OAuth42User]:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(request, credentials, client)
    except HTTPException:
        return None


class OAuth42SessionManager:
    """Session manager for OAuth42 authentication."""
    
    def __init__(self, client: OAuth42AsyncClient):
        self.client = client
    
    async def login(
        self,
        request: Request,
        code: str,
        state: str,
        expected_state: str,
        redirect_uri: Optional[str] = None,
        code_verifier: Optional[str] = None,
    ) -> OAuth42User:
        """Handle OAuth2 callback and create session.
        
        Args:
            request: FastAPI request
            code: Authorization code from callback
            state: State from callback
            expected_state: Expected state for CSRF validation
            redirect_uri: Redirect URI used in authorization
            code_verifier: PKCE code verifier
            
        Returns:
            Authenticated user
        """
        # Exchange code for tokens
        tokens = await self.client.exchange_code(
            code=code,
            state=state,
            expected_state=expected_state,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
        
        # Get user info
        user_info = await self.client.get_user_info(tokens.access_token)
        
        # Store in session if available
        if hasattr(request, "session"):
            request.session["access_token"] = tokens.access_token
            if tokens.refresh_token:
                request.session["refresh_token"] = tokens.refresh_token
            request.session["user_id"] = user_info.sub
            request.session["user_email"] = user_info.email
        
        # Create user object
        user = OAuth42User.from_userinfo(user_info, tokens)
        
        return user
    
    async def logout(self, request: Request, response: Response):
        """Clear session and logout user.
        
        Args:
            request: FastAPI request
            response: FastAPI response
        """
        if hasattr(request, "session"):
            request.session.clear()
        
        # Clear any cookies if needed
        response.delete_cookie("session")
