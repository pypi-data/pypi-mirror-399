"""Configuration file option group."""

from pathlib import Path
from typing import Optional

import typer


class ConfigOptions:
    """Configuration file option group.

    Contains options related to configuration file loading and management.
    """

    config = typer.Option(
        None,
        "--config",
        help="Configuration file path (config.toml, .env.haniwers, etc). "
        "If not specified, ConfigLoader searches default locations.",
    )
    """Configuration file path.

    Allows users to override the default configuration file location. When not
    specified, the application searches standard locations in order:
    1. Current directory (./config.toml)
    2. Project root (haniwers.toml)
    3. User home directory (~/.config/haniwers/)

    Type: Optional[Path]
    Default: None (auto-discovery)
    """
