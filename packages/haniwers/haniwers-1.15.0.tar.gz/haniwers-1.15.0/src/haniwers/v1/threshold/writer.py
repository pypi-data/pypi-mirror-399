"""Threshold writing functions for detector channels.

Provides functions to write threshold values with validation, retry logic,
CSV integration, and logging. Uses v1 text-based command protocol with strict JSON validation.

Two-layer architecture:
    - Low-level: write_threshold(), write_threshold_with_retry()
    - High-level (recommended): apply_threshold(), apply_thresholds()

Public API:
    - apply_threshold(): Single sensor with retry and optional logging
    - apply_thresholds(): Multiple sensors in batch
    - write_threshold_to_csv(): Append operation result to CSV log
"""

import csv
import json
import time
from pathlib import Path

import pendulum

from haniwers.v1.config.model import SensorConfig
from haniwers.v1.daq.device import Device
from haniwers.v1.daq.mocker import BaseMocker
from haniwers.v1.log.logger import logger
from haniwers.v1.helpers.exceptions import (
    InvalidChannelError,
    InvalidThresholdError,
)
from haniwers.v1.helpers.validator import (
    validate_channel,
    validate_threshold,
)
from haniwers.v1.threshold.model import ThresholdWriteResult

# Device Communication Timing (seconds)
# These values are tuned for reliable serial communication
DEVICE_STABILIZATION_DELAY = 0.1  # Wait time after write for device to process
RETRY_INTERVAL = 0.5  # Wait time between retry attempts


def write_threshold(device: Device, ch: int, vth: int) -> bool:
    """Write a threshold value to a detector channel (low-level API).

    Sends the threshold value using the v1 text-based protocol.
    The device must be connected before calling this function.

    Protocol (v1 text-based):
        1. Validate channel (1-3) and threshold (1-1023)
        2. Stop data stream (SET_STREAM 0) to prevent response mixing
        3. Send text command: "SET_THRESHOLD {channel} {value}\n"
        4. Read device response and parse:
           - JSON format: {"type":"response","status":"ok","channel":ch,"threshold":vth}
           - Threshold field must match requested value (strict validation)
        5. Resume data stream (SET_STREAM 1)

    Args:
        device: Connected Device (real or mock) for serial communication
        ch: Channel number (1=top, 2=mid, 3=btm)
        vth: Threshold value (1-1023)

    Returns:
        True if device confirmed write with matching threshold, False if rejected or mismatched

    Raises:
        InvalidChannelError: If ch not in 1-3
        InvalidThresholdError: If vth not in 1-1023

    Example:
        >>> device = Device("/dev/tty.usbserial")
        >>> device.connect()
        >>> success = write_threshold(device, ch=1, vth=280)
        >>> device.disconnect()

    Note:
        This is a low-level function with no retry logic. For most use cases,
        use `apply_threshold()` which adds retry and logging automatically.
        Requires kurikintons v1.6+ firmware.
    """
    # Validate inputs first
    validate_channel(ch)
    validate_threshold(vth)

    # Flush device buffers to clear any pending data
    device.flush()

    # Step 1: Stop data stream to prevent mixing with command response
    logger.debug("Stopping data stream (SET_STREAM 0)")
    device.write("SET_STREAM 0\n")
    # Wait for stream to stop and device to stabilize
    time.sleep(DEVICE_STABILIZATION_DELAY)
    # Flush any buffered data from stream stop
    device.flush()

    # Step 2: Send threshold command
    # Text command (v1 text protocol)
    command = f"SET_THRESHOLD {ch} {vth}\n"

    logger.debug(f"Writing threshold: ch={ch}, vth={vth} -> command='{command.strip()}'")

    device.write(command)

    # Step 3: Read response lines, skipping any debug output
    response1 = None
    while True:
        line = device.readline().strip()
        # Skip debug lines (they start with "DEBUG")
        if line.startswith("DEBUG"):
            logger.debug(f"Skipped debug output: {line}")
            continue
        # This is the actual response
        response1 = line
        break

    logger.debug(f"Device response: '{response1}'")

    # Wait for device stabilization after write
    time.sleep(DEVICE_STABILIZATION_DELAY)

    # Step 4: Parse response and determine result
    result = False

    # Parse response: JSON format only (strict validation)
    if not response1.startswith("{"):
        logger.warning(
            f"Unexpected device response: '{response1}' "
            f"(expected JSON: {{'type':'response','status':'ok','channel':{ch},'threshold':{vth}}}). "
            f"Check firmware version compatibility (requires kurikintons v1.6+)."
        )
        result = False
    else:
        try:
            response_json = json.loads(response1)
            # Check JSON response format: {"type":"response","status":"ok",...}
            if response_json.get("type") != "response":
                logger.warning(
                    f"Invalid JSON response type: '{response_json.get('type')}' (expected 'response')"
                )
                result = False
            else:
                status = response_json.get("status")
                response_channel = response_json.get("channel")

                if status == "ok" and response_channel == ch:
                    # Strict threshold validation (requires kurikintons v1.6+)
                    response_threshold = response_json.get("threshold")
                    if response_threshold is None:
                        logger.error(
                            f"Threshold field missing in JSON response. "
                            f"Firmware version may be too old (requires kurikintons v1.6+)"
                        )
                        result = False
                    elif response_threshold != vth:
                        logger.error(
                            f"Threshold mismatch: requested={vth}, device confirmed={response_threshold}"
                        )
                        result = False
                    else:
                        if isinstance(device, BaseMocker):
                            logger.info(f"Mock threshold write successful: ch={ch}, vth={vth}")
                        else:
                            logger.info(f"Threshold write successful: ch={ch}, vth={vth}")
                        result = True

                elif status == "error":
                    logger.warning(f"Device rejected threshold write: ch={ch}, vth={vth}")
                    result = False
                else:
                    logger.warning(
                        f"Unexpected response status: '{status}' or channel: '{response_channel}' "
                        f"(expected status='ok', channel={ch})"
                    )
                    result = False

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: '{response1}' (error: {e})")
            result = False

    # Step 5: Resume data stream
    logger.debug("Resuming data stream (SET_STREAM 1)")
    device.write("SET_STREAM 1\n")
    # Wait for stream to resume
    time.sleep(DEVICE_STABILIZATION_DELAY)

    return result


