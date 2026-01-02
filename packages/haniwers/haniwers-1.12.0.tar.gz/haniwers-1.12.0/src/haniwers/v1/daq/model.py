"""Data structures for cosmic ray detector measurements.

What is this module?
    This module defines how detector measurements are stored and shared between
    different parts of the system. Each measurement from the OSECHI detector is
    called an "event" - it's one snapshot of all sensor readings at one moment.

Key event types:
    1. RawEvent: Exactly what the detector sent (7 sensor values + timestamp)
       - Direct from hardware
       - No processing or filtering
       - Used for archival and reproducibility

    2. MockEvent: Simulated detector data for testing
       - Generated from CSV files during development
       - Has extra timing parameters (speed, jitter)
       - Lets developers test without hardware

    3. ProcessedEvent: Analyzed detector data (hit detection applied)
       - Shows which sensors detected cosmic rays (hits)
       - Includes analysis results (hit_type, etc.)
       - Used for scientific analysis

    4. HitEvent: Hit detection results for three sensors
    5. AdcEvent: Analog-to-digital converter values
    6. SlowEvent: Environmental data (temperature, pressure, humidity)
    7. GnssEvent: GPS location data (planned)

Why events are structured this way:
    - Easy to save to CSV files
    - Easy to load from CSV files
    - Can be serialized to strings and back
    - Type-safe with validation
    - Each event is immutable (doesn't change after creation)

Example workflow:
    1. Detector sends raw data → RawEvent created
    2. User applies thresholds → ProcessedEvent created
    3. ProcessedEvent saved to CSV file
    4. Later, CSV file loaded back into ProcessedEvent for analysis
"""

from dataclasses import dataclass
from pydantic import BaseModel, Field
import pendulum
from datetime import datetime

from haniwers.v1 import schema


