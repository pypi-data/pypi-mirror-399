"""Serial port connectivity testing.

Provides functions to test connections to OSECHI detector devices
by reading detector data from the serial port and validating the format.
"""

import time
from typing import Optional

import serial

from haniwers.v1.log.logger import logger as base_logger
from haniwers.v1.port.model import DetectorData, TestResult

# Bind context for all port testing operations
logger = base_logger.bind(context="port.tester")


def test_port_connectivity(
    device: str,
    baudrate: int = 115200,
    timeout: float = 5.0,
) -> TestResult:
    """Test connectivity to OSECHI detector.

    Opens the specified port and attempts to read detector data
    to verify it's the correct device.

    Args:
        device: Path to serial device (e.g., /dev/ttyUSB0, COM3)
        baudrate: Baud rate in bits per second (default: 115200)
        timeout: Read timeout in seconds (default: 5.0)

    Returns:
        TestResult object indicating success or failure with details

    Example:
        >>> result = test_port_connectivity("/dev/ttyUSB0")
        >>> if result.success:
        ...     print(f"Connected in {result.response_time:.2f}s")
        ... else:
        ...     print(f"Error: {result.error_type}")
    """
    logger.info(f"Testing connection to {device}...")

    start_time = time.time()
    result: Optional[TestResult] = None

    try:
        # Serial port communication basics:
        # - baudrate: Data transmission speed (bits per second)
        #   OSECHI detector is typically configured to 115200 bps
        # - timeout=N: Maximum seconds to wait for data
        #   If no data arrives within timeout, readline() returns empty bytes (b"")
        # - Context manager (with): Automatically closes port on exit, even if error occurs
        with serial.Serial(device, baudrate=baudrate, timeout=timeout) as port:
            logger.debug(f"Port opened: {port.name}")

            # readline() blocks until either:
            # 1. A newline character (\n) is received
            # 2. Timeout expires (returns b"")
            # OSECHI sends one line per sampling period (typically 1 second)
            raw_data = port.readline()

            if not raw_data:
                # Empty bytes means timeout - no data received within timeout period
                # Indicates either wrong port, device unpowered, or wrong baud rate
                result = TestResult.failure_result(
                    error_type="timeout",
                    message=f"No data received within {timeout} seconds\n"
                    "Possible causes:\n"
                    "  - Device is not an OSECHI detector\n"
                    "  - Detector is not powered on\n"
                    "  - Wrong baud rate (check DAQ config)",
                )
                logger.error(result.format_for_display())
                return result

            # Decode bytes to string
            # OSECHI sends ASCII text, but we specify UTF-8 for compatibility
            # UnicodeDecodeError indicates binary data or wrong device type
            try:
                line = raw_data.decode("UTF-8").strip()
                logger.debug(f"Received: {line}")
            except UnicodeDecodeError as e:
                result = TestResult.failure_result(
                    error_type="invalid_data",
                    message=f"Cannot decode data: {e}\n"
                    "Data might be corrupted or using wrong encoding",
                )
                logger.error(result.format_for_display())
                return result

            # Parse and validate data format
            # This checks if the data matches OSECHI detector format:
            # "top mid btm adc tmp atm hmd" (7 space-separated fields)
            try:
                data = DetectorData.from_line(line)
                logger.debug(f"Parsed: top={data.top}, mid={data.mid}, btm={data.btm}")
            except ValueError as e:
                result = TestResult.failure_result(
                    error_type="invalid_data",
                    message=f"Received data but format is invalid\n"
                    f"  Data sample: {line}\n"
                    f"  Error: {e}\n\n"
                    "Expected format: top mid btm adc tmp atm hmd\n"
                    "Example: 2 0 0 936 27.37 100594.35 41.43",
                )
                logger.error(result.format_for_display())
                return result

            # Validate sensor value ranges (non-fatal check)
            # Out-of-range values are warnings, not errors
            # Example: tmp=0.0 indicates BME280 sensor not connected (acceptable for testing)
            if not data.is_valid():
                logger.warning("Data received but values are out of expected ranges")
                logger.warning(
                    f"Data: top={data.top}, tmp={data.tmp}°C, atm={data.atm}Pa, hmd={data.hmd}%"
                )

            # Test successful - port is communicating with OSECHI detector
            elapsed = time.time() - start_time
            result = TestResult.success_result(response_time=elapsed, data_sample=line)

            logger.info(result.message)
            logger.info(f"  Data sample: {line}")
            logger.info("")
            logger.info("✓ Data format valid")
            logger.info(f"  - Event counts: top={data.top}, mid={data.mid}, btm={data.btm}")
            logger.info(f"  - Temperature: {data.tmp}°C")
            logger.info(f"  - Pressure: {data.atm} Pa")
            logger.info(f"  - Humidity: {data.hmd}%")
            logger.info("")
            logger.info("✓ This port is ready for data acquisition!")

            return result

    except serial.SerialException as e:
        # SerialException is raised by pyserial for all serial port errors
        # We categorize errors by analyzing the error message string
        # This hierarchical error handling provides specific guidance for each case
        error_str = str(e).lower()

        # Permission errors (Linux/macOS): User lacks read/write permissions
        # Common on Linux where serial ports require dialout/uucp group membership
        if "permission" in error_str or "access" in error_str:
            result = TestResult.failure_result(
                error_type="permission",
                message="Permission denied\n\n"
                "On Linux/macOS, try:\n"
                f"  sudo haniwers-v1 port test {device}\n\n"
                "Or add your user to the dialout/uucp group (permanent solution)",
            )
            logger.error(result.format_for_display())
            return result

        # Port busy: Another process is using the port
        # Can happen if DAQ is already running, or another serial terminal is open
        elif "busy" in error_str or "in use" in error_str:
            result = TestResult.failure_result(
                error_type="port_busy",
                message="Port is already in use\n\n"
                "Try:\n"
                "  - Close other programs using this port\n"
                "  - Check if another haniwers process is running\n"
                "  - Restart if necessary",
            )
            logger.error(result.format_for_display())
            return result

        # Port not found: Device path doesn't exist in filesystem
        # Common when device is unplugged or path is misspelled
        # On macOS, port names can change when reconnecting USB devices
        elif (
            "not found" in error_str or "does not exist" in error_str or "no such file" in error_str
        ):
            result = TestResult.failure_result(
                error_type="port_not_found",
                message=f"Device not found: {device}\n\n"
                "Possible causes:\n"
                "  - Device has been unplugged\n"
                "  - Wrong device path\n"
                "  - Device name has changed\n\n"
                "Run 'haniwers-v1 port list' to see available ports",
            )
            logger.error(result.format_for_display())
            return result

        # Unknown error: Unexpected SerialException not matching above patterns
        # This catch-all ensures all errors are handled gracefully
        else:
            result = TestResult.failure_result(
                error_type="unknown", message=f"Unexpected serial error: {e}"
            )
            logger.error(result.format_for_display())
            return result
