"""Custom exceptions for Haniwers module.

This module defines domain-specific exceptions for:
- Threshold validation and device communication errors
- Configuration file parsing and validation
- Data processing errors
"""


class InvalidChannelError(ValueError):
    """Raised when channel number is outside valid range (1-3).

    The OSECHI detector has exactly 3 layers (top, middle, bottom),
    corresponding to channels 1, 2, and 3 respectively.

    Example:
        >>> validate_channel(4)
        Traceback (most recent call last):
            ...
        InvalidChannelError: Channel must be 1-3, got 4
    """

    pass


class InvalidThresholdError(ValueError):
    """Raised when threshold value is outside valid range (1-1023).

    The threshold is a 10-bit value representing the detector's sensitivity.
    Valid range is 1-1023 (0 is reserved/invalid for writing operations).

    Example:
        >>> validate_threshold(2000)
        Traceback (most recent call last):
            ...
        InvalidThresholdError: Threshold must be 1-1023, got 2000
    """

    pass


class InvalidThresholdFormatError(ValueError):
    """Raised when threshold configuration string has invalid format.

    The threshold configuration must be in the format:
    'channel:threshold;channel:threshold;...'

    Valid examples:
    - '1:280' for single channel
    - '1:290;2:320;3:298' for multiple channels

    Invalid examples:
    - '1 280' (missing ':' separator)
    - '1:' (missing threshold value)
    - ':280' (missing channel number)
    - '1:280;' (trailing semicolon)

    Example:
        >>> parse_thresholds('1 280')  # Missing colon
        Traceback (most recent call last):
            ...
        InvalidThresholdFormatError: Invalid threshold format: '1 280'. Expected 'channel:value'
    """

    pass


class InvalidIDError(ValueError):
    """Raised when an ID (run_id, etc.) is not found in configuration.

    The specified ID does not exist in the configuration file or database.
    This typically means:
    - ID was typed incorrectly
    - ID has not been registered yet
    - Configuration needs to be updated

    Example:
        >>> # Run ID 999 not found in runs.csv
        >>> _get_run_info(runs_csv, "999", workspace)
        Traceback (most recent call last):
            ...
        InvalidIDError: Run ID '999' not found in runs.csv. Available: [1, 2, 3, ...]
    """

    pass


class InvalidCSVError(IOError):
    """Raised when a CSV file has formatting or structural issues.

    This error occurs when:
    - Required columns are missing
    - CSV file is malformed or unreadable
    - File format is invalid or incompatible

    Example:
        >>> # Missing required columns in runs.csv
        >>> _get_run_info(runs_csv, "1", workspace)
        Traceback (most recent call last):
            ...
        InvalidCSVError: No 'path_raw_data' column found in runs.csv. \
            Expected columns: [run_id, path_raw_data, search_pattern, ...]
    """

    pass