@dataclass
class RawEvent:
    """One complete snapshot of all detector sensors at one moment.

    What is RawEvent?
        The exact data received from the OSECHI detector hardware. Nothing has
        been changed or processed - it's raw. Use this for archival and
        reproducibility (you can always re-analyze later).

    When to use RawEvent?
        - Storing detector data for future re-analysis
        - Debugging detector communication
        - Working with unprocessed measurements
        - Creating test data

    Data fields:
        time: When this measurement happened (timezone-aware timestamp)
        top: Sensor 1 reading (0-1023, measures cosmic ray detection)
        mid: Sensor 2 reading (0-1023)
        btm: Sensor 3 reading (0-1023)
        adc: Analog-to-digital converter value (typically 0-4095)
        tmp: Temperature in °C (example: 24.5)
        atm: Atmospheric pressure in Pa (example: 10020.5)
        hmd: Humidity in % (example: 34.5)

    Example workflow:
        1. Detector sends: "10 5 0 823 24.5 10020.5 34.5"
        2. RawEvent created: RawEvent.from_serial(line, timestamp)
        3. Store or process: event.to_list() saves to CSV

    Serialization:
        - to_serial(): "10 5 0 823 24.5 10020.5 34.5" (without timestamp)
        - to_list(): ["2025-10-19T14:23:45", "10", "5", ...] (with timestamp)
        - from_serial(): Parse detector output
        - from_list(): Parse CSV file
    """

    time: pendulum.DateTime
    top: int
    mid: int
    btm: int
    adc: int
    tmp: float
    atm: float
    hmd: float

    def _format_fields(self) -> list[str]:
        """Internal helper: Convert sensor readings to text strings.

        This is a private helper method (starts with _). Use to_serial() or
        to_list() instead for normal usage.
        """
        fields = [
            str(self.top),
            str(self.mid),
            str(self.btm),
            str(self.adc),
            f"{self.tmp:.2f}",
            f"{self.atm:.2f}",
            f"{self.hmd:.2f}",
        ]
        return fields

    def to_serial(self) -> str:
        """Convert event to the format the detector outputs (space-separated).

        What this does:
            Creates a string that looks exactly like what the OSECHI detector
            sends over the serial port (USB cable).

        Returns:
            str: "top mid btm adc tmp atm hmd" (timestamp not included)

        Example:

        ```python
        event = RawEvent(...)
        serial_string = event.to_serial()
        # Output: "10 5 0 823 24.50 10020.50 34.50"
        ```

        When to use:
            - Debugging detector output
            - Writing detector data to serial log
            - Comparing with actual detector output
        """
        fields = self._format_fields()
        return (" ").join(fields)

    def to_list(self) -> list[str]:
        """Convert event to a list of text values (for saving to CSV).

        What this does:
            Creates a list with the timestamp first, then all 7 sensor values.
            This format is perfect for saving to CSV files.

        Returns:
            list[str]: ["timestamp", "top", "mid", "btm", "adc", "tmp", "atm", "hmd"]

        Example:

        ```python
        event = RawEvent(...)
        row = event.to_list()
        # Output: ["2025-10-19T14:23:45+09:00", "10", "5", "0", "823", "24.50", "10020.50", "34.50"]

        # Save to CSV:
        csv_writer.writerow(row)
        ```

        When to use:
            - Saving events to CSV files
            - Creating pandas DataFrames from events
            - Any case where you need a list of values
        """
        fields = self._format_fields()
        time = self.time.to_iso8601_string()
        return [time] + fields

    @classmethod
    def _from_values(cls, time: pendulum.DateTime, values: list[str]) -> "RawEvent":
        """Internal helper: Create RawEvent from timestamp and 7 sensor values.

        This is a private method (starts with _). Use from_serial() or from_list()
        instead for normal usage. Those methods handle parsing and validation.

        Args:
            time: The measurement timestamp (timezone-aware)
            values: List of 7 strings: [top, mid, btm, adc, tmp, atm, hmd]

        Returns:
            RawEvent: A new RawEvent object with parsed values

        Raises:
            ValueError: If values list doesn't have exactly 7 items
            ValueError: If any value can't be converted to its expected type
        """
        if (len(values)) != 7:
            msg = f"Expected 7 values, got {len(values)}: {values}"
            raise ValueError(msg)

        return cls(
            time=time,
            top=int(values[0]),
            mid=int(values[1]),
            btm=int(values[2]),
            adc=int(values[3]),
            tmp=float(values[4]),
            atm=float(values[5]),
            hmd=float(values[6]),
        )

    @classmethod
    def from_serial(cls, line: str, time: pendulum.DateTime) -> "RawEvent | None":
        """Parse detector output and create a RawEvent.

        What this does:
            Takes a line of detector output (space-separated values) and
            converts it into a RawEvent object with a timestamp.

            Empty or corrupted lines are skipped gracefully (returns None instead
            of raising an exception). This allows data collection to continue even
            when the detector sends malformed data.

        Args:
            line: Space-separated detector output
                  Example: "10 5 0 823 24.5 10020.5 34.5"
                  Empty lines or corrupted data are silently skipped
            time: Timestamp to assign to this event (timezone-aware)

        Returns:
            RawEvent | None:
                - RawEvent: Successfully parsed valid detector data
                - None: Empty line or invalid data (skipped gracefully)

        Example:

        ```python
        from haniwers.v1.daq.device import Device
        import pendulum

        device = Device(config)
        device.connect()

        # Read line from detector
        line = device.readline()  # "10 5 0 823 24.5 10020.5 34.5"

        # Create RawEvent (None if empty/invalid)
        timestamp = pendulum.now()
        event = RawEvent.from_serial(line, timestamp)

        if event is not None:
            # Save to CSV only if valid
            row = event.to_list()
            csv_writer.writerow(row)
        ```

        When to use:
            - Reading real detector output
            - Processing detector logs
            - Converting detector strings to events

        Note:
            Invalid lines are silently skipped. Caller should handle None returns
            to avoid writing corrupted data to output files.
        """
        values = line.strip().split()
        if len(values) != 7:
            # Silently skip empty or malformed lines
            return None

        try:
            return cls._from_values(time, values)
        except (ValueError, TypeError):
            # Skip lines with non-numeric values or conversion errors
            return None

    @classmethod
    def from_list(cls, values: list[str]) -> "RawEvent":
        """Parse a CSV row and create a RawEvent.

        What this does:
            Takes a row from a CSV file (with timestamp) and converts it
            into a RawEvent object.

        Args:
            values: List of 8 strings: [timestamp, top, mid, btm, adc, tmp, atm, hmd]
                   Usually from CSV or pandas DataFrame row

        Returns:
            RawEvent: A new RawEvent object with parsed values

        Raises:
            ValueError: If timestamp can't be parsed or wrong number of values

        Example:

        ```python
        import csv
        import pendulum

        # Read from CSV file
        with open("detector_data.csv") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row

            for row in reader:
                # row = ["2025-10-19T14:23:45", "10", "5", "0", "823", "24.5", "10020.5", "34.5"]
                event = RawEvent.from_list(row)
                print(event)
        ```

        When to use:
            - Loading events from CSV files
            - Processing pandas DataFrames
            - Re-analyzing saved detector data
        """
        time = pendulum.parse(values[0])
        return cls._from_values(time, values[1:])

    @classmethod
    def header(cls) -> list[str]:
        """Get the column names for CSV files.

        What this does:
            Returns the names that should be in the first row of a CSV file
            when saving RawEvents. Uses schema.RAW_COLUMNS for consistency.

        Returns:
            list[str]: Column names from schema.RAW_COLUMNS
            Example: ["timestamp", "top", "mid", "btm", "adc", "tmp", "atm", "hmd"]

        Example:

        ```python
        import csv

        events = [RawEvent(...), RawEvent(...), ...]

        with open("detector_data.csv", "w") as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow(RawEvent.header())

            # Write data rows
            for event in events:
                writer.writerow(event.to_list())
        ```

        When to use:
            - Creating CSV files from detector data
            - Loading CSV files with proper headers
        """
        return schema.RAW_COLUMNS


