from __future__ import annotations
from pathlib import Path
from typing import Optional
from haniwers.v1.config.model import HaniwersConfig
from platformdirs import user_config_dir
import sys
import os
from dotenv import load_dotenv

from haniwers.v1.log.logger import logger as base_logger


class ConfigLoader:
    """Loader class to locate and load a valid HaniwersConfig from TOML files."""

    def __init__(self, config_path: Optional[Path] = None):
        # Load environment variables from .env early
        load_dotenv(dotenv_path=".env.haniwers")
        self.logger = base_logger.bind(context=self.__class__.__name__)
        self._config_path = config_path or self.get_default_config_path()
        self._config = self._load_file(self._config_path)
        self._apply_env_overrides()

    @property
    def config(self) -> HaniwersConfig:
        """Returns the loaded and validated configuration object."""
        return self._config

    def _load_file(self, path: Path) -> HaniwersConfig:
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        self.logger.debug(f"Loading config file from: {path}")
        return HaniwersConfig.from_toml(path)

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Search for a config file in standard locations and return the first match.

        Configuration Priority for File Search:
            1. ./hnw.toml (project-specific config)
            2. ./config.toml (generic config)

        Note (P1-5 simplification):
            For simpler configuration management, only two standard locations are searched.
            For custom locations, use --config CLI option to specify explicitly.
            Searching ~/.config/haniwers/ has been removed for complexity reduction.

        Args:
            None

        Returns:
            Path to the first config file found

        Raises:
            FileNotFoundError: If no config file is found in standard locations

        Example:
            ```python
            path = ConfigLoader.get_default_config_path()
            loader = ConfigLoader(path)
            config = loader.config
            ```
        """
        # Simplified search: only 2 standard locations
        candidates = [
            Path("./hnw.toml"),
            Path("./config.toml"),
        ]

        for path in candidates:
            if path.exists():
                base_logger.bind(context=cls.__name__).info(f"Using config file: {path}")
                return path

        base_logger.bind(context=cls.__name__).warning(
            "No config file found in expected locations."
        )
        searched = "\n - ".join(str(p) for p in candidates)
        raise FileNotFoundError(
            f"No config file found in expected locations:\n - {searched}\n"
            "For custom config location, use: haniwers --config /path/to/config.toml\n"
            "Or run 'haniwers init' to create a sample config file."
        )

    def _apply_env_overrides(self) -> None:
        """Override config values from environment variables if set.

        Why this method:
            Supports overriding critical device parameters via environment variables
            for deployment and CI/CD automation scenarios.

        Note:
            This is a temporary legacy method. For P1-5 simplification,
            environment variable overrides should be handled via CLI options instead.
            See CLAUDE.md: "Configuration Priority" for design details.
        """
        # device.port ← HANIWERS_DEVICE_PORT
        port = os.environ.get("HANIWERS_DEVICE_PORT")
        if port is not None:
            self._config.device.port = port

        # device.baudrate ← HANIWERS_DEVICE_BAUDRATE (int)
        baudrate = os.environ.get("HANIWERS_DEVICE_BAUDRATE")
        if baudrate is not None:
            try:
                self._config.device.baudrate = int(baudrate)
            except ValueError:
                self.logger.warning(f"Invalid HANIWERS_DEVICE_BAUDRATE: {baudrate}")

        # device.timeout ← HANIWERS_DEVICE_TIMEOUT (float)
        timeout = os.environ.get("HANIWERS_DEVICE_TIMEOUT")
        if timeout is not None:
            try:
                self._config.device.timeout = float(timeout)
            except ValueError:
                self.logger.warning(f"Invalid HANIWERS_DEVICE_TIMEOUT: {timeout}")

        # sampler.workspace ← HANIWERS_WORKSPACE
        workspace = os.environ.get("HANIWERS_WORKSPACE")
        if workspace is not None and self._config.sampler is not None:
            self._config.sampler.workspace = workspace


def get_default_config_path() -> Path:
    """Convenience function to retrieve the default config path."""
    return ConfigLoader.get_default_config_path()


if __name__ == "__main__":
    """Self test.

    uv run src/haniwers/v1/config/loader.py
    """

    try:
        config_path = Path("hnw.toml")
        loader = ConfigLoader(config_path)
        cfg = loader.config
        print(f"[OK] Loaded config from {config_path}")
        print(cfg.model_dump)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        sys.exit(1)
