"""CLI documentation generator for Haniwers v1.

Extracts option metadata from Typer commands and generates comprehensive
Markdown reference documentation.

This script inspects all CLI commands and their options, extracting metadata
(help text, type, default value, rich_help_panel) and generates a structured
Markdown reference suitable for documentation.

Usage:
    Generate CLI reference and save to docs:
    $ poetry run python -m haniwers.v1.cli._doc_generator \\
        > docs/_shared/cli-reference.md

    Or view in terminal:
    $ poetry run python -m haniwers.v1.cli._doc_generator | less

Output:
    Generates Markdown with:
    - Table of contents (TOC) with command links
    - Command sections with descriptions
    - Option tables grouped by rich_help_panel category
    - Type information, defaults, and help text for each option
"""

import inspect
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from haniwers.v1.cli import config, daq, mock, port, preprocess, threshold, version


class OptionMetadata:
    """Metadata extracted from a Typer Option."""

    def __init__(
        self,
        name: str,
        type_: str,
        default: Any,
        help_text: str,
        required: bool,
        panel: Optional[str] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ):
        """Initialize option metadata.

        Args:
            name: Option parameter name
            type_: Type annotation as string
            default: Default value
            help_text: Help documentation
            required: Whether option is required
            panel: rich_help_panel category
            min_val: Minimum value constraint
            max_val: Maximum value constraint
        """
        self.name = name
        self.type = type_
        self.default = default
        self.help = help_text
        self.required = required
        self.panel = panel or "General Options"
        self.min_val = min_val
        self.max_val = max_val

    def cli_flag(self) -> str:
        """Convert parameter name to CLI flag format."""
        return f"--{self.name.replace('_', '-')}"

    def default_str(self) -> str:
        """Format default value for display."""
        if self.default is None:
            return "-"
        if isinstance(self.default, bool):
            return "false" if not self.default else "true"
        if isinstance(self.default, Path):
            return f"`{str(self.default)}`"
        return f"`{self.default}`"

    def type_str(self) -> str:
        """Format type for display."""
        # Clean up type string
        type_str = self.type.replace("typing.", "").replace("pathlib.", "")
        return type_str


class CommandMetadata:
    """Metadata extracted from a Typer command."""

    def __init__(
        self,
        name: str,
        help_text: str,
        options: List[OptionMetadata],
        is_subcommand: bool = False,
    ):
        """Initialize command metadata.

        Args:
            name: Command name
            help_text: Command help text
            options: List of option metadata
            is_subcommand: Whether this is a subcommand
        """
        self.name = name
        self.help = help_text
        self.options = options
        self.is_subcommand = is_subcommand

    def anchor(self) -> str:
        """Generate anchor for markdown links."""
        return self.name.lower().replace(" ", "-")


def extract_option_metadata(
    param: inspect.Parameter,
) -> Optional[OptionMetadata]:
    """Extract metadata from a function parameter with Typer Option.

    Args:
        param: Function parameter to inspect

    Returns:
        OptionMetadata if parameter has Typer Option, None otherwise
    """
    # Check if parameter has a default that is a Typer Option
    if not hasattr(param.default, "__class__"):
        return None

    if param.default.__class__.__name__ != "OptionInfo":
        return None

    option_info = param.default

    # Extract type annotation
    type_annotation = param.annotation
    if type_annotation == inspect.Parameter.empty:
        type_str = "str"
    else:
        type_str = str(type_annotation)

    # Get default value
    default_value = getattr(option_info, "default", None)
    if default_value == ...:
        required = True
        default_value = None
    else:
        required = False

    # Get help text
    help_text = getattr(option_info, "help", "") or ""

    # Get rich_help_panel (category)
    panel = getattr(option_info, "rich_help_panel", None)

    # Get min/max constraints
    min_val = getattr(option_info, "min", None)
    max_val = getattr(option_info, "max", None)

    return OptionMetadata(
        name=param.name,
        type_=type_str,
        default=default_value,
        help_text=help_text,
        required=required,
        panel=panel,
        min_val=min_val,
        max_val=max_val,
    )


