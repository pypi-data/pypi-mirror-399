"""Audit logging for OAuth-authenticated operations.

Provides centralized logging with OAuth user identity for all tool invocations.
"""

import logging
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("mcvsphere.audit")

# Context variable to store current user info for the request
_current_user: ContextVar[dict[str, Any] | None] = ContextVar("current_user", default=None)


def set_current_user(user_info: dict[str, Any] | None) -> None:
    """Set the current user for this request context.

    Args:
        user_info: User information extracted from OAuth token, or None for anonymous.
    """
    _current_user.set(user_info)


def get_current_user() -> dict[str, Any] | None:
    """Get the current user for this request context.

    Returns:
        User information dict or None if no user is authenticated.
    """
    return _current_user.get()


def get_username() -> str:
    """Get the username of the current user.

    Returns:
        Username string, or 'anonymous' if no user is authenticated.
    """
    user = get_current_user()
    if not user:
        return "anonymous"

    # Try common OAuth claim names in order of preference
    for claim in ("preferred_username", "email", "sub"):
        if value := user.get(claim):
            return str(value)

    return "unknown"


def get_user_groups() -> list[str]:
    """Get the groups of the current user.

    Returns:
        List of group names, or empty list if none.
    """
    user = get_current_user()
    if not user:
        return []
    return user.get("groups", [])


def _sanitize_args(args: dict[str, Any]) -> dict[str, Any]:
    """Remove sensitive values from args for logging.

    Args:
        args: Tool arguments dict.

    Returns:
        Sanitized args with sensitive values redacted.
    """
    sensitive_patterns = {"password", "secret", "token", "credential", "key"}

    def is_sensitive(key: str) -> bool:
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)

    return {k: "***REDACTED***" if is_sensitive(k) else v for k, v in args.items()}


def _truncate(value: str | None, max_length: int = 200) -> str | None:
    """Truncate a string value for logging.

    Args:
        value: String to truncate.
        max_length: Maximum length.

    Returns:
        Truncated string or None.
    """
    if value is None:
        return None
    if len(value) <= max_length:
        return value
    return value[:max_length] + "..."


def audit_log(
    tool_name: str,
    args: dict[str, Any],
    result: str | None = None,
    error: str | None = None,
    duration_ms: float | None = None,
) -> None:
    """Log a tool invocation with OAuth user identity.

    Args:
        tool_name: Name of the MCP tool invoked.
        args: Tool arguments (will be sanitized).
        result: Tool result string (will be truncated).
        error: Error message if tool failed.
        duration_ms: Execution time in milliseconds.
    """
    username = get_username()
    groups = get_user_groups()

    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "user": username,
        "groups": groups,
        "tool": tool_name,
        "args": _sanitize_args(args),
        "duration_ms": round(duration_ms, 2) if duration_ms else None,
        "result": _truncate(result),
        "error": error,
    }

    # Remove None values for cleaner logs
    log_entry = {k: v for k, v in log_entry.items() if v is not None}

    if error:
        logger.warning("AUDIT_FAIL: %s", log_entry)
    else:
        logger.info("AUDIT: %s", log_entry)


def audit_permission_denied(
    tool_name: str,
    args: dict[str, Any],
    required_permission: str,
) -> None:
    """Log a permission denied event.

    Args:
        tool_name: Name of the MCP tool attempted.
        args: Tool arguments (will be sanitized).
        required_permission: The permission level that was required.
    """
    username = get_username()
    groups = get_user_groups()

    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "user": username,
        "groups": groups,
        "tool": tool_name,
        "args": _sanitize_args(args),
        "required_permission": required_permission,
        "event": "PERMISSION_DENIED",
    }

    logger.warning("AUDIT_DENIED: %s", log_entry)


def audit_auth_event(
    event_type: str,
    username: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Log an authentication event.

    Args:
        event_type: Type of auth event (login, logout, token_refresh, etc.)
        username: Username if known.
        details: Additional event details.
    """
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event_type,
        "user": username or get_username(),
        **(details or {}),
    }

    logger.info("AUTH_EVENT: %s", log_entry)
