"""Configuration management for StrictDoc MCP Server.

This module handles loading configuration from files and environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib  # type: ignore


class Config:
    """Configuration for StrictDoc MCP Server.

    Loads configuration from:
    1. Config file (strictdoc-mcp.toml or ~/.config/strictdoc-mcp/config.toml)
    2. Environment variables (override config file)

    Attributes
    ----------
    log_level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    strictdoc_cli_path : Optional[str]
        Path to strictdoc CLI executable. If None, uses 'strictdoc' from PATH.
    default_output_dir : Optional[str]
        Default output directory for exports.
    """

    def __init__(self) -> None:
        """Initialize configuration with defaults."""
        self.log_level: str = "INFO"
        self.strictdoc_cli_path: Optional[str] = None
        self.default_output_dir: Optional[str] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        config_file = self._find_config_file()
        if config_file:
            self._load_from_file(config_file)
        self._load_from_env()

    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file.

        Searches in:
        1. Current directory: strictdoc-mcp.toml
        2. User config: ~/.config/strictdoc-mcp/config.toml

        Returns
        -------
        Optional[Path]
            Path to config file if found, None otherwise.
        """
        # Check current directory
        current_dir_file = Path("strictdoc-mcp.toml")
        if current_dir_file.exists():
            return current_dir_file

        # Check user config directory
        user_config_dir = Path.home() / ".config" / "strictdoc-mcp"
        user_config_file = user_config_dir / "config.toml"
        if user_config_file.exists():
            return user_config_file

        return None

    def _load_from_file(self, config_file: Path) -> None:
        """Load configuration from TOML file.

        Parameters
        ----------
        config_file : Path
            Path to configuration file.
        """
        try:
            with open(config_file, "rb") as f:
                config_data: Dict[str, Any] = tomllib.load(f)
        except Exception as e:
            # Log error but continue with defaults
            print(f"Warning: Failed to load config file {config_file}: {e}", file=sys.stderr)
            return

        # Load log level
        if "log_level" in config_data:
            self.log_level = str(config_data["log_level"]).upper()

        # Load strictdoc CLI path
        if "strictdoc_cli_path" in config_data:
            self.strictdoc_cli_path = str(config_data["strictdoc_cli_path"])

        # Load default output directory
        if "default_output_dir" in config_data:
            self.default_output_dir = str(config_data["default_output_dir"])

    def _load_from_env(self) -> None:
        """Load configuration from environment variables.

        Environment variables override config file values.
        """
        # STRICTDOC_MCP_LOG_LEVEL
        env_log_level = os.getenv("STRICTDOC_MCP_LOG_LEVEL")
        if env_log_level:
            self.log_level = env_log_level.upper()

        # STRICTDOC_MCP_CLI_PATH
        env_cli_path = os.getenv("STRICTDOC_MCP_CLI_PATH")
        if env_cli_path:
            self.strictdoc_cli_path = env_cli_path

        # STRICTDOC_MCP_DEFAULT_OUTPUT_DIR
        env_output_dir = os.getenv("STRICTDOC_MCP_DEFAULT_OUTPUT_DIR")
        if env_output_dir:
            self.default_output_dir = env_output_dir

    def get_strictdoc_command(self) -> str:
        """Get the strictdoc command to use.

        Returns
        -------
        str
            Command to use for strictdoc CLI.
        """
        if self.strictdoc_cli_path:
            return self.strictdoc_cli_path
        return "strictdoc"


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance.

    Returns
    -------
    Config
        Global configuration instance.
    """
    global _config
    if _config is None:
        _config = Config()
    return _config

