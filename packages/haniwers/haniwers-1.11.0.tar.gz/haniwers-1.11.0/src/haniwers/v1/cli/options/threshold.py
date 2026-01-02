"""Threshold settings option group."""

from pathlib import Path
from typing import Optional

import typer


class ThresholdOptions:
    """Threshold settings option group.

    Contains options for configuring detector thresholds and threshold
    operations.
    """

    thresholds = typer.Option(
        ...,
        "--thresholds",
        "-t",
        help="Threshold configuration: 'channel:threshold;channel:threshold;...'. "
        "Examples: '1:290' (single channel), '1:290;2:320;3:298' (all channels).",
        rich_help_panel="Threshold Settings",
    )
    """Threshold configuration.

    Specifies detector thresholds for one or more channels. Format: semicolon-
    separated channel:value pairs.

    Examples:
    - '1:290' - Set channel 1 to 290
    - '1:290;2:320;3:298' - Set all three channels
    - '2:310' - Set only channel 2

    Valid range: 1-1023 for threshold, channels 1-3.

    Type: str
    Default: Required (no default)
    """

    suppress_threshold = typer.Option(
        1000,
        "--suppress-threshold",
        min=1,
        max=1023,
        help="Suppression threshold for non-target channels during scanning (default: 1000). "
        "When scanning one channel, set other channels to this threshold value to suppress their signals.",
        rich_help_panel="Threshold Settings",
    )
    """Suppression threshold for non-target channels.

    During threshold scanning, sets the detection threshold for non-target channels
    to suppress their signals while measuring a specific channel. OSECHI detector
    threshold values range from 1 (lowest, most sensitive) to 1023 (highest, least sensitive).
    Default is 1000, which effectively suppresses noise on non-target channels.

    Type: int
    Default: 1000
    Minimum: 1
    Maximum: 1023
    """

    max_retry = typer.Option(
        3,
        "--max-retry",
        min=1,
        help="Maximum number of retry attempts on communication failure (default: 3).",
        rich_help_panel="Threshold Settings",
    )
    """Maximum retry attempts option.

    When communication with detector fails, retry this many times before giving up.
    Use higher values for unreliable connections.

    Type: int
    Default: 3 retries
    Minimum: 1 retry
    """

    history = typer.Option(
        "threshold_history.csv",
        "--history",
        help="Audit log file for threshold operations (CSV format with timestamp). "
        "Automatically saved in workspace directory.",
        rich_help_panel="Threshold Settings",
    )
    """Threshold history audit log.

    CSV file that records all threshold setting operations with timestamps.
    Useful for auditing and debugging. Automatically saved in the workspace.

    Type: Path
    Default: 'threshold_history.csv'
    """
