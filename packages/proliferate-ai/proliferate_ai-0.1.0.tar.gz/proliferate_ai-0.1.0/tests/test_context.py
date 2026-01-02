"""Tests for context storage."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest

from proliferate.context import (
    AccountContext,
    ProliferateContext,
    RequestContext,
    UserContext,
    clear_context,
    get_account,
    get_context,
    get_full_context,
    get_tag,
    get_tags,
    get_user,
    reset_context,
    set_account,
    set_request_context,
    set_tag,
    set_user,
)


class TestContextVars:
    """Test that contextvars works correctly for async isolation."""

    def setup_method(self) -> None:
        """Clear context before each test."""
        clear_context()

    def test_basic_user_context(self) -> None:
        """Test basic user context get/set."""
        assert get_user() is None

        user: UserContext = {"id": "user_123", "email": "test@example.com"}
        set_user(user)

        assert get_user() == user

    def test_basic_account_context(self) -> None:
        """Test basic account context get/set."""
        assert get_account() is None

        account: AccountContext = {"id": "acct_456", "name": "Acme Corp"}
        set_account(account)

        assert get_account() == account

    def test_tags(self) -> None:
        """Test tag get/set."""
        assert get_tags() == {}

        set_tag("feature", "checkout_v2")
        set_tag("step", "payment")

        assert get_tag("feature") == "checkout_v2"
        assert get_tag("step") == "payment"
        assert get_tags() == {"feature": "checkout_v2", "step": "payment"}

    def test_request_context(self) -> None:
        """Test request context."""
        req = RequestContext(
            request_id="req_123",
            method="POST",
            url="https://api.example.com/checkout",
            path="/checkout",
            headers={"content-type": "application/json"},
            client_ip="192.168.1.1",
        )
        set_request_context(req)

        ctx = get_context()
        assert ctx.request is not None
        assert ctx.request.request_id == "req_123"
        assert ctx.request.method == "POST"

    def test_reset_context(self) -> None:
        """Test context reset clears everything."""
        set_user({"id": "user_123"})
        set_account({"id": "acct_456"})
        set_tag("key", "value")

        assert get_user() is not None

        reset_context()

        assert get_user() is None
        assert get_account() is None
        assert get_tags() == {}

    def test_full_context(self) -> None:
        """Test get_full_context returns all context."""
        set_user({"id": "user_123", "email": "test@example.com"})
        set_account({"id": "acct_456", "name": "Acme Corp"})
        set_tag("feature", "checkout")
        set_request_context(RequestContext(
            request_id="req_123",
            method="POST",
            url="https://api.example.com/checkout",
        ))

        full = get_full_context()

        assert full["user"] == {"id": "user_123", "email": "test@example.com"}
        assert full["account"] == {"id": "acct_456", "name": "Acme Corp"}
        assert full["tags"] == {"feature": "checkout"}
        assert full["request"]["method"] == "POST"

    def test_sensitive_headers_filtered(self) -> None:
        """Test that sensitive headers are filtered out."""
        set_request_context(RequestContext(
            request_id="req_123",
            method="POST",
            url="https://api.example.com/checkout",
            headers={
                "content-type": "application/json",
                "authorization": "Bearer secret_token",
                "cookie": "session=abc123",
                "x-api-key": "pk_secret",
            },
        ))

        full = get_full_context()
        headers = full["request"]["headers"]

        assert "content-type" in headers
        assert "authorization" not in headers
        assert "cookie" not in headers
        assert "x-api-key" not in headers


class TestAsyncIsolation:
    """Test that context is isolated between async tasks."""

    @pytest.mark.asyncio
    async def test_async_tasks_isolated(self) -> None:
        """Test that two async tasks have isolated context."""
        results: dict[str, str | None] = {}

        async def task_a() -> None:
            reset_context()
            set_user({"id": "user_A"})
            await asyncio.sleep(0.01)  # Yield to other task
            user = get_user()
            results["task_a"] = user["id"] if user else None

        async def task_b() -> None:
            reset_context()
            set_user({"id": "user_B"})
            await asyncio.sleep(0.01)  # Yield to other task
            user = get_user()
            results["task_b"] = user["id"] if user else None

        await asyncio.gather(task_a(), task_b())

        # Each task should see its own context
        assert results["task_a"] == "user_A"
        assert results["task_b"] == "user_B"

    @pytest.mark.asyncio
    async def test_many_concurrent_tasks(self) -> None:
        """Test context isolation with many concurrent tasks."""
        results: dict[int, str | None] = {}

        async def task(task_id: int) -> None:
            reset_context()
            set_user({"id": f"user_{task_id}"})
            await asyncio.sleep(0.001)
            user = get_user()
            results[task_id] = user["id"] if user else None

        await asyncio.gather(*[task(i) for i in range(100)])

        # Each task should have its own user
        for i in range(100):
            assert results[i] == f"user_{i}"


class TestThreadIsolation:
    """Test that context works correctly with threads."""

    def test_threads_isolated(self) -> None:
        """Test that threads have isolated context."""
        results: dict[str, str | None] = {}

        def thread_a() -> None:
            reset_context()
            set_user({"id": "user_A"})
            import time
            time.sleep(0.01)
            user = get_user()
            results["thread_a"] = user["id"] if user else None

        def thread_b() -> None:
            reset_context()
            set_user({"id": "user_B"})
            import time
            time.sleep(0.01)
            user = get_user()
            results["thread_b"] = user["id"] if user else None

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(thread_a)
            future_b = executor.submit(thread_b)
            future_a.result()
            future_b.result()

        assert results["thread_a"] == "user_A"
        assert results["thread_b"] == "user_B"
