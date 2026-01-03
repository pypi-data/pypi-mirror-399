"""Scan-specific threshold scanning options."""

import typer


class ScanOptions:
    """Scan-specific threshold scanning option group.

    Contains options specific to threshold scanning mode (serial/parallel commands).
    For measurement duration, use SamplerOptions.duration which works for both
    general DAQ and threshold scanning operations.

    These options control the scan parameters and are not used by other commands.
    """

    nsteps = typer.Option(
        10,
        "--nsteps",
        min=1,
        help="Number of steps on each side of center (default: 10).",
        rich_help_panel="Scan Settings",
    )
    """Number of scan steps around center.

    Controls how many threshold steps to measure on each side of the center
    threshold value. Higher values create finer granularity in the scan.
    Example: nsteps=10 means scan from center-10 to center+10.

    Type: int
    Default: 10 steps
    Minimum: 1 step
    """

    step = typer.Option(
        1,
        "--step",
        min=1,
        help="Threshold increment between measurement points (default: 1).",
        rich_help_panel="Scan Settings",
    )
    """Threshold increment between scan points.

    The step size for threshold increments during scanning. Smaller steps provide
    finer resolution but take longer. Typical values: 1-5.

    Type: int
    Default: 1
    Minimum: 1
    """
