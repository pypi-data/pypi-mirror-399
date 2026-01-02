"""Tests for the Proliferate client."""

import os
from unittest.mock import MagicMock, patch

import pytest

from proliferate.client import (
    ProliferateClient,
    _detect_environment,
    _detect_release,
    _get_exception_type,
)
from proliferate.context import clear_context, set_account, set_tag, set_user


class TestReleaseDetection:
    """Test auto-detection of release version."""

    def test_detect_from_proliferate_release(self) -> None:
        """Test detection from PROLIFERATE_RELEASE env var."""
        with patch.dict(os.environ, {"PROLIFERATE_RELEASE": "v1.2.3"}):
            assert _detect_release() == "v1.2.3"

    def test_detect_from_github_sha(self) -> None:
        """Test detection from GITHUB_SHA env var."""
        with patch.dict(os.environ, {"GITHUB_SHA": "abc123def456"}, clear=True):
            assert _detect_release() == "abc123def456"

    def test_detect_from_release_version(self) -> None:
        """Test detection from RELEASE_VERSION env var (Docker convention)."""
        with patch.dict(os.environ, {"RELEASE_VERSION": "build-123"}, clear=True):
            assert _detect_release() == "build-123"

    def test_priority_order(self) -> None:
        """Test that PROLIFERATE_RELEASE takes priority."""
        with patch.dict(os.environ, {
            "PROLIFERATE_RELEASE": "priority",
            "GITHUB_SHA": "fallback",
        }):
            assert _detect_release() == "priority"


class TestEnvironmentDetection:
    """Test auto-detection of environment."""

    def test_detect_from_environment(self) -> None:
        """Test detection from ENVIRONMENT env var."""
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            assert _detect_environment() == "staging"

    def test_default_to_production(self) -> None:
        """Test default is production."""
        with patch.dict(os.environ, {}, clear=True):
            assert _detect_environment() == "production"


class TestExceptionTypeFormatting:
    """Test exception type name formatting."""

    def test_builtin_exception(self) -> None:
        """Test builtin exceptions don't have module prefix."""
        exc = ValueError("test")
        assert _get_exception_type(exc) == "ValueError"

    def test_custom_exception(self) -> None:
        """Test custom exceptions have full module path."""
        class CustomError(Exception):
            pass

        exc = CustomError("test")
        result = _get_exception_type(exc)
        assert "CustomError" in result
        assert "test_client" in result  # Module name

    def test_nested_exception(self) -> None:
        """Test nested class exceptions."""
        class Outer:
            class InnerError(Exception):
                pass

        exc = Outer.InnerError("test")
        result = _get_exception_type(exc)
        assert "Outer.InnerError" in result


class TestClientInitialization:
    """Test client initialization."""

    def test_init_requires_endpoint(self) -> None:
        """Test that endpoint is required."""
        client = ProliferateClient()
        with pytest.raises(ValueError, match="endpoint is required"):
            client.init(endpoint="", api_key="pk_test")

    def test_init_requires_api_key(self) -> None:
        """Test that api_key is required."""
        client = ProliferateClient()
        with pytest.raises(ValueError, match="api_key is required"):
            client.init(endpoint="https://api.example.com", api_key="")

    def test_init_sets_values(self) -> None:
        """Test that init sets all values correctly."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_test_123",
            environment="testing",
            release="v1.0.0",
        )

        assert client.is_initialized
        assert client.environment == "testing"
        assert client.release == "v1.0.0"

    def test_init_strips_trailing_slash(self) -> None:
        """Test that trailing slash is removed from endpoint."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors/",
            api_key="pk_test",
        )
        assert client._endpoint == "https://api.example.com/api/v1/errors"


class TestExceptionCapture:
    """Test exception capture functionality."""

    def setup_method(self) -> None:
        """Clear context before each test."""
        clear_context()

    @patch("proliferate.client.send_event")
    def test_capture_exception(self, mock_send: MagicMock) -> None:
        """Test basic exception capture."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_test_123",
            environment="testing",
            release="v1.0.0",
        )

        try:
            raise ValueError("Test error message")
        except ValueError as e:
            event_id = client.capture_exception(e)

        assert event_id is not None
        # Called twice: once for init message, once for exception
        assert mock_send.call_count == 2

        # Get the exception call (last call)
        payload = mock_send.call_args_list[-1][0][1]
        assert payload["api_key"] == "pk_test_123"
        assert payload["environment"] == "testing"
        assert payload["release"] == "v1.0.0"
        assert payload["exception"]["type"] == "ValueError"
        assert payload["exception"]["message"] == "Test error message"
        assert "Traceback" in payload["exception"]["stack"]

    @patch("proliferate.client.send_event")
    def test_capture_with_context(self, mock_send: MagicMock) -> None:
        """Test capture includes user/account context."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_test_123",
        )

        # Set context
        set_user({"id": "user_123", "email": "test@example.com"})
        set_account({"id": "acct_456", "name": "Acme Corp"})
        set_tag("feature", "checkout")

        try:
            raise ValueError("Test error")
        except ValueError as e:
            client.capture_exception(e)

        payload = mock_send.call_args[0][1]
        assert payload["user"] == {"id": "user_123", "email": "test@example.com"}
        assert payload["account"] == {"id": "acct_456", "name": "Acme Corp"}
        assert payload["extra"]["tags"] == {"feature": "checkout"}

    @patch("proliferate.client.send_event")
    def test_capture_with_extra(self, mock_send: MagicMock) -> None:
        """Test capture with extra data."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_test_123",
        )

        try:
            raise ValueError("Test error")
        except ValueError as e:
            client.capture_exception(e, extra={"order_id": "123", "amount": 99.99})

        payload = mock_send.call_args[0][1]
        assert payload["extra"]["order_id"] == "123"
        assert payload["extra"]["amount"] == 99.99

    @patch("proliferate.client.send_event")
    def test_disabled_client_doesnt_send(self, mock_send: MagicMock) -> None:
        """Test that disabled client doesn't send events."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_test_123",
            enabled=False,
        )

        try:
            raise ValueError("Test error")
        except ValueError as e:
            event_id = client.capture_exception(e)

        assert event_id is None
        mock_send.assert_not_called()


class TestMessageCapture:
    """Test message capture functionality."""

    def setup_method(self) -> None:
        """Clear context before each test."""
        clear_context()

    @patch("proliferate.client.send_event")
    def test_capture_message(self, mock_send: MagicMock) -> None:
        """Test basic message capture."""
        client = ProliferateClient()
        client.init(
            endpoint="https://api.example.com/api/v1/errors",
            api_key="pk_test_123",
        )

        event_id = client.capture_message("Something happened", level="warning")

        assert event_id is not None
        # Called twice: once for init message, once for captured message
        assert mock_send.call_count == 2

        # Get the captured message call (last call)
        payload = mock_send.call_args_list[-1][0][1]
        assert payload["message"] == "Something happened"
        assert payload["level"] == "warning"
        assert payload["type"] == "message"
