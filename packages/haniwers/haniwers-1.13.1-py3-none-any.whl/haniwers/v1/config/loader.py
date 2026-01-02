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
        """Search for a config file in standard locations and return the first match."""
        config_dir = Path(user_config_dir("haniwers"))
        candidates = [
            Path("./hnw.toml"),
            Path("./config.toml"),
            *sorted(Path("./config/").glob("*.toml")),
            config_dir / "hnw.toml",
            config_dir / "config.toml",
            *sorted(config_dir.glob("*.toml")),
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
            "Run 'haniwers init' to create a sample config file."
        )

    def _apply_env_overrides(self) -> None:
        """Override config values from environment variables if set."""
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

        # daq.workspace ← HANIWERS_WORKSPACE
        workspace = os.environ.get("HANIWERS_WORKSPACE")
        if workspace is not None:
            if hasattr(self._config, "daq") and hasattr(self._config.daq, "workspace"):
                self._config.daq.workspace = workspace
            if hasattr(self._config, "scan") and hasattr(self._config.scan, "workspace"):
                self._config.scan.workspace = workspace


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
