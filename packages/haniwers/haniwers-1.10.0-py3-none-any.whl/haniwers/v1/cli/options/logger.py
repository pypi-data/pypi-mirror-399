"""Logging options group."""

from typing import Optional

import typer


class LoggerOptions:
    """Logging option group.

    Contains options for configuring application logging behavior.
    """

    verbose = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (DEBUG level logging)",
        rich_help_panel="Logger Options",
    )
    """Verbose logging option.

    When enabled, sets logging to DEBUG level to show detailed diagnostic
    information. Useful for troubleshooting and development.

    Type: bool
    Default: False (INFO level logging)
    """

    logfile = typer.Option(
        None,
        "--logfile",
        help="Write logs to file (in addition to stderr)",
        rich_help_panel="Logger Options",
    )
    """Log file output option.

    When specified, writes log output to the given file path in addition to
    standard error output (stderr). Useful for capturing logs for later analysis
    or archival purposes.

    Type: Optional[str]
    Default: None (logs to stderr only)
    """
