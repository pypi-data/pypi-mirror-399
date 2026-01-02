"""Data models for threshold scanning operations.

Immutable NamedTuple data structures for threshold operations and scanning results.

Classes:
    ThresholdWriteResult: Result of a single threshold write operation
    ThresholdScanResult: Result of a single threshold scan measurement point

See also:
    - threshold/writer.py: Implements threshold write operations
    - daq/sampler.py: Data collection pattern for scanning operations
"""

from typing import NamedTuple


class ThresholdWriteResult(NamedTuple):
    """Result of a threshold write operation.

    Immutable result object returned by apply_threshold() and apply_thresholds().
    Records the timestamp, channel, threshold value, success status, and attempt count
    for a single threshold write operation. Used for audit trail logging to CSV.

    Attributes:
        timestamp: ISO8601 timestamp with timezone
        id: Channel/sensor ID (1-3)
        vth: Threshold value written (1-1023)
        success: Whether write succeeded (True/False)
        attempts: Number of write attempts made (1 = first try, >1 = retried)

    Example:
        >>> result = ThresholdWriteResult(
        ...     timestamp="2025-10-29T01:35:52.668533+09:00",
        ...     id=3,
        ...     vth=1000,
        ...     success=True,
        ...     attempts=2
        ... )
        >>> print(f"Ch{result.id}: {result.vth} in {result.attempts} attempts")
        Ch3: 1000 in 2 attempts
    """

    timestamp: str
    id: int
    vth: int
    success: bool
    attempts: int


class ThresholdScanResult(NamedTuple):
    """Result of a single threshold scan measurement point.

    Immutable result representing one measurement during threshold scanning.
    Records the timestamp, event count, threshold values for all channels,
    and event hit counts for all detector layers. Each row in a scan CSV represents
    one ThresholdScanResult.

    Attributes:
        timestamp: ISO8601 timestamp with timezone
        event_count: Total number of events collected during this measurement
        ch1: Threshold value for channel 1 (top layer) (1-1023)
        ch2: Threshold value for channel 2 (middle layer) (1-1023)
        ch3: Threshold value for channel 3 (bottom layer) (1-1023)
        top: Number of events detected in top layer
        mid: Number of events detected in middle layer
        btm: Number of events detected in bottom layer

    Example:
        >>> result = ThresholdScanResult(
        ...     timestamp="2025-10-29T00:17:55.545716+09:00",
        ...     event_count=10,
        ...     ch1=1000,
        ...     ch2=1000,
        ...     ch3=306,
        ...     top=9,
        ...     mid=0,
        ...     btm=2
        ... )
        >>> print(f"Channels: {result.ch1}, {result.ch2}, {result.ch3}")
        Channels: 1000, 1000, 306
    """

    timestamp: str
    event_count: int
    ch1: int
    ch2: int
    ch3: int
    top: int
    mid: int
    btm: int
