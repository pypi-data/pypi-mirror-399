"""Tests for exceptions module."""

from __future__ import annotations

import pytest

from pydantic_ai_middleware import InputBlocked, MiddlewareError, OutputBlocked, ToolBlocked


class TestMiddlewareError:
    """Tests for MiddlewareError."""

    def test_middleware_error_is_exception(self) -> None:
        """Test that MiddlewareError is an Exception."""
        error = MiddlewareError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"


class TestInputBlocked:
    """Tests for InputBlocked exception."""

    def test_input_blocked_default_reason(self) -> None:
        """Test InputBlocked with default reason."""
        error = InputBlocked()
        assert error.reason == "Input blocked"
        assert str(error) == "Input blocked"
        assert isinstance(error, MiddlewareError)

    def test_input_blocked_custom_reason(self) -> None:
        """Test InputBlocked with custom reason."""
        error = InputBlocked("Custom reason")
        assert error.reason == "Custom reason"
        assert str(error) == "Custom reason"


class TestToolBlocked:
    """Tests for ToolBlocked exception."""

    def test_tool_blocked_default_reason(self) -> None:
        """Test ToolBlocked with default reason."""
        error = ToolBlocked("my_tool")
        assert error.tool_name == "my_tool"
        assert error.reason == "Tool blocked"
        assert str(error) == "Tool 'my_tool' blocked: Tool blocked"
        assert isinstance(error, MiddlewareError)

    def test_tool_blocked_custom_reason(self) -> None:
        """Test ToolBlocked with custom reason."""
        error = ToolBlocked("dangerous_tool", "Not authorized")
        assert error.tool_name == "dangerous_tool"
        assert error.reason == "Not authorized"
        assert str(error) == "Tool 'dangerous_tool' blocked: Not authorized"


class TestOutputBlocked:
    """Tests for OutputBlocked exception."""

    def test_output_blocked_default_reason(self) -> None:
        """Test OutputBlocked with default reason."""
        error = OutputBlocked()
        assert error.reason == "Output blocked"
        assert str(error) == "Output blocked"
        assert isinstance(error, MiddlewareError)

    def test_output_blocked_custom_reason(self) -> None:
        """Test OutputBlocked with custom reason."""
        error = OutputBlocked("Contains PII")
        assert error.reason == "Contains PII"
        assert str(error) == "Contains PII"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_inherit_from_middleware_error(self) -> None:
        """Test that all custom exceptions inherit from MiddlewareError."""
        assert issubclass(InputBlocked, MiddlewareError)
        assert issubclass(ToolBlocked, MiddlewareError)
        assert issubclass(OutputBlocked, MiddlewareError)

    def test_can_catch_all_with_middleware_error(self) -> None:
        """Test that all exceptions can be caught with MiddlewareError."""
        with pytest.raises(MiddlewareError):
            raise InputBlocked()

        with pytest.raises(MiddlewareError):
            raise ToolBlocked("tool")

        with pytest.raises(MiddlewareError):
            raise OutputBlocked()
