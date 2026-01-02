"""Custom exception classes for port management.

Provides domain-specific exceptions for clear error handling
and actionable error messages.
"""


class PortPermissionError(Exception):
    """Raised when user lacks permission to access serial port.

    Common on Linux where serial ports require dialout/uucp group membership.
    """

    pass


class PortBusyError(Exception):
    """Raised when another process is already using the port.

    Can happen if DAQ is already running, or another serial terminal is open.
    """

    pass


class PortNotFoundError(Exception):
    """Raised when device path doesn't exist.

    Common when device is unplugged or path is misspelled.
    On macOS, port names can change when reconnecting USB devices.
    """

    pass


class InvalidDetectorDataError(Exception):
    """Raised when received data doesn't match OSECHI detector format.

    The data should be 7 space-separated fields:
    top mid btm adc tmp atm hmd
    """

    pass
