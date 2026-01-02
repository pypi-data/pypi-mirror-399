"""
Proliferate - Error Monitoring SDK for Python

A lightweight, async-safe error monitoring SDK for Python applications.
Provides automatic exception capture with rich context for debugging.

Quick Start:
    import proliferate
    from proliferate.integrations.fastapi import ProliferateMiddleware

    # Initialize the SDK
    proliferate.init(
        endpoint="https://api.example.com/api/v1/errors",
        api_key="pk_abc123",
        # environment and release are auto-detected
    )

    # Add middleware to FastAPI
    app.add_middleware(ProliferateMiddleware)

    # Set context in your route handlers
    @app.post("/api/checkout")
    async def checkout(request: CheckoutRequest, user: User = Depends(get_user)):
        proliferate.set_account({"id": user.account_id, "name": user.account_name})
        proliferate.set_user({"id": user.id, "email": user.email})
        proliferate.set_tag("endpoint", "checkout")

        # ... your business logic ...
        # Any unhandled exception will be automatically captured with full context

Manual Capture (for handled exceptions):
    try:
        result = await risky_operation()
    except PaymentDeclined as e:
        # Capture handled exception
        proliferate.capture_exception(e, extra={"payment_method": "card"})
        return {"error": "Payment declined"}

    # Capture informational messages
    proliferate.capture_message("User did something unusual", level="warning")
"""

from typing import Any, Optional

from proliferate.client import _client
from proliferate.context import AccountContext, UserContext

__version__ = "0.1.0"
__all__ = [
    # Core functions
    "init",
    "set_user",
    "set_account",
    "set_tag",
    "capture_exception",
    "capture_message",
    # Types
    "UserContext",
    "AccountContext",
    # Accessor functions
    "is_initialized",
    "get_release",
    "get_environment",
]


def init(
    endpoint: str,
    api_key: str,
    environment: Optional[str] = None,
    release: Optional[str] = None,
    enabled: bool = True,
) -> None:
    """
    Initialize the Proliferate SDK.

    Args:
        endpoint: API endpoint URL (e.g., "https://api.example.com/api/v1/errors")
        api_key: Project API key (starts with pk_)
        environment: Environment name (e.g., 'production', 'staging').
                     Auto-detected from ENVIRONMENT, ENV, etc. if not provided.
        release: Release version (e.g., git SHA).
                 Auto-detected from GITHUB_SHA, RELEASE_VERSION, etc. if not provided.
        enabled: Whether to actually send errors. Set False for local development.

    Example:
        proliferate.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_abc123",
        )
    """
    _client.init(
        endpoint=endpoint,
        api_key=api_key,
        environment=environment,
        release=release,
        enabled=enabled,
    )


def set_user(user: Optional[UserContext]) -> None:
    """
    Set user context for error reports.

    This context will be included in all error reports from the current
    request/task. Call this early in your request handler.

    Args:
        user: User context dict with 'id' and optional 'email', or None to clear.

    Example:
        proliferate.set_user({"id": "user_123", "email": "bob@example.com"})
    """
    _client.set_user(user)


def set_account(account: Optional[AccountContext]) -> None:
    """
    Set account/organization context for error reports.

    This context will be included in all error reports from the current
    request/task. Useful for B2B apps to track which customer is affected.

    Args:
        account: Account context dict with 'id' and optional 'name', or None to clear.

    Example:
        proliferate.set_account({"id": "acct_456", "name": "Acme Corp"})
    """
    _client.set_account(account)


def set_tag(key: str, value: Any) -> None:
    """
    Set a custom tag for error reports.

    Tags are arbitrary key-value pairs that help with debugging and filtering.
    They're included in all error reports from the current request/task.

    Args:
        key: Tag name
        value: Tag value (will be JSON serialized)

    Example:
        proliferate.set_tag("feature_flag", "new_checkout_v2")
        proliferate.set_tag("checkout_step", "payment")
        proliferate.set_tag("cart_total", 99.99)
    """
    _client.set_tag(key, value)


def capture_exception(
    exception: Optional[BaseException] = None,
    extra: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """
    Capture an exception and send it to Proliferate.

    Use this for handled exceptions that you want to track but don't want
    to re-raise. For unhandled exceptions, the middleware will capture them
    automatically.

    Args:
        exception: Exception to capture. If None, captures the current exception
                   from sys.exc_info() (useful in except blocks).
        extra: Additional context data to include with this specific error.

    Returns:
        Event ID if captured, None if SDK not initialized or capture failed.

    Example:
        try:
            result = await risky_operation()
        except PaymentDeclined as e:
            proliferate.capture_exception(e, extra={"order_id": "123"})
            return {"error": "Payment declined"}

        # Or capture current exception:
        except Exception:
            proliferate.capture_exception()  # Captures from sys.exc_info()
            raise
    """
    return _client.capture_exception(exception=exception, extra=extra)


def capture_message(
    message: str,
    level: str = "info",
    extra: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """
    Capture a message (not an exception).

    Use this to track important events that aren't exceptions, like
    unusual user behavior or configuration issues.

    Args:
        message: Message to capture.
        level: Severity level ('error', 'warning', 'info').
        extra: Additional context data.

    Returns:
        Event ID if captured, None if SDK not initialized.

    Example:
        proliferate.capture_message(
            "User attempted to access restricted resource",
            level="warning",
            extra={"resource": "/admin/users"}
        )
    """
    return _client.capture_message(message=message, level=level, extra=extra)


def is_initialized() -> bool:
    """Check if the SDK is initialized."""
    return _client.is_initialized


def get_release() -> Optional[str]:
    """Get the current release version."""
    return _client.release


def get_environment() -> Optional[str]:
    """Get the current environment."""
    return _client.environment
