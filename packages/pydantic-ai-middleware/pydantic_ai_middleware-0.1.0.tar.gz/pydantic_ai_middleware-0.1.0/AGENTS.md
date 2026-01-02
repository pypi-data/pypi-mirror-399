# AGENTS.md

Instructions for AI coding assistants working on this repository.

## Project Overview

**pydantic-ai-middleware** is a simple middleware library for [pydantic-ai](https://ai.pydantic.dev/) agents. It provides clean before/after hooks at every lifecycle stage without imposing a guardrails structure - you decide what to do (logging, guardrails, metrics, transformations).

## Quick Reference

| Task | Command |
|------|---------|
| Install | `make install` |
| Test | `make test` |
| Test + Coverage | `uv run coverage run -m pytest && uv run coverage report` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Typecheck | `uv run pyright` and `uv run mypy .` |
| All checks | `make all` |
| Build docs | `make docs-serve` |

## Architecture

```
pydantic_ai_middleware/
├── base.py        # AgentMiddleware - base class with lifecycle hooks
├── agent.py       # MiddlewareAgent - wraps agents with middleware
├── toolset.py     # MiddlewareToolset - wraps toolsets for tool call interception
├── decorators.py  # @before_run, @after_run, etc. - function decorators
├── exceptions.py  # InputBlocked, ToolBlocked, OutputBlocked
└── __init__.py    # Public API exports
```

### Key Design: Middleware Chain

Middleware executes in order for `before_*` hooks and reverse order for `after_*` hooks:

```python
agent = MiddlewareAgent(
    agent=base_agent,
    middleware=[mw1, mw2, mw3],
)
# before_run: mw1 -> mw2 -> mw3 -> [Agent]
# after_run:  [Agent] -> mw3 -> mw2 -> mw1
```

### Lifecycle Hooks

| Hook | When Called | Can Modify |
|------|-------------|------------|
| `before_run` | Before agent starts | Prompt |
| `after_run` | After agent finishes | Output |
| `before_model_request` | Before each model call | Messages |
| `before_tool_call` | Before tool execution | Tool arguments |
| `after_tool_call` | After tool execution | Tool result |
| `on_error` | When error occurs | Exception |

## Code Standards

- **Coverage**: 100% required - check with `uv run coverage report`
- **Types**: Pyright and mypy - all functions need type annotations
- **Style**: ruff handles formatting and linting

## Testing

Tests are in `tests/` directory. Use pytest-asyncio for async tests:

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai_middleware import MiddlewareAgent, AgentMiddleware

async def test_middleware():
    model = TestModel()
    model.custom_output_text = "test"
    agent = Agent(model, output_type=str)
    middleware_agent = MiddlewareAgent(agent, middleware=[...])
    result = await middleware_agent.run("test")
```

## When Modifying

1. Run tests after changes: `make test`
2. Check coverage stays at 100%
3. Run `uv run pyright` for type errors
4. Format with `uv run ruff format .`
