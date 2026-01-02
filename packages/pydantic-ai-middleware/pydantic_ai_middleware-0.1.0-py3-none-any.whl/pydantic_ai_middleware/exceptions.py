"""Exceptions for pydantic-ai-middleware."""

from __future__ import annotations


class MiddlewareError(Exception):
    """Base exception for middleware errors."""


class InputBlocked(MiddlewareError):
    """Raised when input is blocked by middleware."""

    def __init__(self, reason: str = "Input blocked") -> None:
        self.reason = reason
        super().__init__(reason)


class ToolBlocked(MiddlewareError):
    """Raised when a tool call is blocked by middleware."""

    def __init__(self, tool_name: str, reason: str = "Tool blocked") -> None:
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"Tool '{tool_name}' blocked: {reason}")


class OutputBlocked(MiddlewareError):
    """Raised when output is blocked by middleware."""

    def __init__(self, reason: str = "Output blocked") -> None:
        self.reason = reason
        super().__init__(reason)
