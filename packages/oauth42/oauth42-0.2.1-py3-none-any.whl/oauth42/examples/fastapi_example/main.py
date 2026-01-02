"""FastAPI OAuth42 integration example.

This example demonstrates how to integrate OAuth42 with a FastAPI application,
including middleware, authentication, and protected routes.

Run with: uvicorn main:app --reload
"""

import os
import httpx
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from oauth42 import OAuth42Client, Config, OAuth42Error, AuthenticationError


app = FastAPI(title="OAuth42 FastAPI Example")

# Session middleware for storing OAuth state
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "dev-secret"))

# Templates
templates = Jinja2Templates(directory="templates")

# OAuth42 client configuration
oauth42_client = OAuth42Client.from_env()


@app.get("/")
async def home(request: Request):
    """Home page showing login/logout state."""
    user = request.session.get("user")
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "user": user}
    )


@app.get("/login")
async def login(request: Request):
    """Initiate OAuth42 login flow."""
    try:
        # Generate authorization URL with PKCE
        auth_url, state, code_verifier = oauth42_client.create_authorization_url(
            scopes=["openid", "profile", "email"],
            use_pkce=True
        )
        
        # Store OAuth state and PKCE verifier in session
        request.session["oauth_state"] = state
        request.session["code_verifier"] = code_verifier
        
        return RedirectResponse(url=auth_url)
        
    except OAuth42Error as e:
        raise HTTPException(status_code=500, detail=f"OAuth error: {e}")


@app.get("/callback")
async def callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Handle OAuth42 callback."""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    # Verify state parameter
    session_state = request.session.get("oauth_state")
    if not session_state or session_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    try:
        # Exchange code for tokens
        code_verifier = request.session.get("code_verifier")
        token_response = oauth42_client.exchange_code(
            code=code,
            state=state,
            code_verifier=code_verifier
        )
        
        # Get user information
        user_info = oauth42_client.get_user_info(token_response.access_token)
        
        # Store user in session
        request.session["user"] = {
            "id": user_info.sub,
            "email": user_info.email,
            "name": user_info.name,
            "username": user_info.username,
            "access_token": token_response.access_token,
            "expires_in": token_response.expires_in
        }
        
        # Clean up OAuth session data
        request.session.pop("oauth_state", None)
        request.session.pop("code_verifier", None)
        
        return RedirectResponse(url="/profile")
        
    except (OAuth42Error, AuthenticationError) as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")


@app.get("/logout")
async def logout(request: Request):
    """Logout user and clear session."""
    request.session.clear()
    return RedirectResponse(url="/")


def get_current_user(request: Request) -> dict:
    """Dependency to get current authenticated user."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.get("/profile")
async def profile(request: Request, current_user: dict = Depends(get_current_user)):
    """Protected profile page."""
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": current_user}
    )


@app.get("/api/me")
async def api_me(current_user: dict = Depends(get_current_user)):
    """API endpoint returning current user info."""
    return JSONResponse(content={
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "username": current_user["username"]
    })


@app.get("/api/protected")
async def api_protected(current_user: dict = Depends(get_current_user)):
    """Example protected API endpoint."""
    return JSONResponse(content={
        "message": "Hello from protected endpoint!",
        "user_id": current_user["id"]
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)