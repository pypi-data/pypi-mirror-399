"""
Celery integration for Proliferate.

This module provides signal handlers that capture Celery task failures
and retries to Proliferate.

Example:
    # celery.py
    from celery import Celery
    import proliferate
    from proliferate.integrations.celery import init_celery

    # Initialize Proliferate
    proliferate.init(
        endpoint="https://api.example.com/api/v1/errors",
        api_key="pk_xxx",
    )

    # Initialize Celery integration
    init_celery()

    # Or with options
    init_celery(
        capture_args=False,      # Don't capture task arguments (privacy)
        capture_retries=True,    # Capture retry events as warnings
        ignore_expected=True,    # Skip expected/handled exceptions
    )

    app = Celery('tasks')

    @app.task
    def my_task(x, y):
        return x + y
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from proliferate.client import _client
from proliferate.context import reset_context

if TYPE_CHECKING:
    from celery import Task
    from celery.exceptions import Retry

logger = logging.getLogger("proliferate")

# Type variable for task decorators
F = TypeVar("F", bound=Callable[..., Any])

# Track if already initialized to prevent double registration
_initialized = False


def init_celery(
    capture_args: bool = False,
    capture_retries: bool = True,
    ignore_expected: bool = True,
    max_arg_length: int = 200,
) -> None:
    """
    Initialize Celery integration with Proliferate.

    This registers signal handlers to capture task failures and retries.

    Args:
        capture_args: Whether to capture task arguments. May contain sensitive
                      data, so defaults to False.
        capture_retries: Whether to capture task retries as warnings.
                         Defaults to True.
        ignore_expected: Whether to skip capturing "expected" exceptions
                         (those that have `expected=True`). Defaults to True.
        max_arg_length: Maximum length for captured argument strings.

    Example:
        from proliferate.integrations.celery import init_celery

        init_celery(
            capture_args=False,
            capture_retries=True,
        )
    """
    global _initialized

    if _initialized:
        logger.warning("Celery integration already initialized, skipping")
        return

    try:
        from celery.signals import (
            task_failure,
            task_prerun,
            task_retry,
        )
    except ImportError:
        logger.error("Celery is not installed. Install with: pip install celery")
        return

    def truncate_arg(arg: Any) -> str:
        """Truncate argument string to max length."""
        s = repr(arg)
        if len(s) > max_arg_length:
            return s[: max_arg_length - 3] + "..."
        return s

    @task_prerun.connect
    def handle_task_prerun(
        sender: Task | None = None,
        task_id: str | None = None,
        task: Task | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        **kw: Any,
    ) -> None:
        """Reset context at the start of each task to prevent leaking."""
        reset_context()

    @task_failure.connect
    def handle_task_failure(
        sender: Task | None = None,
        task_id: str | None = None,
        exception: BaseException | None = None,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        traceback: Any | None = None,
        einfo: Any | None = None,
        **kw: Any,
    ) -> None:
        """Capture task failure to Proliferate."""
        if exception is None:
            return

        # Check if this is an expected exception
        if ignore_expected and getattr(exception, "expected", False):
            logger.debug(f"Skipping expected exception in task {sender}")
            return

        # Build extra context
        extra: dict[str, Any] = {
            "celery": True,
            "task_id": task_id,
        }

        if sender is not None:
            extra["task_name"] = sender.name
            extra["task_retries"] = getattr(sender.request, "retries", 0)
            extra["task_hostname"] = getattr(sender.request, "hostname", None)
            extra["task_delivery_info"] = getattr(sender.request, "delivery_info", None)

        if capture_args:
            if args:
                extra["task_args"] = [truncate_arg(a) for a in args]
            if kwargs:
                extra["task_kwargs"] = {
                    k: truncate_arg(v) for k, v in kwargs.items()
                }

        # Capture to Proliferate
        if isinstance(exception, Exception):
            _client.capture_exception(exception, extra=extra)
        else:
            _client.capture_message(
                str(exception),
                level="error",
                extra=extra,
            )

    if capture_retries:
        @task_retry.connect
        def handle_task_retry(
            sender: Task | None = None,
            reason: BaseException | str | None = None,
            request: Any | None = None,
            **kw: Any,
        ) -> None:
            """Capture task retry as a warning."""
            extra: dict[str, Any] = {
                "celery": True,
                "celery_retry": True,
            }

            if sender is not None:
                extra["task_name"] = sender.name

            if request is not None:
                extra["task_id"] = getattr(request, "id", None)
                extra["task_retries"] = getattr(request, "retries", 0)
                extra["task_hostname"] = getattr(request, "hostname", None)

            # Capture as warning
            if isinstance(reason, Exception):
                _client.capture_message(
                    f"Task {sender.name if sender else 'unknown'} retrying: {reason}",
                    level="warning",
                    extra=extra,
                )
            else:
                _client.capture_message(
                    f"Task {sender.name if sender else 'unknown'} retrying: {reason}",
                    level="warning",
                    extra=extra,
                )

    _initialized = True
    logger.info("Celery integration initialized")


def capture_task_error(task: Task, error: Exception, **extra: Any) -> None:
    """
    Manually capture a task error with context.

    Use this when you catch and handle exceptions within a task
    but still want to report them.

    Args:
        task: The Celery task instance
        error: The exception to capture
        **extra: Additional context to include

    Example:
        @app.task
        def my_task():
            try:
                risky_operation()
            except SpecificError as e:
                capture_task_error(my_task, e, operation="risky_operation")
                # Handle the error gracefully
                return {"status": "failed", "error": str(e)}
    """
    context = {
        "celery": True,
        "task_name": task.name,
        "task_id": getattr(task.request, "id", None),
        "task_retries": getattr(task.request, "retries", 0),
        **extra,
    }

    _client.capture_exception(error, extra=context)


def proliferate_task(
    capture_args: bool = False,
    capture_result: bool = False,
    ignore_exceptions: tuple[type[Exception], ...] = (),
) -> Callable[[F], F]:
    """
    Decorator that adds Proliferate error capturing to a Celery task.

    Use this as an alternative to global signal handlers when you want
    per-task configuration.

    Args:
        capture_args: Whether to capture task arguments.
        capture_result: Whether to capture task result on success.
        ignore_exceptions: Exception types to ignore.

    Example:
        from proliferate.integrations.celery import proliferate_task

        @app.task
        @proliferate_task(capture_args=True)
        def my_task(x, y):
            return x + y

        @app.task
        @proliferate_task(ignore_exceptions=(ValueError,))
        def validation_task(data):
            if not data:
                raise ValueError("Empty data")
            return process(data)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Reset context at start
            reset_context()

            try:
                result = func(*args, **kwargs)

                # Optionally capture success
                if capture_result:
                    _client.capture_message(
                        f"Task {func.__name__} completed successfully",
                        level="info",
                        extra={
                            "celery": True,
                            "task_name": func.__name__,
                            "result": repr(result)[:200],
                        },
                    )

                return result

            except ignore_exceptions:
                # Re-raise without capturing
                raise

            except Exception as exc:
                # Capture the error
                extra: dict[str, Any] = {
                    "celery": True,
                    "task_name": func.__name__,
                }

                if capture_args:
                    extra["task_args"] = repr(args)[:200]
                    extra["task_kwargs"] = repr(kwargs)[:200]

                _client.capture_exception(exc, extra=extra)
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