class MockEvent(BaseModel):
    """Simulated detector data for testing without real hardware.

    What is MockEvent?
        A RawEvent that also has timing parameters. Used when testing code
        without access to the real OSECHI detector. Usually loaded from
        CSV test data files.

    When to use?
        - Developing and testing analysis code
        - Teaching students without detector access
        - Reproducing bugs from saved data
        - Unit testing DAQ processing

    Data fields:
        raw: The sensor measurements (from RawEvent)
        deltaT: Time between measurements in seconds (default: 1.0)
        jitter: Random timing variation in seconds (default: 0.0)
        speed: Playback speed multiplier (default: 1.0, 2.0 = twice as fast)

    Example:

    ```python
    # Load mock data from CSV file
    with open("test_data.csv") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            # Convert CSV row to RawEvent first
            raw_event = RawEvent.from_list(row)

            # Wrap in MockEvent with timing parameters
            mock_event = MockEvent(
                raw=raw_event,
                deltaT=1.0,
                jitter=0.05,
                speed=1.0
            )
            print(f"Mock event at {mock_event.raw.time}")
    ```
    """

    raw: RawEvent
    deltaT: float = 1.0
    jitter: float = 0.0
    speed: float = 1.0

    model_config = {"arbitrary_types_allowed": True}

    def to_serial(self) -> str:
        """Convert to detector output format (space-separated string)."""
        return self.raw.to_serial()

    @classmethod
    def _from_values(
        cls,
        time: pendulum.DateTime,
        values: list[str],
        *,
        deltaT: float,
        jitter: float,
        speed: float,
    ) -> "MockEvent":
        """Deserialize the RawEvent from values.

        Internal method.
        Please see `from_serial` or `from_list` for usage.

        :Returns:
        - `RawEvent`: The deserialized RawEvent instance

        :Raises:
        - `ValueError`: if the number of fields is not 7.
        """
        if (len(values)) != 7:
            msg = f"Expected 7 values, got {len(values)}: {values}"
            raise ValueError(msg)

        raw_event = RawEvent._from_values(time, values)

        return cls(
            raw=raw_event,
            deltaT=deltaT,
            jitter=jitter,
            speed=speed,
        )

    @classmethod
    def from_list(cls, values: list[str], *, deltaT: float, jitter: float, speed: float):
        """Deserialize a MockEvent from a list of strings (with timestamp).

        :Example:
        Create single mocked event.
        ```python
        mocked_event = MockEvent.from_list(values, deltaT=1.0, jitter=0.05, speed=1.0)
        ```

        :Example:
        Create list of mocked events from dataframe.
        ```python
        mocked_events = [
            MockEvents.from_list(row, deltaT=1.0, jitter=0.05, speed=1.0) for row in df.values.tolist()
        ]
        ```

        """
        time = pendulum.parse(values[0])
        return cls._from_values(time, values[1:], deltaT=deltaT, jitter=jitter, speed=speed)


class HitEvent(BaseModel):
    top: bool
    mid: bool
    btm: bool
    hit_type: int = Field(ge=0, le=7)

    @classmethod
    def from_raw_event(cls, raw: RawEvent, threshold: dict[str, int]) -> "HitEvent":
        pass


