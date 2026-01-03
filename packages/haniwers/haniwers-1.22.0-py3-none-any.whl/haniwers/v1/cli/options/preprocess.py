"""Preprocessing options group."""

import typer


class PreprocessOptions:
    """Preprocessing option group.

    Contains options for raw data preprocessing (raw2csv, raw2tmp, and run2csv commands).
    Used to configure time-based data aggregation and timestamp adjustments.
    """

    interval = typer.Option(
        600,
        "--interval",
        min=1,
        help="Resample interval in seconds (e.g., 600 = 10 minutes, 300 = 5 minutes).",
        rich_help_panel="Processing Options",
    )
    """Data aggregation interval option.

    Groups incoming data into time windows of this size. Reduces volume by computing
    statistics (mean, std, etc.) within each time window. Typical values: 300-1800 seconds.

    Type: int
    Default: 600 seconds (10 minutes)
    Minimum: 1 second
    """

    offset = typer.Option(
        0,
        "--offset",
        help="Time offset in seconds to apply to all timestamps (e.g., 0, -3600 for -1-hour offset).",
        rich_help_panel="Processing Options",
    )
    """Timestamp offset option.

    Adds this many seconds to all timestamps during processing. Useful when
    detector time differs from system time or when adjusting to a different timezone.
    Can be negative to shift backwards in time.

    Type: int
    Default: 0 (no offset)
    """
