# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Development Commands

### Core Development Tasks

- **Install dependencies**: `make install`
- **Run all checks**: `make all` (format, lint, typecheck, test)
- **Run tests**: `make test`
- **Build docs**: `make docs` or `make docs-serve`

### Single Test Commands

- **Run specific test**: `uv run pytest tests/test_agent.py::test_function_name -v`
- **Run test file**: `uv run pytest tests/test_agent.py -v`
- **Run with debug**: `uv run pytest tests/test_agent.py -v -s`

## Project Architecture

### Core Components

**Base Middleware (`pydantic_ai_middleware/base.py`)**
- `AgentMiddleware[DepsT]` - Abstract base class for all middleware
- Lifecycle hooks: `before_run`, `after_run`, `before_model_request`, `before_tool_call`, `after_tool_call`, `on_error`

**Middleware Agent (`pydantic_ai_middleware/agent.py`)**
- `MiddlewareAgent` - Wraps an agent and applies middleware
- Delegates to wrapped agent while intercepting lifecycle events

**Middleware Toolset (`pydantic_ai_middleware/toolset.py`)**
- `MiddlewareToolset` - Wraps a toolset to intercept tool calls
- Applies `before_tool_call` and `after_tool_call` middleware hooks

**Decorators (`pydantic_ai_middleware/decorators.py`)**
- `@before_run`, `@after_run`, etc. - Create middleware from functions
- `_FunctionMiddleware` - Internal class that wraps functions

**Exceptions (`pydantic_ai_middleware/exceptions.py`)**
- `MiddlewareError` - Base exception
- `InputBlocked` - Block input processing
- `ToolBlocked` - Block tool execution
- `OutputBlocked` - Block output

### Key Design Patterns

**Middleware Chain**
```python
# Middleware executes in order for before_*, reverse for after_*
agent = MiddlewareAgent(
    agent=base_agent,
    middleware=[mw1, mw2, mw3],  # before: 1->2->3, after: 3->2->1
)
```

**Type-Safe Dependencies**
```python
class MyMiddleware(AgentMiddleware[MyDeps]):
    async def before_run(self, prompt, deps: MyDeps | None):
        # deps is properly typed
        ...
```

## Testing Strategy

- **Unit tests**: `tests/` directory
- **Test model**: Use `TestModel` from pydantic-ai for deterministic testing
- **Coverage**: 100% required
- **pytest-asyncio**: Auto mode enabled

## Key Configuration Files

- **`pyproject.toml`**: Project configuration
- **`Makefile`**: Development automation
- **`.pre-commit-config.yaml`**: Pre-commit hooks
- **`mkdocs.yml`**: Documentation configuration

## Coverage

Every pull request MUST have 100% coverage. Check with `make test`.
