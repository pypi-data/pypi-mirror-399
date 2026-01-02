"""Tests for environment configuration."""

import pytest

from expt_logger.env import DEFAULT_BASE_URL, get_api_key, get_base_url
from expt_logger.exceptions import ConfigurationError


def test_get_api_key_from_override():
    """Test get_api_key with explicit override."""
    api_key = get_api_key(override="test-key-123")
    assert api_key == "test-key-123"


def test_get_api_key_from_env(monkeypatch):
    """Test get_api_key from environment variable."""
    monkeypatch.setenv("EXPT_LOGGER_API_KEY", "env-key-456")
    api_key = get_api_key()
    assert api_key == "env-key-456"


def test_get_api_key_override_takes_precedence(monkeypatch):
    """Test that override takes precedence over environment variable."""
    monkeypatch.setenv("EXPT_LOGGER_API_KEY", "env-key")
    api_key = get_api_key(override="override-key")
    assert api_key == "override-key"


def test_get_api_key_missing_raises_error(monkeypatch):
    """Test that missing API key raises ConfigurationError."""
    monkeypatch.delenv("EXPT_LOGGER_API_KEY", raising=False)
    with pytest.raises(ConfigurationError) as exc_info:
        get_api_key()
    assert "API key not found" in str(exc_info.value)


def test_get_base_url_from_override():
    """Test get_base_url with explicit override."""
    base_url = get_base_url(override="https://custom.example.com")
    assert base_url == "https://custom.example.com"


def test_get_base_url_from_env(monkeypatch):
    """Test get_base_url from environment variable."""
    monkeypatch.setenv("EXPT_LOGGER_BASE_URL", "https://test.example.com")
    base_url = get_base_url()
    assert base_url == "https://test.example.com"


def test_get_base_url_default(monkeypatch):
    """Test get_base_url returns default when not set."""
    monkeypatch.delenv("EXPT_LOGGER_BASE_URL", raising=False)
    base_url = get_base_url()
    assert base_url == DEFAULT_BASE_URL


def test_get_base_url_override_takes_precedence(monkeypatch):
    """Test that override takes precedence over environment variable."""
    monkeypatch.setenv("EXPT_LOGGER_BASE_URL", "https://env.example.com")
    base_url = get_base_url(override="https://override.example.com")
    assert base_url == "https://override.example.com"


def test_get_base_url_strips_trailing_slash():
    """Test that trailing slashes are removed from base URL."""
    base_url = get_base_url(override="https://example.com/")
    assert base_url == "https://example.com"

    base_url = get_base_url(override="https://example.com///")
    assert base_url == "https://example.com"


def test_get_base_url_strips_trailing_slash_from_env(monkeypatch):
    """Test that trailing slashes are removed from environment variable."""
    monkeypatch.setenv("EXPT_LOGGER_BASE_URL", "https://test.example.com/")
    base_url = get_base_url()
    assert base_url == "https://test.example.com"
