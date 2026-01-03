"""Serial device communication for cosmic ray detector.

What is this module?
    This module handles communication with the OSECHI detector over a serial
    port (USB cable). It provides two ways to talk to the detector:
    1. Low-level functions: Direct access to serial port operations
    2. High-level Device class: Recommended for most users (easier and safer)

Why use this?
    The detector sends data through a USB cable. This module makes it easy to:
    - Connect to the detector
    - Send commands to the detector
    - Read data back from the detector
    - Handle errors gracefully

When to use Device class vs functions?
    Use Device class (recommended):
    - Most common use case
    - Handles connection lifecycle automatically
    - Built-in logging for debugging
    - Cleaner code

    Use low-level functions:
    - When you need fine-grained control
    - Building higher-level abstractions
    - Advanced troubleshooting

Example with Device class (recommended):

```python
from haniwers.v1.config.model import DeviceConfig
from haniwers.v1.daq.device import Device

# Create configuration
config = DeviceConfig(
    label="detector",
    port="/dev/ttyUSB0",
    baudrate=115200,
    timeout=1.0
)

# Use Device class
device = Device(config)
device.connect()
device.write("READ")
line = device.readline()
device.disconnect()
```

Example with low-level functions:

```python
from haniwers.v1.daq.device import connect, write, readline, disconnect

device = connect(config)
write(device, "READ")
line = readline(device)
disconnect(device)
```
"""

import serial
from contextlib import contextmanager
from haniwers.v1.config.model import DeviceConfig
from haniwers.v1.helpers.mac_address import format_mac_address, get_device_mac
from haniwers.v1.port import detect_port

from haniwers.v1.log.logger import logger as base_logger

"""
Module level functions
"""


def connect(config: DeviceConfig) -> serial.Serial:
    """Open a serial connection to the detector.

    What this does:
        Opens a USB serial connection to the detector using the settings from
        your configuration (port, speed, timeout).

    Args:
        config (DeviceConfig): Connection settings (port, baudrate, timeout)

    Returns:
        serial.Serial: An open connection object. Use this to send commands
        and read data from the detector.

    Raises:
        serial.SerialException: If the port doesn't exist or is already in use

    Beginner tip:
        For most use cases, use the Device class instead of this function.
        The Device class handles connection lifecycle and is safer:

        ```python
        device = Device(config)
        device.connect()  # Use this pattern instead
        ```

    Example:

    ```python
    from haniwers.v1.config.model import DeviceConfig
    from haniwers.v1.daq.device import connect

    config = DeviceConfig(
        port="/dev/ttyUSB0",
        baudrate=115200,
        timeout=1.0
    )
    device = connect(config)
    ```
    """
    import time

    ser = serial.Serial(
        port=config.port,
        baudrate=config.baudrate,
        timeout=config.timeout,
    )

    # Wait for device to stabilize after connection
    # This allows the device to complete any initialization/boot sequence
    time.sleep(0.5)

    # Clear any buffered data (boot messages, etc) from the device
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    return ser


def readline(device: serial.Serial) -> str:
    """Read one line of data from the detector.

    What this does:
        Waits for data from the detector, reads one complete line, and converts
        it from binary data into readable text (a Python string).

    Args:
        device (serial.Serial): An open connection from connect() or Device.connect()

    Returns:
        str: The data as text, with extra whitespace removed

    Raises:
        UnicodeDecodeError: If detector sends non-UTF-8 data (rare, indicates hardware issue)
        serial.SerialException: If the connection is broken

    How it works:
        1. Waits for data from detector
        2. Reads until it sees a newline character (\\n)
        3. Converts bytes to text (UTF-8 decoding)
        4. Removes leading/trailing whitespace
        5. Returns the text string

    Beginner tip:
        Use the Device class which handles this for you:

        ```python
        device = Device(config)
        device.connect()
        line = device.readline()  # Much safer!
        ```

    Example:

    ```python
    from haniwers.v1.daq.device import readline

    line = readline(device)
    print(f"Received: {line}")
    # Output: "1 2 3 4 5 6 7"
    ```
    """
    return device.readline().decode("utf-8").strip()


