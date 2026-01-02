"""Validator for OSECHI detector and file operations.

Provides validation functions for:
- OSECHI detector hardware parameters (channels, thresholds)
- File system operations (files, directories)
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
        Parallel threshold scanning requires all channels to have the same number
        of threshold steps for synchronized data collection. This validator ensures
        threshold ranges are compatible before starting the scan.

    What to test:
        - Accept when all channels have same number of steps
        - Reject when channels have different step counts
        - Provide clear error message showing step counts per channel
        - Accept both serial and parallel modes (serial has no restrictions)

    Args:
        sensors: Dictionary mapping channel keys (e.g., 'ch1', 'ch2', 'ch3')
                to SensorConfig objects
        scan_type: Type of scanning - "serial" or "parallel" (default: "parallel")

    Raises:
        ValueError: If parallel scan has channels with different step counts

    Example (parallel - coordinated stepping):
        >>> from haniwers.v1.config.model import SensorConfig
        >>> sensors = {
        ...     'ch1': SensorConfig(id=1, name='ch1', label='top', step_size=5,
        ...                         center=200, nsteps=10, threshold=None),
        ...     'ch2': SensorConfig(id=2, name='ch2', label='mid', step_size=5,
        ...                         center=300, nsteps=10, threshold=None),
        ... }
        >>> validate_threshold_scan_config(sensors, scan_type="parallel")
        # OK - both have nsteps=10, so same number of steps

    Example (parallel - mismatched stepping - ERROR):
        >>> sensors = {
        ...     'ch1': SensorConfig(id=1, name='ch1', label='top', step_size=5,
        ...                         center=200, nsteps=10, threshold=None),
        ...     'ch2': SensorConfig(id=2, name='ch2', label='mid', step_size=5,
        ...                         center=300, nsteps=5, threshold=None),
        ... }
        >>> validate_threshold_scan_config(sensors, scan_type="parallel")
        Traceback (most recent call last):
            ...
        ValueError: Parallel scanning requires all channels to have same number of steps...

    Note for beginners:
        This validator is called automatically before parallel threshold scanning starts.
        If it fails, you need to ensure all channels have the same center, nsteps, and
        step_size configuration.
    """
    # Serial scanning has no restrictions on step counts per channel
    if scan_type == "serial":
        return

    # Parallel scanning: all channels must have same number of steps
    if scan_type == "parallel":
        step_counts = {}
        for ch_key, sensor in sensors.items():
            ch = sensor.id
            num_steps = len(list(sensor.threshold_range()))
            step_counts[ch] = num_steps

        # Check if all step counts are the same
        unique_counts = set(step_counts.values())
        if len(unique_counts) > 1:
            raise ValueError(
                f"Parallel scanning requires all channels to have same number of steps. "
                f"Got: {step_counts}. "
                f"Ensure all channels have same center, nsteps, and step_size configuration."
            )
