"""Sampler settings option group."""

from typing import Optional

import typer


class SamplerOptions:
    """Sampler configuration option group.

    Contains all options for configuring data acquisition including acquisition
    mode (count_based/time_based), file management, output behavior, and
    configuration identity. These options correspond directly to SamplerConfig
    attributes for full CLI-to-config symmetry.
    """

    label = typer.Option(
        None,
        "--label",
        help="Sampler configuration identifier/label (e.g., 'main', 'scan_001'). "
        "Used for logging, documentation, and result tracking.",
        rich_help_panel="Sampler Settings",
    )
    """Sampler configuration label.

    Human-readable identifier for this sampler configuration. Useful for organizing
    multiple configurations and tracking results. Examples: 'main', 'scan_001', 'test_run'.

    Corresponds to: SamplerConfig.label

    Type: Optional[str]
    Default: None (use config file value)
    """

    events_per_file = typer.Option(
        None,
        "--events-per-file",
        min=1,
        help="Number of detector events per output file before rollover.",
        rich_help_panel="Sampler Settings",
    )
    """Events per file rollover option.

    Number of events to record before automatically starting a new output file.
    Helps manage file sizes. Set to 10000 to create a new file every 10k events.

    Corresponds to: SamplerConfig.events_per_file

    Type: Optional[int]
    Default: None (use config file value)
    Minimum: 1 event
    """

    number_of_files = typer.Option(
        None,
        "--number-of-files",
        min=1,
        help="Maximum number of files to create in a single DAQ session.",
        rich_help_panel="Sampler Settings",
    )
    """Maximum files in session option.

    Maximum number of output files to create during this session. Helps prevent
    unlimited disk usage. When reached, the oldest files may be overwritten.

    Corresponds to: SamplerConfig.number_of_files

    Type: Optional[int]
    Default: None (use config file value, typically unlimited)
    Minimum: 1 file
    """

    stream_mode = typer.Option(
        True,
        "--stream-mode",
        help="Enable continuous streaming mode (write immediately, no buffering).",
        rich_help_panel="Sampler Settings",
    )
    """Streaming mode option.

    When enabled, data is written immediately to disk without buffering. This is
    slower but ensures no data loss if the program crashes. Disable for better
    performance when data loss is acceptable.

    Corresponds to: SamplerConfig.stream_mode

    Type: bool
    Default: False (buffered mode)
    """

    mode = typer.Option(
        None,
        "--mode",
        help="Data acquisition mode: 'count_based' (fixed number of events) or "
        "'time_based' (fixed duration). If not specified, uses mode from [sampler] "
        "config section (default: count_based).",
        rich_help_panel="Sampler Settings",
    )
    """DAQ mode option.

    Selects acquisition mode:
    - count_based: Collect a fixed number of events then stop
    - time_based: Run for a fixed time period then stop

    Corresponds to: SamplerConfig.mode

    Type: Optional[str]
    Default: None (use config file value, typically 'count_based')
    Valid values: 'count_based', 'time_based'
    """

    duration = typer.Option(
        None,
        "--duration",
        min=0.1,
        help="Data collection duration in seconds for time_based mode or measurement "
        "duration per threshold during scanning. When specified with DAQ/write, "
        "automatically switches to time_based mode. When used with threshold scanning "
        "(serial/parallel), specifies measurement time per threshold step.",
        rich_help_panel="Sampler Settings",
    )
    """Duration option (flexible: acquisition or per-threshold measurement).

    Context-dependent duration:
    - **In DAQ/Write**: Total acquisition time when mode=time_based
    - **In Threshold Scanning**: Measurement duration per threshold step
    - Automatically enables time_based mode when specified with DAQ
    - Overrides duration setting from config file

    Corresponds to: SamplerConfig.duration

    Type: Optional[float]
    Default: None (use config file value, typically time-based defaults to command defaults)
    Minimum: 0.1 seconds
    """
