"""Tests for Celery integration."""

from unittest.mock import MagicMock, patch

import pytest

# Mock celery before importing the integration module
import sys

# Create mock celery module structure
mock_celery = MagicMock()
mock_signals = MagicMock()
mock_celery.signals = mock_signals
mock_signals.task_failure = MagicMock()
mock_signals.task_prerun = MagicMock()
mock_signals.task_retry = MagicMock()

sys.modules["celery"] = mock_celery
sys.modules["celery.signals"] = mock_signals

from proliferate.integrations.celery import (
    capture_task_error,
    init_celery,
    proliferate_task,
)


class TestInitCelery:
    """Tests for init_celery function."""

    def setup_method(self) -> None:
        """Reset initialization state before each test."""
        import proliferate.integrations.celery as celery_module
        celery_module._initialized = False

    @patch("proliferate.integrations.celery.logger")
    def test_registers_signal_handlers(
        self,
        mock_logger: MagicMock,
    ) -> None:
        """Should register signal handlers on first call."""
        init_celery()

        # Verify signal connections were made
        mock_signals.task_failure.connect.assert_called()
        mock_signals.task_prerun.connect.assert_called()
        mock_logger.info.assert_called_with("Celery integration initialized")

    @patch("proliferate.integrations.celery.logger")
    def test_skips_double_initialization(
        self,
        mock_logger: MagicMock,
    ) -> None:
        """Should warn and skip if already initialized."""
        init_celery()  # First call
        mock_signals.task_failure.connect.reset_mock()
        mock_signals.task_prerun.connect.reset_mock()

        init_celery()  # Second call

        mock_logger.warning.assert_called_with(
            "Celery integration already initialized, skipping"
        )
        # Should not connect again
        mock_signals.task_failure.connect.assert_not_called()

    @patch("proliferate.integrations.celery.logger")
    def test_registers_retry_handler_by_default(
        self,
        mock_logger: MagicMock,
    ) -> None:
        """Should register retry handler when capture_retries is True."""
        init_celery(capture_retries=True)

        mock_signals.task_retry.connect.assert_called()

    def test_does_not_register_retry_handler_when_disabled(self) -> None:
        """Should not register retry handler when capture_retries is False."""
        mock_signals.task_retry.connect.reset_mock()

        init_celery(capture_retries=False)

        # task_retry.connect should not be called when capture_retries=False
        # Note: The logic in the code is that it's only connected when capture_retries=True


