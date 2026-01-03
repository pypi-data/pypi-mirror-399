"""Output settings option group."""

from pathlib import Path
from typing import Optional

import typer


class OutputOptions:
    """Output settings option group.

    Contains options for configuring data file output location and naming.
    """

    workspace = typer.Option(
        Path("."),
        "--workspace",
        help="Output directory for data files. Timestamped subdirectory created automatically.",
        rich_help_panel="Output Settings",
    )
    """Output workspace directory.

    Specifies where to save data files. A timestamped subdirectory is created
    automatically within this directory. Example: workspace/2025-10-27_14-35-22/

    Type: Optional[Path]
    Default: None (use config file value)
    """

    filename_prefix = typer.Option(
        None,
        "--filename-prefix",
        help="Prefix for output file names (e.g., 'run001').",
        rich_help_panel="Output Settings",
    )
    """Output filename prefix.

    Prefix added to all output files created during this session. Helps organize
    files by run. Example: --filename-prefix=run001 creates run001_001.csv, etc.

    Type: Optional[str]
    Default: None (use config file value)
    """

    filename_suffix = typer.Option(
        None,
        "--filename-suffix",
        help="File extension/suffix for output files (e.g., '.csv').",
        rich_help_panel="Output Settings",
    )
    """Output filename suffix.

    File extension/suffix for output files. Controls the file format name.

    Type: Optional[str]
    Default: None (use config file value, typically '.csv')
    """
