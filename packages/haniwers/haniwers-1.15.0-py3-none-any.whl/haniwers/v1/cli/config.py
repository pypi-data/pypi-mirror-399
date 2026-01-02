"""Configuration management commands for Haniwers.

What is this?
    This module provides two commands to help you work with configuration files:
    1. `show`: View what's in your configuration file (validates all settings)
    2. `init`: Create template configuration files to get started quickly

Why this matters
    Haniwers needs configuration files (written in TOML format) to know how to:
    - Connect to your OSECHI detector (port, baud rate, timeout)
    - Collect data (how many events per file, output format, etc.)
    - Configure sensors (threshold ranges, channel settings)

    This module makes it easy to:
    - Check if your configuration is valid before running experiments
    - Generate starter templates without typing from scratch
    - Understand what each configuration setting means

How it works
    All configuration files are validated using Pydantic models.
    This means Haniwers checks that:
    - All required fields are present
    - All values are the correct type (numbers, text, paths)
    - All values are within valid ranges

    If something is wrong, you get a helpful error message right away.

Available commands
    - show: Display and validate a configuration file
      Shows the complete configuration in JSON format (easy to read)

    - init: Generate template configuration files
      Creates starter files you can customize for your setup
"""

import typer
from typing import Optional
from pathlib import Path
from haniwers.v1.config.loader import ConfigLoader
from haniwers.v1.config.generator import ConfigGenerator
from haniwers.v1.cli.options import ConfigOptions
from haniwers.v1.helpers.console import print_error

app = typer.Typer(help="Configuration management")


@app.command(name="show")
def show_config(
    ctx: typer.Context,
    config: Optional[Path] = ConfigOptions.config,
) -> None:
    """Display and validate your configuration file.

    What is this?
        This command reads your configuration file (in TOML format) and displays
        all settings in a readable JSON format. At the same time, it validates
        every setting to make sure your configuration is valid.

    Why this matters
        Before you run data acquisition or other commands, you want to know:
        - Is my configuration file valid? (all required fields present?)
        - Do all my settings make sense? (values in valid ranges?)
        - What will Haniwers actually use? (see the complete configuration)

        This command answers all three questions immediately.

    How it works
        - Reads your TOML configuration file
        - Validates every setting through Pydantic models
        - Shows you the complete configuration in JSON format
        - If there's an error, shows a helpful error message

    Parameters
    ----------
    config : Path or None, default=None
        Path to your TOML configuration file.

        Priority order:
        1. Command-level --config (if you provide it): highest priority
        2. Global --config (if you used global option): middle priority
        3. Default "hnw.toml" (if neither provided): fallback

        Examples:
            - haniwers-v1 config show
              (uses default: hnw.toml in current directory)

            - haniwers-v1 config show --config my_config.toml
              (uses my_config.toml)

            - haniwers-v1 --config my_config.toml config show
              (global option, uses my_config.toml)

    Typical usage for beginners
    ---------------------------
    After creating a config file with `haniwers-v1 config init`:

        >>> # Check if your new configuration is valid
        >>> haniwers-v1 config show

    To view a specific configuration file:

        >>> # View settings from a different config file
        >>> haniwers-v1 config show --config examples/daq.toml

    When something goes wrong:

        >>> # If there's an error, you get a message like:
        >>> # [ERROR] Failed to load config: sensors.ch1.id - Field required
        >>> # This tells you exactly what's missing or wrong

    Beginner note:
        JSON format looks like: `{"key": "value", "nested": {"key2": "value2"}}`
        It's just a structured way to display data - same information as TOML,
        just organized differently for easy reading.
    """
    config_path = config or ctx.obj.get("config_path")

    try:
        loader = ConfigLoader(config_path)
        json = loader.config.model_dump_json(indent=2)
        typer.echo(json)
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        raise typer.Exit(code=1)


@app.command()
def init(
    kind: str = typer.Argument("config", help="Kind of file to generate (all, config, env)"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing files without confirmation"
    ),
) -> None:
    """Create template configuration files to get started quickly.

    What is this?
        This command generates starter configuration files with sensible defaults.
        These files are templates - you customize them for your specific setup.

    Why this matters
        Creating configuration files from scratch is tedious and error-prone.
        This command:
        - Generates complete template files with all required fields
        - Includes helpful comments explaining each setting
        - Creates both configuration (.toml) and environment (.env) files
        - Saves you hours of setup time

    How it works
        1. Choose what to generate:
           - config (default): Creates hnw.toml configuration file
           - env: Creates .env.haniwers environment file
           - all: Creates both files together

        2. Decide what to do if file exists:
           - Without --force: Prompts you before overwriting
           - With --force: Overwrites without asking (be careful!)

        3. Customize the generated files for your detector

    Parameters
    ----------
    kind : str, default="config"
        What type of file to generate.

        Options:
        - "config": Generate hnw.toml (main configuration)
          Contains device settings, sensor configuration, DAQ settings

        - "env": Generate .env.haniwers (environment variables)
          Contains paths, API keys, and other environment settings

        - "all": Generate both config and env files
          Recommended for new projects - gives you everything at once

    force : bool, default=False
        Skip confirmation if files already exist.

        - False (default): If file exists, you're asked: "Overwrite? (y/n)"
          Prevents accidentally deleting your configuration
          Good for beginners - safer default

        - True: If file exists, overwrites without asking
          Use only when you're sure you want to replace the file
          Use with caution!

    Typical usage for beginners
    ---------------------------
    Getting started for the first time:

        >>> # Generate starter configuration files
        >>> haniwers-v1 config init all
        Generated: hnw.toml, .env.haniwers
        >>> # Now edit these files for your setup

    If you just need the configuration:

        >>> # Generate only the config file
        >>> haniwers-v1 config init config
        Generated: hnw.toml

    If you messed up and need fresh templates:

        >>> # Overwrite existing files without confirmation
        >>> haniwers-v1 config init all --force
        # Old files replaced with fresh templates

    What to do next
    ---------------
    After running `config init`:

        1. Open the generated files in a text editor
        2. Find the settings that need your input (usually marked with comments)
        3. Update them for your detector and setup
        4. Run `haniwers-v1 config show` to validate your changes
        5. Start using Haniwers with your configuration!

    Beginner note:
        The generated files have comments (lines starting with #) explaining
        what each setting does. Read these comments carefully - they guide you
        through customization. The default values are reasonable starting points
        that you refine for your specific detector and environment.
    """
    try:
        generator = ConfigGenerator(force)
        generator.run(kind=kind.lower())
    except ValueError as e:
        print_error(f"Invalid kind: {e}")
        raise typer.Exit(code=1)
