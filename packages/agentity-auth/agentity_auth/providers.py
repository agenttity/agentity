"""OAuth2 provider configurations for Agentity Auth.

Credentials are loaded from environment variables:
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
  GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
  APPLE_CLIENT_ID, APPLE_CLIENT_SECRET, APPLE_TEAM_ID, APPLE_KEY_ID
  MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET
"""

import os
from .models import ProviderConfig

AUTH_BASE_URL = os.getenv("AGENTITY_AUTH_URL", "http://localhost:8765")


def _load_providers() -> dict[str, ProviderConfig]:
    return {
        "google": ProviderConfig(
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
            scope="openid email profile",
            redirect_uri=f"{AUTH_BASE_URL}/auth/callback/{{provider}}",
        ),
        "github": ProviderConfig(
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            userinfo_url="https://api.github.com/user",
            scope="read:user user:email",
            redirect_uri=f"{AUTH_BASE_URL}/auth/callback/{{provider}}",
        ),
        "apple": ProviderConfig(
            client_id=os.getenv("APPLE_CLIENT_ID", ""),
            client_secret=os.getenv("APPLE_CLIENT_SECRET", ""),
            authorize_url="https://appleid.apple.com/auth/authorize",
            token_url="https://appleid.apple.com/auth/token",
            userinfo_url="",
            scope="name email",
            redirect_uri=f"{AUTH_BASE_URL}/auth/callback/{{provider}}",
        ),
        "microsoft": ProviderConfig(
            client_id=os.getenv("MICROSOFT_CLIENT_ID", ""),
            client_secret=os.getenv("MICROSOFT_CLIENT_SECRET", ""),
            authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            userinfo_url="https://graph.microsoft.com/oidc/userinfo",
            scope="openid email profile",
            redirect_uri=f"{AUTH_BASE_URL}/auth/callback/{{provider}}",
        ),
    }


PROVIDERS = _load_providers()


def get_provider(name: str) -> ProviderConfig:
    p = PROVIDERS.get(name)
    if not p:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    return p
