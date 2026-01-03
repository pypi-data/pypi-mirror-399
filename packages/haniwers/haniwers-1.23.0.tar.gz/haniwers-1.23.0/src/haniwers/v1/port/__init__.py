"""Port management package.

Provides port enumeration, connectivity testing, and ESP32 diagnostics.

Public API:
    - list_available_ports(): Enumerate serial ports on the system
    - test_port_connectivity(): Test connection to OSECHI detector
    - diagnose_esp32(): Run ESP32 diagnostics using esptool

Data classes:
    - DetectorData: OSECHI detector sensor readings
    - FlashInfo: ESP32 flash chip information
    - TestResult: Port connectivity test results

Example usage:

    # List available ports
    from haniwers.v1.port import list_available_ports
    ports = list_available_ports()

    # Test port connectivity
    from haniwers.v1.port import test_port_connectivity
    result = test_port_connectivity("/dev/ttyUSB0")
    if result.success:
        print(f"Connected in {result.response_time:.2f}s")
        print(f"Data: {result.data_sample}")

    # Run ESP32 diagnostics
    from haniwers.v1.port import diagnose_esp32
    diagnose_esp32("/dev/ttyUSB0")

    # Access data classes
    from haniwers.v1.port import DetectorData, FlashInfo, TestResult
    data = DetectorData.from_line("2 0 0 936 27.37 100594.35 41.43")
"""

from .diagnoser import diagnose_esp32
from .lister import detect_port, list_available_ports
from .model import DetectorData, FlashInfo, TestResult
from .tester import test_port_connectivity

__all__ = [
    "detect_port",
    "list_available_ports",
    "test_port_connectivity",
    "diagnose_esp32",
    "DetectorData",
    "FlashInfo",
    "TestResult",
]
