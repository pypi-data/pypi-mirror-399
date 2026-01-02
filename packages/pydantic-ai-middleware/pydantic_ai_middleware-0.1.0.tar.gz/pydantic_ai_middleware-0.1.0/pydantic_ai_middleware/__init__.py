"""pydantic-ai-middleware - Simple middleware library for Pydantic-AI.

This library provides clean middleware hooks for Pydantic-AI agents,
allowing you to intercept and modify agent behavior at various points
in the execution lifecycle.
"""

from __future__ import annotations

from .agent import MiddlewareAgent
from .base import AgentMiddleware
from .decorators import (
    after_run,
    after_tool_call,
    before_model_request,
    before_run,
    before_tool_call,
    on_error,
)
from .exceptions import InputBlocked, MiddlewareError, OutputBlocked, ToolBlocked
from .toolset import MiddlewareToolset

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "AgentMiddleware",
    "MiddlewareAgent",
    "MiddlewareToolset",
    # Decorators
    "before_run",
    "after_run",
    "before_model_request",
    "before_tool_call",
    "after_tool_call",
    "on_error",
    # Exceptions
    "MiddlewareError",
    "InputBlocked",
    "ToolBlocked",
    "OutputBlocked",
]
