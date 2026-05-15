"""OAuth2 provider configurations for Agentity Auth."""

from .models import ProviderConfig

PROVIDERS = {
    "google": ProviderConfig(
        client_id="",
        client_secret="",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
        scope="openid email profile",
    ),
    "github": ProviderConfig(
        client_id="",
        client_secret="",
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scope="read:user user:email",
    ),
    "apple": ProviderConfig(
        client_id="",
        client_secret="",
        authorize_url="https://appleid.apple.com/auth/authorize",
        token_url="https://appleid.apple.com/auth/token",
        userinfo_url="",
        scope="name email",
    ),
    "microsoft": ProviderConfig(
        client_id="",
        client_secret="",
        authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        userinfo_url="https://graph.microsoft.com/oidc/userinfo",
        scope="openid email profile",
    ),
}


def get_provider(name: str) -> ProviderConfig:
    p = PROVIDERS.get(name)
    if not p:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    return p


def set_credentials(provider: str, client_id: str, client_secret: str):
    if provider in PROVIDERS:
        PROVIDERS[provider].client_id = client_id
        PROVIDERS[provider].client_secret = client_secret
