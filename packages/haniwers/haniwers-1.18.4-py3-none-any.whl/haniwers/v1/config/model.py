"""Configuration management for Haniwers data acquisition system.

What is this module?
    Provides data validation and management for all system components using Pydantic models.
    Configuration is loaded from TOML files and automatically validated.

What configurations are available?
    - `DeviceConfig`: Physical OSECHI detector settings (port, baud rate, timeout)
    - `SensorConfig`: Individual sensor settings (threshold, scan range, mode selection)
    - `SamplerConfig`: UNIFIED data acquisition settings (count-based or time-based modes)
    - `MockerConfig`: Simulation/testing settings (CSV replay, speed, timing)
    - `HaniwersConfig`: Top-level container that combines all above configurations

When do validators run?

    Pydantic validators automatically run at THREE key moments:

    1. **Loading from TOML file** (most common):
       ```python
       cfg = HaniwersConfig.from_toml(Path("config.toml"))
       # ✅ All validators run here - catches bad config files immediately
       ```

    2. **Creating config objects directly in Python**:
       ```python
       config = SamplerConfig(
           label="test",
           events_per_file=-100,  # ❌ Validator catches this!
           ...
       )
       # Raises: ValueError: Value must be positive, got -100
       ```

    3. **After substituting CLI arguments**:
       ```python
       cfg = HaniwersConfig.from_toml(Path("config.toml"))
       cfg.sampler.mode = "time_based"  # Changed by CLI flag

       # Re-validate after substitution:
       try:
           SamplerConfig.model_validate(cfg.sampler.model_dump())
       except ValueError as e:
           print(f"Invalid: {e}")
       ```

    Beginner note:
        Think of validators as "gatekeepers" - they check every value before it gets used.
        If something is wrong, they reject it with a helpful error message. This happens
        AUTOMATICALLY whenever Pydantic creates or validates a config object.

    NEW in v1: Use `SamplerConfig` for all data acquisition configurations.
"""

from __future__ import annotations
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Dict
from pathlib import Path
import tomllib
import warnings
from deprecated import deprecated

from haniwers.v1.log.logger import logger as base_logger


