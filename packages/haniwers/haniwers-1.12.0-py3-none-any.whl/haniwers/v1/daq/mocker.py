"""Fake detector for testing software without real hardware.

What is this module?
    This module simulates an OSECHI cosmic ray detector when you don't have
    the real hardware. Perfect for development, testing, and teaching.

Two ways to get fake detector data:

1. Mocker: Replays recorded data from a CSV file
   - Use real detector measurements saved from previous experiments
   - Control playback speed (1x, 2x, 10x, etc.)
   - Add timing variation (jitter) for realism
   - Loop the data or play once
   - Perfect for reproducible testing

2. RandomMocker: Generates random synthetic data
   - Creates fake detector measurements with realistic ranges
   - No CSV file needed
   - Useful for stress testing (fast playback)
   - Great when you have no recorded data available

Why use fake detectors?
   ✓ Develop code without hardware (saves money, time)
   ✓ Test code reliably (same data every time)
   ✓ Teach students without hardware (democratizes learning)
   ✓ Debug code issues (can replay specific scenarios)
   ✓ Benchmark code performance (synthetic data is fast)

Key interfaces:
   Both Mocker and RandomMocker implement the same interface as real detectors:
   - readline(): Get next measurement
   - write(): Fake send commands (no-op)
   - flush(): Fake buffer clear (no-op)
   - close(): Stop the fake detector
   - is_open: Boolean flag (True/False)

Example (Mocker - replay recorded data):

```python
from pathlib import Path
from haniwers.v1.config.model import MockerConfig
from haniwers.v1.daq.mocker import Mocker

config = MockerConfig(
    csv_path=Path("recorded_data.csv"),
    shuffle=False,      # Don't randomize order
    speed=2.0,          # 2x faster replay
    jitter=0.05,        # Add tiny timing variation
    loop=True           # Repeat forever
)

mocker = Mocker(config, seed=42)
for i in range(5):
    line = mocker.readline()
    print(f"Event {i}: {line.decode()}")
```

Example (RandomMocker - generate random data):

```python
from haniwers.v1.config.model import MockerConfig
from haniwers.v1.daq.mocker import RandomMocker

config = MockerConfig(speed=10.0)  # csv_path not needed
mocker = RandomMocker(config, seed=42)

for i in range(5):
    line = mocker.readline()
    print(f"Random event {i}: {line.decode()}")
```

When to use each:

Mocker:
    - Testing code with realistic data
    - Reproducing specific scenarios
    - CI/CD pipelines (deterministic testing)
    - Teaching with real examples

RandomMocker:
    - Stress testing (lots of data quickly)
    - Testing error handling
    - When you have no recorded data
    - Benchmarking performance
"""

import random
from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
from pathlib import Path
from time import sleep

import pandas as pd
import pendulum

from haniwers.v1.config.model import MockerConfig
from haniwers.v1.daq.model import MockEvent, RawEvent
from haniwers.v1.log.logger import logger as base_logger
from haniwers.v1 import schema

# Bind context for mocker module logging
log = base_logger.bind(context="mocker")


