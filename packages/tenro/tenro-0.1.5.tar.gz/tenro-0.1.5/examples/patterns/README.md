# Patterns Examples

Tenro API feature demonstrations - learn what Tenro can do.

## Requirements

```bash
# Set API key (required for import, but calls are intercepted by Tenro)
export OPENAI_API_KEY=sk-your-key-or-dummy

# Install dependencies
uv sync --group examples
```

## Run

```bash
uv run pytest examples/patterns/ -v
```

## Examples

| File | Description |
|------|-------------|
| `test_simulating_responses.py` | Control LLM/tool returns with `result=`, `results=[]` |
| `test_simulating_errors.py` | Test error handling with exceptions |
| `test_verifying_calls.py` | Assert call counts with `times=`, `min=`, `max=` |
| `test_verifying_content.py` | Check responses with `output_contains=` |
| `test_verifying_never_called.py` | Ensure operations didn't happen |
| `test_verifying_call_sequence.py` | Verify execution order |
| `test_optional_simulations.py` | Handle conditional branches with `optional=True` |
| `test_dynamic_behavior.py` | Input-dependent responses with `side_effect=` |
