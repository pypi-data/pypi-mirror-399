"""Proliferate SDK Client."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from proliferate.context import (
    AccountContext,
    UserContext,
    get_full_context,
)
from proliferate.context import (
    set_account as ctx_set_account,
)
from proliferate.context import (
    set_tag as ctx_set_tag,
)
from proliferate.context import (
    set_user as ctx_set_user,
)
from proliferate.transport import send_event

logger = logging.getLogger("proliferate")


def _detect_release() -> Optional[str]:
    """
    Auto-detect release version from environment.

    Checks common CI/CD environment variables and falls back to git.
    """
    env_vars = [
        "PROLIFERATE_RELEASE",
        "RELEASE_VERSION",  # Docker build arg convention
        "GITHUB_SHA",
        "VERCEL_GIT_COMMIT_SHA",
        "CF_PAGES_COMMIT_SHA",
        "RENDER_GIT_COMMIT",
        "RAILWAY_GIT_COMMIT_SHA",
        "HEROKU_SLUG_COMMIT",
        "GITLAB_CI_COMMIT_SHA",
        "CIRCLE_SHA1",
        "GIT_COMMIT",
        "COMMIT_SHA",
    ]

    for var in env_vars:
        value = os.environ.get(var)
        if value:
            return value

    # Try git (usually fails in Docker, that's okay)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None


def _detect_environment() -> str:
    """Detect environment from common env vars."""
    env_vars = [
        "PROLIFERATE_ENVIRONMENT",
        "ENVIRONMENT",
        "ENV",
        "PYTHON_ENV",
        "APP_ENV",
    ]

    for var in env_vars:
        value = os.environ.get(var)
        if value:
            return value

    return "production"


def _get_exception_type(exc: BaseException) -> str:
    """
    Get the full module path for an exception type.

    Example: stripe.error.CardError instead of just CardError
    """
    exc_type = type(exc)
    module = exc_type.__module__
    name = exc_type.__qualname__

    if module == "builtins":
        return name
    return f"{module}.{name}"


class ProliferateClient:
    """Main client for the Proliferate SDK."""

    def __init__(self) -> None:
        self._endpoint: Optional[str] = None
        self._api_key: Optional[str] = None
        self._environment: Optional[str] = None
        self._release: Optional[str] = None
        self._initialized = False
        self._enabled = True
        self._original_excepthook: Any = None
        self._original_threading_excepthook: Any = None

    def init(
        self,
        endpoint: str,
        api_key: str,
        environment: Optional[str] = None,
        release: Optional[str] = None,
        enabled: bool = True,
    ) -> None:
        """
        Initialize the SDK.

        Args:
            endpoint: API endpoint URL (e.g., "https://api.example.com/api/v1/errors")
            api_key: Project API key (starts with pk_)
            environment: Environment name. Auto-detected if not provided.
            release: Release version. Auto-detected if not provided.
            enabled: Whether to actually send errors. Set False for testing.
        """
        if not endpoint:
            raise ValueError("endpoint is required")
        if not api_key:
            raise ValueError("api_key is required")

        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._environment = environment or _detect_environment()
        self._release = release or _detect_release()
        self._enabled = enabled
        self._initialized = True

        self._setup_automatic_capture()

        # Send init ping for connection verification
        self._send_init_ping()

        logger.info(
            f"[Proliferate] Initialized - release: {self._release}, "
            f"environment: {self._environment}"
        )

    def _send_init_ping(self) -> None:
        """
        Send an init ping to verify SDK connection.
        This is a lightweight message that confirms the SDK is properly configured.
        """
        if not self._endpoint or not self._api_key:
            return

        if not self._enabled:
            return

        event_id = str(uuid.uuid4())

        payload: dict[str, Any] = {
            "api_key": self._api_key,
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self._environment,
            "release": self._release,
            "type": "message",
            "level": "info",
            "message": "proliferate-sdk-init",
            "extra": {
                "sdk_platform": "python",
                "sdk_version": "0.1.0",
            },
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            send_event(self._endpoint, payload)
        except Exception:
            # Don't fail init if ping fails
            pass

    @property
    def is_initialized(self) -> bool:
        """Check if the SDK is initialized."""
        return self._initialized

    @property
    def release(self) -> Optional[str]:
        """Get the current release version."""
        return self._release

    @property
    def environment(self) -> Optional[str]:
        """Get the current environment."""
        return self._environment

    def set_user(self, user: Optional[UserContext]) -> None:
        """Set user context for the current request/task."""
        ctx_set_user(user)

    def set_account(self, account: Optional[AccountContext]) -> None:
        """Set account context for the current request/task."""
        ctx_set_account(account)

    def set_tag(self, key: str, value: Any) -> None:
        """Set a custom tag for the current request/task."""
        ctx_set_tag(key, value)

    def capture_exception(
        self,
        exception: Optional[BaseException] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Capture an exception and send it to Proliferate.

        Args:
            exception: Exception to capture. If None, captures current exception.
            extra: Additional context data to include.

        Returns:
            Event ID if captured, None otherwise.
        """
        if not self._initialized or not self._endpoint or not self._api_key:
            return None

        if not self._enabled:
            logger.debug("[Proliferate] SDK disabled, not sending error")
            return None

        # Get exception info
        tb = None
        if exception is None:
            exc_info = sys.exc_info()
            if exc_info[0] is None:
                return None
            exception = exc_info[1]
            tb = exc_info[2]
        else:
            tb = exception.__traceback__

        if exception is None:
            return None

        # Format traceback - Python tracebacks are already readable!
        if tb:
            stack_trace = "".join(traceback.format_exception(type(exception), exception, tb))
        else:
            stack_trace = f"{_get_exception_type(exception)}: {exception}"

        event_id = str(uuid.uuid4())

        # Get full context from contextvars
        context_data = get_full_context()

        # Build payload matching the backend's ErrorEventCreate schema
        payload: dict[str, Any] = {
            "api_key": self._api_key,
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self._environment,
            "release": self._release,
            "type": "exception",
            "level": "error",
            "exception": {
                "type": _get_exception_type(exception),
                "message": str(exception),
                "stack": stack_trace,
            },
        }

        # Add context fields at top level (matching JS SDK format)
        if context_data.get("user"):
            payload["user"] = context_data["user"]
        if context_data.get("account"):
            payload["account"] = context_data["account"]

        # Add request info if available
        if context_data.get("request"):
            payload["url"] = context_data["request"].get("url")

        # Combine extra and tags
        combined_extra: dict[str, Any] = {}
        if context_data.get("tags"):
            combined_extra["tags"] = context_data["tags"]
        if context_data.get("request"):
            combined_extra["request"] = context_data["request"]
        if extra:
            combined_extra.update(extra)

        if combined_extra:
            payload["extra"] = combined_extra

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        send_event(self._endpoint, payload)
        return event_id

    def capture_message(
        self,
        message: str,
        level: str = "info",
        extra: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Capture a message (not an exception).

        Args:
            message: Message to capture.
            level: Severity level ('error', 'warning', 'info').
            extra: Additional context data.

        Returns:
            Event ID if captured, None otherwise.
        """
        if not self._initialized or not self._endpoint or not self._api_key:
            return None

        if not self._enabled:
            return None

        event_id = str(uuid.uuid4())

        # Get full context
        context_data = get_full_context()

        payload: dict[str, Any] = {
            "api_key": self._api_key,
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self._environment,
            "release": self._release,
            "type": "message",
            "level": level,
            "message": message,
        }

        # Add context fields
        if context_data.get("user"):
            payload["user"] = context_data["user"]
        if context_data.get("account"):
            payload["account"] = context_data["account"]
        if context_data.get("request"):
            payload["url"] = context_data["request"].get("url")

        # Combine extra
        combined_extra: dict[str, Any] = {}
        if context_data.get("tags"):
            combined_extra["tags"] = context_data["tags"]
        if context_data.get("request"):
            combined_extra["request"] = context_data["request"]
        if extra:
            combined_extra.update(extra)

        if combined_extra:
            payload["extra"] = combined_extra

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        send_event(self._endpoint, payload)
        return event_id

    def _setup_automatic_capture(self) -> None:
        """Set up automatic exception capture for unhandled exceptions."""
        # Hook sys.excepthook for main thread
        self._original_excepthook = sys.excepthook
        sys.excepthook = self._excepthook

        # Hook threading.excepthook for worker threads (Python 3.8+)
        if hasattr(threading, "excepthook"):
            self._original_threading_excepthook = threading.excepthook
            threading.excepthook = self._threading_excepthook

    def _excepthook(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: Any,
    ) -> None:
        """Custom excepthook to capture uncaught exceptions."""
        self.capture_exception(exc_value)

        # Call original handler (prints traceback)
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_tb)

    def _threading_excepthook(self, args: Any) -> None:
        """Custom threading excepthook to capture uncaught exceptions in threads."""
        self.capture_exception(args.exc_value)

        # Call original handler
        if self._original_threading_excepthook:
            self._original_threading_excepthook(args)


# Global client instance
_client = ProliferateClient()
