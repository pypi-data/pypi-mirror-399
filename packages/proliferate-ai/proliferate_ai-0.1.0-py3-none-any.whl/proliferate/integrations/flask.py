"""
Flask integration for Proliferate.

This module provides integration for Flask applications that:
1. Captures request context (method, URL, headers, etc.)
2. Resets context at the start of each request
3. Catches unhandled exceptions and reports them

Example:
    from flask import Flask
    import proliferate
    from proliferate.integrations.flask import init_app

    app = Flask(__name__)

    proliferate.init(
        endpoint="https://api.example.com/api/v1/errors",
        api_key="pk_xxx",
    )

    init_app(app)

    @app.route("/api/checkout", methods=["POST"])
    def checkout():
        proliferate.set_account({"id": "acct_123", "name": "Acme Corp"})
        proliferate.set_user({"id": "user_456", "email": "bob@acme.com"})
        # ... business logic
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from proliferate.client import _client
from proliferate.context import RequestContext, reset_context, set_request_context

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger("proliferate")


def init_app(app: Flask) -> None:
    """
    Initialize Proliferate for a Flask application.

    This sets up:
    1. A before_request hook that resets context and captures request info
    2. An error handler that captures exceptions to Proliferate

    Args:
        app: The Flask application instance

    Usage:
        from flask import Flask
        from proliferate.integrations.flask import init_app

        app = Flask(__name__)
        init_app(app)
    """

    @app.before_request  # type: ignore[misc, untyped-decorator, unused-ignore]
    def proliferate_before_request() -> None:
        """Reset context and capture request information."""
        # Reset context for this request (prevents leaking between requests)
        reset_context()

        # Extract request context
        request_context = _extract_request_context()
        set_request_context(request_context)

    @app.errorhandler(Exception)  # type: ignore[misc, untyped-decorator, unused-ignore]
    def proliferate_error_handler(error: Exception) -> None:
        """Capture unhandled exceptions to Proliferate."""
        # Capture the exception with full context
        _client.capture_exception(error)

        # Re-raise to let Flask handle it (return 500 response)
        raise error


def _extract_request_context() -> RequestContext:
    """Extract request context from the Flask request."""
    from flask import request

    # Generate or use existing request ID
    request_id = (
        request.headers.get("x-request-id")
        or request.headers.get("x-correlation-id")
        or str(uuid.uuid4())
    )

    # Get client IP (handle proxies)
    client_ip = request.remote_addr

    # Check for forwarded IP
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take the first IP in the chain (original client)
        client_ip = forwarded_for.split(",")[0].strip()

    # Convert headers to dict (lowercase keys for consistency)
    headers = {k.lower(): v for k, v in request.headers}

    # Convert query params to dict
    query_params = dict(request.args)

    return RequestContext(
        request_id=request_id,
        method=request.method,
        url=request.url,
        path=request.path,
        headers=headers,
        query_params=query_params,
        client_ip=client_ip,
    )


class FlaskProliferate:
    """
    Alternative class-based Flask extension.

    This follows the Flask extension pattern and can be used with
    the application factory pattern.

    Usage:
        # Option 1: Direct initialization
        from flask import Flask
        from proliferate.integrations.flask import FlaskProliferate

        app = Flask(__name__)
        proliferate_ext = FlaskProliferate(app)

        # Option 2: Application factory pattern
        proliferate_ext = FlaskProliferate()

        def create_app():
            app = Flask(__name__)
            proliferate_ext.init_app(app)
            return app
    """

    def __init__(self, app: Flask | None = None) -> None:
        """
        Initialize the extension.

        Args:
            app: Optional Flask application. If provided, init_app is called.
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize the extension with a Flask application.

        Args:
            app: The Flask application instance
        """
        init_app(app)
