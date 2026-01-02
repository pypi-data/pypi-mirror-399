# OAuth42 Python SDK

Official Python SDK for OAuth42 - Enterprise OAuth2/OIDC Authentication Provider

## Features

- 🔐 Complete OAuth2/OIDC client implementation
- ⚡ Async/await support with `httpx`
- 🛡️ PKCE (Proof Key for Code Exchange) support
- 🔄 Automatic token refresh
- 🎯 Type-safe with Pydantic models
- 🚀 Framework integrations (FastAPI, Flask)
- 🐍 Python 3.12+ support

## Installation

Install with uv (recommended):
```bash
uv add oauth42
```

Or with pip:
```bash
pip install oauth42
```

## Quick Start

### Basic Usage

```python
from oauth42 import OAuth42Client

# Initialize client
client = OAuth42Client(
    client_id="your-client-id",
    client_secret="your-client-secret",
    issuer="https://api.oauth42.com",
    redirect_uri="http://localhost:8000/callback"
)

# Create authorization URL
auth_url, state, code_verifier = client.create_authorization_url()

# Exchange authorization code for tokens
tokens = client.exchange_code(
    code=request.args.get("code"),
    state=request.args.get("state"),
    expected_state=state,
    code_verifier=code_verifier
)

# Get user information
user_info = client.get_user_info(tokens.access_token)
print(f"Hello, {user_info.email}!")
```

### Async Support

```python
from oauth42 import OAuth42AsyncClient

async with OAuth42AsyncClient.from_env() as client:
    # Create authorization URL
    auth_url, state, verifier = client.create_authorization_url()
    
    # Exchange code for tokens
    tokens = await client.exchange_code(
        code=code,
        state=state,
        expected_state=expected_state,
        code_verifier=verifier
    )
    
    # Get user info
    user_info = await client.get_user_info(tokens.access_token)
```

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI, Depends
from oauth42.middleware.fastapi import OAuth42Middleware, get_current_user
from oauth42 import OAuth42AsyncClient, OAuth42User

app = FastAPI()
client = OAuth42AsyncClient.from_env()
app.add_middleware(OAuth42Middleware, client=client)

@app.get("/protected")
async def protected_route(user: OAuth42User = Depends(get_current_user)):
    return {"message": f"Hello, {user.email}!"}

@app.get("/login")
async def login():
    auth_url, state, verifier = client.create_authorization_url()
    # Store state and verifier in session
    return {"auth_url": auth_url}

@app.get("/callback")
async def callback(code: str, state: str):
    # Retrieve stored state and verifier
    tokens = await client.exchange_code(
        code=code,
        state=state,
        expected_state=stored_state,
        code_verifier=stored_verifier
    )
    return {"access_token": tokens.access_token}
```

### Flask

```python
from flask import Flask, redirect, url_for
from oauth42 import OAuth42Client
from oauth42.middleware.flask import OAuth42Flask

app = Flask(__name__)
client = OAuth42Client.from_env()
oauth42 = OAuth42Flask(app, client)

@app.route("/protected")
@oauth42.require_auth
def protected():
    user = oauth42.get_current_user()
    return f"Hello, {user.email}!"

@app.route("/login")
def login():
    return oauth42.authorize_redirect()

@app.route("/callback")
def callback():
    tokens = oauth42.authorize_access_token()
    return redirect(url_for("protected"))
```

## Configuration

### Environment Variables

```bash
# Required
OAUTH42_CLIENT_ID=your-client-id
OAUTH42_CLIENT_SECRET=your-client-secret
OAUTH42_ISSUER=https://api.oauth42.com

# Optional
OAUTH42_REDIRECT_URI=http://localhost:8000/callback
OAUTH42_SCOPES=openid profile email
OAUTH42_VERIFY_SSL=true
```

### Programmatic Configuration

```python
from oauth42 import Config, OAuth42Client

config = Config(
    client_id="your-client-id",
    client_secret="your-client-secret",
    issuer="https://api.oauth42.com",
    redirect_uri="http://localhost:8000/callback",
    scopes=["openid", "profile", "email", "company"]
)

client = OAuth42Client(config=config)
```

## Examples

See the `examples/` directory for complete working examples:

- **FastAPI Example**: Modern async web application with session management
- **Flask Example**: Traditional web application with template rendering

### Running the Examples

#### FastAPI Example

```bash
cd examples/fastapi_app
uv sync
uv run python main.py
```

Visit http://localhost:8000

#### Flask Example

```bash
cd examples/flask_app
uv sync
uv run python app.py
```

Visit http://localhost:5000

## Testing

Run unit tests:
```bash
uv run pytest tests/unit
```

Run integration tests (requires OAuth42 backend):
```bash
# Start OAuth42 backend first
make hybrid-dev-up
make dev-setup

# Run integration tests
uv run pytest tests/integration -m integration
```

## Development

### Setup Development Environment

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy oauth42
```

### Project Structure

```
oauth42/
├── client.py           # Main OAuth42 client implementation
├── auth/              # Authentication flows
├── middleware/        # Framework integrations
│   ├── fastapi.py    # FastAPI middleware
│   └── flask.py      # Flask extension
├── types/            # Type definitions
│   ├── models.py     # Pydantic models
│   └── exceptions.py # Custom exceptions
└── utils/            # Utility functions
```

## License

Copyright (c) 2024 OAuth42, Inc. All rights reserved.

This SDK is proprietary software provided by OAuth42, Inc. for use with OAuth42 services.
See LICENSE file for terms and conditions.

## Support

- Documentation: https://docs.oauth42.com/sdk/python
- Issues: https://github.com/oauth42/oauth42/issues
- Email: support@oauth42.com