"""Tests for Django integration."""

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock the Django context imports before importing the module
mock_context = MagicMock()
mock_context.reset_context = MagicMock()
mock_context.set_request_context = MagicMock()
mock_context.set_user_context = MagicMock()
mock_context.RequestContext = MagicMock()
mock_context.UserContext = MagicMock()

# Patch the context module in proliferate
sys.modules["proliferate.context"] = mock_context

# Now import the test targets (they'll use the mocked context)
from proliferate.integrations.django import (
    ProliferateLoggingHandler,
    ProliferateMiddleware,
    _extract_headers,
    _get_client_ip,
)


class TestGetClientIp:
    """Tests for _get_client_ip function."""

    def test_returns_x_forwarded_for_first_ip(self) -> None:
        """Should return the first IP from X-Forwarded-For."""
        request = MagicMock()
        request.META = {"HTTP_X_FORWARDED_FOR": "1.2.3.4, 5.6.7.8, 9.10.11.12"}

        ip = _get_client_ip(request)

        assert ip == "1.2.3.4"

    def test_returns_single_forwarded_ip(self) -> None:
        """Should return single IP from X-Forwarded-For."""
        request = MagicMock()
        request.META = {"HTTP_X_FORWARDED_FOR": "1.2.3.4"}

        ip = _get_client_ip(request)

        assert ip == "1.2.3.4"

    def test_returns_remote_addr_when_no_forwarded(self) -> None:
        """Should fall back to REMOTE_ADDR."""
        request = MagicMock()
        request.META = {"REMOTE_ADDR": "192.168.1.1"}

        ip = _get_client_ip(request)

        assert ip == "192.168.1.1"

    def test_returns_none_when_no_ip_available(self) -> None:
        """Should return None when no IP is available."""
        request = MagicMock()
        request.META = {}

        ip = _get_client_ip(request)

        assert ip is None


class TestExtractHeaders:
    """Tests for _extract_headers function."""

    def test_extracts_http_headers(self) -> None:
        """Should extract HTTP_ prefixed headers."""
        request = MagicMock()
        request.META = {
            "HTTP_CONTENT_TYPE": "application/json",
            "HTTP_USER_AGENT": "TestAgent/1.0",
            "HTTP_X_CUSTOM_HEADER": "custom-value",
            "SERVER_NAME": "localhost",  # Should be excluded
        }

        headers = _extract_headers(request)

        assert headers == {
            "content-type": "application/json",
            "user-agent": "TestAgent/1.0",
            "x-custom-header": "custom-value",
        }

    def test_excludes_sensitive_headers_by_default(self) -> None:
        """Should exclude Authorization and Cookie headers."""
        request = MagicMock()
        request.META = {
            "HTTP_AUTHORIZATION": "Bearer secret-token",
            "HTTP_COOKIE": "session=abc123",
            "HTTP_CONTENT_TYPE": "application/json",
        }

        headers = _extract_headers(request)

        assert "authorization" not in headers
        assert "cookie" not in headers
        assert headers == {"content-type": "application/json"}

    def test_excludes_custom_headers(self) -> None:
        """Should exclude custom specified headers."""
        request = MagicMock()
        request.META = {
            "HTTP_X_API_KEY": "secret-key",
            "HTTP_CONTENT_TYPE": "application/json",
        }

        headers = _extract_headers(request, exclude=["HTTP_X_API_KEY"])

        assert "x-api-key" not in headers
        assert headers == {"content-type": "application/json"}

    def test_handles_empty_meta(self) -> None:
        """Should handle empty META dict."""
        request = MagicMock()
        request.META = {}

        headers = _extract_headers(request)

        assert headers == {}


