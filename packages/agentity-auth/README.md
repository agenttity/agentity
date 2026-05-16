# agentity-auth

**OIDC authentication plugin for Agentity.**
Verify human ownership of agent identities via Google, GitHub, Apple, and Microsoft login.

## Installation

```bash
pip install agentity-auth
```

## Usage

Mount the router on your FastAPI application:

```python
from fastapi import FastAPI
from agentity_auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)
```

### Configuration

Set OAuth2 credentials as environment variables:

```bash
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx
GITHUB_CLIENT_ID=Ov23lixxx
GITHUB_CLIENT_SECRET=xxx
APPLE_CLIENT_ID=com.example
APPLE_CLIENT_SECRET=xxx  # client secret generated from private key
MICROSOFT_CLIENT_ID=xxx
MICROSOFT_CLIENT_SECRET=xxx
```

All providers are optional — only configure the ones you need.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/auth/login/{provider}` | Redirect to OAuth2 consent screen |
| `GET` | `/auth/callback/{provider}` | Exchange auth code for session |
| `GET` | `/auth/session/{token}` | Get owner info from session token |
| `GET` | `/auth/me` | Get current owner from `Agentity-Session` header |
| `POST` | `/auth/register-verified` | Verify `owner_did` matches session |

### Integration with registry

```python
from fastapi import FastAPI
from agentity_registry.main import create_app
from agentity_auth import router as auth_router

app = create_app()                     # creates FastAPI with /register, /did, /revoke, etc.
app.include_router(auth_router)        # adds /auth/login, /auth/callback, /auth/me
```

## Supported providers

| Provider | Scopes | User info |
|----------|--------|-----------|
| Google | `openid email profile` | Email, name, Google profile |
| GitHub | `read:user user:email` | Email, name, GitHub profile |
| Apple | `name email` | Email, name (Sign in with Apple) |
| Microsoft | `openid email profile User.Read` | Email, name, MS profile |

## Session model

```python
class OwnerInfo(BaseModel):
    did: str              # did:agentity:human:{fingerprint}
    provider: str         # google | github | apple | microsoft
    provider_sub: str     # Provider's user ID
    email: str
    name: str
    verified: bool
```

License: Apache 2.0
