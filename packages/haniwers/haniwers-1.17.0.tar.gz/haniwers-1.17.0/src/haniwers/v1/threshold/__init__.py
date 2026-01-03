"""Threshold writer module for OSECHI detector.

This module provides functions to write threshold values to detector channels,
with support for validation, retry logic, CSV integration, and logging.

Public API:
    Writing (low-level):
        - write_threshold: Write single threshold (raw integers)
        - write_threshold_with_retry: Write with automatic retry

    High-level API (recommended):
        - apply_threshold: Apply single sensor config with retry and logging
        - apply_thresholds: Apply multiple sensor configs in batch

    CSV and logging:
        - write_threshold_to_csv: Record operation result to CSV log

    Exceptions:
        - InvalidChannelError: Channel not in range 1-3
        - InvalidThresholdError: Threshold not in range 1-1023
        - **Note**: Moved to v1/helpers/exceptions.py

Example (recommended API):
    >>> from haniwers.v1.threshold import apply_threshold
    >>> from haniwers.v1.daq.device import Device
    >>> from haniwers.v1.config.model import SensorConfig
    >>> device = Device("/dev/tty.usbserial")
    >>> device.connect()
    >>> sensor = SensorConfig(
    ...     id=1, name="ch1", label="top", step_size=1, threshold=280,
    ...     center=512, nsteps=10
    ... )
    >>> result = apply_threshold(device, sensor)
    >>> if result.success:
    ...     print(f"Set to {result.vth} in {result.attempts} attempts")
"""

from haniwers.v1.threshold.model import (
    ThresholdWriteResult,
    ThresholdScanResult,
)
from haniwers.v1.threshold.writer import (
    write_threshold,
    write_threshold_with_retry,
    apply_threshold,
    apply_thresholds,
    write_threshold_to_csv,
)

__all__ = [
    # Result types
    "ThresholdWriteResult",
    "ThresholdScanResult",
    # Writing functions (low-level)
    "write_threshold",
    "write_threshold_with_retry",
    # High-level API (recommended)
    "apply_threshold",
    "apply_thresholds",
    # CSV and logging functions
    "write_threshold_to_csv",
]
