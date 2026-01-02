"""FastMCP server setup for mcvsphere."""

import logging
import sys
from pathlib import Path

from fastmcp import FastMCP

from mcvsphere.auth import create_auth_provider
from mcvsphere.config import Settings, get_settings
from mcvsphere.connection import VMwareConnection
from mcvsphere.middleware import RBACMiddleware
from mcvsphere.mixins import (
    ConsoleMixin,
    DiskManagementMixin,
    GuestOpsMixin,
    HostManagementMixin,
    MonitoringMixin,
    NICManagementMixin,
    OVFManagementMixin,
    PowerOpsMixin,
    ResourcesMixin,
    SerialPortMixin,
    SnapshotsMixin,
    VCenterOpsMixin,
    VMLifecycleMixin,
)

logger = logging.getLogger(__name__)


def create_server(settings: Settings | None = None) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        settings: Optional settings instance. If not provided, will load from
                  environment variables and/or config file.

    Returns:
        Configured FastMCP server instance with VMware tools registered.
    """
    if settings is None:
        settings = get_settings()

    # Configure logging - MUST go to stderr for stdio transport compatibility
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # For stdio mode, suppress most logging to avoid interference
    if settings.mcp_transport == "stdio":
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,  # Explicitly use stderr
    )

    # Create auth provider if OAuth enabled
    auth = create_auth_provider(settings)

    # Create FastMCP server
    mcp = FastMCP(
        name="mcvsphere",
        instructions=(
            "Model Control for vSphere - AI-driven VMware virtual machine management. "
            "Provides tools for VM lifecycle management, power operations, "
            "snapshots, guest OS operations, monitoring, and infrastructure resources."
        ),
        auth=auth,
    )

    # Add RBAC middleware when OAuth is enabled
    if settings.oauth_enabled:
        mcp.add_middleware(RBACMiddleware())
        logger.info("RBAC middleware enabled - permissions enforced via OAuth groups")

    # Create shared VMware connection
    logger.info("Connecting to VMware vCenter/ESXi...")
    conn = VMwareConnection(settings)

    # Create and register all mixins
    mixins = [
        VMLifecycleMixin(conn),
        PowerOpsMixin(conn),
        SnapshotsMixin(conn),
        MonitoringMixin(conn),
        GuestOpsMixin(conn),
        ResourcesMixin(conn),
        DiskManagementMixin(conn),
        NICManagementMixin(conn),
        OVFManagementMixin(conn),
        HostManagementMixin(conn),
        VCenterOpsMixin(conn),
        ConsoleMixin(conn),
        SerialPortMixin(conn),
    ]

    tool_count = 0
    resource_count = 0

    for mixin in mixins:
        mixin.register_all(mcp)
        tool_count += len(getattr(mixin, "_mcp_tools", []))
        resource_count += len(getattr(mixin, "_mcp_resources", []))

    # Get actual counts from MCP server
    actual_tools = len(mcp._tool_manager._tools)
    actual_resources = len(mcp._resource_manager._resources)

    logger.info(
        "mcvsphere ready - %d tools, %d resources registered",
        actual_tools,
        actual_resources,
    )

    return mcp


def run_server(config_path: Path | None = None) -> None:
    """Run the mcvsphere server.

    Args:
        config_path: Optional path to YAML/JSON config file.
    """
    # Load settings
    settings = Settings.from_yaml(config_path) if config_path else get_settings()

    # Only print banner for HTTP/SSE modes (stdio must stay clean for JSON-RPC)
    if settings.mcp_transport in ("sse", "http", "streamable-http"):
        try:
            from importlib.metadata import version

            package_version = version("mcvsphere")
        except Exception:
            package_version = "dev"

        print(f"mcvsphere v{package_version}", file=sys.stderr)
        print("─" * 40, file=sys.stderr)
        transport_name = "HTTP" if settings.mcp_transport in ("http", "streamable-http") else "SSE"
        print(
            f"Starting {transport_name} transport on {settings.mcp_host}:{settings.mcp_port}",
            file=sys.stderr,
        )
        if settings.oauth_enabled:
            print(f"OAuth: ENABLED via {settings.oauth_issuer_url}", file=sys.stderr)
            print("RBAC: ENABLED - permissions enforced via groups", file=sys.stderr)
        else:
            print("OAuth: disabled (single-user mode)", file=sys.stderr)
        print("─" * 40, file=sys.stderr)

    # Create and run server
    mcp = create_server(settings)

    if settings.mcp_transport in ("http", "streamable-http"):
        mcp.run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)
    elif settings.mcp_transport == "sse":
        mcp.run(transport="sse", host=settings.mcp_host, port=settings.mcp_port)
    else:
        # stdio mode - suppress banner to keep stdout clean for JSON-RPC
        mcp.run(show_banner=False)
