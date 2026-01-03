"""Port management commands for haniwers v1 CLI.

Provides commands for discovering and testing serial ports.
Helps users identify which port connects to the OSECHI detector.

Commands:
    list: Show all available serial ports
    test: Test connectivity to OSECHI detector
    diagnose: Diagnose ESP32 flash chip using esptool

This module acts as a thin CLI layer that orchestrates port management
functionality defined in haniwers.v1.port modules.
"""

from typing import Optional

import typer

from haniwers.v1.cli.options import DeviceOptions
from haniwers.v1.log.logger import logger as base_logger
from haniwers.v1.port import (
    diagnose_esp32,
    list_available_ports,
    test_port_connectivity,
)

# Bind context for all port operations
logger = base_logger.bind(context="cli.port")

app = typer.Typer(help="Serial port management")


@app.command()
def list() -> None:
    """List all available serial ports.

    Shows device paths, descriptions, and USB information
    for all serial ports on the system.

    Example:
        $ haniwers-v1 port list
    """
    try:
        list_available_ports()
    except PermissionError:
        logger.error("Permission denied: Cannot access serial ports")
        logger.info("Try running with sudo or add user to dialout/uucp group")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Failed to enumerate serial ports: {e}")
        raise typer.Exit(code=1)


@app.command(name="test")
def test_connectivity(
    device: str = typer.Argument(..., help="Device path to test (e.g., /dev/ttyUSB0, COM3)"),
    # Device communication options (using centralized DeviceOptions with port-specific defaults)
    baudrate: Optional[int] = DeviceOptions.baudrate,
    timeout: Optional[float] = DeviceOptions.timeout,
) -> None:
    """Test connectivity to OSECHI detector.

    Opens the specified port and attempts to read detector data
    to verify it's the correct device.

    Args:
        device: Path to serial device (e.g., /dev/ttyUSB0, COM3)
        baudrate: Baud rate in bits per second (default: 115200)
        timeout: Read timeout in seconds (default: 5.0)

    Example:
        $ haniwers-v1 port test /dev/ttyUSB0
        $ haniwers-v1 port test COM3 --timeout 10
        $ haniwers-v1 port test /dev/ttyUSB0 --baudrate 9600
        $ haniwers-v1 port test /dev/ttyUSB0 --baudrate 9600 --timeout 10
    """
    # Use sensible port-test defaults if not specified
    # Port testing is a standalone utility, so defaults are different from DAQ commands
    port_baudrate = baudrate if baudrate is not None else 115200
    port_timeout = timeout if timeout is not None else 5.0

    result = test_port_connectivity(
        device=device,
        baudrate=port_baudrate,
        timeout=port_timeout,
    )

    if not result.success:
        raise typer.Exit(code=1 if result.error_type != "permission" else 2)


@app.command()
def diagnose(
    device: str = typer.Argument(..., help="Device path to diagnose (e.g., /dev/ttyUSB0, COM3)"),
    baudrate: int = typer.Option(115200, help="Baud rate for communication"),
    flash_id: bool = typer.Option(False, "--flash-id", help="Show flash chip ID only"),
    chip_id: bool = typer.Option(False, "--chip-id", help="Show chip ID only"),
    summary: bool = typer.Option(False, "--summary", help="Show chip summary only"),
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

    Example:
        $ haniwers-v1 port diagnose /dev/ttyUSB0
        $ haniwers-v1 port diagnose /dev/ttyUSB0 --flash-id
        $ haniwers-v1 port diagnose COM3 --baudrate 9600
    """
    try:
        diagnose_esp32(
            device=device,
            baudrate=baudrate,
            flash_id=flash_id,
            chip_id=chip_id,
            summary=summary,
        )
    except Exception as e:
        logger.error(f"✗ Diagnosis failed: {e}")
        raise typer.Exit(code=1)
