"""Common CLI option definitions for haniwers v1 commands.

This module provides reusable Typer Option definitions organized by functionality.
Instead of duplicating option definitions across multiple command files, this
centralized approach ensures consistency and reduces maintenance burden.

**Purpose**: Implement the DRY (Don't Repeat Yourself) principle by maintaining
a single source of truth for all common CLI options used by daq, threshold, and
scan commands.

**Usage Example**:
    Instead of defining options in each command file, import them:

    .. code-block:: python

        from haniwers.v1.cli.options import DeviceOptions, OutputOptions, SamplerOptions

        def my_command(
            port: Optional[str] = DeviceOptions.port,
            workspace: Optional[Path] = OutputOptions.workspace,
            label: Optional[str] = SamplerOptions.label,
        ) -> None:
            \"\"\"My CLI command using common options.\"\"\"
            pass

**Organization**: Options are grouped by functionality in separate classes
(ConfigOptions, DeviceOptions, OutputOptions, etc.). Each class uses Typer's
rich_help_panel to organize help text visually.

**Benefits**:
- Single source of truth: Change an option once, affects all commands
- Consistency: All commands show identical help text for common options
- Maintainability: No more duplicate option definitions
- Developer experience: IDE autocomplete works correctly with class attributes
- Backward compatible: No CLI interface changes, purely internal refactoring
"""

from pathlib import Path
from typing import Optional

import typer


# ==============================================================================
# Configuration Options
# ==============================================================================


class ConfigOptions:
    """Configuration file option group.

    Contains options related to configuration file loading and management.
    """

    config = typer.Option(
        None,
        "--config",
        help="Configuration file path (config.toml, .env.haniwers, etc). "
        "If not specified, ConfigLoader searches default locations.",
    )
    """Configuration file path.

    Allows users to override the default configuration file location. When not
    specified, the application searches standard locations in order:
    1. Current directory (./config.toml)
    2. Project root (haniwers.toml)
    3. User home directory (~/.config/haniwers/)

    Type: Optional[Path]
    Default: None (auto-discovery)
    """


# ==============================================================================
# Device Settings Options
# ==============================================================================


class DeviceOptions:
    """Device settings option group.

    Contains options for configuring serial port communication with the
    OSECHI cosmic ray detector.
    """

    port = typer.Option(
        None,
        "--port",
        help="Serial port path for OSECHI detector (e.g., /dev/ttyUSB0, COM3). "
        "Use 'haniwers-v1 port list' to find available ports.",
        rich_help_panel="Device Settings",
    )
    """Serial port path.

    Specifies which serial port to communicate with the OSECHI detector. This
    overrides the port specified in the configuration file.

    Examples:
    - /dev/ttyUSB0 (Linux)
    - /dev/cu.usbserial-140 (macOS)
    - COM3 (Windows)

    Tip: Use 'haniwers-v1 port list' to discover available ports.

    Type: Optional[str]
    Default: None (use config file value)
    """

    baudrate = typer.Option(
        115200,
        "--baudrate",
        help="Serial communication baud rate (bits/second). "
        "Standard values: 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200.",
        rich_help_panel="Device Settings",
    )
    """Serial baud rate.

    Sets the communication speed for serial port. Must be one of the standard serial
    port baud rates: 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400,
    57600, or 115200. This overrides the baudrate in the configuration file.

    Type: int
    Default: 115200 (standard modern serial communication speed)
    Allowed values: Standard serial port baud rates only
    """

    timeout = typer.Option(
        None,
        "--timeout",
        min=0.1,
        help="Serial read timeout in seconds (e.g., 1.0, 2.0).",
        rich_help_panel="Device Settings",
    )
    """Serial read timeout.

    Specifies how long to wait for a response from the OSECHI detector before
    timing out. Typical values: 1.0-5.0 seconds.

    Type: Optional[float]
    Default: None (use config file value)
    Minimum: 0.1 seconds
    """

    device_label = typer.Option(
        None,
        "--device-label",
        help="Device identifier label for logging and documentation.",
        rich_help_panel="Device Settings",
    )
    """Device identifier label.

    Human-readable label to identify this detector in logs and documentation.
    Useful when multiple detectors are in use. Example: "detector_001_main_lab".

    Type: Optional[str]
    Default: None (use config file value)
    """


# ==============================================================================
# Output Settings Options
# ==============================================================================


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


# ==============================================================================
# Sampler Settings Options
# ==============================================================================


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


# ==============================================================================
# Threshold Options
# ==============================================================================


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


# ==============================================================================
# Preprocessing Options
# ==============================================================================


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


# ==============================================================================
# Scan Options
# ==============================================================================


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


# ==============================================================================
# Testing Options
# ==============================================================================