def extract_command_metadata(func, command_name: Optional[str] = None) -> CommandMetadata:
    """Extract metadata from a Typer command function.

    Args:
        func: Command function to inspect
        command_name: Override command name (for subcommands)

    Returns:
        CommandMetadata with command information and options
    """
    sig = inspect.signature(func)
    options = []

    for param in sig.parameters.values():
        # Skip special parameters
        if param.name in ("ctx", "context"):
            continue

        opt = extract_option_metadata(param)
        if opt:
            options.append(opt)

    # Get command name
    name = command_name or func.__name__
    name = name.replace("_", " ")

    # Get docstring (first line)
    docstring = inspect.getdoc(func) or ""
    help_text = docstring.split("\n", maxsplit=1)[0] if docstring else ""

    return CommandMetadata(
        name=name,
        help_text=help_text,
        options=options,
    )


def collect_all_commands() -> List[CommandMetadata]:
    """Collect metadata from all CLI commands.

    Returns:
        List of CommandMetadata for all commands
    """
    commands = []

    # Single-command modules
    commands.append(extract_command_metadata(daq.daq, "daq"))
    commands.append(extract_command_metadata(mock.mock, "mock"))
    commands.append(extract_command_metadata(version.version, "version"))

    # Config subcommands
    commands.append(extract_command_metadata(config.show_config, "config show"))
    commands.append(extract_command_metadata(config.init, "config init"))

    # Threshold subcommands
    commands.append(extract_command_metadata(threshold.write, "threshold write"))
    if hasattr(threshold, "serial"):
        commands.append(extract_command_metadata(threshold.serial, "threshold serial"))
    if hasattr(threshold, "parallel"):
        commands.append(extract_command_metadata(threshold.parallel, "threshold parallel"))

    # Port subcommands
    commands.append(extract_command_metadata(port.list, "port list"))
    commands.append(extract_command_metadata(port.test_connectivity, "port test"))
    if hasattr(port, "diagnose"):
        commands.append(extract_command_metadata(port.diagnose, "port diagnose"))

    # Preprocess subcommands
    if hasattr(preprocess, "raw2csv"):
        commands.append(extract_command_metadata(preprocess.raw2csv, "preprocess raw2csv"))
    if hasattr(preprocess, "run2csv"):
        commands.append(extract_command_metadata(preprocess.run2csv, "preprocess run2csv"))

    return commands


def generate_markdown(commands: List[CommandMetadata]) -> str:
    """Generate Markdown documentation from command metadata.

    Args:
        commands: List of CommandMetadata to document

    Returns:
        Markdown string with full CLI reference
    """
    lines = [
        "# CLI Reference",
        "",
        "Complete reference for all Haniwers v1 CLI commands and options.",
        "",
        "This document is automatically generated from CLI command definitions.",
        "See each command's help for more details: `haniwers-v1 <command> --help`",
        "",
    ]

    # Generate table of contents
    lines.extend(
        [
            "## Table of Contents",
            "",
        ]
    )

    for cmd in commands:
        anchor = cmd.anchor()
        lines.append(f"- [{cmd.name}](#{anchor})")

    lines.append("")

    # Generate detailed sections for each command
    for cmd in commands:
        anchor = cmd.anchor()
        lines.extend(
            [
                f"## {cmd.name}",
                "{: #" + anchor + "}",
                "",
                cmd.help or "*(no description available)*",
                "",
            ]
        )

        if not cmd.options:
            lines.append("*(no options)*")
            lines.append("")
            continue

        # Group options by panel
        panels: Dict[str, List[OptionMetadata]] = {}
        for opt in cmd.options:
            panel = opt.panel
            if panel not in panels:
                panels[panel] = []
            panels[panel].append(opt)

        # Generate option tables by panel
        for panel_name in sorted(panels.keys()):
            opts = panels[panel_name]
            lines.extend(
                [
                    f"### {panel_name}",
                    "",
                    "| Option | Type | Default | Description |",
                    "|--------|------|---------|-------------|",
                ]
            )

            for opt in opts:
                req_marker = " (required)" if opt.required else ""
                # Truncate long descriptions
                desc = opt.help.split("\n")[0][:80]
                lines.append(
                    f"| `{opt.cli_flag()}` | {opt.type_str()} | "
                    f"{opt.default_str()} | {desc}{req_marker} |"
                )

            lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point for documentation generation."""
    try:
        # Collect all commands
        commands = collect_all_commands()

        # Generate Markdown
        markdown = generate_markdown(commands)

        # Output to stdout
        print(markdown)

    except Exception as e:
        print(
            f"Error generating CLI documentation: {e}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    main()