class DeviceConfig(BaseModel):
    """Configuration settings for the OSECHI hardware detector.

    What is this?
        Stores serial port connection details for communicating with the physical OSECHI detector.

    Attributes:
        label: Human-readable name for this device (e.g., "YOUR_OSECHI_NAME")
        port: Serial port path (e.g., "/dev/cu.usbserial-140" on macOS, "COM3" on Windows)
               Special value: "auto" for automatic port detection
        baudrate: Communication speed in bits per second (typically 115200)
        timeout: Maximum seconds to wait for a response from the device

    Example (with explicit port):
        ```toml
        [device]
        label = "OSECHI_Main"
        port = "/dev/cu.usbserial-140"
        baudrate = 115200
        timeout = 1.0
        ```

    Example (with auto-detection):
        ```toml
        [device]
        label = "OSECHI_Main"
        port = "auto"
        baudrate = 115200
        timeout = 1.0
        ```
        When port="auto", the device will be auto-detected at runtime.
        Use `haniwers-v1 port list` to find your OSECHI port manually.
    """

    label: str
    port: str
    baudrate: int
    timeout: float

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        """Validate serial port path format.

        Why this matters:
            Serial port paths vary by platform. Common patterns include /dev/ttyUSB0 on Linux,
            /dev/cu.usbserial-* on macOS, COM3 on Windows. Special value "auto" triggers
            automatic detection. Early validation helps catch typos.

        What to test:
            - Accept /dev/ttyUSB0, /dev/cu.*, COM3, etc.
            - Accept special value "auto" for automatic detection
            - Reject empty strings
            - Warn on unusual patterns (just informative, don't block)

        Beginner note:
            Port validation is platform-specific but we can do basic sanity checks.
            Use "auto" to let the system find the OSECHI detector automatically.
        """
        if not v or not isinstance(v, str):
            raise ValueError(f"port must be a non-empty string, got '{v}'")
        return v

    @field_validator("baudrate")
    @classmethod
    def validate_baudrate(cls, v):
        """Validate serial port baud rate.

        Why this matters:
            Only standard baud rates work with serial hardware. Invalid rates cause
            communication failures that are hard to debug.

        What to test:
            - Accept standard rates: 9600, 19200, 38400, 57600, 115200
            - Reject non-standard rates with clear error
            - Reject zero or negative values

        Beginner note:
            Baud rate is the communication speed. OSECHI typically uses 115200.
        """
        standard_rates = {
            300,
            600,
            1200,
            2400,
            4800,
            9600,
            14400,
            19200,
            28800,
            38400,
            57600,
            115200,
        }
        if v not in standard_rates:
            raise ValueError(f"baudrate must be one of {sorted(standard_rates)}, got {v}")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Validate communication timeout value.

        Why this matters:
            Timeout must be positive. Zero or negative values cause hangs or
            immediate failures.

        What to test:
            - Accept positive floats (0.1, 1.0, 5.0, etc.)
            - Reject zero and negative values with clear error
            - Allow reasonable range (0.1 to 30 seconds)

        Beginner note:
            Timeout is how long to wait for a response. 1.0 second is typical.
        """
        if v <= 0:
            raise ValueError(f"timeout must be positive, got {v}")
        if v > 60:
            raise ValueError(f"timeout is unusually large ({v}s). Did you mean {v / 1000}s?")
        return v


class SensorConfig(BaseModel):
    """Configuration for an individual sensor channel (e.g., top, mid, btm).

    What is this?
        Defines threshold scan parameters for one sensor detector channel. Includes the detection
        threshold value and the range of thresholds to scan during experiments.

    Threshold Scan Modes:
        This class supports TWO mutually exclusive modes for defining scan ranges:

        **Center-Based Mode (RECOMMENDED)** - Define range around a center point:
            - center: The middle threshold value (1-1023)
            - nsteps: Number of steps above and below center
            - Full range: center ± (nsteps × step_size)
            - Example: center=512, nsteps=2, step_size=10 → scans [492, 502, 512, 522, 532]

        **Start-Based Mode (DEPRECATED)** - Define range from a starting point:
            - start_threshold: Initial threshold value
            - num_steps: Number of steps to scan forward
            - Full range: start_threshold to start_threshold + (num_steps × step_size)
            - ⚠️ This mode will be removed in v2.0.0. Please use center-based mode instead.

    Attributes:
        id: Numeric channel ID (typically 1, 2, 3 for OSECHI detector with 3 channels)
        name: Unique identifier for the sensor (e.g., "ch1", "ch2", "ch3", "top", "mid", "btm")
        label: Human-readable sensor name (e.g., "top", "middle", "bottom")
        center: Center point for center-based scan mode (1-1023). Used when scanning threshold.
        nsteps: Number of steps from center in center-based mode. 10 means "center " +/- 10 steps.
        step_size: Increment between successive threshold values (in ADC units). 1 is good (and minimum).
        threshold: Current detection threshold ("none" or numeric value) (1-1023). Used when writing threshold.
        start_threshold: Starting point for start-based scan mode (DEPRECATED)
        num_steps: Number of scan steps in start-based mode (DEPRECATED)

    Example (all three sensors):
        ```toml
        [sensors.ch1]
        id = 1
        name = "ch1"
        label = "top"
        center = 512
        nsteps = 10
        step_size = 1
        threshold = "none"

        [sensors.ch2]
        id = 2
        name = "ch2"
        label = "mid"
        center = 311
        nsteps = 10
        step_size = 1
        threshold = "none"

        [sensors.ch3]
        id = 3
        name = "ch3"
        label = "btm"
        center = 420
        nsteps = 10
        step_size = 1
        threshold = "none"
        ```
    """

    id: int
    name: str
    label: str
    step_size: int
    threshold: Optional[int] = None

    # Start-based mode (deprecated)
    start_threshold: Optional[int] = None
    num_steps: Optional[int] = None

    # Center-based mode (recommended)
    center: Optional[int] = None
    nsteps: Optional[int] = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        """Validate that id is a positive integer within OSECHI channel range.

        Why this matters:
            Channel ID should be positive and match physical detector channels.
            OSECHI typically has 3 channels (1, 2, 3). Invalid IDs cause channel confusion.

        What to test:
            - Accept positive integers (1, 2, 3, etc.)
            - Reject zero
            - Reject negative values
            - Allow any positive value (for future extensibility to >3 channels)

        Beginner note:
            Channel ID is how the detector refers to each sensor. OSECHI has 3 channels
            with IDs 1, 2, 3 (top, middle, bottom).
        """
        if v <= 0:
            raise ValueError(f"id must be positive, got {v}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate that name is a non-empty string.

        Why this matters:
            Name should be a unique identifier for the sensor (e.g., "ch1", "ch2", "ch3").
            Empty or invalid names make sensors hard to reference.

        What to test:
            - Accept non-empty strings (e.g., "ch1", "top", "sensor_1")
            - Reject empty strings
            - Allow any string (no strict format enforced)

        Beginner note:
            Name is the key used in the config dictionary. Examples: "ch1", "ch2", "ch3"
            or "top", "mid", "btm". Choose whatever makes sense for your setup.
        """
        if not v or not isinstance(v, str):
            raise ValueError(f"name must be a non-empty string, got '{v}'")
        return v

    @field_validator("step_size")
    @classmethod
    def validate_step_size(cls, v):
        """Validate that step_size is a positive integer.

        Why this matters:
            Step size determines the granularity of threshold scanning. Must be positive
            (at least 1) and an integer. Zero or negative values don't make sense for scanning.

        What to test:
            - Accept positive integers (1, 2, 5, 10, etc.)
            - Reject zero
            - Reject negative values
            - Error message clearly states the requirement

        Beginner note:
            Step size is like "jump size" when scanning thresholds. If step_size=10,
            you check thresholds like 100, 110, 120, 130, etc.
        """
        if v <= 0:
            raise ValueError(f"step_size must be positive, got {v}")
        return v

    @field_validator("center")
    @classmethod
    def validate_center(cls, v):
        """Validate that center (when specified) is in valid detector range.

        Why this matters:
            Center threshold must be within the OSECHI detector range (1-1023) for
            center-based scan mode. Invalid values cause scanning to fail.

        What to test:
            - Accept values in range 1-1023
            - Reject values outside this range with clear error
            - Allow None (not in center-based mode)
            - Error message shows valid range

        Beginner note:
            Center is the middle point of your threshold scan. OSECHI detector supports
            thresholds from 1 to 1023 (8-bit plus 2 bits), so center must fit in this range.
        """
        if v is not None and not (1 <= v <= 1023):
            raise ValueError(f"center must be in range 1-1023, got {v}")
        return v

    @field_validator("nsteps")
    @classmethod
    def validate_nsteps(cls, v):
        """Validate that nsteps (when specified) is a positive integer.

        Why this matters:
            Nsteps defines how many steps above and below center to scan. Must be positive.
            Zero or negative values don't make sense for threshold scanning.

        What to test:
            - Accept positive integers (1, 2, 5, 10, etc.)
            - Reject zero
            - Reject negative values
            - Allow None (not in center-based mode)
            - Error message clearly states the requirement

        Beginner note:
            If center=512 and nsteps=3 with step_size=10, you scan:
            [482, 492, 502, 512, 522, 532, 542] (3 steps below and above center)
        """
        if v is not None and v <= 0:
            raise ValueError(f"nsteps must be positive, got {v}")
        return v

    @field_validator("threshold", mode="before")
    @classmethod
    def convert_none_string(cls, v):
        """Convert the string 'none' (case-insensitive) to None.

        Why this matters:
            TOML files use string "none" to represent no threshold, but Python expects None.
            This validator automatically handles the conversion so users don't need to worry about it.

        What to test:
            - Converts "none" (any case) to None
            - Preserves numeric threshold values unchanged
            - Preserves existing None values

        Beginner note:
            Field validators run before Pydantic's built-in type checking. This allows us to
            normalize user input from TOML format to Python values.
        """
        if isinstance(v, str) and v.lower() == "none":
            return None
        return v

    @model_validator(mode="after")
    def validate_mode_exclusivity(self):
        """Ensure exactly one scan mode is specified and all values are valid.

        Why this matters:
            Users must choose ONLY ONE scan mode (not both, not neither). This prevents ambiguous
            or conflicting configurations that could lead to unexpected behavior.

        What to test:
            - Reject configurations with both modes specified
            - Reject configurations with neither mode specified
            - Accept center-based mode and validate ranges (center 1-1023, nsteps > 0)
            - Accept start-based mode (with deprecation warning)
            - Check that center is within valid range for detector

        Beginner note:
            Model validators run AFTER field validation, so all individual field values have
            already been checked. This validator ensures the combination of fields makes sense.
            It also warns users about deprecated start-based mode to encourage migration.
        """
        start_mode_specified = (self.start_threshold is not None) and (self.num_steps is not None)
        center_mode_specified = (self.center is not None) and (self.nsteps is not None)

        if start_mode_specified and center_mode_specified:
            raise ValueError(
                "Cannot specify both start-based (start_threshold, num_steps) and center-based (center, nsteps) modes"
            )

        if not start_mode_specified and not center_mode_specified:
            raise ValueError(
                "Must specify either start-based mode (start_threshold, num_steps) or center-based mode (center, nsteps)"
            )

        # Deprecation warning for start-based mode
        if start_mode_specified:
            warnings.warn(
                f"SensorConfig '{self.label}' uses deprecated start-based mode (start_threshold={self.start_threshold}, num_steps={self.num_steps}). "
                "This mode will be removed in haniwers v2.0.0. Please migrate to center-based mode (center, nsteps).",
                DeprecationWarning,
                stacklevel=2,
            )

        # Validate center range (1-1023)
        if center_mode_specified:
            if not (1 <= self.center <= 1023):
                raise ValueError(f"center must be in range 1-1023, got {self.center}")
            if self.nsteps <= 0:
                raise ValueError(f"nsteps must be positive, got {self.nsteps}")

        return self

    def threshold_range(self) -> range:
        """Generate the threshold scan range based on configured mode.

        Why this matters:
            Converts configuration parameters into the actual sequence of threshold values
            to scan. This makes it easy for data acquisition code to iterate through the scan.

        What to test:
            - Center-based mode: generates symmetric range around center
            - Start-based mode: generates range starting from start_threshold
            - Returned range is inclusive on both ends
            - Range uses configured step_size

        Returns:
            Python range object with threshold values from min to max (inclusive) with step_size

        Example:
            - Center-based: center=512, nsteps=2, step_size=10 → [492, 502, 512, 522, 532]
            - Start-based: start=400, num_steps=3, step_size=10 → [400, 410, 420, 430]

        Beginner note:
            Python's range(a, b, step) includes a but excludes b. We add step_size to the
            upper limit to make it inclusive, matching user expectations.
        """
        if self.center is not None:
            # Center-based mode
            min_threshold = self.center - self.nsteps * self.step_size
            max_threshold = self.center + self.nsteps * self.step_size
            # Create range from min to max (inclusive) with step_size
            return range(min_threshold, max_threshold + self.step_size, self.step_size)
        else:
            # Start-based mode
            stop = self.start_threshold + self.num_steps * self.step_size
            return range(self.start_threshold, stop, self.step_size)