def load_events(path: Path, jitter: float, speed: float, shuffle: bool) -> list[MockEvent]:
    """Load recorded detector measurements from a CSV file.

    What this does:
        Reads a CSV file containing previous detector measurements and prepares
        them for playback with optional speed control and randomization.

    Args:
        path: Path to CSV file (e.g., "data/detector_run_001.csv")
        jitter: Timing variation in seconds (0.0 = exact, 0.1 = ±0.1s random)
        speed: Playback speed (1.0 = normal, 2.0 = twice as fast, 10.0 = 10x fast)
        shuffle: Mix up the event order randomly (True/False)

    Returns:
        List of MockEvent objects ready for playback with Mocker

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV format is wrong (missing columns, bad types, etc.)

    CSV file format:
        - No header row (just data)
        - Columns (in order): timestamp, top, mid, btm, adc, tmp, atm, hmd
        - timestamp: ISO8601 timestamp (e.g., "2025-10-19T14:23:45+09:00")
        - Numbers: integers for sensors, floats for environmental data

    How it works:
        1. Read all rows from CSV file
        2. For each row: Create a MockEvent with timing info
        3. Calculate time between events (deltaT)
        4. If shuffle=True: Randomize the order
        5. Return list of events

    Performance:
        - Fast: Loads 100K rows in <3 seconds
        - Memory: ~300-350 MB for 100K rows

    Example:

    ```python
    from pathlib import Path
    from haniwers.v1.daq.mocker import load_events

    # Load recorded data
    events = load_events(
        path=Path("data/detector_run_001.csv"),
        jitter=0.05,        # ±0.05s timing variation
        speed=2.0,          # Play back 2x faster
        shuffle=False       # Keep original order
    )

    print(f"Loaded {len(events)} events")
    # Output: Loaded 10000 events

    # Peek at first event
    first = events[0]
    print(f"First event: {first.raw.to_serial()}")
    # Output: First event: 5 2 8 512 25.43 100550.12 55.67
    ```

    When to use:
        - Testing code with real detector data
        - Reproducing specific measurement scenarios
        - Automated testing (same data every time)
    """
    log.debug(f"Reading CSV: {path}")

    # Validate file exists
    if not path.exists():
        log.error(f"CSV file not found: {path}")
        raise FileNotFoundError(f"CSV file not found: {path}")

    # Specify dtypes to optimize memory and speed
    dtype_spec = {
        "top": "int16",  # 0-10 range fits in int16
        "mid": "int16",
        "btm": "int16",
        "adc": "int16",  # 0-1024 fits in int16
        "tmp": "float32",  # float32 sufficient for sensor readings
        "atm": "float32",
        "hmd": "float32",
    }

    try:
        # Read CSV with optimizations
        names = RawEvent.header()
        timestamp = schema.RAW_COLUMNS[0]  # First column is the timestamp
        df = pd.read_csv(
            path,
            names=names,
            dtype=dtype_spec,
            parse_dates=[timestamp],
            engine="c",  # Use fast C parser (default)
        )
        log.debug(f"CSV read complete: {len(df)} rows")
    except Exception as e:
        log.error(f"Failed to read CSV: {e}")
        raise ValueError(f"Invalid CSV format: {e}")

    # Calculate time differences efficiently
    df["deltaT"] = df[timestamp].diff().dt.total_seconds().fillna(1.0)

    # Convert to MockEvent list with error handling
    events = []
    invalid_count = 0

    for idx, row in enumerate(df.to_dict("records")):
        try:
            values = [str(row[n]) for n in names]
            event = MockEvent.from_list(
                values,
                deltaT=float(row.get("deltaT", 1.0)),
                jitter=jitter,
                speed=speed,
            )
            events.append(event)
        except (ValueError, KeyError) as e:
            invalid_count += 1
            log.warning(f"Skipping invalid row {idx}: {e}")

    # Report results
    if invalid_count > 0:
        log.warning(
            f"Partial load: {len(events)} valid events, {invalid_count} invalid rows skipped"
        )

    if shuffle:
        random.shuffle(events)
        log.debug("Events shuffled")

    log.info(f"Loaded {len(events)} events from {path}")
    return events