class TestingOptions:
    """Testing option group.

    Contains options for testing without physical hardware, including mock data
    acquisition mode and synthetic data generation. Use with OutputOptions for
    filename_prefix and workspace settings. Options correspond to MockerConfig
    in config.model.MockerConfig for full CLI-to-config symmetry.
    """

    mock = typer.Option(
        False,
        "--mock",
        help="Use RandomMocker instead of real device for testing (no hardware required).",
        rich_help_panel="Testing",
    )
    """Mock mode option.

    When enabled, uses a simulated random detector instead of real hardware.
    Useful for testing without the physical OSECHI detector connected.

    Type: bool
    Default: False (use real device)
    """

    label = typer.Option(
        None,
        "--mocker-label",
        help="Label for mock configuration (e.g., 'replay-demo', 'stress-test'). "
        "Used for logging and documentation of mock runs.",
        rich_help_panel="Testing",
    )
    """Mock configuration label.

    Human-readable identifier for this mock/mocker configuration. Useful for
    organizing multiple test scenarios and tracking test results. Examples:
    'replay-demo', 'stress-test', 'validation-run'.

    Corresponds to: MockerConfig.label

    Type: Optional[str]
    Default: None (use config file value)
    """

    load_from = typer.Option(
        None,
        "--load-from",
        help="CSV file to replay (mutually exclusive with --random)",
        rich_help_panel="Testing",
    )
    """CSV file to replay.

    Path to a CSV file containing previously recorded detector data. When
    specified, the mock command replays events from this file instead of
    generating random data. Mutually exclusive with --random.

    Corresponds to: MockerConfig.csv_path

    Type: Optional[Path]
    Default: None (must specify --random or --load-from)
    """

    random = typer.Option(
        False,
        "--random",
        help="Generate random synthetic data (mutually exclusive with --load-from)",
        rich_help_panel="Testing",
    )
    """Random data generation mode.

    When enabled, generates synthetic random detector events instead of
    replaying from a file. Mutually exclusive with --load-from.

    Type: bool
    Default: False (use --load-from to replay file)
    """

    events = typer.Option(
        None,
        "--events",
        help="Number of events to acquire (default: all events in CSV for replay)",
        rich_help_panel="Testing",
    )
    """Event count option.

    Limit the number of events to process. For replay mode, defaults to all
    events in the CSV file. For random mode, generates this many events.

    Type: Optional[int]
    Default: None (all events for replay, or unlimited for generation)
    """

    speed = typer.Option(
        1.0,
        "--speed",
        help="Speed multiplier for replay/generation (0.1 to 100.0, default: 1.0)",
        rich_help_panel="Testing",
    )
    """Replay/generation speed multiplier.

    Scales the speed of event processing. Values > 1.0 speed up playback,
    values < 1.0 slow it down. Useful for testing with different data rates.

    Corresponds to: MockerConfig.speed

    Type: float
    Default: 1.0 (normal speed)
    Valid range: 0.1 to 100.0
    """

    shuffle = typer.Option(
        False,
        "--shuffle",
        help="Shuffle event order (replay mode only)",
        rich_help_panel="Testing",
    )
    """Event order shuffling option.

    When enabled, randomizes the order of events during replay. Useful for
    testing code that should be order-independent. Only applies to replay mode.

    Corresponds to: MockerConfig.shuffle

    Type: bool
    Default: False (preserve original event order)
    """

    jitter = typer.Option(
        0.0,
        "--jitter",
        min=0.0,
        help="Random timing variation in seconds (Gaussian noise std dev, default: 0.0). "
        "Adds realistic timing jitter to mock events.",
        rich_help_panel="Testing",
    )
    """Timing jitter for mock events.

    Amount of random timing variation (in seconds) to add to mock-generated
    events. Uses Gaussian (normal) distribution with this value as standard
    deviation. Useful for simulating realistic detector timing variations.
    Examples: 0.001 for 1ms jitter, 0.01 for 10ms jitter.

    Corresponds to: MockerConfig.jitter

    Type: float
    Default: 0.0 (no jitter)
    Valid range: >= 0.0
    """

    loop = typer.Option(
        True,
        "--loop/--no-loop",
        help="Loop back to start when CSV replay ends (default: --loop). "
        "When disabled (--no-loop), stop after reaching end of file.",
        rich_help_panel="Testing",
    )
    """Loop flag for CSV replay.

    When enabled, replay mode loops back to the beginning of the CSV file when
    reaching the end. When disabled, stops after all events are replayed once.
    This option only applies to CSV replay mode (--load-from), not random
    generation mode.

    Corresponds to: MockerConfig.loop

    Type: bool
    Default: True (loop enabled)
    """

    seed = typer.Option(
        None,
        "--seed",
        help="Random seed for reproducibility (random mode only)",
        rich_help_panel="Testing",
    )
    """Random seed for reproducibility.

    Sets the random seed for deterministic event generation. Use the same seed
    to reproduce identical random event sequences. Only applies to random mode.

    Type: Optional[int]
    Default: None (random seed each run)
    """


# ==============================================================================
# Logging Options
# ==============================================================================


class LoggerOptions:
    """Logging option group.

    Contains options for configuring application logging behavior.
    """

    verbose = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (DEBUG level logging)",
        rich_help_panel="Logger Options",
    )
    """Verbose logging option.

    When enabled, sets logging to DEBUG level to show detailed diagnostic
    information. Useful for troubleshooting and development.

    Type: bool
    Default: False (INFO level logging)
    """

    logfile = typer.Option(
        None,
        "--logfile",
        help="Write logs to file (in addition to stderr)",
        rich_help_panel="Logger Options",
    )
    """Log file output option.

    When specified, writes log output to the given file path in addition to
    standard error output (stderr). Useful for capturing logs for later analysis
    or archival purposes.

    Type: Optional[str]
    Default: None (logs to stderr only)
    """
