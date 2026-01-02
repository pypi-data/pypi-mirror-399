"""
Async-safe context storage using contextvars.

This module provides context propagation that works correctly with:
- Synchronous code
- Async code (asyncio)
- Multi-threaded code
- FastAPI/Starlette ASGI applications

Unlike threading.local, contextvars automatically propagates context across
async task boundaries, making it safe for concurrent request handling.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict


class UserContext(TypedDict, total=False):
    """User context from SDK."""

    id: str
    email: Optional[str]


class AccountContext(TypedDict, total=False):
    """Account context from SDK."""

    id: str
    name: Optional[str]


@dataclass
class RequestContext:
    """HTTP request context captured by middleware."""

    request_id: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    path: Optional[str] = None
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    client_ip: Optional[str] = None


@dataclass
class ProliferateContext:
    """
    Complete context for the current request/task.

    This holds all contextual information that will be sent with error reports.
    Each async task gets its own copy via contextvars.
    """

    # User and account context (set by application code)
    user: Optional[UserContext] = None
    account: Optional[AccountContext] = None

    # Custom tags (set by application code)
    tags: dict[str, Any] = field(default_factory=dict)

    # Request context (set by middleware)
    request: Optional[RequestContext] = None

    # Breadcrumbs for debugging (future feature)
    breadcrumbs: list[dict[str, Any]] = field(default_factory=list)


# The magic: each async task gets its own copy of context
_context: ContextVar[Optional[ProliferateContext]] = ContextVar("proliferate_context", default=None)


def get_context() -> ProliferateContext:
    """
    Get the current context, creating one if it doesn't exist.

    This is safe to call from any context (sync, async, threaded).
    """
    ctx = _context.get()
    if ctx is None:
        ctx = ProliferateContext()
        _context.set(ctx)
    return ctx


def reset_context() -> ProliferateContext:
    """
    Reset context for a new request.

    Called by middleware at the start of each request to ensure
    clean context that won't leak between requests.

    Returns the new empty context.
    """
    ctx = ProliferateContext()
    _context.set(ctx)
    return ctx


def clear_context() -> None:
    """Clear all context."""
    _context.set(None)


# --- User Context ---


def set_user(user: Optional[UserContext]) -> None:
    """
    Set user context for the current request.

    Example:
        proliferate.set_user({"id": "user_123", "email": "bob@acme.com"})
    """
    ctx = get_context()
    ctx.user = user


def get_user() -> Optional[UserContext]:
    """Get user context for the current request."""
    ctx = _context.get()
    return ctx.user if ctx else None


# --- Account Context ---


def set_account(account: Optional[AccountContext]) -> None:
    """
    Set account/organization context for the current request.

    Example:
        proliferate.set_account({"id": "acct_456", "name": "Acme Corp"})
    """
    ctx = get_context()
    ctx.account = account


def get_account() -> Optional[AccountContext]:
    """Get account context for the current request."""
    ctx = _context.get()
    return ctx.account if ctx else None


# --- Tags ---


def set_tag(key: str, value: Any) -> None:
    """
    Set a custom tag for the current request.

    Tags are arbitrary key-value pairs that help with debugging.

    Example:
        proliferate.set_tag("feature_flag", "new_checkout_v2")
        proliferate.set_tag("checkout_step", "payment")
    """
    ctx = get_context()
    ctx.tags[key] = value


def get_tag(key: str) -> Optional[Any]:
    """Get a tag value."""
    ctx = _context.get()
    return ctx.tags.get(key) if ctx else None


def get_tags() -> dict[str, Any]:
    """Get all tags for the current request."""
    ctx = _context.get()
    return dict(ctx.tags) if ctx else {}


# --- Request Context ---


def set_request_context(request: RequestContext) -> None:
    """Set request context (called by middleware)."""
    ctx = get_context()
    ctx.request = request


def get_request_context() -> Optional[RequestContext]:
    """Get request context."""
    ctx = _context.get()
    return ctx.request if ctx else None


# --- Full Context for Error Reporting ---


def get_full_context() -> dict[str, Any]:
    """
    Get the full context as a dictionary for error reporting.

    This is called when capturing an exception to include all
    contextual information in the error report.
    """
    ctx = _context.get()
    if ctx is None:
        return {}

    result: dict[str, Any] = {}

    if ctx.user:
        result["user"] = dict(ctx.user)

    if ctx.account:
        result["account"] = dict(ctx.account)

    if ctx.tags:
        result["tags"] = dict(ctx.tags)

    if ctx.request:
        # Filter out sensitive headers
        safe_headers = _filter_sensitive_headers(ctx.request.headers)
        result["request"] = {
            "request_id": ctx.request.request_id,
            "method": ctx.request.method,
            "url": ctx.request.url,
            "path": ctx.request.path,
            "headers": safe_headers,
            "query_params": ctx.request.query_params,
            "client_ip": ctx.request.client_ip,
        }
        # Remove None values
        result["request"] = {k: v for k, v in result["request"].items() if v is not None}

    return result


def _filter_sensitive_headers(headers: dict[str, str]) -> dict[str, str]:
    """Remove sensitive headers from the dict."""
    sensitive_keys = {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "api-key",
        "x-auth-token",
        "x-csrf-token",
        "x-xsrf-token",
    }
    return {k: v for k, v in headers.items() if k.lower() not in sensitive_keys}
