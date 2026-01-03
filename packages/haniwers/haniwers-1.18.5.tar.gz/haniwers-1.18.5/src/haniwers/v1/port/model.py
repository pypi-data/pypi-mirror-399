"""Data structures representing port management information.

Contains the core data classes for port testing and diagnostics:
- DetectorData: OSECHI detector sensor readings
- FlashInfo: ESP32 flash chip information
- TestResult: Port connectivity test results
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DetectorData:
    """One line of data from OSECHI detector.

    Format: "top mid btm adc tmp atm hmd"
    Example: "2 0 0 936 27.37 100594.35 41.43"

    Fields:
        top: Top layer hit count (0-10)
        mid: Middle layer hit count (0-10)
        btm: Bottom layer hit count (0-10)
        adc: ADC value (0-1023, 10-bit)
        tmp: Temperature in °C (15-35)
        atm: Atmospheric pressure in Pa (95000-105000)
        hmd: Humidity in % (0-100)
    """

    top: int
    mid: int
    btm: int
    adc: int
    tmp: float
    atm: float
    hmd: float

    @classmethod
    def from_line(cls, line: str) -> "DetectorData":
        """Parse a line of detector data.

        Args:
            line: Space-separated values string

        Returns:
            DetectorData instance

        Raises:
            ValueError: If line format is invalid

        Example:
            >>> data = DetectorData.from_line("2 0 0 936 27.37 100594.35 41.43")
            >>> data.tmp
            27.37
        """
        # OSECHI detector sends data as space-separated ASCII text over serial
        # Format: "top mid btm adc tmp atm hmd" (7 fields)
        # Example: "2 0 0 936 27.37 100594.35 41.43"
        fields = line.strip().split()

        # Validate field count before attempting to parse
        # This catches malformed data early with a helpful error message
        if len(fields) != 7:
            raise ValueError(
                f"Expected 7 fields, got {len(fields)}. Valid format: 'top mid btm adc tmp atm hmd'"
            )

        try:
            # Parse each field with appropriate type conversion:
            # - Fields 0-3 (top, mid, btm, adc): Integer event counts and ADC value
            # - Fields 4-6 (tmp, atm, hmd): Float sensor readings (temperature, pressure, humidity)
            return cls(
                top=int(fields[0]),  # Top scintillator layer hit count
                mid=int(fields[1]),  # Middle scintillator layer hit count
                btm=int(fields[2]),  # Bottom scintillator layer hit count
                adc=int(fields[3]),  # Analog-to-Digital Converter value (0-1023)
                tmp=float(fields[4]),  # Temperature in Celsius
                atm=float(fields[5]),  # Atmospheric pressure in Pascals
                hmd=float(fields[6]),  # Relative humidity percentage
            )
        except (ValueError, IndexError) as e:
            # ValueError: Type conversion failed (e.g., "abc" to int)
            # IndexError: Should not happen due to field count check, but catch as safety
            raise ValueError(f"Failed to parse detector data: {e}")

    def is_valid(self) -> bool:
        """Check if values are within expected ranges.

        Returns:
            True if all values are reasonable, False otherwise
        """
        # Validate sensor readings against physically reasonable ranges
        # These ranges help detect:
        # - Sensor malfunctions (e.g., tmp=0.0 indicates BME280 not connected)
        # - Data corruption during serial transmission
        # - Wrong device type (non-OSECHI detector)
        return (
            0 <= self.top <= 10  # Scintillator hit counts (0-10 per sampling period)
            and 0 <= self.mid <= 10
            and 0 <= self.btm <= 10
            and 0 <= self.adc <= 1023  # 10-bit ADC range
            and 15.0 <= self.tmp <= 35.0  # Room temperature range (°C)
            and 95000.0 <= self.atm <= 105000.0  # Sea level pressure range (Pa)
            and 0.0 <= self.hmd <= 100.0  # Relative humidity percentage
        )


@dataclass
class FlashInfo:
    """ESP32 flash chip information from esptool.

    Stores flash chip details obtained via esptool flash_id command.

    Fields:
        manufacturer: Flash chip manufacturer ID (hex string)
        device: Flash chip device ID (hex string)
        flash_size: Detected flash size (e.g., "8MB")
        flash_voltage: Flash voltage setting (e.g., "3.3V")
        chip_type: ESP32 chip variant (e.g., "ESP32-D0WD-V3")
        crystal: Crystal frequency (e.g., "40MHz")
        mac_address: MAC address of the chip
    """

    manufacturer: Optional[str] = None
    device: Optional[str] = None
    flash_size: Optional[str] = None
    flash_voltage: Optional[str] = None
    chip_type: Optional[str] = None
    crystal: Optional[str] = None
    mac_address: Optional[str] = None

    def is_healthy(self) -> bool:
        """Check if flash chip communication is successful.

        Returns:
            True if flash chip responds normally, False otherwise

        A manufacturer ID of "ff" indicates communication failure.
        """
        return self.manufacturer is not None and self.manufacturer.lower() != "ff"

    def get_diagnosis(self) -> str:
        """Get diagnostic message based on flash chip status.

        Returns:
            Human-readable diagnostic message with recommendations
        """
        if self.is_healthy():
            return "✓ Flash chip communication successful"

        # Flash chip communication failed
        messages = ["✗ Flash chip communication failed"]

        if self.manufacturer == "ff" and self.device == "ffff":
            messages.append("\nPossible causes:")
            messages.append("  - OSECHI power switch is OFF")
            messages.append("  - Device not powered")
            messages.append("  - Hardware connection issue")

        if self.flash_voltage == "1.8V":
            messages.append("\nFlash voltage is 1.8V (should be 3.3V)")
            messages.append("  - Check OSECHI power switch")
            messages.append("  - GPIO12 may be floating")

        return "\n".join(messages)


@dataclass
class TestResult:
    """Result of a port connectivity test.

    Stores whether the test succeeded and why.

    Fields:
        success: True if test passed, False otherwise
        message: Human-readable result message
        response_time: Time to receive data in seconds (optional)
        data_sample: First line of data received (optional)
        error_type: Error category if failed (optional)
    """

    success: bool
    message: str
    response_time: Optional[float] = None
    data_sample: Optional[str] = None
    error_type: Optional[str] = None

    @classmethod
    def success_result(cls, response_time: float, data_sample: str) -> "TestResult":
        """Create a successful test result.

        Args:
            response_time: Time taken to receive data (seconds)
            data_sample: First line of valid data

        Returns:
            TestResult with success=True
        """
        return cls(
            success=True,
            message=f"✓ Port test successful (response in {response_time:.2f}s)",
            response_time=response_time,
            data_sample=data_sample,
        )

    @classmethod
    def failure_result(cls, error_type: str, message: str) -> "TestResult":
        """Create a failed test result.

        Args:
            error_type: Category of error (timeout, permission, etc.)
            message: Human-readable error explanation

        Returns:
            TestResult with success=False
        """
        return cls(success=False, message=f"✗ {message}", error_type=error_type)

    def format_for_display(self) -> str:
        """Format result for user-friendly display.

        Returns:
            Multi-line formatted string with all relevant info
        """
        lines = [self.message]

        if self.success and self.data_sample:
            lines.append(f"  Data sample: {self.data_sample}")

        if self.error_type:
            lines.append(f"  Error type: {self.error_type}")

        return "\n".join(lines)
