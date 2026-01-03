"""Event reading functionality for Sampler data acquisition.

This module provides methods for reading individual events and streaming events
from detector devices. It handles the low-level device I/O and event parsing.

Methods in this module:
- read_event(): Read one measurement from device
- stream_events(): Generator yielding events one at a time
- collect_events(): Collect all events into a list
"""

from typing import Union, Optional, TYPE_CHECKING
from collections.abc import Iterator
import pendulum

from haniwers.v1.daq.model import RawEvent
from haniwers.v1.log.logger import logger as base_logger

if TYPE_CHECKING:
    from haniwers.v1.daq.device import Device


class EventReader:
    """Responsible for reading events from detector devices.

    This class handles:
    - Reading individual events from device (with timestamps)
    - Streaming events one-at-a-time (generator pattern)
    - Collecting all events into a list

    These methods are extracted from the Sampler class to follow
    Single Responsibility Principle (SRP).
    """

    def __init__(self, device: "Device", logger=None):
        """Initialize EventReader with device reference.

        Args:
            device: Device instance to read from
            logger: Logger instance (uses base logger if not provided)
        """
        self.device = device
        self.logger = logger or base_logger
        self._invalid_count = 0  # Track invalid lines during iteration

    def read_event(self) -> "RawEvent | None":
        """Read one measurement from the device and add timestamp.

        What this does:
            1. Waits for detector to send one line of measurement data
            2. Records the exact time data was received (to nearest microsecond)
            3. Parses the 7 sensor values from the detector format
            4. Returns a RawEvent object with all data, or None if line is invalid

            Invalid or empty lines are returned as None (not raising errors).
            This allows data collection to continue even if the detector sends
            corrupted data.

        Returns:
            RawEvent | None:
                - RawEvent: Valid measurement with timestamp, ready for analysis
                - None: Empty or invalid line from detector (skipped gracefully)

        How it works:
            1. device.readline() - Blocks until detector sends data
            2. pendulum.now() - Get timezone-aware timestamp (current time)
            3. RawEvent.from_serial() - Parse detector format to RawEvent (or None)
            4. Return RawEvent object or None

        When to use:
            - Core of data acquisition loop
            - Usually called by stream_events() or collect_events()
            - Rarely called directly (use acquire_by_count() instead)

        Note about None returns:
            stream_events() automatically skips None values, so only valid
            RawEvent objects are yielded to callers. This means data collection
            continues gracefully even when detector sends empty lines.

        Raises:
            serial.SerialException: If device disconnected

        Beginner tip:
            Use acquire_by_count() or acquire_by_time() instead of calling
            this repeatedly. Those methods handle iteration and file saving:

        ```python
        # DON'T do this:
        for i in range(1000):
            event = sampler.read_event()
            if event is not None:
                process(event)

        # DO this instead:
        sampler.acquire_by_count(Path("data.csv"), 1000)
        ```

        Example (low-level, for understanding):

        ```python
        reader = EventReader(device, logger)

        # Read one measurement (may be None if invalid line)
        event = reader.read_event()
        if event is not None:
            print(f"Timestamp: {event.time}")
            print(f"Top sensor: {event.top}")
        ```
        """
        line = self.device.readline()
        timestamp = pendulum.now()
        return RawEvent.from_serial(line, timestamp)

    def stream_events(self, iterator: Iterator) -> Iterator[RawEvent]:
        """Generator that yields measurements one at a time as they arrive.

        What this does:
            Takes an iterator (count-based or time-based) and yields measurements
            one-by-one from the detector. Each time you ask for the next measurement,
            it reads from the device and returns a RawEvent object.

            Invalid or empty lines from the detector are automatically skipped without
            raising errors. This allows data collection to continue even if the
            detector sends corrupted data. Warning logs are generated when invalid
            lines are encountered.

        Args:
            iterator (Iterator): Controls when to stop reading
                - count_based_iterator(1000): Yield 1000 times
                - time_based_iterator(10.0): Yield for 10 seconds
                - range(5): Yield 5 times

        Yields:
            RawEvent: One measurement at a time, as they arrive from detector
                      (invalid lines are silently skipped)

        How it works (generator pattern):
            1. Loop through each iteration from the provided iterator
            2. For each iteration, read one event from device (read_event())
            3. Skip invalid/empty lines (None values) and log warning
            4. Yield valid RawEvent to caller
            5. Pause until caller asks for next measurement
            6. Repeat until iterator exhausted

        Note on invalid data:
            When the detector sends empty or malformed lines (e.g., not exactly 7 values),
            read_event() returns None. The generator skips these and logs a warning,
            then tries again. This means fewer valid events may be collected than the
            iterator requested, but data collection continues gracefully instead of crashing.

        When to use:
            - Memory-efficient for large data collection (one event at a time)
            - Allows processing events as they arrive
            - Usually called by save_events() or collect_events()
            - Rarely called directly

        Beginner tip:
            This is a "lazy" generator - measurements are read only when requested.
            Contrast with collect_events() which reads ALL measurements first,
            then returns them as a list:

        ```python
        # Generator: One at a time (memory-efficient)
        for event in reader.stream_events(iterator):
            print(event)  # Process as events arrive

        # List: All at once (loads everything into memory)
        all_events = reader.collect_events(iterator)
        print(f"Total: {len(all_events)}")
        ```

        Example (low-level, for understanding):

        ```python
        reader = EventReader(device, logger)

        # Create an iterator for 100 measurements
        from haniwers.v1.daq.sampler._iterators import count_based_iterator
        iterator = count_based_iterator(100)

        # Stream events one at a time (invalid lines skipped automatically)
        count = 0
        skipped = 0
        for event in reader.stream_events(iterator):
            count += 1
            if count <= 3:
                print(f"Event {count}: {event.ch1}, {event.ch2}, {event.ch3}")

        print(f"Received {count} total events")
        ```

        Performance note:
            Streaming is much more memory-efficient than collect_events()
            for large datasets because only one event is in memory at a time.

        Note on invalid lines:
            Invalid/empty lines are counted but not logged in real-time.
            Call get_invalid_count() after iteration to retrieve the count.
        """
        self._invalid_count = 0  # Reset counter
        for _ in iterator:
            event = self.read_event()
            if event is not None:
                yield event
            else:
                self._invalid_count += 1
                # Log individual skips only in verbose mode
                self.logger.debug(
                    f"Skipped invalid/empty detector line (total: {self._invalid_count})"
                )

    def get_invalid_count(self) -> int:
        """Get the count of invalid/empty lines skipped during last iteration.

        Returns:
            int: Number of invalid lines skipped. Returns 0 if no iteration occurred.

        Example:
            >>> reader = EventReader(device)
            >>> events = list(reader.stream_events(iterator))
            >>> skipped = reader.get_invalid_count()
            >>> if skipped > 0:
            ...     print(f"Skipped {skipped} invalid lines")
        """
        return getattr(self, "_invalid_count", 0)

    def collect_events(self, iterator: Iterator) -> list[RawEvent]:
        """Collect all measurements into a list.

        What this does:
            Reads all measurements from the detector (following the iterator),
            collects them in memory, then returns them as a list.

            Invalid or empty lines from the detector are automatically skipped without
            raising errors (see stream_events() for details).

        Args:
            iterator (Iterator): Controls when to stop reading
                - count_based_iterator(1000): Collect 1000 events
                - time_based_iterator(10.0): Collect for 10 seconds
                - range(5): Collect 5 events

        Returns:
            list[RawEvent]: All collected measurements with timestamps

        How it works:
            1. Uses stream_events() internally (generator)
            2. Collects all yielded RawEvent objects into a list
            3. Returns complete list to caller

        When to use:
            - When you need all data at once for processing
            - For smaller datasets (loads everything into memory)
            - Usually called by save_events() or run() internally
            - Rarely called directly

        Beginner tip:
            Use stream_events() for memory efficiency with large datasets.
            Use collect_events() only when you need all data at once.

        ```python
        # Efficient for large data:
        for event in reader.stream_events(iterator):
            process_one(event)

        # All-at-once (uses more memory):
        all_events = reader.collect_events(iterator)
        process_all(all_events)
        ```

        Example:

        ```python
        reader = EventReader(device, logger)

        # Collect 10 measurements
        from haniwers.v1.daq.sampler._iterators import count_based_iterator
        iterator = count_based_iterator(10)
        events = reader.collect_events(iterator)

        print(f"Collected {len(events)} events")
        for i, event in enumerate(events[:3]):
            print(f"  Event {i+1}: {event.timestamp}")
        ```

        Performance note:
            For 10,000+ events, stream_events() is more memory-efficient.
            For <1,000 events, collect_events() is simpler and more convenient.
        """
        return list(self.stream_events(iterator))