def write(device: serial.Serial, data: str | bytes) -> int:
    """Send a command or data to the detector.

    What this does:
        Takes your message and sends it to the detector through the serial
        connection. Converts text to binary as needed.

    Args:
        device (serial.Serial): An open connection from connect()
        data (str | bytes): The message to send
            - str: Text command (e.g., "READ", "THRESHOLD 300")
              Automatically converted to bytes using UTF-8
            - bytes: Raw binary data (e.g., b"\\x01\\x14\\x60")
              Sent as-is without conversion

    Returns:
        int: Number of bytes successfully sent to the detector

    How it works:
        1. If data is text: Convert to bytes using UTF-8 encoding
        2. If data is bytes: Send as-is
        3. Send all bytes to the detector
        4. Return how many bytes were sent

    Beginner tip:
        Use the Device class for safety:

        ```python
        device = Device(config)
        device.connect()
        bytes_sent = device.write("READ")
        ```

    Example:

    ```python
    from haniwers.v1.daq.device import write

    # Send text command
    bytes_sent = write(device, "READ")
    print(f"Sent {bytes_sent} bytes")

    # Send raw bytes
    bytes_sent = write(device, b"\\x01\\x14\\x60")
    ```
    """
    if isinstance(data, bytes):
        written_bytes = device.write(data)
    else:
        written_bytes = device.write(data.encode("utf-8"))
    return written_bytes


def flush(device: serial.Serial) -> None:
    """Clear any leftover data in the connection buffers.

    What this does:
        Removes any stale data that's sitting in the connection pipes (buffers).
        Useful when switching between different commands or operations.

    Args:
        device (serial.Serial): An open connection from connect()

    Why use this:
        If detector sends old data but you don't read it, it stays in the buffer.
        Next time you read(), you might get old data instead of new data.
        Call flush() to clean things out before starting a new operation.

    Example:

    ```python
    device = Device(config)
    device.connect()
    device.flush()  # Clear any old data
    device.write("READ")
    line = device.readline()  # Gets fresh data
    ```
    """

    device.reset_input_buffer()
    device.reset_output_buffer()


def disconnect(device: serial.Serial) -> None:
    """Close the connection to the detector.

    What this does:
        Properly shuts down the serial connection, releasing the USB port
        so other programs can use it.

    Args:
        device (serial.Serial): An open connection from connect()

    Why use this:
        Always close connections when done. If you don't:
        - Port stays locked (other programs can't use detector)
        - Memory resources aren't released
        - Connection may stay open in background

    Example:

    ```python
    device = Device(config)
    device.connect()
    device.write("READ")
    line = device.readline()
    device.disconnect()  # Always close when done!
    ```
    """
    if device.is_open:
        device.close()


def is_available(config: DeviceConfig) -> bool:
    """Check if the detector is ready to connect.

    What this does:
        Tests if the USB port exists and isn't already in use by another program.
        Does NOT communicate with the detector, just checks port availability.

    Args:
        config (DeviceConfig): Connection settings (port, baudrate, timeout)

    Returns:
        bool: True if port is available and ready to connect, False otherwise

    When to use:
        - Before connecting: Make sure port is free
        - Debugging: Figure out why connect() fails
        - Finding detectors: Check which ports have connected detectors

    Example:

    ```python
    from haniwers.v1.config.model import DeviceConfig
    from haniwers.v1.daq.device import is_available

    config = DeviceConfig(
        label="detector",
        port="/dev/ttyUSB0",
        baudrate=115200,
        timeout=1.0
    )

    if is_available(config):
        print("✓ Detector is ready to use")
        device = Device(config)
        device.connect()
    else:
        print("✗ Port not available. Check:")
        print("  - Is detector plugged in?")
        print("  - Is another program using this port?")
        print("  - Try different port: haniwers-v1 port list")
    ```
    """
    try:
        test = serial.Serial(port=config.port, baudrate=config.baudrate, timeout=config.timeout)
        if test.is_open:
            test.close()
        return True
    except serial.SerialException:
        return False


