"""OAuth authentication configuration for mcvsphere.

Provides OIDCProxy configuration for Authentik or other OIDC providers.
"""

import logging

from mcvsphere.config import Settings

logger = logging.getLogger(__name__)


def create_auth_provider(settings: Settings):
    """Create OAuth provider if enabled.

    Args:
        settings: Application settings with OAuth configuration.

    Returns:
        OIDCProxy instance if OAuth is enabled, None otherwise.
    """
    if not settings.oauth_enabled:
        logger.debug("OAuth authentication disabled")
        return None

    # Import here to avoid loading auth dependencies when not needed
    from fastmcp.server.auth import OIDCProxy

    # Build the OIDC config URL from issuer URL
    # Authentik format: https://auth.example.com/application/o/<app>/
    # Discovery URL: https://auth.example.com/application/o/<app>/.well-known/openid-configuration
    issuer_url = settings.oauth_issuer_url.rstrip("/")
    if not issuer_url.endswith("/.well-known/openid-configuration"):
        config_url = f"{issuer_url}/.well-known/openid-configuration"
    else:
        config_url = issuer_url

    # Build base URL for the MCP server
    # This URL is used for OAuth callbacks and must be HTTPS and externally accessible
    if settings.oauth_base_url:
        base_url = settings.oauth_base_url.rstrip("/")
    else:
        # Default: construct from host/port (for direct HTTPS access)
        host = "localhost" if settings.mcp_host in ("0.0.0.0", "127.0.0.1") else settings.mcp_host
        base_url = f"https://{host}:{settings.mcp_port}"

    logger.info("Configuring OAuth with OIDC provider: %s", issuer_url)
    logger.info("OAuth base URL: %s", base_url)

    try:
        # Note: Authentik's access tokens are opaque and don't include scope claims.
        # We request scopes during authorization but don't validate them in the token.
        # Authentication is sufficient - Authentik enforces scope grants at the IdP level.
        auth = OIDCProxy(
            config_url=config_url,
            client_id=settings.oauth_client_id,
            client_secret=settings.oauth_client_secret.get_secret_value(),
            base_url=base_url,
            required_scopes=[],  # Don't validate scopes in token (Authentik uses opaque tokens)
            allowed_client_redirect_uris=[
                "http://localhost:*",
                "http://127.0.0.1:*",
            ],
            require_authorization_consent=False,
        )

        logger.info("OAuth authentication enabled via OIDC")
        return auth

    except Exception as e:
        logger.error("Failed to configure OAuth: %s", e)
        raise ValueError(f"OAuth configuration failed: {e}") from e
