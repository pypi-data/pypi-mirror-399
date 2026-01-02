# Exceptions

Custom exceptions for middleware control flow.

## MiddlewareError

::: pydantic_ai_middleware.MiddlewareError

Base exception for all middleware errors.

## InputBlocked

::: pydantic_ai_middleware.InputBlocked

Raised to block input processing.

```python
from pydantic_ai_middleware import InputBlocked

raise InputBlocked("Content not allowed")
raise InputBlocked()  # Uses default message
```

## ToolBlocked

::: pydantic_ai_middleware.ToolBlocked

Raised to block a tool call.

```python
from pydantic_ai_middleware import ToolBlocked

raise ToolBlocked("dangerous_tool", "Not authorized")
raise ToolBlocked("tool_name")  # Uses default reason
```

## OutputBlocked

::: pydantic_ai_middleware.OutputBlocked

Raised to block output.

```python
from pydantic_ai_middleware import OutputBlocked

raise OutputBlocked("Contains sensitive information")
raise OutputBlocked()  # Uses default message
```
