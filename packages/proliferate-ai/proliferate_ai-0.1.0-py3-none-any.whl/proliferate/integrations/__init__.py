"""
Proliferate framework integrations.

This module provides integrations for popular Python web frameworks.

Available integrations:
- FastAPI: ProliferateMiddleware for ASGI applications
- Flask: init_app() function and FlaskProliferate extension
- Django: ProliferateMiddleware for Django applications
- Celery: init_celery() for background task monitoring
"""

from proliferate.integrations.fastapi import ProliferateMiddleware as FastAPIMiddleware
from proliferate.integrations.flask import FlaskProliferate, init_app

# Re-export FastAPI middleware with its original name for backwards compatibility
ProliferateMiddleware = FastAPIMiddleware

__all__ = [
    # FastAPI
    "ProliferateMiddleware",
    "FastAPIMiddleware",
    # Flask
    "FlaskProliferate",
    "init_app",
]

# Lazy imports for optional dependencies
def __getattr__(name: str):
    if name in ("DjangoMiddleware", "ProliferateLoggingHandler"):
        from proliferate.integrations.django import (
            ProliferateMiddleware as DjangoMiddleware,
            ProliferateLoggingHandler,
        )
        if name == "DjangoMiddleware":
            return DjangoMiddleware
        return ProliferateLoggingHandler

    if name in ("init_celery", "capture_task_error", "proliferate_task"):
        from proliferate.integrations.celery import (
            init_celery,
            capture_task_error,
            proliferate_task,
        )
        if name == "init_celery":
            return init_celery
        if name == "capture_task_error":
            return capture_task_error
        return proliferate_task

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