def write_threshold_with_retry(
    device: Device, ch: int, vth: int, max_retry: int = 3
) -> ThresholdWriteResult:
    """Write threshold with automatic retry on communication failure.

    Wraps write_threshold() with retry logic for reliability. Retries up to
    max_retry times with 0.5 second intervals between attempts. Returns
    structured result with attempt count.

    Validation errors (invalid channel/threshold) raise immediately without
    retry, since retrying won't fix bad input data.

    Args:
        device: Connected Device for serial communication
        ch: Channel number (1-3)
        vth: Threshold value (1-1023)
        max_retry: Maximum write attempts (default: 3)

    Returns:
        ThresholdWriteResult with success status and attempts made

    Raises:
        InvalidChannelError: If ch not in 1-3
        InvalidThresholdError: If vth not in 1-1023

    Example:
        >>> device = Device("/dev/tty.usbserial")
        >>> device.connect()
        >>> result = write_threshold_with_retry(device, ch=1, vth=280, max_retry=3)
        >>> print(f"Success: {result.success}, Attempts: {result.attempts}")
    """
    for attempt in range(1, max_retry + 1):
        # Attempt write (validation happens inside write_threshold)
        success = write_threshold(device, ch, vth)

        if success:
            if attempt > 1:
                logger.info(f"Threshold write succeeded on attempt {attempt}/{max_retry}")
            return ThresholdWriteResult(
                timestamp=pendulum.now().to_iso8601_string(),
                id=ch,
                vth=vth,
                success=True,
                attempts=attempt,
            )

        # If not the last attempt, wait before retrying
        if attempt < max_retry:
            time.sleep(RETRY_INTERVAL)

    # All attempts exhausted
    logger.error(f"All {max_retry} threshold write attempts failed: ch={ch}, vth={vth}")
    return ThresholdWriteResult(
        timestamp=pendulum.now().to_iso8601_string(),
        id=ch,
        vth=vth,
        success=False,
        attempts=max_retry,
    )


