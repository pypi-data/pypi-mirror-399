"""Validator for OSECHI detector and file operations.

Provides validation functions for:
- OSECHI detector hardware parameters (channels, thresholds)
- File system operations (files, directories)
- CLI parameter validation with proper error handling

This module consolidates all validation logic (P1-6) to reduce duplication
across the codebase and maintain consistent error handling patterns.
"""

from pathlib import Path

from haniwers.v1.helpers.exceptions import (
    InvalidChannelError,
    InvalidThresholdError,
)


def validate_channel(ch: int) -> None:
    """Validate that channel number is in valid range (1-3).

    The OSECHI detector has 3 layers (top, middle, bottom) corresponding
    to channels 1, 2, and 3 respectively.

    Args:
        ch: Channel number to validate

    Raises:
        InvalidChannelError: If ch is not in range 1-3

    Example:
        >>> validate_channel(1)  # OK - valid channel
        >>> validate_channel(4)  # Raises InvalidChannelError
        Traceback (most recent call last):
            ...
        InvalidChannelError: Channel must be 1-3, got 4

    Note for beginners:
        This function performs input validation to catch programming errors
        early. Always call this before device communication to avoid sending
        invalid commands to the hardware.
    """
    if not 1 <= ch <= 3:
        raise InvalidChannelError(f"Channel must be 1-3, got {ch}")


def validate_threshold(vth: int) -> None:
    """Validate that threshold value is in valid range (1-1023).

    The threshold is a 10-bit value (0-1023) representing the detector's
    sensitivity. Value 0 is reserved and invalid for write operations.

    Args:
        vth: Threshold value to validate

    Raises:
        InvalidThresholdError: If vth is not in range 1-1023

    Example:
        >>> validate_threshold(280)  # OK - valid threshold
        >>> validate_threshold(2000)  # Raises InvalidThresholdError
        Traceback (most recent call last):
            ...
        InvalidThresholdError: Threshold must be 1-1023, got 2000

    Note for beginners:
        Threshold values determine detector sensitivity:
        - Lower values: More sensitive (detects weaker signals, more noise)
        - Higher values: Less sensitive (detects only strong signals)
        - Typical values: 250-350 (from threshold scanning/fitting)
    """
    if not 1 <= vth <= 1023:
        raise InvalidThresholdError(f"Threshold must be 1-1023, got {vth}")


