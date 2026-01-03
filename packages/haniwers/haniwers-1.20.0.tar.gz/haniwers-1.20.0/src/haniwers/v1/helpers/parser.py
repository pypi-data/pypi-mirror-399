"""Parser utilities for OSECHI detector configuration.

This module provides functions to parse and validate threshold configuration
from command-line arguments and configuration files.
"""

from haniwers.v1.helpers.exceptions import (
    InvalidChannelError,
    InvalidThresholdError,
    InvalidThresholdFormatError,
)


def parse_thresholds(thresholds_str: str) -> dict[int, int]:
    """Parse threshold configuration string into channel:value pairs.

    Parses a string in the format 'channel:threshold;channel:threshold;...'
    and returns a dictionary mapping channel numbers to threshold values.

    This parser validates:
    - Format: Each pair must be 'channel:threshold' separated by semicolons
    - Channel range: Must be 1-3 (top, mid, btm layers)
    - Threshold range: Must be 1-1023 (10-bit value)

    Args:
        thresholds_str: Threshold configuration string
            Examples:
            - '1:280' for single channel
            - '1:290;2:320;3:298' for multiple channels

    Returns:
        Dictionary mapping channel (int) to threshold (int)
        Example: {1: 290, 2: 320, 3: 298}

    Raises:
        InvalidThresholdFormatError: If format is invalid
            - Missing ':' separator in pair
            - Non-integer channel or threshold values
        InvalidChannelError: If channel not in range 1-3
        InvalidThresholdError: If threshold not in range 1-1023

    Example:
        >>> parse_thresholds('1:280')
        {1: 280}

        >>> parse_thresholds('1:290;2:320;3:298')
        {1: 290, 2: 320, 3: 298}
    """
    threshold_dict: dict[int, int] = {}

    for pair in thresholds_str.split(";"):
        if ":" not in pair:
            msg = f"Invalid threshold format: '{pair}'. Expected 'channel:value'"
            raise InvalidThresholdFormatError(msg)

        try:
            ch_str, vth_str = pair.split(":")
            ch = int(ch_str.strip())
            vth = int(vth_str.strip())
        except ValueError as e:
            msg = f"Invalid threshold values in '{pair}'. Channel and value must be integers."
            raise InvalidThresholdFormatError(msg) from e

        # Validate channel range (1-3 for OSECHI detector)
        if not (1 <= ch <= 3):
            msg = f"Channel {ch} out of range 1-3"
            raise InvalidChannelError(msg)

        # Validate threshold range (1-1023 for 10-bit value)
        if not (1 <= vth <= 1023):
            msg = f"Threshold {vth} out of range 1-1023 for channel {ch}"
            raise InvalidThresholdError(msg)

        threshold_dict[ch] = vth

    return threshold_dict
