"""MAC address retrieval and formatting utilities for device identification.

⚠️  DEPRECATED: This module is deprecated. Use Device.get_mac_address() instead.

What is MAC address handling?
    ESP32 devices have unique hardware identifiers (MAC addresses) that can be used
    to track and identify specific detectors. This module provides two functions:
    1. get_device_mac() - DEPRECATED: Use Device.get_mac_address() instead
    2. format_mac_address() - Still used for converting MAC formats

Why do we need this?
    - Device identification: Each ESP32 has a unique MAC address (AA:BB:CC:DD:EE:FF)
    - Filesystem safety: MAC addresses need conversion to filesystem-safe names
    - Consistent format: Standardize to lowercase hex without colons (aabbccddeeef)
    - Data tracking: Enables tracing which detector produced which dataset

MIGRATION GUIDE:
    Old code (DEPRECATED):
    ```python
    from haniwers.v1.helpers.mac_address import get_device_mac, format_mac_address
    mac = get_device_mac("/dev/cu.usbserial-140")
    ```

    New code (RECOMMENDED):
    ```python
    from haniwers.v1.daq.device import Device
    device = Device(config)
    device.connect()  # Automatically retrieves MAC via GET_MAC_ADDRESS
    mac = device.mac_address
    ```

Example:
    ```python
    from haniwers.v1.helpers.mac_address import get_device_mac, format_mac_address

    # Get MAC address from device on port
    mac = get_device_mac("/dev/cu.usbserial-140")
    if mac:
        print(f"Device MAC: {mac}")  # Output: "aabbccddeeef"
    else:
        print("Could not retrieve MAC address")

    # Format a MAC address for use in filenames
    formatted = format_mac_address("AA:BB:CC:DD:EE:FF")
    print(formatted)  # Output: "aabbccddeeef"

    # Handle invalid inputs gracefully
    result = format_mac_address(None)
    print(result)  # Output: "unknown"
    ```
"""

from typing import Optional
import serial
from serial.tools import list_ports


def get_device_mac(port: str) -> Optional[str]:
    """Retrieve MAC address from ESP32 device connected on specified port.

    ⚠️  DEPRECATED: Use Device.get_mac_address() instead.

    Connects to the device and retrieves its hardware MAC address.
    This can be used to uniquely identify which physical detector
    produced a dataset.

    Args:
        port (str): Serial port path (e.g., "/dev/cu.usbserial-140")
                   Must be a valid and accessible port

    Returns:
        str | None: MAC address in colon-separated format ("AA:BB:CC:DD:EE:FF")
                   Returns None if unable to retrieve MAC address

    How it works:
        1. Enumerate serial ports looking for the specified port
        2. Try to retrieve MAC address from port metadata
        3. Fall back to sending GET_MAC command via serial (legacy)
        4. Return raw MAC address or None on failure

    When to use:
        DEPRECATED - Use Device.get_mac_address() instead.
        This function is kept for backward compatibility only.

    Note:
        This function opens and closes a serial connection.
        Device must be powered on and connected to the specified port.

    Example:
        ```python
        # DEPRECATED: Get MAC from connected device
        # mac = get_device_mac("/dev/cu.usbserial-140")

        # RECOMMENDED: Use Device class instead
        from haniwers.v1.daq.device import Device
        device = Device(config)
        device.connect()  # Automatically retrieves MAC
        mac = device.mac_address
        ```
    """
    import warnings

    warnings.warn(
        "get_device_mac() is deprecated. Use Device.get_mac_address() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    try:
        # Try to get MAC from port metadata first (fast path)
        for port_info in list_ports.comports():
            if port_info.device == port and port_info.serial_number:
                # Some UART bridges encode MAC in serial number
                return port_info.serial_number

        # Fall back: try to query device via serial command
        # This requires opening a connection to the device
        try:
            ser = serial.Serial(port=port, baudrate=115200, timeout=2.0)
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            # Try standard esptool protocol: GET_MAC command
            # Device responds with colon-separated MAC
            ser.write(b"GET_MAC\n")
            response = ser.readline().decode("utf-8", errors="ignore").strip()
            ser.close()

            # Validate response format (should be "XX:XX:XX:XX:XX:XX")
            if response and response.count(":") == 5:
                return response
        except (serial.SerialException, UnicodeDecodeError):
            # Serial communication failed or invalid response encoding
            pass

        # Unable to retrieve MAC
        return None

    except Exception:
        # Catch unexpected exceptions (e.g., from list_ports enumeration)
        # to ensure function never raises - returns None as fallback for robustness
        return None


def format_mac_address(mac: str | None) -> str:
    """Convert MAC address to filesystem-safe filename format.

    ⚠️  DEPRECATED: This function is deprecated. Device.mac_address_formatted from
    Device.get_mac_address() handles formatting automatically.

    What this does:
        Takes a MAC address in any format and converts it to lowercase hex
        without colons, suitable for use in filenames. Returns fallback
        identifier "unknown" for invalid inputs.

    Args:
        mac (str | None): MAC address in various formats
            - Standard format: "AA:BB:CC:DD:EE:FF" (colon-separated)
            - Alternative format: "AABBCCDDEEEF" (no colons)
            - None or empty: Returns "unknown" fallback
            - Any other format: Attempts to extract hex digits

    Returns:
        str: Formatted MAC address
            - Valid MAC: 12 lowercase hex characters (e.g., "aabbccddeeef")
            - Invalid/None/Empty: "unknown" (fallback identifier)

    How it works:
        1. Check for None or empty string → return "unknown"
        2. Remove all colons and hyphens from input
        3. Convert remaining characters to lowercase
        4. Validate result has 12 hex characters
        5. Return formatted MAC or "unknown" if invalid

    When to use:
        DEPRECATED - Use Device.mac_address_formatted instead.
        This function is kept for backward compatibility only.

    Raises:
        Nothing (always returns valid string, never raises exceptions)

    Examples:
        ```python
        # Standard colon-separated format (common from esptool)
        format_mac_address("AA:BB:CC:DD:EE:FF")
        # Returns: "aabbccddeeef"

        # Hyphen-separated format
        format_mac_address("AA-BB-CC-DD-EE-FF")
        # Returns: "aabbccddeeef"

        # Already formatted
        format_mac_address("aabbccddeeef")
        # Returns: "aabbccddeeef"

        # Uppercase input (converts to lowercase)
        format_mac_address("AA:BB:CC:DD:EE:FF")
        # Returns: "aabbccddeeef"

        # Invalid inputs return fallback
        format_mac_address(None)
        # Returns: "unknown"

        format_mac_address("")
        # Returns: "unknown"

        format_mac_address("invalid")
        # Returns: "unknown"
        ```
    """
    import warnings

    warnings.warn(
        "format_mac_address() is deprecated. Use Device.mac_address_formatted instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Handle None or empty input
    if not mac:
        return "unknown"

    # Remove separators (colons, hyphens) and convert to lowercase
    cleaned = mac.replace(":", "").replace("-", "").lower()

    # Validate: must be 12 hex characters
    if len(cleaned) != 12:
        return "unknown"

    # Validate: all characters must be hexadecimal digits
    try:
        int(cleaned, 16)  # Try to parse as hexadecimal
    except ValueError:
        # Not valid hex
        return "unknown"

    return cleaned
