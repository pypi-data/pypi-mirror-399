"""Rich-based console messaging for Haniwers v1 CLI.

This module provides colored console output using the Rich library,
replacing typer.echo() calls throughout the codebase with a unified,
color-coded messaging interface.

Color scheme:
    [bold cyan]INFO:[/]      - Informational messages (progress, status)
    [bold green]SUCCESS:[/]  - Success messages (operations completed)
    [bold yellow]WARNING:[/] - Warning messages (partial skip)
    [bold red]ERROR:[/]      - Error messages (critical failures)

Stderr routing:
    error() and warning() messages automatically route to stderr.
    info() and success() messages go to stdout.

Usage example:
    ```python
    from haniwers.v1.helpers.console import print_info, print_error

    try:
        result = perform_operation()
        print_info(f"Operation completed: {result}")
    except Exception as e:
        print_error(f"Operation failed: {e}")
    ```
"""

import sys
from rich.console import Console

# Module-level singleton Console instances
_stdout = Console(file=sys.stdout)  # stdout
_stderr = Console(file=sys.stderr)  # stderr


def print_info(message: str, **kwargs) -> None:
    """Print informational message in cyan to stdout.

    Args:
        message: Message text (without prefix, prefix is auto-added)
        **kwargs: Additional Rich print() arguments (style, highlight, etc.)

    Example:
        ```python
        print_info("接続しました")
        # Output: [bold cyan]INFO:[/] 接続しました
        ```
    """
    _stdout.print(f"[bold cyan]INFO:[/] {message}", **kwargs)


def print_success(message: str, **kwargs) -> None:
    """Print success message in green to stdout.

    Args:
        message: Message text (without prefix)
        **kwargs: Additional Rich print() arguments

    Example:
        ```python
        print_success("完了しました")
        # Output: [bold green]SUCCESS:[/] 完了しました
        ```
    """
    _stdout.print(f"[bold green]SUCCESS:[/] {message}", **kwargs)


def print_warning(message: str, **kwargs) -> None:
    """Print warning message in yellow to stderr.

    Args:
        message: Message text (without prefix)
        **kwargs: Additional Rich print() arguments

    Example:
        ```python
        print_warning("問題があり処理をスキップしました")
        # Output to stderr:
        # [bold yellow]WARNING:[/] 問題があり処理をスキップしました
        ```
    """
    _stderr.print(f"[bold yellow]WARNING:[/] {message}", **kwargs)


def print_error(message: str, **kwargs) -> None:
    """Print error message in red to stderr.

    Args:
        message: Message text (without prefix)
        **kwargs: Additional Rich print() arguments

    Example:
        ```python
        print_error("重大な問題で処理を中止しました")
        # Output to stderr:
        # [bold red]ERROR:[/] 重大な問題で処理を中止しました
        ```
    """
    _stderr.print(f"[bold red]ERROR:[/] {message}", **kwargs)


def get_console() -> Console:
    """Get the module-level Console instance for stdout.

    Returns:
        Console: The singleton Console instance for advanced usage

    Example:
        ```python
        # For advanced usage (tables, panels, progress bars, etc.)
        console = get_console()
        console.print_table(my_table)
        ```

    Note:
        Most use cases should use print_info(), print_success(), etc.
        Only use get_console() when you need Rich features like tables.
    """
    return _stdout