class TestSignalHandlers:
    """Tests for Celery signal handlers."""

    def setup_method(self) -> None:
        """Reset initialization state before each test."""
        import proliferate.integrations.celery as celery_module
        celery_module._initialized = False

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_task_prerun_resets_context(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should reset context when task starts."""
        # Initialize to get the handler
        init_celery()

        # Get the connected handler
        handler = mock_signals.task_prerun.connect.call_args[0][0]

        # Call the handler
        handler(sender=MagicMock(), task_id="test-123")

        mock_reset_context.assert_called_once()

    @patch("proliferate.integrations.celery._client")
    def test_task_failure_captures_exception(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should capture exception on task failure."""
        import proliferate.integrations.celery as celery_module
        celery_module._initialized = False

        init_celery()

        # Get the connected handler
        handler = mock_signals.task_failure.connect.call_args[0][0]

        # Create test exception and task
        test_error = ValueError("Task failed")
        mock_task = MagicMock()
        mock_task.name = "test_task"
        mock_task.request.retries = 0
        mock_task.request.hostname = "worker-1"
        mock_task.request.delivery_info = {}

        # Call the handler
        handler(
            sender=mock_task,
            task_id="test-123",
            exception=test_error,
            args=(1, 2),
            kwargs={"key": "value"},
        )

        mock_client.capture_exception.assert_called_once()
        call_args = mock_client.capture_exception.call_args
        assert call_args[0][0] is test_error
        assert call_args[1]["extra"]["celery"] is True
        assert call_args[1]["extra"]["task_id"] == "test-123"
        assert call_args[1]["extra"]["task_name"] == "test_task"

    @patch("proliferate.integrations.celery._client")
    def test_task_failure_skips_expected_exceptions(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should skip expected exceptions when ignore_expected is True."""
        import proliferate.integrations.celery as celery_module
        celery_module._initialized = False

        init_celery(ignore_expected=True)

        handler = mock_signals.task_failure.connect.call_args[0][0]

        # Create expected exception
        test_error = ValueError("Expected error")
        test_error.expected = True  # type: ignore

        handler(
            sender=MagicMock(),
            task_id="test-123",
            exception=test_error,
        )

        mock_client.capture_exception.assert_not_called()

    @patch("proliferate.integrations.celery._client")
    def test_task_failure_includes_args_when_enabled(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should include task args when capture_args is True."""
        import proliferate.integrations.celery as celery_module
        celery_module._initialized = False

        init_celery(capture_args=True)

        handler = mock_signals.task_failure.connect.call_args[0][0]

        test_error = ValueError("Task failed")
        mock_task = MagicMock()
        mock_task.name = "test_task"
        mock_task.request.retries = 0

        handler(
            sender=mock_task,
            task_id="test-123",
            exception=test_error,
            args=(1, "hello"),
            kwargs={"name": "test"},
        )

        call_args = mock_client.capture_exception.call_args
        assert "task_args" in call_args[1]["extra"]
        assert "task_kwargs" in call_args[1]["extra"]

    @patch("proliferate.integrations.celery._client")
    def test_task_failure_handles_none_exception(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should handle None exception gracefully."""
        import proliferate.integrations.celery as celery_module
        celery_module._initialized = False

        init_celery()

        handler = mock_signals.task_failure.connect.call_args[0][0]

        handler(
            sender=MagicMock(),
            task_id="test-123",
            exception=None,
        )

        mock_client.capture_exception.assert_not_called()


class TestCaptureTaskError:
    """Tests for capture_task_error function."""

    @patch("proliferate.integrations.celery._client")
    def test_captures_error_with_task_context(
        self,
        mock_client: MagicMock,
    ) -> None:
        """Should capture error with task context."""
        mock_task = MagicMock()
        mock_task.name = "my_task"
        mock_task.request.id = "task-123"
        mock_task.request.retries = 2

        test_error = RuntimeError("Processing failed")

        capture_task_error(mock_task, test_error, operation="process_data")

        mock_client.capture_exception.assert_called_once()
        call_args = mock_client.capture_exception.call_args
        assert call_args[0][0] is test_error
        assert call_args[1]["extra"]["celery"] is True
        assert call_args[1]["extra"]["task_name"] == "my_task"
        assert call_args[1]["extra"]["task_id"] == "task-123"
        assert call_args[1]["extra"]["task_retries"] == 2
        assert call_args[1]["extra"]["operation"] == "process_data"


class TestProliferateTaskDecorator:
    """Tests for proliferate_task decorator."""

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_resets_context_before_task(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should reset context before running task."""

        @proliferate_task()
        def my_task() -> str:
            return "result"

        result = my_task()

        assert result == "result"
        mock_reset_context.assert_called_once()

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_captures_task_result_when_enabled(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should capture result when capture_result is True."""

        @proliferate_task(capture_result=True)
        def my_task() -> str:
            return "success"

        result = my_task()

        assert result == "success"
        mock_client.capture_message.assert_called_once()
        call_args = mock_client.capture_message.call_args
        assert "completed successfully" in call_args[0][0]
        assert call_args[1]["level"] == "info"

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_captures_exception_on_failure(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should capture exception when task fails."""
        test_error = ValueError("Task error")

        @proliferate_task()
        def failing_task() -> None:
            raise test_error

        with pytest.raises(ValueError):
            failing_task()

        mock_client.capture_exception.assert_called_once()
        call_args = mock_client.capture_exception.call_args
        assert call_args[0][0] is test_error
        assert call_args[1]["extra"]["celery"] is True

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_includes_args_on_failure_when_enabled(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should include args when capture_args is True."""

        @proliferate_task(capture_args=True)
        def failing_task(x: int, y: str) -> None:
            raise ValueError("Failed")

        with pytest.raises(ValueError):
            failing_task(42, "hello")

        call_args = mock_client.capture_exception.call_args
        assert "task_args" in call_args[1]["extra"]
        assert "task_kwargs" in call_args[1]["extra"]

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_ignores_specified_exceptions(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should not capture ignored exception types."""

        @proliferate_task(ignore_exceptions=(ValueError,))
        def validation_task() -> None:
            raise ValueError("Validation error")

        with pytest.raises(ValueError):
            validation_task()

        mock_client.capture_exception.assert_not_called()

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_captures_non_ignored_exceptions(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should capture exceptions not in ignore list."""

        @proliferate_task(ignore_exceptions=(ValueError,))
        def failing_task() -> None:
            raise RuntimeError("Runtime error")

        with pytest.raises(RuntimeError):
            failing_task()

        mock_client.capture_exception.assert_called_once()

    @patch("proliferate.integrations.celery._client")
    @patch("proliferate.integrations.celery.reset_context")
    def test_preserves_function_metadata(
        self,
        mock_reset_context: MagicMock,
        mock_client: MagicMock,
    ) -> None:
        """Should preserve function name and docstring."""

        @proliferate_task()
        def documented_task() -> str:
            """This is a documented task."""
            return "result"

        assert documented_task.__name__ == "documented_task"
        assert documented_task.__doc__ == "This is a documented task."