class SamplerConfig(BaseModel):
    """Unified configuration for data acquisition in both count-based and time-based modes.

    What is this?
        Unified configuration model for all data acquisition strategies. The `mode` parameter
        determines whether data is acquired in count-based mode (fixed number of events) or
        time-based mode (fixed duration). This single configuration replaces separate configurations.

    Why this matters (Beginner note):
        Previously, users had to understand TWO separate config sections ([daq] and [scan]).
        Now there's just ONE section ([sampler]) with a mode parameter that controls behavior:
        - mode="count_based": Acquire fixed number of events (like old [daq])
        - mode="time_based": Acquire for fixed duration (like old [scan])

    Attributes:
        # Sampler (Data Acquisition Mode)
        mode: Data acquisition mode - "count_based" (default) or "time_based"
        duration: How many seconds to collect data (used when mode="time_based")

        # Output (File Management)
        label: Human-readable name for this sampler configuration (e.g., "main")
        workspace: Directory where output files will be saved (created if doesn't exist)
        filename_prefix: Start of output filename (e.g., "osechi_data")
        filename_suffix: End of output filename (e.g., ".csv")
        events_per_file: How many detector events to accumulate before starting a new file
        number_of_files: Maximum number of output files to create before stopping
        stream_mode: True for real-time streaming output, False for buffered output

        # Threshold (Event Filtering and Retry Logic)
        suppress_threshold: Noise floor threshold for event filtering (default: 1000)
        max_retry: Maximum retry attempts if setting threshold fails (default: 3)

    Example (count-based mode - like old [daq]):
        ```toml
        [sampler]
        label = "main"
        workspace = "."
        filename_prefix = "osechi_data"
        filename_suffix = ".csv"
        events_per_file = 10000
        number_of_files = 10000
        stream_mode = true
        mode = "count_based"
        ```

    Example (time-based mode - like old [scan]):
        ```toml
        [sampler]
        label = "scan_main"
        workspace = "."
        filename_prefix = "scan_"
        filename_suffix = ".dat"
        events_per_file = 10000
        number_of_files = 10
        stream_mode = false
        mode = "time_based"
        duration = 60.0
        suppress_threshold = 1000
        max_retry = 3
        ```

    CLI Usage Examples:

        Count-based acquisition (default mode from config):
        ```bash
        # Uses mode from config.toml [sampler] section
        haniwers-v1 daq --config config.toml
        ```

        Time-based acquisition (implicit mode from --duration):
        ```bash
        # Automatically switches to mode="time_based" due to --duration flag
        haniwers-v1 daq --config config.toml --duration 30
        ```

        Explicit mode override (CLI flag wins):
        ```bash
        # Explicit --mode flag takes precedence over everything
        haniwers-v1 daq --config config.toml --mode time_based --duration 60
        ```

    Beginner note:
        - When mode="count_based": `events_per_file` and `number_of_files` control output
        - When mode="time_based": `duration` controls how long to collect, `suppress_threshold`
          filters noise, and `max_retry` handles retry logic
        - The `stream_mode` setting applies to both modes (real-time vs buffered output)
        - CLI flags override config file settings (see examples above)
    """

    # Sampler (Data Acquisition Mode)
    mode: str = "count_based"  # Default to count_based mode
    duration: Optional[float] = None

    # Output (File Management)
    label: str
    workspace: str
    filename_prefix: str
    filename_suffix: str
    events_per_file: int
    number_of_files: int
    stream_mode: bool

    # Threshold (Event Filtering and Retry Logic)
    suppress_threshold: int = 1000
    max_retry: int = 3

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        """Validate that mode is one of the allowed values.

        Why this matters:
            Users should only specify "count_based" or "time_based" mode. Any typo or
            invalid value should be caught immediately with a clear error message.

        What to test:
            - Accept "count_based" and "time_based"
            - Reject invalid mode values with clear error message
            - Case sensitivity is strict (user must specify exact case)

        Beginner note:
            Field validators run during Pydantic validation, catching errors before
            any code tries to use the invalid mode value.
        """
        if v not in ["count_based", "time_based"]:
            raise ValueError(f"mode must be 'count_based' or 'time_based', got '{v}'")
        return v

    @field_validator("events_per_file", "number_of_files", "max_retry")
    @classmethod
    def validate_positive_int(cls, v):
        """Validate that integer fields are positive.

        Why this matters:
            Negative or zero values for event counts, file counts, or retries don't make
            sense. Catch these configuration errors early with clear messages.

        What to test:
            - Accept positive integers
            - Reject zero
            - Reject negative values
            - Error message clearly states the requirement

        Beginner note:
            This validator applies to multiple fields (events_per_file, number_of_files, max_retry)
            using the @field_validator decorator's ability to specify multiple field names.
        """
        if v <= 0:
            raise ValueError(f"Value must be positive, got {v}")
        return v

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v):
        """Validate that duration (when provided) is positive.

        Why this matters:
            Duration only applies to time_based mode. When specified, it must be > 0.
            Allow None (for count_based mode) but validate any actual value.

        What to test:
            - Accept positive floats
            - Accept None (default)
            - Reject zero and negative values with clear error

        Beginner note:
            This validator uses mode="before" behavior (default) to check the value
            before Pydantic's built-in float validation.
        """
        if v is not None and v <= 0:
            raise ValueError(f"duration must be positive when specified, got {v}")
        return v

    @field_validator("suppress_threshold")
    @classmethod
    def validate_threshold(cls, v):
        """Validate that suppress_threshold is in valid detector range.

        Why this matters:
            The OSECHI detector threshold values range from 1-1023. Suppress threshold
            should be within this range for meaningful event filtering.

        What to test:
            - Accept values in range 1-1023
            - Reject values outside this range with clear error
            - Error message shows valid range

        Beginner note:
            This ensures configuration values match hardware capabilities before
            trying to use them during acquisition.
        """
        if not (1 <= v <= 1023):
            raise ValueError(f"suppress_threshold must be in range 1-1023, got {v}")
        return v


