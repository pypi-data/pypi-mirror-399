"""ESP32 flash chip diagnostics using esptool.

Provides functions to connect to ESP32 devices and diagnose
flash chip information for troubleshooting.
"""

import io
import re
from contextlib import redirect_stdout
from typing import Optional

import esptool

from haniwers.v1.log.logger import logger
from haniwers.v1.port.model import FlashInfo


def diagnose_esp32(
    device: str,
    baudrate: int = 115200,
    flash_id: bool = False,
    chip_id: bool = False,
    summary: bool = False,
) -> None:
    """Diagnose ESP32 flash chip using esptool.

    Connects to ESP32 device and retrieves flash chip information.
    Useful for troubleshooting firmware upload issues.

    Args:
        device: Path to serial device (e.g., /dev/ttyUSB0, COM3)
        baudrate: Baud rate in bits per second (default: 115200)
        flash_id: Show only flash chip ID information
        chip_id: Show only chip ID information
        summary: Show only chip summary information

    Raises:
        Exception: If connection fails or unexpected error occurs

    Example:
        >>> diagnose_esp32("/dev/ttyUSB0")
    """
    logger.info(f"Diagnosing ESP32 on {device}...")

    # Determine which commands to run
    show_all = not (flash_id or chip_id or summary)

    try:
        # Connect to ESP32 chip
        # esptool.detect_chip() returns an ESPLoader instance
        logger.debug(f"Connecting to chip at {device} (baud: {baudrate})...")
        esp = esptool.detect_chip(port=device, baud=baudrate, connect_attempts=3)

        logger.info(f"✓ Connected to {esp.get_chip_description()}")

        # Run stub flasher for faster and more reliable operations
        # The stub provides better flash access and higher baud rates
        logger.debug("Uploading stub flasher...")
        esp = esp.run_stub()

        # Capture esptool output
        # esptool prints to stdout, so we redirect it to capture the output
        output_buffer = io.StringIO()

        # Show flash ID information
        if show_all or flash_id:
            logger.info("\n=== Flash Memory Information ===")
            with redirect_stdout(output_buffer):
                esptool.flash_id(esp)
            flash_output = output_buffer.getvalue()
            print(flash_output)

            # Parse and validate flash info
            flash_info = _parse_flash_output(flash_output)
            diagnosis = flash_info.get_diagnosis()
            logger.info(f"\n{diagnosis}")

        # Show chip ID information
        if show_all or chip_id:
            logger.info("\n=== Chip Information ===")
            logger.info(f"Chip type: {esp.get_chip_description()}")
            logger.info(f"Chip features: {', '.join(esp.get_chip_features())}")
            logger.info(f"Crystal frequency: {esp.get_crystal_freq()}MHz")
            logger.info(f"MAC address: {':'.join(f'{b:02x}' for b in esp.read_mac())}")

        # Show summary (efuse)
        if show_all or summary:
            logger.info("\n=== Chip Summary ===")
            logger.info("(Summary output not yet implemented)")

    except esptool.FatalError as e:
        logger.error(f"✗ esptool error: {e}")
        logger.error("\nPossible causes:")
        logger.error("  - Device not connected")
        logger.error("  - Wrong port or baud rate")
        logger.error("  - OSECHI power switch is OFF")
        raise
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        raise


def _parse_flash_output(output: str) -> FlashInfo:
    """Parse esptool flash_id output into FlashInfo.

    Args:
        output: Raw output from esptool.flash_id()

    Returns:
        FlashInfo instance with parsed fields

    The output format looks like:
        Manufacturer: 20
        Device: 4017
        Detected flash size: 8MB
        Flash voltage set by a strapping pin: 3.3V
    """
    info = FlashInfo()

    # Parse manufacturer ID (hex)
    if match := re.search(r"Manufacturer:\s+([0-9a-fA-F]+)", output):
        info.manufacturer = match.group(1)

    # Parse device ID (hex)
    if match := re.search(r"Device:\s+([0-9a-fA-F]+)", output):
        info.device = match.group(1)

    # Parse flash size
    if match := re.search(r"Detected flash size:\s+(\S+)", output):
        info.flash_size = match.group(1)

    # Parse flash voltage
    if match := re.search(r"Flash voltage.*?:\s+([\d.]+V)", output):
        info.flash_voltage = match.group(1)

    return info
