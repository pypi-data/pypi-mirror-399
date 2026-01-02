"""Experiment logger public API."""

import logging
from typing import Any

from expt_logger.config import Config
from expt_logger.exceptions import ValidationError
from expt_logger.run import Run

logger = logging.getLogger(__name__)

_active_run: Run | None = None


def init(
    name: str | None = None,
    config: dict[str, Any] | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Run:
    """Initialize a new experiment run.

    Args:
        name: Optional experiment name
        config: Optional experiment configuration
        api_key: Optional API key (defaults to EXPT_LOGGER_API_KEY env var)
        base_url: Optional base URL (defaults to EXPT_LOGGER_BASE_URL env var)

    Returns:
        Run instance

    Example:
        >>> import expt_logger
        >>> run = expt_logger.init(name="my-experiment", config={"lr": 0.001})
        >>> print(run.experiment_url)
    """
    global _active_run

    if _active_run is not None:
        logger.warning("Run already initialized. Call end() first.")
        return _active_run

    _active_run = Run(name=name, config=config, api_key=api_key, base_url=base_url)
    return _active_run


def log(
    metrics: dict[str, float],
    step: int | None = None,
    mode: str | None = None,
    commit: bool = True,
) -> None:
    """Log scalar metrics.

    Args:
        metrics: Dictionary of metric name -> value
        step: Optional step number (overrides automatic step counter)
        mode: Optional mode (e.g., "train", "eval")
        commit: Whether to flush buffer after logging (default: True)

    Raises:
        RuntimeError: If no active run exists

    Example:
        >>> import expt_logger
        >>> expt_logger.init()
        >>> expt_logger.log({"loss": 0.5, "accuracy": 0.9})
    """
    if _active_run is None:
        raise RuntimeError("No active run. Call init() first.")
    _active_run.log(metrics, step=step, mode=mode, commit=commit)


def log_rollout(
    prompt: str | dict[str, str],
    messages: list[dict[str, str]],
    rewards: dict[str, float],
    step: int | None = None,
    mode: str | None = None,
    commit: bool = True,
) -> None:
    """Log a rollout (conversation + rewards).

    Args:
        prompt: The prompt text (str) or dict with 'content' key
        messages: List of message dicts with 'role' and 'content'
        rewards: Dictionary of reward name -> value
        step: Optional step number (overrides automatic step counter)
        mode: Optional mode (defaults to "train")
        commit: Whether to flush buffer after logging (default: True)

    Raises:
        RuntimeError: If no active run exists
        ValidationError: If input data is invalid

    Example:
        >>> import expt_logger
        >>> expt_logger.init()
        >>> expt_logger.log_rollout(
        ...     prompt="What is 2+2?",
        ...     messages=[{"role": "assistant", "content": "4"}],
        ...     rewards={"correctness": 1.0}
        ... )
        >>> # Or with dict prompt
        >>> expt_logger.log_rollout(
        ...     prompt={"role": "user", "content": "What is 2+2?"},
        ...     messages=[{"role": "assistant", "content": "4"}],
        ...     rewards={"correctness": 1.0}
        ... )
    """
    if _active_run is None:
        raise RuntimeError("No active run. Call init() first.")
    _active_run.log_rollout(
        prompt=prompt,
        messages=messages,
        rewards=rewards,
        step=step,
        mode=mode,
        commit=commit,
    )


def commit() -> None:
    """Commit all pending metrics and rollouts, then increment step.

    Raises:
        RuntimeError: If no active run exists

    Example:
        >>> import expt_logger
        >>> expt_logger.init()
        >>> expt_logger.log({"loss": 0.5}, commit=False)
        >>> expt_logger.log({"accuracy": 0.9}, commit=False)
        >>> expt_logger.commit()  # Flush both metrics at same step
    """
    if _active_run is None:
        raise RuntimeError("No active run. Call init() first.")
    _active_run.commit()


def end() -> None:
    """End the active run and clean up resources.

    This function is idempotent - calling it multiple times is safe.
    It is also called automatically on program exit.

    Example:
        >>> import expt_logger
        >>> expt_logger.init()
        >>> expt_logger.log({"loss": 0.5})
        >>> expt_logger.end()
    """
    global _active_run

    if _active_run is None:
        return

    _active_run.end()
    _active_run = None


def experiment_url() -> str:
    """Get the URL for viewing the current experiment.

    Returns:
        Full URL to experiment page

    Raises:
        RuntimeError: If no active run exists

    Example:
        >>> import expt_logger
        >>> expt_logger.init()
        >>> print(expt_logger.experiment_url())
    """
    if _active_run is None:
        raise RuntimeError("No active run. Call init() first.")
    return _active_run.experiment_url


def base_url() -> str:
    """Get the base URL of the API server.

    Returns:
        Base URL string

    Raises:
        RuntimeError: If no active run exists

    Example:
        >>> import expt_logger
        >>> expt_logger.init()
        >>> print(expt_logger.base_url())
    """
    if _active_run is None:
        raise RuntimeError("No active run. Call init() first.")
    return _active_run.base_url


def config() -> Config:
    """Get the configuration object for the current run.

    Returns:
        Config instance with dict-like and attribute access

    Raises:
        RuntimeError: If no active run exists

    Example:
        >>> import expt_logger
        >>> expt_logger.init(config={"lr": 0.001})
        >>> cfg = expt_logger.config()
        >>> print(cfg.lr)
        >>> cfg.batch_size = 32  # Auto-syncs to server
    """
    if _active_run is None:
        raise RuntimeError("No active run. Call init() first.")
    return _active_run.config


__all__ = [
    "init",
    "log",
    "log_rollout",
    "commit",
    "end",
    "experiment_url",
    "base_url",
    "config",
    "ValidationError",
]