class TestProliferateMiddleware:
    """Tests for ProliferateMiddleware."""

    def test_middleware_initialization(self) -> None:
        """Should initialize with get_response callable."""
        get_response = MagicMock()

        middleware = ProliferateMiddleware(get_response)

        assert middleware.get_response == get_response

    def test_resets_context_on_each_request(self) -> None:
        """Should reset context at the start of each request."""
        get_response = MagicMock(return_value=MagicMock())
        middleware = ProliferateMiddleware(get_response)

        # Reset the mocks
        mock_context.reset_context.reset_mock()
        mock_context.set_request_context.reset_mock()

        request = MagicMock()
        request.path = "/api/test"
        request.method = "GET"
        request.META = {}
        request.GET = {}
        request.build_absolute_uri.return_value = "http://localhost/api/test"
        request.user = None

        middleware(request)

        mock_context.reset_context.assert_called_once()
        mock_context.set_request_context.assert_called_once()

    def test_excludes_configured_paths(self) -> None:
        """Should skip processing for excluded paths."""
        get_response = MagicMock(return_value=MagicMock())
        middleware = ProliferateMiddleware(get_response)
        middleware._config = {"exclude_paths": ["/health/", "/metrics/"]}

        request = MagicMock()
        request.path = "/health/ready"

        with patch("proliferate.integrations.django.reset_context") as mock_reset:
            middleware(request)

            mock_reset.assert_not_called()

    @patch("proliferate.integrations.django._client")
    @patch("proliferate.integrations.django.reset_context")
    @patch("proliferate.integrations.django.set_request_context")
    def test_captures_exception_on_error(
        self,
        mock_set_request_context: MagicMock,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should capture exception when view raises."""
        test_error = ValueError("Test error")
        get_response = MagicMock(side_effect=test_error)
        middleware = ProliferateMiddleware(get_response)

        request = MagicMock()
        request.path = "/api/test"
        request.method = "GET"
        request.META = {}
        request.GET = {}
        request.build_absolute_uri.return_value = "http://localhost/api/test"
        request.user = None

        with pytest.raises(ValueError):
            middleware(request)

        mock_client.capture_exception.assert_called_once_with(test_error)

    @patch("proliferate.integrations.django._client")
    def test_process_exception_captures_error(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should capture exception in process_exception hook."""
        get_response = MagicMock()
        middleware = ProliferateMiddleware(get_response)

        request = MagicMock()
        test_error = RuntimeError("View error")

        result = middleware.process_exception(request, test_error)

        assert result is None  # Should return None to let Django continue
        mock_client.capture_exception.assert_called_once_with(test_error)

    def test_captures_user_context_when_authenticated(self) -> None:
        """Should capture user context when user is authenticated."""
        # Reset the mocks
        mock_context.reset_context.reset_mock()
        mock_context.set_user_context.reset_mock()
        mock_context.UserContext.reset_mock()

        get_response = MagicMock(return_value=MagicMock())
        middleware = ProliferateMiddleware(get_response)
        middleware._config = {"capture_user": True}

        request = MagicMock()
        request.path = "/api/test"
        request.method = "GET"
        request.META = {}
        request.GET = {}
        request.build_absolute_uri.return_value = "http://localhost/api/test"

        # Mock authenticated user
        user = MagicMock()
        user.is_authenticated = True
        user.id = 123
        user.email = "test@example.com"
        user.username = "testuser"
        request.user = user

        middleware(request)

        # Verify UserContext was created with the right values
        mock_context.UserContext.assert_called_once_with(
            id="123",
            email="test@example.com",
            username="testuser",
        )
        # Verify set_user_context was called
        mock_context.set_user_context.assert_called_once()

    def test_skips_user_context_for_anonymous_user(self) -> None:
        """Should not capture user context for anonymous users."""
        # Reset the mocks
        mock_context.set_user_context.reset_mock()

        get_response = MagicMock(return_value=MagicMock())
        middleware = ProliferateMiddleware(get_response)
        middleware._config = {"capture_user": True}

        request = MagicMock()
        request.path = "/api/test"
        request.method = "GET"
        request.META = {}
        request.GET = {}
        request.build_absolute_uri.return_value = "http://localhost/api/test"

        # Mock anonymous user
        user = MagicMock()
        user.is_authenticated = False
        request.user = user

        middleware(request)

        mock_context.set_user_context.assert_not_called()


class TestProliferateLoggingHandler:
    """Tests for ProliferateLoggingHandler."""

    @patch("proliferate.integrations.django._client")
    def test_captures_exception_from_log_record(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should capture exception when exc_info is present."""
        handler = ProliferateLoggingHandler()

        test_error = ValueError("Log error")
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred: %s",
            args=("details",),
            exc_info=(ValueError, test_error, None),
        )

        handler.emit(record)

        mock_client.capture_exception.assert_called_once()
        call_args = mock_client.capture_exception.call_args
        assert call_args[0][0] is test_error
        assert call_args[1]["extra"]["logger"] == "test.logger"
        assert call_args[1]["extra"]["level"] == "ERROR"

    @patch("proliferate.integrations.django._client")
    def test_captures_message_when_no_exception(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should capture as message when no exception info."""
        handler = ProliferateLoggingHandler()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error message without exception",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        mock_client.capture_message.assert_called_once()
        call_args = mock_client.capture_message.call_args
        assert call_args[0][0] == "Error message without exception"
        assert call_args[1]["level"] == "error"

    @patch("proliferate.integrations.django._client")
    def test_captures_warning_level_correctly(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should set level to warning for warning-level logs."""
        handler = ProliferateLoggingHandler()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=42,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        mock_client.capture_message.assert_called_once()
        call_args = mock_client.capture_message.call_args
        assert call_args[1]["level"] == "warning"

    @patch("proliferate.integrations.django._client")
    def test_handles_emit_error_gracefully(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should handle errors in emit without raising."""
        mock_client.capture_message.side_effect = Exception("Capture failed")
        handler = ProliferateLoggingHandler()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Should not raise
        handler.emit(record)