def generate_fields() -> list[str]:
    """Generate one random fake detector measurement.

    What this does:
        Creates a single detector event with realistic random values.
        Similar to what the detector would send, but all values are random.

    Returns:
        List of 8 text values: [timestamp, top, mid, btm, adc, temp, pressure, humidity]
        Ready to be parsed into a RawEvent

    Value ranges (realistic for cosmic ray detector):
        - timestamp: Current time (when this function is called)
        - top sensor: 0-10 (cosmic ray signal)
        - mid sensor: 0-10 (cosmic ray signal)
        - btm sensor: 0-10 (cosmic ray signal)
        - adc: 0-1024 (pulse height)
        - temperature: 20-30 °C
        - pressure: 100500-100600 Pa (atmospheric)
        - humidity: 30-70 % (relative)

    Example:

    ```python
    from haniwers.v1.daq.mocker import generate_fields
    from haniwers.v1.daq.model import RawEvent

    # Generate random sensor values
    fields = generate_fields()
    print(fields)
    # Output: ['2025-10-19T14:23:45+09:00', '5', '2', '8', '512', '25.43', '100550.12', '55.67']

    # Convert to RawEvent
    event = RawEvent.from_list(fields)
    print(f"Sensor readings: top={event.top}, mid={event.mid}, btm={event.btm}")
    # Output: Sensor readings: top=5, mid=2, btm=8
    ```

    Note:
        This uses Python's global random state. For reproducible (deterministic)
        generation, use RandomMocker with a seed instead.

    When to use:
        - Quick testing with random data
        - Generating many events for stress testing
        - When exact reproducibility isn't important
    """
    return [
        pendulum.now().to_iso8601_string(),
        str(random.randint(0, 10)),
        str(random.randint(0, 10)),
        str(random.randint(0, 10)),
        str(random.randint(0, 1024)),
        f"{random.uniform(20, 30):.2f}",  # Temperature with 2 decimals
        f"{random.uniform(100500, 100600):.2f}",  # Atmospheric pressure - FIXED RANGE (100500-100600 Pa)
        f"{random.uniform(30, 70):.2f}",  # Humidity with 2 decimals
    ]


class BaseMocker(ABC):
    """Abstract base class for all mock serial devices.

    Provides the standard serial device interface (readline, write, flush, close)
    that real hardware implements. This ensures mock devices can be swapped in
    transparently.

    Attributes:
        config (MockerConfig): Device configuration
        csv_path (Optional[Path]): Path to CSV file (may be None for RandomMocker)
        shuffle (bool): Whether to shuffle events
        speed (float): Playback speed multiplier
        jitter (float): Timing jitter amount
        loop (bool): Whether to loop playback
        is_open (bool): Device state (True = open, False = closed)
    """

    def __init__(self, config: MockerConfig) -> None:
        """Initialize base mocker with configuration.

        Args:
            config: Mocker configuration object

        Postconditions:
            - self.is_open = True
            - Configuration values stored in instance attributes
            - self._response_queue initialized for threshold write responses
        """
        self.config = config
        self.csv_path = getattr(config, "csv_path")
        self.shuffle = getattr(config, "shuffle")
        self.speed = getattr(config, "speed")
        self.jitter = getattr(config, "jitter")
        self.loop = getattr(config, "loop")
        self.is_open = True
        self._response_queue: deque = (
            deque()
        )  # Internal queue for threshold write response simulation

    def set_next_response(self, response: str) -> None:
        """Queue response for next readline() call.

        What this does:
            When a threshold write operation needs to simulate a device response
            (like confirming the channel number), this method queues the response
            so the next readline() call will return it instead of detector data.

        Args:
            response: Response string to queue (e.g., "1" for channel 1 success, "dame" for rejection)

        Example:
            >>> mocker.set_next_response("1")
            >>> response = mocker.readline()  # Returns "1"

        Note:
            This is primarily used by threshold write operations to simulate device
            responses during testing with mock devices. Normal DAQ operations don't
            use this method.
        """
        self._response_queue.append(response)

    def connect(self) -> None:
        """Open the mock device (set is_open=True).

        What this does:
            Opens the mock device for reading. For mock devices, this just sets
            is_open=True. Compatible with Device.connect() interface.

        Raises:
            Nothing - mock devices always open successfully

        Example:
            >>> mocker = RandomMocker(config)
            >>> mocker.connect()  # Now ready to read
            >>> mocker.is_open
            True

        Note:
            Mock devices are automatically open after __init__, so this is often
            a no-op unless close() was called first. But it's provided for
            interface compatibility with Device.
        """
        self.is_open = True
        log.debug("Mock device opened")

    @abstractmethod
    def readline(self) -> bytes:
        """Read one line from the mock serial interface.

        Abstract method - must be implemented by subclasses.

        Returns:
            UTF-8 encoded bytes representing one event in serial format,
            or empty bytes (b"") if device is closed or no data available.

        Example:
            b"2 0 0 1136 27.37 100594.35 41.43"
        """
        pass

    def write(self, data: bytes) -> int:
        """Simulate writing data to the device.

        Mock devices don't actually write data, but this method provides
        compatibility with real serial device interface.

        Args:
            data: Bytes to "write" (ignored)

        Returns:
            Number of bytes "written" (always len(data))

        Example:
            >>> mocker.write(b"command")
            7
        """
        return len(data)

    def flush(self) -> None:
        """Simulate flushing the device buffer.

        Mock devices don't have buffers, but this method provides
        compatibility with real serial device interface.

        This is a no-op (does nothing).

        Example:
            >>> mocker.flush()
            # No effect
        """
        pass

    def disconnect(self) -> None:
        """Close the mock device.

        Sets is_open = False. Subsequent readline() calls will return empty string.

        Postconditions:
            - self.is_open = False
            - readline() returns ""

        Example:
            >>> mocker.disconnect()
            >>> mocker.readline()
            ''
        """
        log.info("Mock device closed")
        self.is_open = False

    def is_available(self) -> bool:
        """Check if the mock device is available (always True for mocks).

        What this does:
            Mock devices are always available (they don't depend on hardware).
            This method exists for compatibility with Device.is_available().

        Returns:
            bool: Always True (mock device is always available)

        Example:
            >>> mocker = RandomMocker(config)
            >>> mocker.is_available()
            True

        Note:
            Unlike Device which checks if a serial port exists, mock devices
            don't depend on hardware, so this always returns True.
        """
        return True

    @contextmanager
    def with_timeout(self, sec: float):
        """Context manager for temporary timeout change (no-op for mocks).

        What this does:
            For compatibility with Device.with_timeout(), but mock devices
            don't have real timeouts, so this is a no-op (does nothing).

        Args:
            sec (float): Timeout value (ignored for mock devices)

        Yields:
            self: The mocker instance (for use in with statement)

        Example:
            >>> mocker = RandomMocker(config)
            >>> with mocker.with_timeout(2.0):
            ...     line = mocker.readline()
            # Timeout doesn't affect mock device

        Note:
            Mock devices always respond instantly, so timeout has no effect.
            This method is provided for interface compatibility only.
        """
        yield self