def validate_file_exists(file_path: str) -> Path:
    """Validate that a file exists and is readable.

    Args:
        file_path: Path to file to validate

    Returns:
        Path: Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        IsADirectoryError: If path exists but is a directory, not a file

    Example:
        >>> validate_file_exists("config.toml")
        PosixPath('config.toml')
        >>> validate_file_exists("nonexistent.csv")
        Traceback (most recent call last):
            ...
        FileNotFoundError: File not found: nonexistent.csv
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise IsADirectoryError(f"Not a file: {path}")

    return path


def validate_directory_exists(dir_path: str) -> Path:
    """Validate that a directory exists and is accessible.

    Args:
        dir_path: Path to directory to validate

    Returns:
        Path: Validated Path object

    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path exists but is a file, not a directory

    Example:
        >>> validate_directory_exists("data/")
        PosixPath('data')
        >>> validate_directory_exists("nonexistent/")
        Traceback (most recent call last):
            ...
        FileNotFoundError: Directory not found: nonexistent

    Note for beginners:
        Use this function to validate input directories before attempting
        to search for files or read configuration from them.
    """
    path = Path(dir_path)
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    return path


def validate_threshold_ranges(sensors: dict, scan_type: str = "parallel") -> None:
    """Validate that threshold ranges are compatible for coordinated scanning.

    Why this matters:
        Parallel threshold scanning requires all channels to have the same
        number of threshold steps for synchronized data collection. This
        validator ensures threshold ranges are compatible before starting
        the scan.

    What to test:
        - Accept when all channels have same number of steps
        - Reject when channels have different step counts
        - Provide clear error message showing step counts per channel
        - Accept both serial and parallel modes (serial has no restrictions)

    Args:
        sensors: Dictionary mapping channel keys (e.g., 'ch1', 'ch2', 'ch3')
                to SensorConfig objects
        scan_type: Type of scanning - "serial" or "parallel"
                  (default: "parallel")

    Raises:
        ValueError: If parallel scan has channels with different step counts

    Example (parallel - coordinated stepping):
        >>> from haniwers.v1.config.model import SensorConfig
        >>> sensors = {
        ...     'ch1': SensorConfig(
        ...         id=1, name='ch1', label='top', step_size=5,
        ...         center=200, nsteps=10, threshold=None
        ...     ),
        ...     'ch2': SensorConfig(
        ...         id=2, name='ch2', label='mid', step_size=5,
        ...         center=300, nsteps=10, threshold=None
        ...     ),
        ... }
        >>> validate_threshold_scan_config(sensors, scan_type="parallel")
        # OK - both have nsteps=10, so same number of steps

    Example (parallel - mismatched stepping - ERROR):
        >>> sensors = {
        ...     'ch1': SensorConfig(
        ...         id=1, name='ch1', label='top', step_size=5,
        ...         center=200, nsteps=10, threshold=None
        ...     ),
        ...     'ch2': SensorConfig(
        ...         id=2, name='ch2', label='mid', step_size=5,
        ...         center=300, nsteps=5, threshold=None
        ...     ),
        ... }
        >>> validate_threshold_scan_config(sensors, scan_type="parallel")
        Traceback (most recent call last):
            ...
        ValueError: Parallel scanning requires all channels to have same...

    Note for beginners:
        This validator is called automatically before parallel threshold
        scanning starts. If it fails, ensure all channels have the same
        center, nsteps, and step_size configuration.
    """
    # Serial scanning has no restrictions on step counts per channel
    if scan_type == "serial":
        return

    # Parallel scanning: all channels must have same number of steps
    if scan_type == "parallel":
        step_counts = {}
        for _, sensor in sensors.items():
            ch = sensor.id
            num_steps = len(list(sensor.threshold_range()))
            step_counts[ch] = num_steps

        # Check if all step counts are the same
        unique_counts = set(step_counts.values())
        if len(unique_counts) > 1:
            msg = (
                "Parallel scanning requires all channels to have same "
                "number of steps. "
                f"Got: {step_counts}. "
                "Ensure all channels have same center, nsteps, and "
                "step_size configuration."
            )
            raise ValueError(msg)


def validate_channel_range(ch: int, min_ch: int = 1, max_ch: int = 3) -> int:
    """Validate and return channel number within specified range.

    Unified validation function for channel range checking across CLI commands.
    Replaces ad-hoc range checks like 'if ch not in [1, 2, 3]'.

    Why this matters:
        Channel validation appears in multiple places (cli/threshold.py, etc.).
        Consolidating into a single function ensures consistent error messages
        and makes future changes easier (e.g., if we ever support more channels).

    Args:
        ch: Channel number to validate
        min_ch: Minimum valid channel number (default: 1)
        max_ch: Maximum valid channel number (default: 3)

    Returns:
        int: The validated channel number

    Raises:
        InvalidChannelError: If channel is outside valid range

    Example:
        >>> validate_channel_range(2)  # Returns 2
        >>> validate_channel_range(5)  # Raises InvalidChannelError
        Traceback (most recent call last):
            ...
        InvalidChannelError: Channel must be 1-3, got 5

    Note for beginners:
        This is the unified validator for channel range checking.
        Use this instead of hardcoded range checks like 'if ch not in [1, 2, 3]'.
    """
    if not (min_ch <= ch <= max_ch):
        raise InvalidChannelError(f"Channel must be {min_ch}-{max_ch}, got {ch}")
    return ch


def validate_threshold_range(vth: int, min_val: int = 1, max_val: int = 1023) -> int:
    """Validate and return threshold value within specified range.

    Unified validation function for threshold range checking across config
    and CLI commands. Replaces ad-hoc range checks.

    Why this matters:
        Threshold range validation appears in 4+ locations:
        - config/model.py (Pydantic validator)
        - config/model.py:suppress_threshold field
        - cli/mock.py (implicit)
        - Multiple other places

        Consolidating into a single function ensures:
        - Consistent error messages
        - Consistent validation rules
        - Easier maintenance and future changes

    Args:
        vth: Threshold value to validate
        min_val: Minimum valid threshold (default: 1)
        max_val: Maximum valid threshold (default: 1023)

    Returns:
        int: The validated threshold value

    Raises:
        InvalidThresholdError: If threshold is outside valid range

    Example:
        >>> validate_threshold_range(280)  # Returns 280
        >>> validate_threshold_range(2000)  # Raises InvalidThresholdError
        Traceback (most recent call last):
            ...
        InvalidThresholdError: Threshold must be 1-1023, got 2000

    Note for beginners:
        This is the unified validator for threshold range checking.
        Use this instead of hardcoded checks in config models or CLI code.
    """
    if not (min_val <= vth <= max_val):
        raise InvalidThresholdError(f"Threshold must be {min_val}-{max_val}, got {vth}")
    return vth


def validate_file_path(file_path: str | Path, must_exist: bool = True) -> Path:
    """Validate file path with flexible error handling.

    Unified validator for file path checking across CLI commands.
    Replaces ad-hoc file existence checks in cli/mock.py and cli/preprocess.py.

    Why this matters:
        File existence validation appears in 3+ locations with different
        error handling patterns:
        - cli/mock.py: typer.BadParameter
        - cli/preprocess.py: typer.Exit
        - helpers/validator.py: FileNotFoundError / IsADirectoryError

        Consolidating ensures consistent behavior while allowing
        callers to choose their error handling strategy.

    Args:
        file_path: Path to file to validate (str or Path)
        must_exist: If True, file must exist; if False, just validate format

    Returns:
        Path: Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist and must_exist=True
        IsADirectoryError: If path exists but is a directory
        TypeError: If file_path is not str or Path

    Example:
        >>> validate_file_path("config.toml")
        PosixPath('config.toml')
        >>> validate_file_path("nonexistent.csv")
        Traceback (most recent call last):
            ...
        FileNotFoundError: File not found: nonexistent.csv

    Note for beginners:
        This is the unified validator for file path checking.
        Use this instead of separate validation in each CLI command.
    """
    path = Path(file_path)

    if must_exist:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise IsADirectoryError(f"Not a file (is a directory): {path}")

    return path


def validate_directory_path(dir_path: str | Path, must_exist: bool = True) -> Path:
    """Validate directory path with flexible error handling.

    Unified validator for directory path checking across CLI commands.
    Replaces ad-hoc directory validation in cli/preprocess.py.

    Why this matters:
        Directory validation appears in 2+ locations with inconsistent
        error handling. This consolidates it into one place.

    Args:
        dir_path: Path to directory to validate (str or Path)
        must_exist: If True, directory must exist; if False, just validate format

    Returns:
        Path: Validated Path object

    Raises:
        FileNotFoundError: If directory doesn't exist and must_exist=True
        NotADirectoryError: If path exists but is a file, not a directory
        TypeError: If dir_path is not str or Path

    Example:
        >>> validate_directory_path("data/")
        PosixPath('data')
        >>> validate_directory_path("nonexistent/")
        Traceback (most recent call last):
            ...
        FileNotFoundError: Directory not found: nonexistent

    Note for beginners:
        This is the unified validator for directory path checking.
        Use this instead of separate validation in each CLI command.
    """
    path = Path(dir_path)

    if must_exist:
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory (is a file): {path}")

    return path


def validate_numeric_range(
    value: float | int,
    min_val: float | int,
    max_val: float | int,
    param_name: str = "value",
) -> float | int:
    """Validate that a numeric value is within specified range.

    Generalized numeric range validation for speed, duration, and other
    parameters. Used to consolidate ad-hoc range checks.

    Why this matters:
        Numeric range validation appears in multiple places:
        - cli/mock.py: speed validation (0.1-100.0)
        - config/model.py: various numeric fields
        - Multiple other commands

        This provides a unified, reusable validator.

    Args:
        value: Numeric value to validate
        min_val: Minimum valid value (inclusive)
        max_val: Maximum valid value (inclusive)
        param_name: Parameter name for error messages (default: "value")

    Returns:
        The validated value (unchanged)

    Raises:
        ValueError: If value is outside [min_val, max_val]

    Example:
        >>> validate_numeric_range(5.0, 0.1, 100.0, "speed")
        5.0
        >>> validate_numeric_range(200.0, 0.1, 100.0, "speed")
        Traceback (most recent call last):
            ...
        ValueError: speed must be in range 0.1-100.0, got 200.0

    Note for beginners:
        This is a general-purpose numeric range validator.
        Use for speed, duration, and similar range-checked parameters.
    """
    if not (min_val <= value <= max_val):
        raise ValueError(f"{param_name} must be in range {min_val}-{max_val}, got {value}")
    return value