class MockerConfig(BaseModel):
    """Configuration settings for the mock device (simulator) used in testing and development.

    What is this?
        The mock device simulates an OSECHI detector without requiring physical hardware.
        Useful for testing analysis code, practicing data acquisition workflows, and CI/CD testing.

    Two Modes:

        **CSV Replay Mode**: Replay recorded detector data from a CSV file
            Set csv_path to a CSV file containing detector events

        **Random Generation Mode**: Generate synthetic detector events on-the-fly
            Leave csv_path as None to generate random events during acquisition

    Attributes:
        label: Human-readable name for this mock configuration (e.g., "replay-demo", "stress-test")
        csv_path: Path to CSV file for replay mode (None = generate random data)
        shuffle: Randomly shuffle event order before playback (only for CSV mode)
        speed: Playback speed multiplier (1.0 = real-time, 2.0 = 2x faster, 0.5 = half speed)
        jitter: Add random timing variation (Gaussian noise, std dev in seconds)
        loop: When reaching end of CSV data, loop back to start (only for CSV mode)

    Loading from TOML:
        MockerConfig is always loaded as part of HaniwersConfig:
        ```python
        cfg = HaniwersConfig.from_toml(Path("config.toml"))
        mocker_cfg = cfg.mocker  # Access MockerConfig
        ```

    Example TOML (CSV Replay):
        ```toml
        [mocker]
        label = "replay-demo"
        csv_path = "data/detector_events.csv"
        shuffle = false
        speed = 1.0
        jitter = 0.01
        loop = true
        ```

    Example TOML (Random Generation):
        ```toml
        [mocker]
        label = "stress-test"
        csv_path = null
        shuffle = false
        speed = 1.0
        jitter = 0.0
        loop = true
        ```

    Beginner note:
        CSV replay is useful for reproducible testing (same data every time).
        Random generation is useful for stress-testing analysis code without worrying about
        specific detector characteristics. The jitter parameter adds realistic timing
        variations that occur with real hardware.
    """

    label: Optional[str] = None
    csv_path: Optional[Path] = None
    shuffle: bool = False
    speed: float = 1.0
    jitter: float = 0.0
    loop: bool = True

    @field_validator("csv_path", mode="before")
    @classmethod
    def validate_path(cls, v):
        """Convert string to Path object if needed.

        Why this matters:
            TOML files represent file paths as strings, but Python's pathlib.Path provides
            better cross-platform handling. This validator normalizes the representation.

        What to test:
            - Converts string paths to Path objects
            - Preserves None values (for random generation mode)
            - Preserves Path objects unchanged

        Beginner note:
            Using pathlib.Path handles path separators correctly on Windows (\\) and Unix (/)
            automatically, making code portable across different operating systems.
        """
        if v is None:
            return None
        if isinstance(v, str):
            return Path(v)
        return v


