"""Version command for Haniwers.

What is this?
    This module provides the version command to display the current Haniwers version.

Why this matters
    You often need to know which version of Haniwers you have installed.
    This is especially important for:
    - Verifying that an update worked correctly
    - Reporting issues with specific version information
    - Checking compatibility with other tools
    - Installing specific versions from package repositories

How it works
    The version command displays the current version of Haniwers
    in a simple, easy-to-read format.

Available commands
    - version: Display the installed Haniwers version
"""

import typer
from haniwers.v1 import __version__
from haniwers.v1.helpers.console import print_info

app = typer.Typer(help="Version information")


@app.command()
def version() -> None:
    """Display the installed Haniwers version.

    What is this?
        This command shows you the version number of Haniwers that's currently installed.

    Why this matters
        Knowing your version helps you:
        - Verify that an update installed correctly
        - Check if you have the latest features and bug fixes
        - Report issues with specific version information
        - Find documentation for your version

    How it works
        The command simply displays the version number in a clear format.

    Typical usage for beginners
    ---------------------------
    To check which version you have:

        >>> haniwers-v1 version
        haniwers 1.8.0

    Or use the global help:

        >>> haniwers-v1 --version
        (also displays version information)
    """
    typer.echo(f"haniwers {__version__}")
