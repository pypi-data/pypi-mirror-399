# Lifecycle Hooks

pydantic-ai-middleware provides hooks at various points in the agent execution lifecycle.

## Available Hooks

| Hook | When Called | Can Modify | Can Block |
|------|-------------|------------|-----------|
| `before_run` | Before agent starts | Prompt | Yes (`InputBlocked`) |
| `after_run` | After agent finishes | Output | Yes (`OutputBlocked`) |
| `before_model_request` | Before each model call | Messages | No |
| `before_tool_call` | Before tool execution | Tool arguments | Yes (`ToolBlocked`) |
| `after_tool_call` | After tool execution | Tool result | No |
| `on_error` | When error occurs | Exception | Can convert |

## before_run

Called before the agent starts processing. Can modify the prompt or block execution.

```python
async def before_run(
    self,
    prompt: str | Sequence[Any],
    deps: DepsT | None,
) -> str | Sequence[Any]:
    # Return modified prompt
    return prompt
```

## after_run

Called after the agent finishes. Can modify the output.

```python
async def after_run(
    self,
    prompt: str | Sequence[Any],
    output: Any,
    deps: DepsT | None,
) -> Any:
    # Return modified output
    return output
```

## before_model_request

Called before each request to the model. Can modify messages.

```python
async def before_model_request(
    self,
    messages: list[ModelMessage],
    deps: DepsT | None,
) -> list[ModelMessage]:
    # Return modified messages
    return messages
```

## before_tool_call

Called before a tool is executed. Can modify arguments or block.

```python
async def before_tool_call(
    self,
    tool_name: str,
    tool_args: dict[str, Any],
    deps: DepsT | None,
) -> dict[str, Any]:
    # Return modified arguments
    return tool_args
```

## after_tool_call

Called after a tool is executed. Can modify the result.

```python
async def after_tool_call(
    self,
    tool_name: str,
    tool_args: dict[str, Any],
    result: Any,
    deps: DepsT | None,
) -> Any:
    # Return modified result
    return result
```

## on_error

Called when an error occurs. Can log, transform, or re-raise.

```python
async def on_error(
    self,
    error: Exception,
    deps: DepsT | None,
) -> Exception | None:
    # Return None to re-raise original
    # Return exception to raise different one
    return None
```
