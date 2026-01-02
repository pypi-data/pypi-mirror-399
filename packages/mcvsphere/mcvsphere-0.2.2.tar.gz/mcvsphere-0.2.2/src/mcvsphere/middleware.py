"""Middleware for permission checking and audit logging.

Provides decorators and hooks for wrapping tool execution with:
- OAuth permission validation
- Audit logging with user identity
- FastMCP middleware integration for RBAC
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

import mcp.types as mt
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult

from mcvsphere.audit import (
    audit_log,
    audit_permission_denied,
    get_current_user,
    get_user_groups,
    set_current_user,
)
from mcvsphere.permissions import (
    PermissionDeniedError,
    PermissionLevel,
    check_permission,
    get_required_permission,
)

if TYPE_CHECKING:
    from fastmcp.server.context import Context

logger = logging.getLogger(__name__)


def with_permission_check(tool_name: str) -> Callable:
    """Decorator factory for permission checking and audit logging.

    Args:
        tool_name: Name of the MCP tool being wrapped.

    Returns:
        Decorator that wraps the tool function with permission checks and audit logging.

    Example:
        @with_permission_check("power_on")
        def power_on(self, name: str) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get user groups from current context
            groups = get_user_groups()
            user = get_current_user()
            username = "anonymous"
            if user:
                username = user.get(
                    "preferred_username", user.get("email", user.get("sub", "unknown"))
                )

            # Check permission
            if not check_permission(tool_name, groups):
                required = get_required_permission(tool_name)
                audit_permission_denied(tool_name, kwargs, required.value)
                raise PermissionDeniedError(username, tool_name, required)

            # Execute tool with timing
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                audit_log(tool_name, kwargs, result=str(result), duration_ms=duration_ms)
                return result
            except PermissionDeniedError:
                # Re-raise permission errors without additional logging
                raise
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                audit_log(tool_name, kwargs, error=str(e), duration_ms=duration_ms)
                raise

        return wrapper

    return decorator


def extract_user_from_context(ctx) -> dict[str, Any] | None:
    """Extract user information from FastMCP context.

    Uses FastMCP's dependency injection to get the access token from
    the current request's context variable.

    Args:
        ctx: FastMCP Context object (unused, kept for API compatibility).

    Returns:
        User info dict from OAuth token claims, or None if not authenticated.
    """
    try:
        # FastMCP stores access token in a context variable, accessed via dependency
        from fastmcp.server.dependencies import get_access_token

        access_token = get_access_token()
        if access_token and hasattr(access_token, "claims"):
            return access_token.claims
    except (RuntimeError, ImportError) as e:
        # RuntimeError: No active HTTP request context
        # ImportError: FastMCP auth dependencies not available
        logger.debug("Could not get access token: %s", e)

    return None


def setup_user_context(ctx) -> None:
    """Set up user context from FastMCP context for the current request.

    Call this at the start of request handling to make user info
    available throughout the request via get_current_user().

    Args:
        ctx: FastMCP Context object.
    """
    user_info = extract_user_from_context(ctx)
    set_current_user(user_info)


class PermissionMiddleware:
    """Middleware for adding permission checks to all tools.

    This can be used to wrap mixin tool registration with permission checking.
    """

    def __init__(self, oauth_enabled: bool = False):
        """Initialize middleware.

        Args:
            oauth_enabled: Whether OAuth authentication is enabled.
        """
        self.oauth_enabled = oauth_enabled

    def wrap_tool(self, tool_name: str, func: Callable) -> Callable:
        """Wrap a tool function with permission checking.

        Args:
            tool_name: Name of the tool.
            func: Original tool function.

        Returns:
            Wrapped function with permission checks.
        """
        if not self.oauth_enabled:
            # No auth - just add basic audit logging
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    audit_log(tool_name, kwargs, result=str(result), duration_ms=duration_ms)
                    return result
                except Exception as e:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    audit_log(tool_name, kwargs, error=str(e), duration_ms=duration_ms)
                    raise

            return wrapper

        # With auth - add permission checking
        return with_permission_check(tool_name)(func)


