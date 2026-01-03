"""CLI package for haniwers v1.

Modular command-line interface with separate modules for each command group.

Structure:
    main.py: Entry point with global options and command registration
    config.py: Configuration management commands (show, init)
    daq.py: Data acquisition command
    scan.py: Threshold scanning command

Usage:
    The main app is exported from this package and used by the haniwers-v1
    entry point defined in pyproject.toml.

Example:
    from haniwers.v1.cli import app
    app()  # Launch CLI
"""

from haniwers.v1.cli.main import app

__all__ = ["app"]