class HaniwersConfig(BaseModel):
    """Top-level configuration container that combines all Haniwers system settings.

    What is this?
        This is the main configuration object that brings together all the sub-configurations
        (device, DAQ, scanning, sensors, and mock device). It validates that all parts work
        together as a complete system.

    Attributes:
        device: DeviceConfig for OSECHI detector serial connection
                Default port is "auto" for automatic detection
        sampler: SamplerConfig for unified data acquisition
        daq: (DEPRECATED) DaqConfig for data acquisition output settings - Use SamplerConfig instead
        scan: (DEPRECATED) ScanConfig for threshold scanning experiment settings - Use SamplerConfig instead
        sensors: Dictionary mapping sensor names (e.g., "top", "mid", "btm") to SensorConfig objects
        mocker: MockerConfig for testing without hardware

    Typical Usage (Configuration Loading):
        1. Create a TOML configuration file with sections for each component
        2. Load it with: `cfg = HaniwersConfig.from_toml(Path("config.toml"))`
        3. Access sub-configs: `cfg.device`, `cfg.sampler`, `cfg.sensors["top"]`, `cfg.mocker`, etc.

    CLI Usage Pattern (Loading Config + Applying CLI Overrides):

        In your CLI command (e.g., `haniwers-v1 daq`), follow this pattern:

        ```python
        # Step 1: Load config from TOML file
        cfg = HaniwersConfig.from_toml(config_path)

        # Step 2: Apply CLI overrides to config
        if cli_mode:
            # Explicit --mode flag takes precedence
            cfg.sampler.mode = cli_mode
        elif cli_duration:
            # Implicit inference from --duration flag
            # (log warning if this overrides config mode)
            if cfg.sampler.mode != "time_based":
                logger.warning(
                    "CLI --duration overrides config mode",
                    config_mode=cfg.sampler.mode,
                    inferred_mode="time_based"
                )
            cfg.sampler.mode = "time_based"
            if cfg.sampler.duration is None:
                cfg.sampler.duration = cli_duration

        # Step 3: Use the resolved config
        device = create_device(cfg.device)
        sampler = Sampler(device, cfg.sampler)
        sampler.run()
        ```

        This approach:
        - Loads configuration once from TOML
        - Modifies the config object with CLI overrides
        - Passes the final resolved config to downstream code
        - Keeps all mode resolution logic in the config object, not scattered across CLI

    NEW: Unified Configuration ([sampler] section):
        Users should prefer [sampler] section which combines count-based and time-based modes.
        The [daq] and [scan] sections are maintained for backward compatibility.

    Example TOML Structure (NEW - unified [sampler]):
        ```toml
        [device]
        label = "OSECHI_Main"
        port = "/dev/cu.usbserial-140"
        baudrate = 115200
        timeout = 1.0

        [sampler]
        label = "main"
        workspace = "."
        filename_prefix = "osechi_data"
        filename_suffix = ".csv"
        events_per_file = 10000
        number_of_files = 10000
        stream_mode = true
        mode = "count_based"

        [sensors.top]
        label = "top"
        step_size = 10
        threshold = "none"
        center = 512
        nsteps = 3

        [mocker]
        csv_path = null
        shuffle = false
        speed = 1.0
        jitter = 0.0
        loop = true
        ```

    Beginner note:
        - **REQUIRED**: All configurations must use [sampler] section
        - Choose mode='count_based' for event-based acquisition
        - Choose mode='time_based' for time-based acquisition
    """

    device: DeviceConfig
    sampler: Optional[SamplerConfig] = None
    sensors: Dict[str, SensorConfig]
    mocker: MockerConfig

    @model_validator(mode="after")
    def validate_config_format(self):
        """Validate configuration format and ensure [sampler] is specified.

        Why this matters:
            [sampler] is now the only supported format for data acquisition configuration.
            Reject configurations missing [sampler] with a clear error message.

        What to test:
            - Accept configuration with [sampler] section
            - Reject configuration missing [sampler] section
            - Error message clearly indicates what's required

        Beginner note:
            All configurations must now use the [sampler] section with either
            mode='count_based' (count-based acquisition) or mode='time_based' (time-based acquisition).
        """
        if self.sampler is None:
            raise ValueError(
                "Configuration must specify [sampler] section. "
                "Use mode='count_based' for event-based acquisition "
                "or mode='time_based' for time-based acquisition."
            )

        return self

    @classmethod
    def from_toml(cls, path: Path) -> "HaniwersConfig":
        """Load complete configuration from a TOML file with validation.

        Why this matters:
            This is the primary way to load and validate a complete Haniwers configuration.
            It ensures all components (device, DAQ, sensors) are present and valid.

        Args:
            path: Path to TOML file containing all configuration sections

        Returns:
            HaniwersConfig instance with all validated sub-configurations

        Raises:
            ValueError: If TOML file cannot be read, parsed, or is missing required sections

        Usage Example:
            ```python
            from pathlib import Path
            config = HaniwersConfig.from_toml(Path("hnw.toml"))

            # Access components
            print(config.device.port)
            print(config.sampler.label)
            print(config.sensors["top"].center)
            ```

        Beginner note:
            The file must have sections for [device], [sampler], [mocker], and at least one
            sensor section like [sensors.top]. If any required section is missing, you'll get
            a clear error message showing what's needed.
        """
        log = base_logger.bind(context="ConfigModel")
        log.debug(f"Reading config file from: {path}")
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            msg = f"Failed to parse TOML file: '{path}': {e}"
            log.warning(msg)
            raise ValueError(msg)
        except Exception as e:
            # Catch FileNotFoundError, PermissionError, etc
            msg = f"Unable to read config file: '{path}': {e}"
            log.error(msg)
            raise ValueError(msg)
        try:
            return cls.model_validate(data)
        except Exception as e:
            # Catch validation errors
            msg = f"Invalid configuration format in '{path}': {e}"
            log.error(msg)
            raise ValueError(msg)


if __name__ == "__main__":
    """Self test.

    uv run src/haniwers/v1/config/model.py
    """

    # 設定ファイルを読み込む
    cfg = HaniwersConfig.from_toml(Path("hnw.toml"))
    print(cfg.model_dump())  # or cfg.dict() in Pydantic v1

    # デバイス設定を確認
    device = cfg.device  # -> DeviceConfig
    print(device)

    # センサー設定を確認
    sensors = cfg.sensors
    print(sensors)

    # Noneへの変換を確認
    for name, sensor in sensors.items():
        print(f"{name} threshold (raw):", sensor.threshold)

    # チャンネルごとのスキャン範囲を確認
    for name, sensor in sensors.items():
        print(f"{name} threshold range:", list(sensor.threshold_range()))

    print("\n--- Sensor threshold ranges ---")
    for name, sensor in sensors.items():
        print(f"{name}: range = {list(sensor.threshold_range())}, threshold = {sensor.threshold}")

    # DAQ設定を確認
    daq = cfg.daq  # -> DaqConfig
    print(daq)

    # スキャン設定を確認
    scan = cfg.scan  # -> ScanConfig
    print(scan)
