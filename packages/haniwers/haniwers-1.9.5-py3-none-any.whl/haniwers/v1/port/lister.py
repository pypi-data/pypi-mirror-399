"""Serial port enumeration and discovery.

Provides functions to list available serial ports and identify
likely OSECHI detector connections through UART bridge detection.
"""

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
        elif port.description and "UART" in port.description.upper():
            logger.info(f"Please use '{port.device}' as your device path")
            break

    return ports
