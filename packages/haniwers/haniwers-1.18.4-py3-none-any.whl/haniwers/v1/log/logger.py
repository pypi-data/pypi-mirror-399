"""Logging configuration for Haniwers.

What is this?
    This module helps Haniwers record what it's doing by saving messages to:
    1. Your screen (so you can watch progress)
    2. A log file (so you can review what happened later)

    Think of it like a diary that Haniwers keeps of all its activities.

How does it work?
    The module uses two tools:
    - loguru: A friendly logging library that makes messages easy to read
    - platformdirs: Automatically finds the right place to save logs on your system

Where are logs saved?
    Log files are saved in version-specific subdirectories (v1) depending on your OS:
    - Linux/macOS: ~/.local/state/haniwers/v1/
    - Windows: %APPDATA%/Haniwers/Logs/v1/

    You don't need to worry about these paths - they're chosen automatically!

Beginner note:
    Most of the time, you don't need to directly import from this module.
    The logging is set up automatically when you use the CLI commands.
    If you're writing your own Python scripts, see the configure_logging() function below.
"""

from pathlib import Path

from loguru import logger
from platformdirs import user_log_dir
from rich.logging import RichHandler
from rich.console import Console

# Format string for all handlers
# Includes location information: module name, function name, and line number
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}:{function}:{line}</cyan> | "
    "<level>{message}</level>"
)


def configure_logging(
    verbose: bool = False,
    logfile: str | None = None,
) -> None:
    """Set up where log messages are displayed and saved.

    What is this?
        This function controls what messages you see on your screen and what gets
        saved to files for later review. Call this once when your program starts.

        Most of the time this runs automatically through the CLI (command-line interface),
        but you can also call it directly in your own Python scripts.

    Understanding log levels
        Haniwers creates different types of messages:
        - DEBUG: Very detailed step-by-step information (for troubleshooting)
        - INFO: Normal status updates (program is working normally)
        - WARNING: Something unexpected but not critical
        - ERROR: Something went wrong that needs attention

    Where messages go
        Screen (terminal window):
            - Normal mode (verbose=False): Shows INFO messages and above (cleaner output)
            - Verbose mode (verbose=True): Shows DEBUG messages and above (every detail)

        Log file:
            - Always saves DEBUG level (captures everything for later review)
            - Saved to a file on disk that persists after the program exits

    Parameters
    ----------
    verbose : bool, default=False
        Control how much detail appears on screen.

        - False: Normal mode - shows only important messages (INFO and above)
          Good for everyday use when you just want to see progress.

        - True: Verbose mode - shows all details including DEBUG messages
          Useful when something isn't working and you need to troubleshoot.

    logfile : str or None, default=None
        Where to save the log file on your computer.

        - None: Use the default location (recommended for most users)
          The system automatically picks the right spot (v1 version-specific):
            * Linux/macOS: ~/.local/state/haniwers/v1/haniwers.log
            * Windows: %APPDATA%/Haniwers/Logs/v1/haniwers.log

        - "path/to/file.log": Save to a specific location you choose
          Example: "my_experiment.log" or "/tmp/debug.log"
          The directory will be created automatically if it doesn't exist.

    Examples
    --------
    Typical usage for most users:

        >>> # Most common: Use defaults (normal screen output, auto log location)
        >>> configure_logging()

    When you need more information on screen:

        >>> # Show detailed debug messages while the program runs
        >>> configure_logging(verbose=True)

    When you want logs in a specific place:

        >>> # Save log file in your current folder
        >>> configure_logging(logfile="my_experiment.log")

        >>> # Full custom setup: detailed output + custom log location
        >>> configure_logging(verbose=True, logfile="./logs/detailed_run.log")

    Using in your own Python scripts:

        >>> from haniwers.v1.log.logger import configure_logging, logger
        >>>
        >>> # Set up logging at the start of your script
        >>> configure_logging(verbose=True, logfile="analysis.log")
        >>>
        >>> # Now you can log messages
        >>> logger.info("Starting data analysis")
        >>> logger.debug("Processing file: data.csv")

    Important to know
    -----------------
    Automatic log management:
        Log files can get large over time. Don't worry - Haniwers automatically
        manages this for you:

        - When a log file reaches 1 MB, a new file is started (rotation)
        - Only the last 10 days of logs are kept
        - Older logs are automatically deleted

        This means you never need to manually clean up log files!

    Beginner note:
        The function always saves DEBUG-level messages to files, even in normal
        (non-verbose) mode. This ensures you have detailed records for later
        review, while keeping screen output clean.
    """
    # Remove all existing handlers
    logger.remove()

    # Add Rich-based stderr handler with configurable level
    level = "DEBUG" if verbose else "ERROR"
    logger.add(
        RichHandler(
            console=Console(stderr=True),
            show_time=True,
            show_level=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
        ),
        level=level,
        format="{message}",
    )

    # Add file handler
    if logfile:
        # Use custom logfile
        logfile_path = Path(logfile)
        logfile_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            logfile_path,
            level="DEBUG",
            format=LOG_FORMAT,
            rotation="1 MB",
            retention="10 days",
            enqueue=True,
        )
    else:
        # Use default log directory (OS-specific via platformdirs with v1 version)
        log_dir = Path(user_log_dir("haniwers", version="v1", ensure_exists=True))
        logger.add(
            log_dir / "haniwers.log",
            level="DEBUG",
            format=LOG_FORMAT,
            rotation="1 MB",
            retention="10 days",
            enqueue=True,
        )

    # Bind default context
    logger.bind(context="haniwers")


# Initialize with defaults on module import
configure_logging()