class Mocker(BaseMocker):
    """Mock serial device that replays events from a CSV file.

    Loads recorded event data and replays it with configurable timing,
    shuffling, and looping. Useful for debugging with real event sequences.

    Attributes:
        events (list[MockEvent]): Loaded events ready for playback
        index (int): Current playback position (0 to len(events)-1)

    Example:
        >>> config = MockerConfig(csv_path=Path("data.csv"), speed=2.0, loop=True)
        >>> mocker = Mocker(config)
        >>> data = mocker.readline()  # Reads first event
        >>> data = mocker.readline()  # Reads second event
    """

    def __init__(self, config: MockerConfig, seed: int | None = None) -> None:
        """Initialize Mocker with CSV file.

        Args:
            config: Mocker configuration (csv_path is required)
            seed: Optional random seed for deterministic shuffling

        Raises:
            ValueError: If config.csv_path is None
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid

        Postconditions:
            - self.events contains loaded MockEvent objects
            - Events are shuffled if config.shuffle=True
            - self.index = 0 (ready to read first event)
            - Random seed is set if provided

        Example:
            >>> config = MockerConfig(
            ...     csv_path=Path("data.csv"),
            ...     shuffle=True,
            ...     speed=2.0,
            ...     jitter=0.1,
            ...     loop=True
            ... )
            >>> mocker = Mocker(config, seed=42)
        """
        super().__init__(config)

        # Validate csv_path is provided for Mocker
        if self.csv_path is None:
            log.error("csv_path is required for Mocker")
            raise ValueError(
                "csv_path is required for Mocker. Use RandomMocker if you don't have a CSV file."
            )

        # Validate csv_path exists
        if not self.csv_path.exists():
            log.error(f"CSV file not found: {self.csv_path}")
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        # Set seed if provided
        if seed is not None:
            random.seed(seed)
            log.debug(f"Random seed set: {seed}")

        # Log initialization
        log.info(
            f"Initializing Mocker: csv_path={self.csv_path}, "
            f"shuffle={self.shuffle}, speed={self.speed}x, "
            f"jitter={self.jitter}s, loop={self.loop}, seed={seed}"
        )

        # Load events with error handling (load_events will log and raise on errors)
        self.events = load_events(self.csv_path, self.jitter, self.speed, self.shuffle)
        self.index = 0

    def readline(self) -> str:
        """Read one event from the loaded CSV data.

        Behavior:
            1. Check response queue first for threshold write responses
            2. If queue has items: return self._response_queue.popleft()
            3. If device is closed or no events, returns ""
            4. Gets current event from self.events[self.index]
            5. Calculates sleep interval: max(0, gauss(deltaT/speed, jitter))
            6. Sleeps for calculated interval (simulates waiting for this event)
            7. Advances index (loops if config.loop=True, stops if False)
            8. Returns event as string (compatible with Device.readline())

        Returns:
            Space-separated sensor values (no timestamp),
            or "" if device is closed or no events.

        Example:
            >>> mocker = Mocker(config)
            >>> mocker.set_next_response("1")  # Queue response
            >>> data = mocker.readline()  # Returns "1"
            >>> data = mocker.readline()  # Returns detector event
            >>> data
            '2 0 0 1136 27.37 100594.35 41.43'
            >>> type(data)
            <class 'str'>

        Timing:
            - Sleep interval = max(0, random.gauss(event.deltaT / event.speed, event.jitter))
            - Gaussian jitter adds realistic variation
            - Negative intervals clamped to 0 (no negative sleep)
            - Sleep happens BEFORE returning event (correct timing simulation)

        Looping:
            - If config.loop=True: index wraps to 0 at end
            - If config.loop=False: index stops at last event (stays at last)
        """
        # Check response queue first for threshold write responses
        if self._response_queue:
            return self._response_queue.popleft()

        if not self.is_open or not self.events:
            return ""

        # Get current event
        event = self.events[self.index]

        # Calculate sleep interval with jitter (how long to wait for this event)
        sleep_interval = max(0, random.gauss(event.deltaT / event.speed, event.jitter))
        if sleep_interval > 0:
            sleep(sleep_interval)

        # Advance to next event AFTER sleeping
        self.index = (
            (self.index + 1) % len(self.events)
            if self.loop
            else min(self.index + 1, len(self.events) - 1)
        )

        # Return the event data (space-separated, no timestamp)
        return event.to_serial()


