"""Device settings option group."""

from typing import Optional

import typer


class DeviceOptions:
    """Device settings option group.

    Contains options for configuring serial port communication with the
    OSECHI cosmic ray detector.
    """

    port = typer.Option(
        None,
        "--port",
        help="Serial port path for OSECHI detector (e.g., /dev/ttyUSB0, COM3). "
        "Use 'haniwers-v1 port list' to find available ports.",
        rich_help_panel="Device Settings",
    )
    """Serial port path.

    Specifies which serial port to communicate with the OSECHI detector. This
    overrides the port specified in the configuration file.

    Examples:
    - /dev/ttyUSB0 (Linux)
    - /dev/cu.usbserial-140 (macOS)
    - COM3 (Windows)

    Tip: Use 'haniwers-v1 port list' to discover available ports.

    Type: Optional[str]
    Default: None (use config file value)
    """

    baudrate = typer.Option(
        115200,
        "--baudrate",
        help="Serial communication baud rate (bits/second). "
        "Standard values: 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200.",
        rich_help_panel="Device Settings",
    )
    """Serial baud rate.

    Sets the communication speed for serial port. Must be one of the standard serial
    port baud rates: 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400,
    57600, or 115200. This overrides the baudrate in the configuration file.

    Type: int
    Default: 115200 (standard modern serial communication speed)
    Allowed values: Standard serial port baud rates only
    """

    timeout = typer.Option(
        None,
        "--timeout",
        min=0.1,
        help="Serial read timeout in seconds (e.g., 1.0, 2.0).",
        rich_help_panel="Device Settings",
    )
    """Serial read timeout.

    Specifies how long to wait for a response from the OSECHI detector before
    timing out. Typical values: 1.0-5.0 seconds.

    Type: Optional[float]
    Default: None (use config file value)
    Minimum: 0.1 seconds
    """

    device_label = typer.Option(
        None,
        "--device-label",
        help="Device identifier label for logging and documentation.",
        rich_help_panel="Device Settings",
    )
    """Device identifier label.

    Human-readable label to identify this detector in logs and documentation.
    Useful when multiple detectors are in use. Example: "detector_001_main_lab".

    Type: Optional[str]
    Default: None (use config file value)
    """