class AdcEvent(BaseModel):
    top: int
    mid: int
    btm: int

    @classmethod
    def from_raw_event(cls, raw: RawEvent, threshold: dict[str, int]) -> "AdcEvent":
        pass


class SlowEvent(BaseModel):
    tmp: float
    atm: float
    hmd: float

    @classmethod
    def from_raw_event(cls, raw: RawEvent) -> "SlowEvent":
        pass


class GnssEvent(BaseModel):
    latitude: float
    longitute: float
    altitude: float | None
    timestamp: datetime | None

    @classmethod
    def from_raw_event(cls, raw: RawEvent) -> "GnssEvent":
        pass


class ProcessedEvent(BaseModel):
    """Detector data after applying hit detection analysis.

    What is ProcessedEvent?
        Answers the question: "Did any cosmic rays hit the detector?"
        A ProcessedEvent takes a RawEvent and applies thresholds to determine
        which sensors detected cosmic rays (hits). This is the data scientists
        use for analysis.

    When to use?
        - Scientific analysis of cosmic ray data
        - Plotting detector efficiency
        - Finding patterns in cosmic ray activity
        - Publishing research results

    Data fields:
        time: When measurement happened
        top_hit: Did top sensor detect cosmic ray? (True/False)
        mid_hit: Did middle sensor detect cosmic ray? (True/False)
        btm_hit: Did bottom sensor detect cosmic ray? (True/False)
        hit_type: Combined hit pattern (0-7, binary encoding of three sensors)
                  Example: 5 means (top=1, mid=0, btm=1)
        adc: Analog-to-digital converter value (pulse height)
        tmp, atm, hmd: Environmental data

    How hit detection works:
        RawEvent has: top=10, mid=5, btm=0
        With threshold: top=8, mid=3, btm=2

        Result:
        - top_hit = (10 > 8) = True
        - mid_hit = (5 > 3) = True
        - btm_hit = (0 > 2) = False
        - hit_type = 0b110 = 6 (binary: top|mid|btm)

    Example workflow:

    ```python
    # Load raw detector data
    raw_event = RawEvent(...)

    # Apply threshold detection
    thresholds = {"top": 8, "mid": 3, "btm": 2}
    processed = ProcessedEvent.from_raw_event(raw_event, thresholds)

    # Now ready for analysis
    if processed.top_hit or processed.mid_hit or processed.btm_hit:
        print(f"Cosmic ray detected at {processed.time}")
    ```

    Serialization:
        - to_list(): ["timestamp", "1", "1", "0", "6", ...] (for CSV)
        - from_list(): Parse CSV back to ProcessedEvent
        - header(): Get column names
    """

    time: pendulum.DateTime
    top_hit: bool
    mid_hit: bool
    btm_hit: bool
    hit_type: int = Field(ge=0, le=7)
    adc: int
    tmp: float
    atm: float
    hmd: float
    raw: RawEvent | None = None

    model_config = {"arbitrary_types_allowed": True}

    def to_list(self) -> list[str]:
        """Convert event to a list of text values (for saving to CSV).

        What this does:
            Creates a list with timestamp and all analysis results.
            Perfect for saving ProcessedEvents to CSV files.

        Returns:
            list[str]: ["timestamp", top_hit, mid_hit, btm_hit, hit_type, adc, tmp, atm, hmd]
                      Booleans converted to "0" or "1"

        Example:

        ```python
        processed = ProcessedEvent.from_raw_event(raw_event, thresholds)
        row = processed.to_list()

        # Save to CSV:
        csv_writer.writerow(row)
        # Output: ["2025-10-19T14:23:45", "1", "1", "0", "6", "823", "24.50", "10020.50", "34.50"]
        ```
        """
        return [
            self.time.to_iso8601_string(),
            str(int(self.top_hit)),
            str(int(self.mid_hit)),
            str(int(self.btm_hit)),
            str(self.hit_type),
            str(self.adc),
            f"{self.tmp:.2f}",
            f"{self.atm:.2f}",
            f"{self.hmd:.2f}",
        ]

    @classmethod
    def from_list(cls, values: list[str]) -> "ProcessedEvent":
        """Parse a CSV row and create a ProcessedEvent.

        What this does:
            Takes a row from a CSV file (analysis results) and converts it
            into a ProcessedEvent object.

        Args:
            values: List of 9 strings: [timestamp, top_hit, mid_hit, btm_hit, hit_type, adc, tmp, atm, hmd]
                   Usually from CSV or pandas DataFrame row

        Returns:
            ProcessedEvent: A new ProcessedEvent object with parsed values

        Raises:
            ValueError: If timestamp can't be parsed or wrong number of values

        Example:

        ```python
        import csv
        import pendulum

        # Load processed events from CSV file
        with open("analysis_results.csv") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row

            for row in reader:
                # row = ["2025-10-19T14:23:45", "1", "1", "0", "6", "823", "24.50", "10020.50", "34.50"]
                event = ProcessedEvent.from_list(row)

                # Analyze results
                cosmic_ray_count = sum([event.top_hit, event.mid_hit, event.btm_hit])
                print(f"Cosmic ray hit {cosmic_ray_count} sensors")
        ```

        When to use:
            - Loading results from previous analysis
            - Creating plots from saved events
            - Re-analyzing published data
        """
        return cls(
            time=pendulum.parse(values[0]),
            top_hit=bool(int(values[1])),
            mid_hit=bool(int(values[2])),
            btm_hit=bool(int(values[3])),
            hit_type=int(values[4]),
            adc=int(values[5]),
            tmp=float(values[6]),
            atm=float(values[7]),
            hmd=float(values[8]),
        )

    @classmethod
    def header(cls) -> list[str]:
        """Get the column names for CSV files.

        What this does:
            Returns the names for the first row of a CSV file when saving
            ProcessedEvents. Uses schema.PROCESSED_COLUMNS for consistency.

        Returns:
            list[str]: Column names from schema.PROCESSED_COLUMNS
            Example: ["datetime", "top", "mid", "btm", "adc", "tmp", "atm", "hmd", "hit_top", "hit_mid", "hit_btm", "hit_type"]

        Example:

        ```python
        import csv

        processed_events = [ProcessedEvent(...), ProcessedEvent(...), ...]

        with open("analysis_results.csv", "w") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(ProcessedEvent.header())

            # Write data
            for event in processed_events:
                writer.writerow(event.to_list())
        ```
        """
        return schema.PROCESSED_COLUMNS

    @classmethod
    def from_raw_event(cls, raw: RawEvent, threshold: dict[str, int]) -> "ProcessedEvent":
        """Apply hit detection to raw detector data.

        What this does:
            Takes raw sensor readings and compares each against a threshold.
            Sensors that read above threshold are marked as "hits" (cosmic rays detected).
            The hit_type field encodes which sensors had hits.

        Args:
            raw: Raw detector measurements with 7 sensor values
            threshold: Threshold values like {"top": 8, "mid": 3, "btm": 2}

        Returns:
            ProcessedEvent: Results showing which sensors detected cosmic rays

        How it works (example):
            raw:      {"top": 10, "mid": 5, "btm": 0, ...}
            threshold: {"top": 8, "mid": 3, "btm": 2}

            Process:
            - top_hit = (10 > 8) = True
            - mid_hit = (5 > 3) = True
            - btm_hit = (0 > 2) = False
            - hit_type = 0b110 = 6

        Example:

        ```python
        from haniwers.v1.daq.device import Device
        import pendulum

        # Connect and read from detector
        device = Device(config)
        device.connect()
        line = device.readline()

        # Create RawEvent
        timestamp = pendulum.now()
        raw_event = RawEvent.from_serial(line, timestamp)

        # Apply threshold detection
        thresholds = {"top": 8, "mid": 3, "btm": 2}
        processed = ProcessedEvent.from_raw_event(raw_event, thresholds)

        # Check results
        if processed.top_hit or processed.mid_hit or processed.btm_hit:
            print(f"✓ Cosmic ray detected! Hit type: {processed.hit_type}")
        else:
            print("✗ No cosmic ray")

        device.disconnect()
        ```

        When to use:
            - Processing real detector data
            - Analyzing cosmic ray events
            - Creating publishable results
        """
        top_hit = raw.top > threshold["top"]
        mid_hit = raw.mid > threshold["mid"]
        btm_hit = raw.btm > threshold["btm"]
        hit_type = (top_hit << 2) | (mid_hit << 1) | btm_hit

        return cls(
            time=raw.time,
            top_hit=top_hit,
            mid_hit=mid_hit,
            btm_hit=btm_hit,
            hit_type=hit_type,
            adc=raw.adc,
            tmp=raw.tmp,
            atm=raw.atm,
            hmd=raw.hmd,
            raw=raw,
        )
