"""Serial port enumeration and discovery.

Provides functions to list available serial ports and identify
likely OSECHI detector connections through UART bridge detection.
"""

from typing import Optional

from serial.tools import list_ports

from haniwers.v1.log.logger import logger


def list_available_ports() -> list:
    """List all available serial ports with device information.

    Enumerates serial ports on the system and identifies likely OSECHI
    detector connections by detecting common UART-to-USB bridge chips
    (FTDI, Silicon Labs, Prolific).

    Returns:
        List of serial port objects with device information

    Example:
        >>> ports = list_available_ports()
        >>> for port in ports:
        ...     print(f"{port.device}: {port.description}")
    """
    # Get all ports
    ports = list_ports.comports()

    if not ports:
        logger.warning("No ports found")
        return ports

    # Display results
    logger.info(f"Found {len(ports)} port{'s' if len(ports) > 1 else ''}")

    for i, port in enumerate(ports):
        description = port.description if port.description != "n/a" else "Unknown"
        manufacturer = f" ({port.manufacturer})" if port.manufacturer else ""
        logger.info(f"Port{i}: {port.device} - {description}{manufacturer}")

    # Suggest UART bridge if found
    # UART bridges are the most common way to connect OSECHI detectors
    # to modern computers (which typically lack native serial ports)
    for port in ports:
        if port.manufacturer in ["FTDI", "Silicon Labs", "Prolific"]:
            logger.info(f"Please use '{port.device}' as your device path")
            break
        if port.description and "UART" in port.description.upper():
            logger.info(f"Please use '{port.device}' as your device path")
            break

    return ports


def detect_port() -> Optional[str]:
    """Automatically detect OSECHI detector serial port.

    Searches available serial ports and identifies likely OSECHI detector
    connections by detecting common UART-to-USB bridge chips (FTDI,
    Silicon Labs, Prolific).

    Returns:
        str: Device path if OSECHI detector found (e.g., "/dev/ttyUSB0")
        None: If no likely detector port found

    Priority (in order):
        1. Ports with manufacturer "FTDI", "Silicon Labs", or "Prolific"
        2. Ports with "UART" in description

    What to test:
        - Return device path when UART bridge found
        - Return None when no ports available
        - Prefer FTDI/SiliconLabs/Prolific over generic UART description
        - Log available ports when auto-detection fails

    Example:
        ```python
        from haniwers.v1.port import detect_port

        port = detect_port()
        if port:
            print(f"Found OSECHI at: {port}")
        else:
            print("No OSECHI detector found")
        ```

    Beginner note:
        Use this function to automatically find your OSECHI detector without
        needing to specify the port path manually.
    """
    log = logger.bind(context="detect_port")
    ports = list_ports.comports()

    if not ports:
        log.warning("No serial ports available on this system")
        return None

    log.debug(f"Scanning {len(ports)} port{'s' if len(ports) > 1 else ''} for OSECHI detector")

    # First priority: Known UART bridge manufacturers
    uart_manufacturers = ["FTDI", "Silicon Labs", "Prolific"]
    for port in ports:
        if port.manufacturer and port.manufacturer in uart_manufacturers:
            log.info(f"Detected OSECHI at {port.device} ({port.manufacturer} bridge)")
            return port.device

    # Second priority: Ports with "UART" in description
    for port in ports:
        if port.description and "UART" in port.description.upper():
            log.info(f"Detected possible OSECHI at {port.device} (UART in description)")
            return port.device

    # No suitable port found - display available ports for user selection
    log.warning("Could not auto-detect OSECHI detector port")
    log.info(f"Available ports ({len(ports)}):")
    for port in ports:
        description = port.description if port.description != "n/a" else "Unknown"
        manufacturer = f" ({port.manufacturer})" if port.manufacturer else ""
        log.info(f"  {port.device}: {description}{manufacturer}")
    log.info("Please specify port manually or check: haniwers-v1 port list")
    return None
