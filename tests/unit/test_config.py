"""Unit tests for configuration management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from strictdoc_mcp.config import Config, get_config


def test_config_defaults() -> None:
    """Test that config has sensible defaults."""
    with patch("strictdoc_mcp.config.Config._find_config_file", return_value=None):
        config = Config()
        assert config.log_level == "INFO"
        assert config.strictdoc_cli_path is None
        assert config.default_output_dir is None


def test_config_get_strictdoc_command() -> None:
    """Test getting strictdoc command."""
    with patch("strictdoc_mcp.config.Config._find_config_file", return_value=None):
        config = Config()
        assert config.get_strictdoc_command() == "strictdoc"

        config.strictdoc_cli_path = "/usr/local/bin/strictdoc"
        assert config.get_strictdoc_command() == "/usr/local/bin/strictdoc"


def test_config_env_override() -> None:
    """Test environment variable overrides."""
    with patch("strictdoc_mcp.config.Config._find_config_file", return_value=None):
        with patch.dict(
            os.environ,
            {
                "STRICTDOC_MCP_LOG_LEVEL": "DEBUG",
                "STRICTDOC_MCP_CLI_PATH": "/custom/path/strictdoc",
                "STRICTDOC_MCP_DEFAULT_OUTPUT_DIR": "/custom/output",
            },
        ):
            config = Config()
            assert config.log_level == "DEBUG"
            assert config.strictdoc_cli_path == "/custom/path/strictdoc"
            assert config.default_output_dir == "/custom/output"


def test_get_config_singleton() -> None:
    """Test that get_config returns a singleton."""
    with patch("strictdoc_mcp.config.Config._find_config_file", return_value=None):
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