class RandomMocker(BaseMocker):
    """Mock serial device that generates random sensor values.

    Generates synthetic event data with realistic value ranges.
    Useful for stress testing or when no recorded data is available.

    Attributes:
        deltaT (float): Fixed time interval (1.0 seconds)
        rng (random.Random): Dedicated random number generator

    Example:
        >>> config = MockerConfig(csv_path=None, speed=10.0)
        >>> mocker = RandomMocker(config, seed=42)
        >>> data = mocker.readline()  # Generates random event
    """

    def __init__(self, config: MockerConfig, seed: int | None = None) -> None:
        """Initialize RandomMocker with optional seed.

        Args:
            config: Mocker configuration (csv_path is ignored)
            seed: Optional random seed for reproducibility

        Postconditions:
            - self.deltaT = 1.0 (fixed interval)
            - self.rng = random.Random(seed) (dedicated RNG instance)
            - Random seed set if provided

        Note:
            csv_path in config is ignored. RandomMocker doesn't use CSV files.

        Example:
            >>> config = MockerConfig(csv_path=None, speed=10.0, jitter=0.05)
            >>> mocker = RandomMocker(config, seed=42)  # Deterministic
            >>> mocker2 = RandomMocker(config)  # Non-deterministic
        """
        super().__init__(config)
        self.deltaT = 1.0  # Fixed interval for random generation

        # Create dedicated Random instance (don't pollute global state)
        self.rng = random.Random(seed)

        # Log initialization
        log.info(
            f"Initializing RandomMocker: speed={self.speed}x, jitter={self.jitter}s, seed={seed}"
        )

    def readline(self) -> str:
        """Generate one random event.

        Behavior:
            1. Check response queue first for threshold write responses
            2. If queue has items: return self._response_queue.popleft()
            3. If device is closed, returns ""
            4. Generates random values using self.rng:
               - time: current timestamp (pendulum.now())
               - top, mid, btm: randint(0, 10)
               - adc: randint(0, 1024)
               - tmp: uniform(20, 30)
               - atm: uniform(100500, 100600)  # FIXED RANGE
               - hmd: uniform(30, 70)
            5. Creates MockEvent with deltaT=1.0
            6. Calculates sleep interval: max(0, gauss(1.0/speed, jitter))
            7. Sleeps for calculated interval (ONCE - double sleep bug fixed)
            8. Returns event as string (compatible with Device.readline())

        Returns:
            Space-separated sensor values (no timestamp),
            or "" if device is closed.

        Value Ranges:
            - top, mid, btm: 0-10 (integer, uniform distribution)
            - adc: 0-1024 (integer, uniform distribution)
            - tmp: 20-30°C (float, uniform distribution)
            - atm: 100500-100600 Pa (float, uniform distribution)
            - hmd: 30-70% (float, uniform distribution)

        Example:
            >>> mocker = RandomMocker(config, seed=42)
            >>> mocker.set_next_response("1")  # Queue response
            >>> mocker.readline()
            '1'
            >>> mocker.readline()
            '5 2 8 512 25.43 100550.12 55.67'
            >>> mocker.readline()
            '3 0 1 789 28.91 100582.45 42.33'

        Reproducibility:
            - Same seed produces identical sequence
            - No seed (seed=None) produces non-deterministic sequence
        """
        # Check response queue first for threshold write responses
        if self._response_queue:
            return self._response_queue.popleft()

        if not self.is_open:
            return ""

        # Generate random values using instance RNG
        values = [
            pendulum.now().to_iso8601_string(),
            str(self.rng.randint(0, 10)),  # top
            str(self.rng.randint(0, 10)),  # mid
            str(self.rng.randint(0, 10)),  # btm
            str(self.rng.randint(0, 1024)),  # adc
            f"{self.rng.uniform(20, 30):.2f}",  # tmp (°C)
            f"{self.rng.uniform(100500, 100600):.2f}",  # atm (Pa) - FIXED RANGE
            f"{self.rng.uniform(30, 70):.2f}",  # hmd (%)
        ]

        mocked = MockEvent.from_list(
            values, deltaT=self.deltaT, jitter=self.jitter, speed=self.speed
        )

        # Calculate sleep interval with jitter (using instance RNG)
        sleep_interval = max(0, self.rng.gauss(mocked.deltaT / mocked.speed, mocked.jitter))
        if sleep_interval > 0:
            sleep(sleep_interval)
        # NOTE: Double sleep bug fixed - removed the second sleep(mocked.deltaT)

        return mocked.to_serial()


if __name__ == "__main__":
    """Self test for mock serial devices.

    Run with:
        uv run src/haniwers/v1/daq/mocker.py
    This will demonstrate both Mocker and RandomMocker

    """

    print("\n[SelfTest] Running RandomMocker...")
    config = MockerConfig(
        csv_path=Path("./test_data/osechi_data_000001.csv"),
        shuffle=True,
        speed=10.0,
        jitter=0.5,
        loop=True,
    )
    mock = RandomMocker(config)
    for _ in range(10):
        print(mock.readline().decode().strip())
