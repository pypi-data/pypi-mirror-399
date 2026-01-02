"""Flask OAuth42 integration example.

This example demonstrates how to integrate OAuth42 with a Flask application,
including session management, authentication, and protected routes.

Run with: python app.py
"""

import os
from functools import wraps
from typing import Optional

from flask import Flask, request, session, redirect, url_for, render_template, jsonify, flash
from werkzeug.exceptions import Unauthorized

from oauth42 import OAuth42Client, Config, OAuth42Error, AuthenticationError


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# OAuth42 client configuration
oauth42_client = OAuth42Client.from_env()


def login_required(f):
    """Decorator for routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """Decorator for API routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    """Home page showing login/logout state."""
    user = session.get('user')
    return render_template('index.html', user=user)


@app.route('/login')
def login():
    """Initiate OAuth42 login flow."""
    try:
        # Generate authorization URL with PKCE
        auth_url, state, code_verifier = oauth42_client.create_authorization_url(
            scopes=["openid", "profile", "email"],
            use_pkce=True
        )
        
        # Store OAuth state and PKCE verifier in session
        session['oauth_state'] = state
        session['code_verifier'] = code_verifier
        
        return redirect(auth_url)
        
    except OAuth42Error as e:
        flash(f'OAuth error: {e}', 'error')
        return redirect(url_for('home'))


@app.route('/callback')
def callback():
    """Handle OAuth42 callback."""
    error = request.args.get('error')
    if error:
        flash(f'OAuth error: {error}', 'error')
        return redirect(url_for('home'))
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        flash('Missing code or state parameter', 'error')
        return redirect(url_for('home'))
    
    # Verify state parameter
    session_state = session.get('oauth_state')
    if not session_state or session_state != state:
        flash('Invalid state parameter', 'error')
        return redirect(url_for('home'))
    
    try:
        # Exchange code for tokens
        code_verifier = session.get('code_verifier')
        token_response = oauth42_client.exchange_code(
            code=code,
            state=state,
            code_verifier=code_verifier
        )
        
        # Get user information
        user_info = oauth42_client.get_user_info(token_response.access_token)
        
        # Store user in session
        session['user'] = {
            'id': user_info.sub,
            'email': user_info.email,
            'name': user_info.name,
            'username': user_info.username,
            'access_token': token_response.access_token,
            'expires_in': token_response.expires_in
        }
        
        # Clean up OAuth session data
        session.pop('oauth_state', None)
        session.pop('code_verifier', None)
        
        flash(f'Successfully logged in as {user_info.name or user_info.email or user_info.username}!', 'success')
        return redirect(url_for('profile'))
        
    except (OAuth42Error, AuthenticationError) as e:
        flash(f'Authentication failed: {e}', 'error')
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    """Logout user and clear session."""
    user = session.get('user')
    session.clear()
    if user:
        flash(f'Successfully logged out!', 'success')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    """Protected profile page."""
    user = session['user']
    return render_template('profile.html', user=user)


@app.route('/api/me')
@api_login_required
def api_me():
    """API endpoint returning current user info."""
    user = session['user']
    return jsonify({
        'id': user['id'],
        'email': user['email'],
        'name': user['name'],
        'username': user['username']
    })


@app.route('/api/protected')
@api_login_required
def api_protected():
    """Example protected API endpoint."""
    user = session['user']
    return jsonify({
        'message': 'Hello from protected endpoint!',
        'user_id': user['id']
    })


@app.route('/api/token-info')
@api_login_required
def api_token_info():
    """API endpoint showing token information."""
    user = session['user']
    
    try:
        # Validate and decode the token
        token_claims = oauth42_client.validate_token(user['access_token'])
        return jsonify({
            'token_valid': True,
            'claims': token_claims,
            'expires_in': user.get('expires_in')
        })
    except Exception as e:
        return jsonify({
            'token_valid': False,
            'error': str(e)
        }), 400


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    app.run(debug=True, host='0.0.0.0', port=5000)