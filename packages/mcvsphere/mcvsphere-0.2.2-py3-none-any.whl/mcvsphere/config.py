"""Configuration management using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ESXi MCP Server configuration.

    Settings are loaded from (in order of precedence):
    1. Environment variables (highest priority)
    2. Config file (YAML/JSON)
    3. Default values
    """

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # vCenter/ESXi connection settings
    vcenter_host: str = Field(description="vCenter or ESXi server hostname/IP")
    vcenter_user: str = Field(description="Login username")
    vcenter_password: SecretStr = Field(description="Login password")

    # Optional VMware settings
    vcenter_datacenter: str | None = Field(
        default=None, description="Datacenter name (auto-selects first if not specified)"
    )
    vcenter_cluster: str | None = Field(
        default=None, description="Cluster name (auto-selects first if not specified)"
    )
    vcenter_datastore: str | None = Field(
        default=None, description="Datastore name (auto-selects largest if not specified)"
    )
    vcenter_network: str = Field(default="VM Network", description="Default network for VMs")
    vcenter_insecure: bool = Field(default=False, description="Skip SSL certificate verification")

    # MCP server settings
    mcp_api_key: SecretStr | None = Field(
        default=None, description="API key for authentication (optional)"
    )
    mcp_host: str = Field(default="0.0.0.0", description="Server bind address")
    mcp_port: int = Field(default=8080, description="Server port")
    mcp_transport: Literal["stdio", "sse", "http", "streamable-http"] = Field(
        default="stdio", description="MCP transport type (http/streamable-http required for OAuth)"
    )

    # OAuth/OIDC settings
    oauth_enabled: bool = Field(
        default=False, description="Enable OAuth authentication via OIDC"
    )
    oauth_issuer_url: str | None = Field(
        default=None,
        description="OIDC issuer URL (e.g., https://auth.example.com/application/o/mcvsphere/)",
    )
    oauth_client_id: str | None = Field(
        default=None, description="OAuth client ID from OIDC provider"
    )
    oauth_client_secret: SecretStr | None = Field(
        default=None, description="OAuth client secret from OIDC provider"
    )
    oauth_scopes: list[str] = Field(
        default_factory=lambda: ["openid", "profile", "email", "groups"],
        description="OAuth scopes to request",
    )
    oauth_required_groups: list[str] = Field(
        default_factory=list,
        description="OAuth groups required for access (empty = any authenticated user)",
    )
    oauth_base_url: str | None = Field(
        default=None,
        description="External base URL for OAuth callbacks (e.g., https://mcp.localhost). Auto-generated if not specified.",
    )

    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    log_file: Path | None = Field(
        default=None, description="Log file path (logs to console if not specified)"
    )

    @field_validator("vcenter_insecure", "oauth_enabled", mode="before")
    @classmethod
    def parse_bool(cls, v: str | bool) -> bool:
        if isinstance(v, bool):
            return v
        return v.lower() in ("true", "1", "yes", "on")

    @model_validator(mode="after")
    def validate_oauth_config(self) -> "Settings":
        """Validate OAuth configuration is complete when enabled."""
        if self.oauth_enabled:
            missing = []
            if not self.oauth_issuer_url:
                missing.append("oauth_issuer_url")
            if not self.oauth_client_id:
                missing.append("oauth_client_id")
            if not self.oauth_client_secret:
                missing.append("oauth_client_secret")
            if missing:
                raise ValueError(
                    f"OAuth is enabled but missing required settings: {', '.join(missing)}"
                )
            # OAuth requires HTTP transport
            if self.mcp_transport == "stdio":
                raise ValueError(
                    "OAuth requires HTTP transport. Set mcp_transport='http', 'sse', or 'streamable-http'"
                )
        return self

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        """Load settings from a YAML file, with env vars taking precedence."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with path.open() as f:
            config_data = yaml.safe_load(f) or {}

        # Map old config keys to new naming convention
        key_mapping = {
            "vcenter_host": "vcenter_host",
            "vcenter_user": "vcenter_user",
            "vcenter_password": "vcenter_password",
            "datacenter": "vcenter_datacenter",
            "cluster": "vcenter_cluster",
            "datastore": "vcenter_datastore",
            "network": "vcenter_network",
            "insecure": "vcenter_insecure",
            "api_key": "mcp_api_key",
            "log_file": "log_file",
            "log_level": "log_level",
        }

        mapped_data = {}
        for old_key, new_key in key_mapping.items():
            if old_key in config_data:
                mapped_data[new_key] = config_data[old_key]

        return cls(**mapped_data)


@lru_cache
def get_settings(config_path: Path | None = None) -> Settings:
    """Get cached settings instance."""
    if config_path:
        return Settings.from_yaml(config_path)
    return Settings()