def write_threshold_to_csv(csv_path: Path, result: ThresholdWriteResult) -> None:
    """Write threshold operation result to CSV file for audit trail.

    Appends a CSV row with all ThresholdWriteResult fields to create a complete
    audit log. Creates parent directory automatically if needed. Uses ISO8601
    timestamp with timezone for unambiguous time recording.

    CSV format (header on first creation only):
        timestamp,id,vth,success,attempts
        2024-05-20T11:00:00.123456+09:00,1,280,True,1

    Args:
        csv_path: Path to CSV log file (appended if exists, created if missing)
        result: ThresholdWriteResult with all operation details

    Raises:
        PermissionError: If csv directory is not writable

    Example:
        >>> from pathlib import Path
        >>> result = ThresholdWriteResult(
        ...     timestamp="2024-05-20T11:00:00.123456+09:00",
        ...     id=1,
        ...     vth=280,
        ...     success=True,
        ...     attempts=1
        ... )
        >>> write_threshold_to_csv(Path("logs/ops.csv"), result)
    """
    # Create parent directories if they don't exist
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert NamedTuple to dict for flexible field handling
    result_dict = result._asdict()
    fieldnames = list(result_dict.keys())

    # Write header on first creation, skip on subsequent appends
    file_exists = csv_path.exists() and csv_path.stat().st_size > 0
    with csv_path.open(mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(result_dict)

    logger.debug(
        f"Wrote threshold to CSV: id={result.id}, vth={result.vth}, success={result.success}, attempts={result.attempts}"
    )


def apply_threshold(
    device: Device,
    sensor: SensorConfig,
    max_retry: int = 3,
    history_path: Path | None = None,
) -> ThresholdWriteResult:
    """Apply threshold to a single sensor (recommended high-level API).

    Writes a sensor's threshold value to the detector with automatic retry and
    optional CSV logging. Recommended for most use cases. For batch operations,
    use apply_thresholds().

    Args:
        device: Connected Device for serial communication
        sensor: SensorConfig with id and threshold fields
        max_retry: Maximum write attempts (default: 3)
        history_path: Optional path to append operation log (CSV format)

    Returns:
        ThresholdWriteResult with success status, attempts made, and values written

    Raises:
        InvalidChannelError: If sensor.id not in 1-3
        InvalidThresholdError: If sensor.threshold not in 1-1023
        PermissionError: If history_path directory is not writable

    Example:
        >>> from haniwers.v1.daq.device import Device
        >>> from haniwers.v1.config.model import SensorConfig
        >>> device = Device("/dev/tty.usbserial")
        >>> device.connect()
        >>> sensor = SensorConfig(id=1, name="ch1", label="top", step_size=1,
        ...                       threshold=280, center=512, nsteps=10)
        >>> result = apply_threshold(device, sensor)
        >>> print(f"Ch{result.id}: {result.vth} ({result.attempts} attempts)")
    """
    # Write threshold with retry, get structured result
    result = write_threshold_with_retry(device, sensor.id, sensor.threshold, max_retry)

    # Write result to CSV if history_path provided
    if history_path is not None:
        try:
            write_threshold_to_csv(history_path, result)
        except PermissionError as e:
            logger.error(f"Failed to write CSV: {e}")
            raise

    # Log result
    if result.success:
        logger.info(
            f"Threshold applied successfully: id={sensor.id}, vth={sensor.threshold}, "
            f"attempts={result.attempts}"
        )
    else:
        logger.warning(
            f"Threshold application failed: id={sensor.id}, vth={sensor.threshold}, "
            f"attempts={result.attempts}"
        )

    return result


def apply_thresholds(
    device: Device,
    sensors: list[SensorConfig],
    max_retry: int = 3,
    history_path: Path | None = None,
) -> list[ThresholdWriteResult]:
    """Apply thresholds to multiple sensors (batch operation).

    Applies threshold values to multiple sensors sequentially. If one sensor
    fails, remaining sensors are still attempted. Results are returned in the
    same order as input sensors.

    Args:
        device: Connected Device for serial communication
        sensors: List of SensorConfig objects to apply
        max_retry: Maximum write attempts per sensor (default: 3)
        history_path: Optional path to append operation log (CSV format)

    Returns:
        List of ThresholdWriteResult objects (one per sensor), in input order

    Raises:
        InvalidChannelError: If any sensor.id not in 1-3
        InvalidThresholdError: If any sensor.threshold not in 1-1023
        PermissionError: If history_path directory is not writable

    Example:
        >>> from haniwers.v1.daq.device import Device
        >>> from haniwers.v1.config.model import SensorConfig
        >>> device = Device("/dev/tty.usbserial")
        >>> device.connect()
        >>> sensors = [
        ...     SensorConfig(id=1, name="ch1", label="top", step_size=1,
        ...                  threshold=280, center=512, nsteps=10),
        ...     SensorConfig(id=2, name="ch2", label="mid", step_size=1,
        ...                  threshold=320, center=512, nsteps=10),
        ... ]
        >>> results = apply_thresholds(device, sensors)
        >>> for r in results:
        ...     print(f"Ch{r.id}: {'OK' if r.success else 'FAILED'}")
    """
    # Process each sensor and collect results
    results: list[ThresholdWriteResult] = []
    for sensor in sensors:
        try:
            # Apply threshold to this sensor
            result = apply_threshold(device, sensor, max_retry, history_path)
            results.append(result)
        except (InvalidChannelError, InvalidThresholdError) as e:
            # Validation error - create failed result and continue
            logger.error(f"Validation error for sensor {sensor.id}: {e}")
            results.append(
                ThresholdWriteResult(
                    timestamp=pendulum.now().to_iso8601_string(),
                    id=sensor.id,
                    vth=sensor.threshold,
                    success=False,
                    attempts=0,
                )
            )
        except Exception as e:
            # Unexpected error - log and create failed result
            logger.error(f"Unexpected error applying sensor {sensor.id}: {e}")
            results.append(
                ThresholdWriteResult(
                    timestamp=pendulum.now().to_iso8601_string(),
                    id=sensor.id,
                    vth=sensor.threshold,
                    success=False,
                    attempts=0,
                )
            )

    # Summary log
    succeeded = sum(1 for r in results if r.success)
    failed = len(results) - succeeded
    logger.info(
        f"Batch operation complete: {succeeded} succeeded, {failed} failed out of {len(results)} sensors"
    )

    return results