class Device:
    """Easy-to-use interface for talking to the cosmic ray detector.

    What is Device?
        The recommended way to communicate with the OSECHI detector.
        It handles all the connection details so you focus on your work.

    Key features:
        ✓ Simple: Just call connect(), write(), readline(), disconnect()
        ✓ Safe: Handles errors and edge cases automatically
        ✓ Logged: All operations are recorded for debugging
        ✓ Tested: Proven pattern used throughout haniwers

    Life cycle:
        1. Create: Device(config)
        2. Connect: device.connect()
        3. Use: device.write(), device.readline()
        4. Disconnect: device.disconnect()

    Example (recommended pattern):

        ```python
        from haniwers.v1.config.model import DeviceConfig
        from haniwers.v1.daq.device import Device

        # Setup
        config = DeviceConfig(
            label="detector",
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=1.0
        )

        # Connect to detector
        device = Device(config)
        device.connect()

        # Talk to detector
        device.write("READ")
        line = device.readline()
        print(f"Received: {line}")

        # Cleanup
        device.disconnect()
        ```

    Advanced features:
        - device.flush(): Clear stale data from buffers
        - device.is_available(): Check if port is ready before connecting
        - device.with_timeout(sec): Temporarily change read timeout
    """

    def __init__(self, config: DeviceConfig):
        """Create a Device object with connection settings.

        What this does:
            Stores your detector configuration settings but does NOT connect yet.
            Call device.connect() afterward to actually open the connection.
            If port is "auto", the device port will be auto-detected at connect time.

        Args:
            config (DeviceConfig): Connection settings (port, baudrate, timeout)
                                   Use port="auto" for automatic port detection

        Example (explicit port):

        ```python
        from haniwers.v1.config.model import DeviceConfig
        from haniwers.v1.daq.device import Device

        config = DeviceConfig(
            label="detector",
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=1.0
        )

        # Create device object (connection not open yet)
        device = Device(config)

        # Now connect
        device.connect()
        ```

        Example (auto-detection):

        ```python
        config = DeviceConfig(
            label="detector",
            port="auto",  # Will auto-detect at connect time
            baudrate=115200,
            timeout=1.0
        )

        device = Device(config)
        device.connect()  # Port is detected here
        ```
        """
        self.config = config
        self.serial = None
        self.logger = base_logger.bind(context=self.__class__.__name__)

    def connect(self) -> None:
        """Open the USB connection to the detector.

        What this does:
            Opens the serial port and establishes communication with the detector.
            After this succeeds, you can use write() and readline() methods.
            If port is "auto", automatically detects the OSECHI port.

        Raises:
            RuntimeError: If the port doesn't exist, is in use, or detector not responding
            RuntimeError: If port="auto" and no OSECHI detector can be found

        Error tips:
            "Port not found": Wrong port number, detector not plugged in
            "Permission denied": Need to add user to dialout group (Linux)
            "Device busy": Another program is using this port
            "Could not auto-detect": No UART bridge detected, try manual port

        Example (explicit port):

        ```python
        device = Device(config)
        try:
            device.connect()
            print("✓ Connected to detector")
        except RuntimeError as e:
            print(f"✗ Connection failed: {e}")
        ```

        Example (auto-detection):

        ```python
        device = Device(config)  # config.port = "auto"
        try:
            device.connect()  # Auto-detects port
            print(f"✓ Connected to detector at {device.config.port}")
        except RuntimeError as e:
            print(f"✗ Auto-detection failed: {e}")
        ```
        """
        # Handle auto-detection
        port = self.config.port
        if port == "auto":
            detected_port = detect_port()
            if detected_port is None:
                msg = "Could not auto-detect OSECHI detector port. Try: haniwers-v1 port list"
                self.logger.error(msg)
                raise RuntimeError(msg)
            port = detected_port
            self.logger.info(f"Auto-detected port: {port}")
            # Update config with detected port for consistency
            self.config.port = port

        self.logger.debug(f"Attempting to connect to {port}")
        try:
            self.serial = connect(self.config)
        except serial.SerialException as e:
            msg = f"Failed to connect to device at {port}: {e}"
            self.logger.error(msg)
            raise RuntimeError(msg) from e

    def readline(self) -> str:
        """Read one line of data from the detector.

        What this does:
            Waits for the detector to send data, reads one complete line,
            and returns it as readable text.

        Returns:
            str: The data received from detector, cleaned up (whitespace removed)

        Raises:
            serial.SerialException: If connection is broken
            UnicodeDecodeError: If detector sends corrupted data (very rare)

        How to use:
            Call write() first to send a command, then readline() to get the response

        Example:

        ```python
        device = Device(config)
        device.connect()

        # Send command
        device.write("READ")

        # Read response
        line = device.readline()
        print(f"Received: {line}")
        # Output: "1 2 3 4 5 6 7"

        device.disconnect()
        ```
        """
        line = readline(self.serial)
        self.logger.opt(lazy=True).debug(f"Read line: {line}")
        return line

    def write(self, data: str | bytes) -> int:
        """Send a command or data to the detector.

        What this does:
            Takes your message and sends it to the detector over the USB connection.
            Automatically converts text to binary format if needed.

        Args:
            data (str | bytes): The message to send to detector
                - str: Text command (e.g., "READ", "THRESHOLD 300")
                  Automatically converted to bytes
                - bytes: Raw binary data (e.g., b"\\x01\\x14\\x60")
                  Sent as-is

        Returns:
            int: Number of bytes successfully sent to detector

        Raises:
            serial.SerialTimeoutException: If detector not responding (timeout)

        Example:

        ```python
        device = Device(config)
        device.connect()

        # Send text command
        bytes_written = device.write("READ")
        print(f"Sent {bytes_written} bytes")

        # Send raw bytes
        bytes_written = device.write(b"\\x01\\x14\\x60")

        device.disconnect()
        ```
        """
        written_bytes = write(self.serial, data)
        if isinstance(data, bytes):
            self.logger.debug(f"Wrote to device: {data.hex()} ({len(data)} bytes)")
        else:
            self.logger.debug(f"Wrote to device: {data}")
        return written_bytes

    def flush(self) -> None:
        """Clear any leftover data in the connection buffers.

        What this does:
            Removes stale data that may be sitting in the USB connection pipes.
            Useful when switching between different commands or operations.

        When to use:
            Before starting a new sequence of reads/writes to ensure clean state
            After errors to clear corrupted data
            Between different command sequences

        Example:

        ```python
        device = Device(config)
        device.connect()

        # Clear any stale data
        device.flush()

        # Now read fresh data
        device.write("READ")
        line = device.readline()
        ```
        """
        flush(self.serial)
        self.logger.debug("Flushed device buffers")

    def disconnect(self) -> None:
        """Close the USB connection to the detector.

        What this does:
            Properly shuts down the serial connection and releases the USB port
            so other programs can use it if needed.

        Important:
            Always call disconnect() when done, especially in scripts that run
            multiple times. If you don't, the port stays locked and connection
            resources aren't released.

        Example:

        ```python
        device = Device(config)
        device.connect()

        try:
            device.write("READ")
            line = device.readline()
        finally:
            # Always close, even if there's an error
            device.disconnect()
        ```

        Better pattern (using context manager):

        ```python
        # Future enhancement: Device may support 'with' statement
        # For now, always use try/finally as shown above
        ```
        """
        disconnect(self.serial)
        self.logger.info("Disconnected from device")

    @contextmanager
    def with_timeout(self, sec: float):
        """Temporarily change the read timeout for one operation.

        What this does:
            Changes how long readline() will wait for data from the detector,
            but only for the code inside the 'with' block. After the block
            exits, the timeout goes back to the original value.

        Args:
            sec (float): New timeout in seconds (e.g., 1.0, 2.5, 0.5)

        When to use:
            Some detector operations are slow and need longer timeout
            Some operations are fast and you want to detect missing data quickly
            Debugging timing issues

        Example:

        ```python
        device = Device(config)
        device.connect()

        # Normal timeout (from config, usually 1.0 seconds)
        line = device.readline()

        # For a slow operation, increase timeout
        with device.with_timeout(5.0):
            slow_line = device.readline()

        # Back to normal timeout
        fast_line = device.readline()

        device.disconnect()
        ```
        """
        original_timeout = self.serial.timeout
        self.serial.timeout = sec
        try:
            yield self
        finally:
            self.serial.timeout = original_timeout

    def is_available(self) -> bool:
        """Check if the detector is ready to connect (port exists and is free).

        What this does:
            Tests if the USB port exists and isn't already in use by another
            program. Does NOT actually connect to the detector, just checks
            that the port is available.

        Returns:
            bool: True if port is available, False if port doesn't exist or is busy

        When to use:
            Before calling connect() to catch problems early
            Debugging connection issues
            Checking if detector is plugged in (gives indirect confirmation)

        Example:

        ```python
        device = Device(config)

        if device.is_available():
            print("✓ Port is available, connecting...")
            device.connect()
        else:
            print("✗ Port not available")
            print("  Check:")
            print("  - Is detector plugged in?")
            print("  - Is another program using this port?")
            print("  - Use: haniwers-v1 port list")
        ```
        """
        available = is_available(self.config)
        if not available:
            self.logger.debug(f"Device {self.config.port} is not available")
        return available

    def get_mac_address(self) -> str:
        """Retrieve ESP32 MAC address from connected device.

        What this does:
            Reads the MAC address from the connected ESP32 device.
            Returns the address in filesystem-safe format (lowercase hex, no colons)
            or falls back to "unknown" if retrieval fails.

        Returns:
            str: MAC address as 12 lowercase hex chars (e.g., 'aabbccddeeef')
                 or 'unknown' if retrieval fails

        How it works:
            1. Retrieves raw MAC address from device via get_device_mac()
            2. Formats to filesystem-safe format using format_mac_address()
            3. Catches exceptions and returns "unknown" on any error
            4. Logs debug/warning messages for troubleshooting

        When to use:
            - After device.connect() to get unique device identifier
            - During DAQ startup to embed in filenames
            - For device tracking and traceability

        Raises:
            Nothing (always returns valid string, never raises exceptions)

        Examples:

        ```python
        device = Device(config)
        device.connect()

        # Get MAC address for filename
        mac = device.get_mac_address()
        print(f"Device MAC: {mac}")
        # Output: "Device MAC: aabbccddeeef" or "Device MAC: unknown"

        device.disconnect()
        ```

        Error cases handled:
            - Port not available: Returns "unknown", logs warning
            - Device not responding: Returns "unknown", logs warning
            - Timeout: Returns "unknown", logs warning
            - Invalid MAC format: Returns "unknown", logs warning
        """
        try:
            # Use get_device_mac() helper to retrieve raw MAC address
            raw_mac = get_device_mac(self.config.port)

            if raw_mac:
                # Format to filesystem-safe format
                formatted_mac = format_mac_address(raw_mac)
                self.logger.debug(f"Retrieved MAC address from {self.config.port}: {formatted_mac}")
                return formatted_mac
            else:
                self.logger.debug(f"Could not retrieve MAC address from {self.config.port}")
                return "unknown"

        except Exception as e:
            self.logger.warning(
                f"Unexpected error retrieving MAC address from {self.config.port}: {type(e).__name__}: {e}"
            )
            return "unknown"