def get_permission_summary() -> dict[str, list[str]]:
    """Get a summary of tools grouped by permission level.

    Returns:
        Dict mapping permission level names to lists of tool names.
    """
    from mcvsphere.permissions import TOOL_PERMISSIONS

    summary: dict[str, list[str]] = {level.value: [] for level in PermissionLevel}

    for tool_name, level in TOOL_PERMISSIONS.items():
        summary[level.value].append(tool_name)

    # Sort tool names within each level
    for level in summary:
        summary[level].sort()

    return summary


class RBACMiddleware(Middleware):
    """FastMCP middleware for Role-Based Access Control.

    Integrates with FastMCP's middleware system to enforce permissions
    on every tool call based on OAuth group memberships.

    Example:
        mcp = FastMCP("my-server", auth=oauth_provider)
        mcp.add_middleware(RBACMiddleware())
    """

    def _extract_user_from_context(
        self, fastmcp_ctx: "Context | None"
    ) -> dict[str, Any] | None:
        """Extract user claims from FastMCP context.

        Uses FastMCP's dependency injection to retrieve the access token
        from the current request's context variable.

        Args:
            fastmcp_ctx: FastMCP Context object (unused, kept for API compatibility).

        Returns:
            User claims dict from OAuth token, or None if not authenticated.
        """
        try:
            # FastMCP stores access token in a context variable, accessed via dependency
            from fastmcp.server.dependencies import get_access_token

            access_token = get_access_token()
            if access_token and hasattr(access_token, "claims"):
                return access_token.claims
        except (RuntimeError, ImportError) as e:
            # RuntimeError: No active HTTP request context
            # ImportError: FastMCP auth dependencies not available
            logger.debug("Could not get access token: %s", e)

        return None

    def _get_username(self, claims: dict[str, Any] | None) -> str:
        """Extract username from OAuth claims.

        Args:
            claims: OAuth token claims dict.

        Returns:
            Username string, or 'anonymous' if no claims.
        """
        if not claims:
            return "anonymous"

        for claim in ("preferred_username", "email", "sub"):
            if value := claims.get(claim):
                return str(value)

        return "unknown"

    def _get_groups(self, claims: dict[str, Any] | None) -> list[str]:
        """Extract groups from OAuth claims.

        Args:
            claims: OAuth token claims dict.

        Returns:
            List of group names, or empty list if no claims.
        """
        if not claims:
            return []

        groups = claims.get("groups", [])
        if isinstance(groups, list):
            return groups
        return []

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """Intercept tool calls to enforce RBAC permissions.

        Args:
            context: Middleware context containing tool call params.
            call_next: Next handler in the middleware chain.

        Returns:
            Tool result if permitted.

        Raises:
            PermissionDeniedError: If user lacks required permission.
        """
        # Extract tool name and arguments from the request
        tool_name = context.message.name
        tool_args = context.message.arguments or {}

        # Get user info from OAuth context
        claims = self._extract_user_from_context(context.fastmcp_context)
        username = self._get_username(claims)
        groups = self._get_groups(claims)

        # Set up audit context for this request
        set_current_user(claims)

        # Check permission
        if not check_permission(tool_name, groups):
            required = get_required_permission(tool_name)
            logger.warning(
                "Permission denied: user=%s groups=%s tool=%s required=%s",
                username,
                groups,
                tool_name,
                required.value,
            )
            audit_permission_denied(tool_name, tool_args, required.value)
            raise PermissionDeniedError(username, tool_name, required)

        # Permission granted - execute tool with timing
        start_time = time.perf_counter()
        try:
            result = await call_next(context)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Audit successful execution
            # ToolResult can be complex, just log that it succeeded
            audit_log(tool_name, tool_args, result="success", duration_ms=duration_ms)

            logger.debug(
                "Tool executed: user=%s tool=%s duration=%.2fms",
                username,
                tool_name,
                duration_ms,
            )

            return result

        except PermissionDeniedError:
            # Re-raise without additional logging
            raise
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            audit_log(tool_name, tool_args, error=str(e), duration_ms=duration_ms)
            logger.error(
                "Tool failed: user=%s tool=%s error=%s duration=%.2fms",
                username,
                tool_name,
                str(e),
                duration_ms,
            )
            raise
