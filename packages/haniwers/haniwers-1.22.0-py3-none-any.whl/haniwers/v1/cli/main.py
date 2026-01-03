"""Main entry point for haniwers v1 CLI.

This module defines the main Typer app and registers all subcommands.
Handles minimal global options (--config, --verbose, --logfile) that are
shared across all commands.

Architecture:
    - Minimal global callback for environment, configuration, and logging setup
    - Subcommands registered from separate modules (config, daq, threshold, etc.)
    - Context object stores only config_path (minimal for subcommands)
    - Logging configured based on global --verbose and --logfile options
    - Device and output settings are command-level options (not global)

Design philosophy:
    Each command explicitly declares the options it needs, making dependencies clear
    and avoiding hidden global state. Global options are limited to cross-cutting
    concerns: logging and configuration file discovery.
"""

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from typer import Context

from haniwers.v1.cli import config, daq, mock, port, preprocess, threshold, version
from haniwers.v1.log.logger import configure_logging

app = typer.Typer(help="Haniwers v1 - Cosmic ray detection analysis tool")


@app.callback()
def main(
    ctx: Context,
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (TOML format). "
        "If not specified, ConfigLoader searches default locations.",
        rich_help_panel="Global Options",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (DEBUG level logging to stderr)",
        rich_help_panel="Global Options",
    ),
    logfile: Optional[str] = typer.Option(
        None,
        "--logfile",
        help="Write logs to file (in addition to stderr). Example: --logfile logs/run.log",
        rich_help_panel="Global Options",
    ),
) -> None:
    """Configure global settings before running subcommands.

    This callback runs before any subcommand executes. It:
    1. Loads environment variables from .env.haniwers (standard location)
    2. Configures logging based on --verbose and --logfile options
    3. Stores global config path in the Typer context for subcommands

    Global options apply to all commands. Use --help on individual commands
    to see command-specific options (device settings, output settings, etc.).

    Args:
        ctx: Typer context (automatically provided)
        config: Path to configuration TOML file (optional)
        verbose: Enable DEBUG level logging to stderr
        logfile: Optional file path to write logs to

    Examples:
        Basic usage with verbose logging:
            $ haniwers-v1 --verbose daq

        With custom config file:
            $ haniwers-v1 --config custom.toml daq

        With log file output:
            $ haniwers-v1 --logfile logs/run.log daq

        Combining all global options:
            $ haniwers-v1 --verbose --logfile logs/debug.log --config custom.toml daq

        With command-specific device options:
            $ haniwers-v1 daq --port /dev/ttyUSB0 --baudrate 115200

    See also:
        - Use 'haniwers-v1 <command> --help' for command-specific options
        - Device/port settings: specify them with individual commands
        - Output settings: specify them with individual commands
    """
    # Load environment variables from standard location
    load_dotenv(dotenv_path=Path(".env.haniwers"))

    # Configure logging
    configure_logging(verbose=verbose, logfile=logfile)

    # Store minimal global configuration
    ctx.obj = {
        "config_path": config,
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
