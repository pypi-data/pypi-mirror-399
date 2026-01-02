# expt_logger

Simple experiment tracking for RL training with a W&B-style API.

## Quick Start

**Install:**
```bash
uv add expt-logger
# or
pip install expt-logger
```

**Set your API key:**
```bash
export EXPT_LOGGER_API_KEY=your_api_key
```

**Start logging:**
```python
import expt_logger

# Initialize run with config
expt_logger.init(
    name="grpo-math",
    config={"lr": 3e-6, "batch_size": 8}
)

# Get experiment URLs
print(f"View experiment: {expt_logger.experiment_url()}")
print(f"Base URL: {expt_logger.base_url()}")

# Log scalar metrics
expt_logger.log({
    "train/loss": 0.45,
    "train/kl": 0.02,
    "train/reward": 0.85
}, commit=False)
# Not committing means the step count will not increase
# and the logs will be buffered

# Log RL rollouts with rewards
expt_logger.log_rollout(
    prompt="What is 2+2?",
    messages=[{"role": "assistant", "content": "The answer is 4."}],
    rewards={"correctness": 1.0, "format": 0.9},
    mode="train",
    commit=True 
)
# When commit is True (the default),
# this log and all buffered logs will be pushed
# and the step count will be incremented

expt_logger.end()
```

## Core Features

### Scalar Metrics

Log training metrics with automatic step tracking:

```python
# Batch multiple metrics at the same step
expt_logger.log({"loss": 0.5}, commit=False)
expt_logger.log({"accuracy": 0.9}, commit=False)
expt_logger.commit()  # Commit both at step 1, then increment to step 2

# Or commit immediately
expt_logger.log({"loss": 0.4})  # Commit at step 2, increment to 3

# Use slash prefixes for train/eval modes
expt_logger.log({
    "train/loss": 0.5,
    "eval/loss": 0.6
}, step=10)

# Or set mode explicitly
expt_logger.log({"loss": 0.5}, mode="eval")
```

**Note:** Metrics default to `"train"` mode when no mode is specified and keys don't have slash prefixes.

### Rollouts (RL-specific)

Log conversation rollouts with multiple reward functions:

```python
# Batch multiple rollouts at the same step
expt_logger.log_rollout(
    prompt="Solve: x^2 - 5x + 6 = 0",
    messages=[
        {"role": "assistant", "content": "Let me factor this..."},
        {"role": "user", "content": "Can you verify?"},
        {"role": "assistant", "content": "Sure! (x-2)(x-3) = 0..."}
    ],
    rewards={
        "correctness": 1.0,
        "format": 0.9,
        "helpfulness": 0.85
    },
    mode="train",
    commit=False
)

expt_logger.log_rollout(
    prompt="Another problem...",
    messages=[{"role": "assistant", "content": "Solution..."}],
    rewards={"correctness": 0.8},
    mode="train"
)
# Commit both rollouts at the same step

# Or commit immediately
expt_logger.log_rollout(
    prompt="Yet another...",
    messages=[{"role": "assistant", "content": "Answer..."}],
    rewards={"correctness": 1.0},
    step=5,
    mode="train"
)
```

- **Messages format:** List of dicts with `"role"` and `"content"` keys
- **Rewards format:** Dict of reward names to float values
- **Mode:** `"train"` or `"eval"` (default: `"train"`)
- **Commit:** `True` (default) to commit immediately, `False` to batch

### Configuration

Track hyperparameters and update them dynamically:

```python
expt_logger.init(config={"lr": 0.001, "batch_size": 32})

# Update config during training
config = expt_logger.config()
config.lr = 0.0005              # attribute style
config["epochs"] = 100          # dict style
config.update({"model": "gpt2"}) # bulk update
```

### API Key & Server Configuration

**API Key** (required):
```bash
export EXPT_LOGGER_API_KEY=your_api_key
```
Or pass directly:
```python
expt_logger.init(api_key="your_key")
```

**Custom server URL** (optional, for self-hosting):
```bash
export EXPT_LOGGER_BASE_URL=https://your-server.com
```
Or:
```python
expt_logger.init(base_url="https://your-server.com")
```

### Accessing Experiment URLs

Get the experiment URL and base URL:

```python
expt_logger.init(name="my-experiment")

# Get the full experiment URL to view in browser
print(expt_logger.experiment_url())
# https://expt-platform.vercel.app/experiments/ccf1f879-50a6-492b-9072-fed6effac731

# Get the base URL of the tracking server
print(expt_logger.base_url())
# https://expt-platform.vercel.app
```

## API Reference

### `expt_logger.init()`

```python
init(
    name: str | None = None,
    config: dict[str, Any] | None = None,
    api_key: str | None = None,
    base_url: str | None = None
) -> Run
```

- `name`: Experiment name (auto-generated if not provided)
- `config`: Initial hyperparameters
- `api_key`: API key (or set `EXPT_LOGGER_API_KEY`)
- `base_url`: Custom server URL (or set `EXPT_LOGGER_BASE_URL`)

### `expt_logger.log()`

```python
log(
    metrics: dict[str, float],
    step: int | None = None,
    mode: str | None = None,
    commit: bool = True
)
```

- `metrics`: Dict of metric names to values
- `step`: Step number (auto-increments if not provided)
- `mode`: Default mode for keys without slashes (default: `"train"`)
- `commit`: If `True` (default), commit immediately and increment step. If `False`, buffer metrics until commit.

### `expt_logger.log_rollout()`

```python
log_rollout(
    prompt: str,
    messages: list[dict[str, str]],
    rewards: dict[str, float],
    step: int | None = None,
    mode: str = "train",
    commit: bool = True
)
```

- `prompt`: The prompt text
- `messages`: List of `{"role": ..., "content": ...}` dicts
- `rewards`: Dict of reward names to values
- `step`: Step number (uses current step if not provided)
- `mode`: `"train"` or `"eval"`
- `commit`: If `True` (default), commit immediately and increment step. If `False`, buffer metrics until commit.

### `expt_logger.commit()`

```python
commit()
```

Commit all pending metrics and rollouts, then increment the step counter.

### `expt_logger.end()`

```python
end()
```

Finish the run and clean up resources.

### Graceful Shutdown

The library handles cleanup on:
- Normal exit (`atexit`)
- Ctrl+C (`SIGINT`)
- `SIGTERM`

All buffered data is flushed before exit.

## Development

For local development, see [DEVELOPMENT.md](DEVELOPMENT.md).
