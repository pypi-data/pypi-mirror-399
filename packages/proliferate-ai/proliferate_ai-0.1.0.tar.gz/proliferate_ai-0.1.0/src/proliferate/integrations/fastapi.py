"""
FastAPI/Starlette integration for Proliferate.

This module provides middleware that:
1. Captures request context (method, URL, headers, etc.)
2. Resets context at the start of each request
3. Catches unhandled exceptions and reports them

Example:
    from fastapi import FastAPI, Depends
    from fastapi.security import OAuth2PasswordBearer
    import proliferate
    from proliferate.integrations.fastapi import ProliferateMiddleware

    app = FastAPI()
    app.add_middleware(ProliferateMiddleware)
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    proliferate.init(
        endpoint="https://api.example.com/api/v1/errors",
        api_key="pk_xxx",
    )

    # Set Proliferate context in your auth dependency - runs once per request
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
        user = await verify_token(token)

        # Set context here, not in every route handler
        proliferate.set_user({"id": user.id, "email": user.email})
        proliferate.set_account({"id": user.account_id, "name": user.account_name})

        return user

    # Routes stay clean - context is already set by the dependency
    @app.post("/api/checkout")
    async def checkout(request: CheckoutRequest, user: User = Depends(get_current_user)):
        # Any unhandled exception here automatically includes user/account context
        ...
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from proliferate.client import _client
from proliferate.context import RequestContext, reset_context, set_request_context

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger("proliferate")


class ProliferateMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware for Proliferate error monitoring.

    This middleware:
    1. Resets context at the start of each request (prevents context leaking)
    2. Captures request information (method, URL, headers)
    3. Catches unhandled exceptions and reports them to Proliferate
    4. Re-raises exceptions so FastAPI can handle the response

    Usage:
        app.add_middleware(ProliferateMiddleware)
    """

    def __init__(
        self,
        app: ASGIApp,
        capture_request_body: bool = False,
    ) -> None:
        """
        Initialize the middleware.

        Args:
            app: The ASGI application
            capture_request_body: Whether to capture request body (not recommended
                                  for privacy/performance reasons)
        """
        super().__init__(app)
        print("ProliferateMiddleware initialized")
        self.capture_request_body = capture_request_body

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Handle the request and capture any exceptions."""
        # Reset context for this request (prevents leaking between requests)
        reset_context()

        # Capture request information
        request_context = self._extract_request_context(request)
        set_request_context(request_context)

        try:
            response: Response = await call_next(request)
            return response
        except Exception as exc:
            # Capture the exception with full context
            _client.capture_exception(exc)
            # Re-raise so FastAPI can handle it (return 500 response)
            raise

    def _extract_request_context(self, request: Request) -> RequestContext:
        """Extract request context from the Starlette request."""
        # Generate or use existing request ID
        request_id = (
            request.headers.get("x-request-id")
            or request.headers.get("x-correlation-id")
            or str(uuid.uuid4())
        )

        # Get client IP (handle proxies)
        client_ip = None
        if request.client:
            client_ip = request.client.host

        # Check for forwarded IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain (original client)
            client_ip = forwarded_for.split(",")[0].strip()

        # Convert headers to dict (lowercase keys for consistency)
        headers = {k.lower(): v for k, v in request.headers.items()}

        # Convert query params to dict
        query_params = dict(request.query_params)

        return RequestContext(
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            headers=headers,
            query_params=query_params,
            client_ip=client_ip,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Alternative setup using FastAPI exception handlers instead of middleware.

    This is useful if you want more control over error responses.

    Usage:
        from fastapi import FastAPI
        from proliferate.integrations.fastapi import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)

    Note: This approach is less comprehensive than the middleware because
    it doesn't capture request context before the handler runs.
    """
    from fastapi.responses import JSONResponse

    @app.exception_handler(Exception)  # type: ignore[misc, untyped-decorator, unused-ignore]
    async def proliferate_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        # Capture to Proliferate
        _client.capture_exception(exc)

        # Return generic error response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
