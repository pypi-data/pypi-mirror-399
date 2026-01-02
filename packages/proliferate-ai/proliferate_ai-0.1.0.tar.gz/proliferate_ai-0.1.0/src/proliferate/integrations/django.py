"""
Django integration for Proliferate.

This module provides middleware that:
1. Captures request context (method, URL, headers, etc.)
2. Resets context at the start of each request
3. Catches unhandled exceptions and reports them
4. Optionally sets user context from Django's authentication

Example:
    # settings.py
    MIDDLEWARE = [
        'proliferate.integrations.django.ProliferateMiddleware',
        'django.middleware.security.SecurityMiddleware',
        # ... other middleware
    ]

    # Configure Proliferate (e.g., in settings.py or apps.py)
    import proliferate

    proliferate.init(
        endpoint="https://api.example.com/api/v1/errors",
        api_key="pk_xxx",
    )

    # Optionally configure the middleware
    PROLIFERATE_CONFIG = {
        'capture_user': True,
        'capture_body': False,
        'exclude_paths': ['/health/', '/metrics/'],
    }
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any, Callable

from proliferate.client import _client
from proliferate.context import (
    RequestContext,
    UserContext,
    reset_context,
    set_request_context,
    set_user_context,
)

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("proliferate")


def _get_client_ip(request: HttpRequest) -> str | None:
    """Extract client IP from request, handling proxies."""
    # Check for forwarded IP first
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        return x_forwarded_for.split(",")[0].strip()

    # Fall back to REMOTE_ADDR
    return request.META.get("REMOTE_ADDR")


def _extract_headers(request: HttpRequest, exclude: list[str] | None = None) -> dict[str, str]:
    """Extract headers from Django request, excluding sensitive ones."""
    exclude = exclude or ["HTTP_AUTHORIZATION", "HTTP_COOKIE"]
    exclude_set = {h.upper() for h in exclude}

    headers = {}
    for key, value in request.META.items():
        if key.startswith("HTTP_") and key not in exclude_set:
            # Convert HTTP_X_HEADER to x-header format
            header_name = key[5:].lower().replace("_", "-")
            headers[header_name] = value

    return headers


class ProliferateMiddleware:
    """
    Django middleware for Proliferate error monitoring.

    This middleware:
    1. Resets context at the start of each request (prevents context leaking)
    2. Captures request information (method, URL, headers)
    3. Optionally captures authenticated user info
    4. Catches unhandled exceptions and reports them to Proliferate

    Configuration (in settings.py):
        PROLIFERATE_CONFIG = {
            'capture_user': True,          # Capture Django user if authenticated
            'capture_body': False,         # Capture request body (not recommended)
            'exclude_paths': ['/health/'], # Skip these paths
            'exclude_headers': [],         # Additional headers to exclude
        }
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware."""
        self.get_response = get_response
        self._config = self._load_config()
        logger.debug("ProliferateMiddleware initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from Django settings."""
        try:
            from django.conf import settings

            return getattr(settings, "PROLIFERATE_CONFIG", {})
        except Exception:
            return {}

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Handle the request and capture any exceptions."""
        # Check if this path should be excluded
        exclude_paths = self._config.get("exclude_paths", [])
        if any(request.path.startswith(p) for p in exclude_paths):
            return self.get_response(request)

        # Reset context for this request (prevents leaking between requests)
        reset_context()

        # Capture request information
        request_context = self._extract_request_context(request)
        set_request_context(request_context)

        # Capture user context if authenticated and configured
        if self._config.get("capture_user", True):
            self._capture_user_context(request)

        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            # Capture the exception with full context
            _client.capture_exception(exc)
            # Re-raise so Django can handle it
            raise

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> HttpResponse | None:
        """
        Handle exceptions that occur in view functions.

        This is called by Django's exception handling before the middleware
        chain is unwound, giving us a chance to capture the exception
        even if a later middleware handles it.
        """
        # Capture to Proliferate
        _client.capture_exception(exception)

        # Return None to let Django continue normal exception handling
        return None

    def _extract_request_context(self, request: HttpRequest) -> RequestContext:
        """Extract request context from the Django request."""
        # Generate or use existing request ID
        request_id = (
            request.META.get("HTTP_X_REQUEST_ID")
            or request.META.get("HTTP_X_CORRELATION_ID")
            or str(uuid.uuid4())
        )

        # Get client IP
        client_ip = _get_client_ip(request)

        # Extract headers
        exclude_headers = self._config.get("exclude_headers", [])
        headers = _extract_headers(request, exclude_headers)

        # Query params
        query_params = dict(request.GET.items())

        return RequestContext(
            request_id=request_id,
            method=request.method,
            url=request.build_absolute_uri(),
            path=request.path,
            headers=headers,
            query_params=query_params,
            client_ip=client_ip,
        )

    def _capture_user_context(self, request: HttpRequest) -> None:
        """Capture user context from Django's authentication system."""
        user = getattr(request, "user", None)
        if user is None:
            return

        # Check if user is authenticated (handles AnonymousUser)
        if not getattr(user, "is_authenticated", False):
            return

        user_context = UserContext(
            id=str(getattr(user, "id", None) or getattr(user, "pk", None) or ""),
            email=getattr(user, "email", None),
            username=getattr(user, "username", None),
        )

        # Only set if we have at least an ID
        if user_context.id:
            set_user_context(user_context)


def setup_logging_handler() -> None:
    """
    Set up a Django logging handler that sends errors to Proliferate.

    This can be used in addition to or instead of the middleware
    to capture errors logged via Django's logging system.

    Example in settings.py:
        LOGGING = {
            'version': 1,
            'handlers': {
                'proliferate': {
                    'level': 'ERROR',
                    'class': 'proliferate.integrations.django.ProliferateLoggingHandler',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['proliferate'],
                    'level': 'ERROR',
                },
            },
        }
    """
    pass  # Handler class is defined below


class ProliferateLoggingHandler(logging.Handler):
    """
    Python logging handler that sends log records to Proliferate.

    Use this to capture errors logged via Django's logging system.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Send a log record to Proliferate."""
        try:
            # Extract exception info if available
            if record.exc_info:
                exc_type, exc_value, exc_tb = record.exc_info
                if exc_value is not None:
                    _client.capture_exception(
                        exc_value,
                        extra={
                            "logger": record.name,
                            "level": record.levelname,
                            "message": record.getMessage(),
                        },
                    )
                    return

            # Otherwise capture as a message
            level = "error" if record.levelno >= logging.ERROR else "warning"
            _client.capture_message(
                record.getMessage(),
                level=level,
                extra={
                    "logger": record.name,
                    "level": record.levelname,
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                },
            )
        except Exception:
            # Don't let logging errors cause more problems
            self.handleError(record)
