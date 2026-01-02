"""Main entry point for haniwers v1 CLI.

This module defines the main Typer app and registers all subcommands.
Handles global options like --env, --config, --verbose, and --logfile
that are shared across all commands.

Architecture:
    - Global callback for environment, configuration, and logging setup
    - Subcommands registered from separate modules (config, daq, scan)
    - Context object stores global configuration for subcommands
    - Logging configured based on global --verbose and --logfile options
"""

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from typer import Context

from haniwers.v1.cli import config, daq, mock, port, preprocess, threshold, version
from haniwers.v1.cli.options import DeviceOptions, LoggerOptions, OutputOptions
from haniwers.v1.log.logger import configure_logging

app = typer.Typer(help="Haniwers v1 commands")


@app.callback()
def main(
    ctx: Context,
    env_path: Path = typer.Option(Path(".env.haniwers"), "--env", help="Path to .env file"),
    config_path: Path = typer.Option(None, "--config", "-c", help="Path to config file"),
    verbose: bool = LoggerOptions.verbose,
    logfile: str = LoggerOptions.logfile,
    # Device settings (global for all commands)
    port: Optional[str] = DeviceOptions.port,
    baudrate: Optional[int] = DeviceOptions.baudrate,
    timeout: Optional[float] = DeviceOptions.timeout,
    device_label: Optional[str] = DeviceOptions.device_label,
    # Output settings (global for all commands)
    workspace: Optional[Path] = OutputOptions.workspace,
) -> None:
    """Load environment variables, configure logging, and set global options.

    This callback runs before any subcommand executes. It:
    1. Loads environment variables from the specified .env file
    2. Configures logging based on --verbose and --logfile options
    3. Stores global configuration in the Typer context for subcommands to access

    Args:
        ctx: Typer context (automatically provided)
        env_path: Path to environment file (.env.haniwers by default)
        config_path: Path to configuration TOML file (optional)
        verbose: Enable DEBUG level logging to stderr
        logfile: Optional file path to write logs to
        port: Serial port path (global for all commands)
        baudrate: Serial communication baud rate (global for all commands)
        timeout: Serial read timeout (global for all commands)
        device_label: Device identifier label (global for all commands)
        workspace: Output directory for data files (global for all commands)

    Example:
        $ haniwers-v1 --verbose daq
        $ haniwers-v1 --logfile logs/run.log preprocess run2csv 1
        $ haniwers-v1 --verbose --logfile logs/debug.log --config custom.toml daq
        $ haniwers-v1 --port /dev/ttyUSB0 --workspace ./output daq
        $ haniwers-v1 --port /dev/ttyUSB0 --baudrate 115200 threshold write --thresholds 1:290
    """
    load_dotenv(dotenv_path=env_path)
    configure_logging(verbose=verbose, logfile=logfile)
    ctx.obj = {
        "env_path": env_path,
        "config_path": config_path,
        "port": port,
        "baudrate": baudrate,
        "timeout": timeout,
        "device_label": device_label,
        "workspace": workspace,
    }


# Register config subcommand group (has sub-commands: show, init)
app.add_typer(config.app, name="config")

# Register threshold subcommand group (has sub-commands: write)
app.add_typer(threshold.app, name="threshold")

# Register port subcommand group (has sub-commands: list, test)
app.add_typer(port.app, name="port")

# Register preprocess subcommand group (has sub-commands: raw2csv, raw2tmp)
app.add_typer(preprocess.app, name="preprocess")

# Register single-command modules (daq, mock, version)
app.command()(daq.daq)
app.command()(mock.mock)
app.command()(version.version)
