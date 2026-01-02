"""Environment configuration for expt-logger."""

import os

from expt_logger.exceptions import ConfigurationError

DEFAULT_BASE_URL = "https://expt-platform.vercel.app"


def get_api_key(override: str | None = None) -> str:
    """Get API key from override or environment variable.

    Priority:
    1. Explicit override parameter
    2. EXPT_LOGGER_API_KEY environment variable
    3. Raise ConfigurationError if not found

    Args:
        override: Optional API key to use instead of environment variable

    Returns:
        API key string

    Raises:
        ConfigurationError: If no API key is found
    """
    if override is not None:
        return override

    api_key = os.environ.get("EXPT_LOGGER_API_KEY")
    if api_key is None:
        raise ConfigurationError(
            "API key not found. Set EXPT_LOGGER_API_KEY environment variable "
            "or pass api_key parameter."
        )

    return api_key


def get_base_url(override: str | None = None) -> str:
    """Get base URL from override or environment variable.

    Priority:
    1. Explicit override parameter
    2. EXPT_LOGGER_BASE_URL environment variable
    3. Default production server URL

    Args:
        override: Optional base URL to use instead of environment variable

    Returns:
        Base URL string with trailing slashes removed
    """
    if override is not None:
        return override.rstrip("/")

    base_url = os.environ.get("EXPT_LOGGER_BASE_URL", DEFAULT_BASE_URL)
    return base_url.rstrip("/")
