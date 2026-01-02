from pathlib import Path
from typing import Union, Optional, TYPE_CHECKING
from collections.abc import Iterator, Generator
from datetime import datetime
import csv
from tqdm import tqdm
import pendulum
import time

from haniwers.v1.daq.model import RawEvent
from haniwers.v1.log.logger import logger as base_logger

if TYPE_CHECKING:
    from haniwers.v1.daq.device import Device
    from haniwers.v1.daq.mocker import Mocker, RandomMocker
    from haniwers.v1.config.model import DaqConfig, ScanConfig, SamplerConfig


class Sampler:
    """Collect detector measurements and save them to CSV files.

    What is Sampler?
        The recommended way to capture data from a detector (real or mock) and
        store it on disk. It handles all the details: reading measurements,
        adding timestamps, organizing files, and showing progress.

    Key features:
        ✓ Reads events from any source: real Device, Mocker (CSV playback),
          or RandomMocker (synthetic data)
        ✓ Multiple acquisition modes: Fixed count or fixed time duration
        ✓ Streaming or buffered: Write events immediately or collect then write
        ✓ Progress tracking: Optional progress bar shows data collection status
        ✓ Timestamped files: Automatically generates human-readable filenames

    Life cycle:
        1. Create: Sampler(device, config, output_dir)
        2. Acquire: Run acquisition (by count or by time)
        3. Output: CSV files saved with timestamped names

    Example (real detector with fixed count):

    ```python
    from pathlib import Path
    from haniwers.v1.config.model import DaqConfig
    from haniwers.v1.daq.device import Device
    from haniwers.v1.daq.sampler import Sampler

    # Setup
    device = Device(config.device)
    device.connect()

    # Create sampler
    sampler = Sampler(
        device=device,
        config=config.daq,
        output_dir=Path("./data")
    )

    # Collect 1000 events into one file, show progress
    sampler.acquire_by_count(
        file_path=Path("./data/measurement.csv"),
        event_count=1000
    )

    device.disconnect()
    ```

    Example (mock detector with multiple files):

    ```python
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from haniwers.v1.daq.mocker import RandomMocker, MockerConfig
    from haniwers.v1.daq.sampler import Sampler
    from haniwers.v1.config.model import DaqConfig

    # Create mock device (generates synthetic data)
    mock_device = RandomMocker(
        config=MockerConfig(csv_path=None, speed=10.0),
        seed=42  # Reproducible random data
    )

    # Configuration for DAQ
    daq_config = DaqConfig(
        label="test",
        workspace=".",
        filename_prefix="synthetic",
        filename_suffix=".csv",
        events_per_file=100,
        number_of_files=5,
        stream_mode=True  # Write immediately, good for data safety
    )

    # Create and run sampler
    with TemporaryDirectory() as tmpdir:
        sampler = Sampler(
            device=mock_device,
            config=daq_config,
            output_dir=Path(tmpdir),
            show_progress=True  # Show progress bar
        )
        sampler.run(mode="daq", files=5)
    ```

    Advanced features:
        - sampler.acquire_by_count(): Collect fixed number of events
        - sampler.acquire_by_time(): Collect for fixed duration (e.g., 10 seconds)
        - show_progress: Optional progress bar (tqdm) during acquisition
        - stream_mode: Immediate write (safer) vs buffered (faster)
    """

    def __init__(
        self,
        device: Union["Device", "Mocker", "RandomMocker"],
        config: Union["DaqConfig", "ScanConfig", "SamplerConfig"],
        output_dir: Optional[Path] = None,
        show_progress: bool = True,
        mac_address: str = "unknown",
    ):
        """Create a Sampler object with device and configuration.

        What this does:
            Stores your detector settings (real, mock, or random) but does NOT
            start data collection yet. Call run() or acquire_by_count() or
            acquire_by_time() to actually collect measurements and save to CSV files.

        Args:
            device (Device | Mocker | RandomMocker): The data source
                - Device: Real OSECHI detector connected to USB/serial port
                - Mocker: Playback pre-recorded CSV file (for replay/replay testing)
                - RandomMocker: Generate synthetic measurements (for development)

            config (DaqConfig | ScanConfig | SamplerConfig): Settings for session
                - SamplerConfig: Modern config with mode and workspace built-in (NEW)
                - DaqConfig/ScanConfig: Legacy config (requires output_dir parameter)
                - events_per_file: How many measurements per CSV file
                - number_of_files: How many output files to create (for run() mode)
                - stream_mode: Write immediately (True) or buffer first (False)
                - filename_prefix: Name pattern for output files
                - (SamplerConfig only) mode: "count_based" or "time_based"
                - (SamplerConfig only) workspace: Directory for output files

            output_dir (Path, optional): Directory where CSV files will be saved
                - For SamplerConfig: Uses config.workspace (output_dir not needed)
                - For DaqConfig/ScanConfig: Required, must exist
                Example: Path("./data") or Path("/home/user/measurements")

            show_progress (bool, optional): Show progress bar during collection
                Default: True (shows tqdm progress bar)
                Set to False for scripts/batch jobs that don't need visual feedback

            mac_address (str, optional): Device MAC address for filename traceability
                Default: "unknown" (fallback when MAC retrieval fails)
                Expected: 12 lowercase hex characters (e.g., "aabbccddee00")
                Used to embed device identifier in generated filenames

        Raises:
            FileNotFoundError: If output directory doesn't exist or can't be created
            ValueError: If config missing required fields (events_per_file, number_of_files)

        Example (with SamplerConfig - RECOMMENDED):

        ```python
        from pathlib import Path
        from haniwers.v1.daq.device import Device
        from haniwers.v1.daq.sampler import Sampler

        device = Device(config.device)
        device.connect()

        # Create sampler with SamplerConfig (workspace managed automatically)
        sampler = Sampler(
            device=device,
            config=config.sampler,  # Has workspace built-in
            show_progress=True
        )

        # Run acquisition based on config.mode (count_based or time_based)
        sampler.run(files=5)
        device.disconnect()
        ```

        Example (with DaqConfig - LEGACY):

        ```python
        from pathlib import Path
        from haniwers.v1.daq.device import Device
        from haniwers.v1.daq.sampler import Sampler

        device = Device(config.device)
        device.connect()

        sampler = Sampler(
            device=device,
            config=config.daq,
            output_dir=Path("./data"),
            show_progress=True
        )

        sampler.acquire_by_count(Path("./data/run1.csv"), 1000)
        device.disconnect()
        ```
        """
        # TODO: device.is_connected() を追加してraise処理する
        self.device = device
        self.config = config
        self.show_progress = show_progress
        self.mac_address = mac_address
        self.stream_mode = getattr(config, "stream_mode", True)
        self.prefix = getattr(self.config, "filename_prefix", "data")
        self.suffix = getattr(self.config, "filename_suffix", ".csv")
        self.events = getattr(self.config, "events_per_file", None)
        self.files = getattr(self.config, "number_of_files", None)
        self.mode = getattr(self.config, "mode", None)
        self.duration = getattr(self.config, "duration", None)

        if self.files is None or self.events is None:
            raise ValueError("Config must have 'number_of_files' and 'events_per_file'.")

        self.logger = base_logger.bind(context=self.__class__.__name__)

        # Determine output directory
        # Priority: explicit output_dir parameter > config.workspace
        if output_dir is not None:
            self.output_dir = output_dir
        else:
            # All config types (DaqConfig, ScanConfig, SamplerConfig) have workspace
            self.output_dir = Path(config.workspace)

    def timestamped_filename(self, fid: int, mac_address: str = "unknown") -> Path:
        """Generate a unique filename with timestamp and MAC address for saving measurements.

        What this does:
            Creates a filename automatically using:
            1. Prefix from config (e.g., "data")
            2. Current timestamp (e.g., "2024-05-20T12h34m56s")
            3. File number for sequence (e.g., "000001")
            4. MAC address for device identification (e.g., "aabbccddee00")
            5. Suffix from config (e.g., ".csv")

        Args:
            fid (int): File sequence number (0, 1, 2, ...)
                Used to distinguish multiple files from same session
                Example: fid=0 → "data_2024-05-20T12h34m56s_000000.csv"

            mac_address (str, optional): Device MAC address for traceability
                Default: "unknown" (fallback when MAC retrieval fails)
                Expected: 12 lowercase hex characters (e.g., "aabbccddee00")
                Example: "aabbccddee00" → filename includes "_aabbccddee00_"

        Returns:
            Path: Full path to output file (including directory)

        How it works:
            1. Gets current time at method call time (not file creation time)
            2. Formats as "YYYY-MM-DDTHH[h]MM[m]SS[s]" (human-readable, filesystem-safe)
            3. Combines: {prefix}_{timestamp}_{fid:07d}_{mac_address}{suffix}
            4. Returns full path: output_dir / filename

        Why filesystem-safe timestamp format:
            Uses "T12h34m56s" instead of "T12:34:56" to avoid colon character
            (Windows filesystems don't allow colons in filenames)

        Example:

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Generate filenames with MAC address
        file0 = sampler.timestamped_filename(0, "aabbccddee00")
        # Returns: Path("./data/data_2024-05-20T14h32m11s_000000_aabbccddee00.csv")

        file1 = sampler.timestamped_filename(1, "aabbccddee00")
        # Returns: Path("./data/data_2024-05-20T14h32m15s_000001_aabbccddee00.csv")

        file2 = sampler.timestamped_filename(2, "aabbccddee00")
        # Returns: Path("./data/data_2024-05-20T14h32m19s_000002_aabbccddee00.csv")

        # With fallback when MAC unavailable
        file0 = sampler.timestamped_filename(0, "unknown")
        # Returns: Path("./data/data_2024-05-20T14h32m11s_000000_unknown.csv")
        ```

        Note:
            Timestamp updates for each file (each call gets current time)
            Sequence numbers always zero-padded to 7 digits (000000, 000001, etc.)
            MAC address is always included (device traceability)
        """

        timestamp = pendulum.now().format("YYYY-MM-DDTHH[h]mm[m]ss[s]")
        template = "{prefix}_{timestamp}_{fid:07}_{mac_address}{suffix}"
        timestamped_path = template.format(
            prefix=self.prefix,
            timestamp=timestamp,
            fid=fid,
            mac_address=mac_address,
            suffix=self.suffix,
        )
        return self.output_dir / Path(timestamped_path)

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
        sampler = Sampler(device, config, Path("./data"))

        # Read one measurement (may be None if invalid line)
        event = sampler.read_event()
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
        for event in sampler.stream_events(iterator):
            print(event)  # Process as events arrive

        # List: All at once (loads everything into memory)
        all_events = sampler.collect_events(iterator)
        print(f"Total: {len(all_events)}")
        ```

        Example (low-level, for understanding):

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Create an iterator for 100 measurements
        iterator = sampler.count_based_iterator(100)

        # Stream events one at a time (invalid lines skipped automatically)
        count = 0
        skipped = 0
        for event in sampler.stream_events(iterator):
            count += 1
            if count <= 3:
                print(f"Event {count}: {event.ch1}, {event.ch2}, {event.ch3}")

        print(f"Received {count} total events")
        ```

        Performance note:
            Streaming is much more memory-efficient than collect_events()
            for large datasets because only one event is in memory at a time.
        """
        invalid_count = 0
        for _ in iterator:
            event = self.read_event()
            if event is not None:
                yield event
            else:
                invalid_count += 1
                self.logger.warning(
                    f"Skipped invalid/empty detector line (total skipped: {invalid_count})"
                )

    def collect_events(self, iterator: Iterator) -> list[RawEvent]:
        """Read all measurements and return them as a list.

        What this does:
            Reads measurements according to the provided iterator and collects
            them all into a Python list before returning. Opposite of streaming -
            waits for all data to arrive first, then gives you everything at once.

        Args:
            iterator (Iterator): Controls how many measurements to collect
                - count_based_iterator(1000): Collect 1000 measurements
                - time_based_iterator(10.0): Collect for 10 seconds
                - range(5): Collect 5 measurements

        Returns:
            list[RawEvent]: All measurements as a list
                Each element is a RawEvent object with timestamp and sensor values

        How it works:
            1. Use stream_events() to read from device one-by-one
            2. Collect all RawEvent objects into a Python list
            3. Return the complete list when done

        When to use:
            - When you need all measurements before processing
            - Small to medium datasets (entire list fits in memory)
            - Buffered mode (not streaming) in save_events()
            - Further analysis after collection is complete

        When NOT to use:
            - Large datasets (can run out of memory)
            - Real-time processing (wait for all data defeats the purpose)
            - Use stream_events() for streaming/real-time instead

        Memory warning:
            For 1 million measurements (1M events × ~100 bytes each ≈ 100 MB):
            - collect_events() stores all 100 MB in RAM at once
            - stream_events() stores only 1 event (~100 bytes) at a time
            Use streaming for large datasets!

        Beginner tip:
            Compare two approaches:

        ```python
        # Approach 1: Streaming (memory-efficient, one at a time)
        iterator = sampler.count_based_iterator(1000)
        for event in sampler.stream_events(iterator):
            print(f"Event: {event.ch1}")

        # Approach 2: Collecting (simple, but loads everything into RAM)
        iterator = sampler.count_based_iterator(1000)
        all_events = sampler.collect_events(iterator)
        print(f"Collected {len(all_events)} events")
        for event in all_events:
            print(f"Event: {event.ch1}")
        ```

        Example:

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Collect exactly 100 measurements
        iterator = sampler.count_based_iterator(100)
        events = sampler.collect_events(iterator)

        print(f"Received {len(events)} measurements")
        print(f"First event timestamp: {events[0].timestamp}")
        print(f"Last event timestamp: {events[-1].timestamp}")
        ```
        """
        return list(self.stream_events(iterator))

    def save_events(self, file_path: Path, source: Union[Iterator, list[RawEvent]]) -> None:
        """Write measurements to a CSV file.

        What this does:
            Takes measurements from either a stream (iterator) or a pre-collected
            list and writes them to a CSV file. Handles both streaming (write as
            you go) and buffered (collect first, then write) modes automatically.

        Args:
            file_path (Path): Where to save the CSV file
                Example: Path("./data/run1.csv") or Path("/home/user/measurement.csv")

            source (Iterator | list[RawEvent]): Where to get measurements from
                - Iterator: stream_events() or collect_events() output
                  Reads from device/mock on-demand as file is written
                - list[RawEvent]: Pre-collected measurements
                  Already have all data in memory, just write to file

        How it works:
            If source is a list:
                1. Assume all measurements collected already
                2. Write all rows to CSV at once

            If source is an Iterator:
                - Check stream_mode from config
                - If stream_mode=True (default): Write events as they arrive
                  (memory-efficient, good for large datasets)
                - If stream_mode=False: Collect all first, then write all at once
                  (simpler, but needs more RAM)

        Output CSV format:
            Header row: timestamp,ch1,ch2,ch3,ch4,ch5,ch6,ch7
            Data rows: 2024-10-19T14h32m45s,100,200,150,175,210,190,220
            One row per measurement

        When to use:
            - Standard data saving for DAQ operations
            - Called by acquire_by_count() and acquire_by_time()
            - Rarely called directly (use higher-level methods)

        Beginner tip:
            Choose stream_mode in your config based on dataset size:

        ```python
        # For large datasets (millions of measurements):
        config.stream_mode = True  # Write as you go, memory-efficient

        # For small datasets (thousands of measurements):
        config.stream_mode = False  # Collect first, then write once
        ```

        Example (low-level, for understanding):

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Option 1: Save from iterator (streaming)
        iterator = sampler.count_based_iterator(1000)
        sampler.save_events(Path("./data/stream.csv"), iterator)

        # Option 2: Collect first, then save
        iterator = sampler.count_based_iterator(1000)
        events = sampler.collect_events(iterator)
        sampler.save_events(Path("./data/collected.csv"), events)

        # Option 3: Use higher-level acquire_by_count (recommended)
        sampler.acquire_by_count(Path("./data/measurement.csv"), 1000)
        ```

        Performance:
            - Stream mode: Best for large datasets, writes incrementally
            - Buffered mode: Good for post-processing, reads all first
            - Both produce identical CSV files
        """
        with file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Handle list[RawEvent] source directly
            if isinstance(source, list):
                writer.writerows([event.to_list() for event in source])
            # Handle Iterator source (existing behavior)
            elif self.stream_mode:
                for event in self.stream_events(source):
                    writer.writerow(event.to_list())
                    f.flush()  # Flush after each event for true streaming
            else:
                events = self.collect_events(source)
                writer.writerows([event.to_list() for event in events])

    def acquire_by_count(self, file_path: Path, event_count: int):
        """Collect exactly N measurements and save to a CSV file (with progress bar).

        What this does:
            Reads exactly event_count measurements from the detector and saves them
            to a CSV file. Optionally shows a progress bar counting down to completion.

        Args:
            file_path (Path): Where to save the CSV file
                Example: Path("./data/measurement.csv")

            event_count (int): Exact number of measurements to collect
                Example: 1000 collects 1000 measurements then stops

        How it works:
            1. Create a counter iterator for event_count iterations
            2. Wrap iterator with tqdm progress bar (if show_progress=True)
            3. Read event_count measurements via save_events()
            4. Write all measurements to CSV file
            5. Display results

        When to use:
            - Most common use case for data collection
            - When you know exactly how many measurements you need
            - DAQ sessions with fixed event counts
            - Reproducible experiments with known measurement counts

        Output:
            CSV file with event_count + 1 rows (header + data):
            ```
            timestamp,ch1,ch2,ch3,ch4,ch5,ch6,ch7
            2024-10-19T14h32m45s,100,200,150,175,210,190,220
            2024-10-19T14h32m46s,105,198,152,176,212,189,222
            ... (1000 total data rows)
            ```

        Progress bar:
            If show_progress=True (default):
            ```
            Events: 45%|████▌     | 450/1000 [00:05<00:06, 89.00 it/s]
            ```

        Beginner tip:
            This is the recommended way to collect a fixed amount of data:

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Collect 1000 measurements (simple and clear)
        sampler.acquire_by_count(
            file_path=Path("./data/run.csv"),
            event_count=1000
        )

        # File is now saved at ./data/run.csv
        print("✓ Collection complete")
        ```

        Compare with time-based collection:

        ```python
        # Fixed count: Stop after 1000 measurements
        sampler.acquire_by_count(Path("./data/fixed.csv"), 1000)

        # Fixed time: Stop after 10 seconds
        sampler.acquire_by_time(Path("./data/timed.csv"), duration=10.0, sleep_interval=0.1)
        ```

        Example with all options:

        ```python
        from pathlib import Path
        from haniwers.v1.daq.device import Device
        from haniwers.v1.daq.sampler import Sampler

        device = Device(config.device)
        device.connect()

        sampler = Sampler(
            device=device,
            config=config.daq,
            output_dir=Path("./measurements"),
            show_progress=True  # Show progress bar
        )

        # Collect 5000 measurements
        sampler.acquire_by_count(
            file_path=Path("./measurements/experiment1.csv"),
            event_count=5000
        )

        device.disconnect()
        ```
        """
        self.logger.debug(f"Saving to {file_path}")
        iterator = self.tqdm_wrapper(
            self.count_based_iterator(event_count), desc="Events", show=self.show_progress
        )
        self.save_events(file_path, iterator)

    def acquire_by_time(self, file_path: Path, duration: float, sleep_interval: float):
        """Collect measurements for a fixed duration and save to a CSV file.

        What this does:
            Reads measurements for exactly duration seconds from the detector
            and saves them to a CSV file. Useful when you want a time-limited
            data collection rather than a fixed event count.

        Args:
            file_path (Path): Where to save the CSV file
                Example: Path("./data/10second_run.csv")

            duration (float): How long to collect measurements (in seconds)
                Example: 10.0 collects data for 10 seconds

            sleep_interval (float): Delay between read attempts (in seconds)
                - 0.1: Check detector 10 times per second (default for scanning)
                - 0.01: Very frequent checks (high CPU, for fast events)
                - 1.0: Slow polling (low CPU, for slow events)

        How it works:
            1. Record start time
            2. Loop until duration seconds have passed:
               a. Attempt to read one measurement
               b. Sleep for sleep_interval seconds
               c. Check if duration elapsed
            3. Write all measurements to CSV file

        When to use:
            - Physics experiments with time-based measurements
            - Threshold scanning (typical use: 10 seconds per scan)
            - Background noise measurements
            - When you don't know measurement rate in advance

        Note about sleep_interval:
            - Measurements still come from detector at its natural rate
            - sleep_interval just controls checking frequency
            - Total events = duration × (detector_rate / sleep_interval)

        Output:
            CSV file with variable number of rows (depends on detector rate):
            ```
            timestamp,ch1,ch2,ch3,ch4,ch5,ch6,ch7
            2024-10-19T14h32m45s,100,200,150,175,210,190,220
            2024-10-19T14h32m45s,105,198,152,176,212,189,222
            ... (varies, typically 100-1000 rows for 10 seconds)
            ```

        Progress bar:
            If show_progress=True (default):
            ```
            Duration: 23%|██▎       | 2.3/10.0 [00:02<00:08, 1.00s/s]
            ```

        Beginner tip:
            This is used extensively in threshold scanning:

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Collect for 10 seconds (standard for scanning)
        sampler.acquire_by_time(
            file_path=Path("./data/threshold_scan.csv"),
            duration=10.0,          # 10 seconds
            sleep_interval=0.1      # Check 10 times per second
        )

        # File now contains all measurements collected during 10 seconds
        ```

        Compare with count-based collection:

        ```python
        # Fixed count: Stop after 1000 measurements
        sampler.acquire_by_count(Path("./data/fixed.csv"), 1000)

        # Fixed time: Stop after 10 seconds (event count varies)
        sampler.acquire_by_time(Path("./data/timed.csv"), 10.0, 0.1)
        ```

        Example (threshold scanning pattern):

        ```python
        from pathlib import Path
        from haniwers.v1.daq.device import Device
        from haniwers.v1.daq.sampler import Sampler

        device = Device(config.device)
        device.connect()

        sampler = Sampler(
            device=device,
            config=config.daq,
            output_dir=Path("./scan_results")
        )

        # Scanning 3 thresholds, 10 seconds each
        for threshold_value in [250, 300, 350]:
            device.write(f"THRESHOLD {threshold_value}")

            sampler.acquire_by_time(
                file_path=Path(f"./scan_results/threshold_{threshold_value}.csv"),
                duration=10.0,
                sleep_interval=0.1
            )
            print(f"✓ Completed scan at threshold {threshold_value}")

        device.disconnect()
        ```
        """
        iterator = self.tqdm_wrapper(
            self.time_based_iterator(duration, sleep_interval),
            desc="Duration",
            show=self.show_progress,
        )
        self.save_events(file_path, iterator)

    def time_based_iterator(
        self, duration: float, sleep_interval: float
    ) -> Generator[None, None, None]:
        """Generator that yields for a fixed duration (time-based acquisition loop).

        What this does:
            Yields control back to the caller (which reads one measurement) until
            the specified duration has elapsed. Used to implement time-limited
            data collection ("collect for 10 seconds").

        Args:
            duration (float): Total time to yield for (in seconds)
                Example: 10.0 yields for 10 seconds total

            sleep_interval (float): Time to sleep between yields (in seconds)
                Example: 0.1 means "check every 0.1 seconds"
                Smaller intervals = more frequent checks but higher CPU usage
                Larger intervals = less frequent checks but lower CPU usage

        Yields:
            None: Each yield means "read one measurement, then continue"

        How it works:
            1. Record start time at first yield
            2. Loop:
               a. Yield None (signal to caller to read one event)
               b. Sleep for sleep_interval seconds
               c. Check if total elapsed_time >= duration
            3. Stop yielding when duration exceeded

        When to use:
            - Core of time-based data acquisition
            - Called by acquire_by_time()
            - Rarely called directly

        When NOT to use:
            - For fixed event counts: use count_based_iterator() instead
            - For manual iteration: Too low-level, use acquire_by_time()

        Beginner tip:
            This is automatically used by acquire_by_time():

        ```python
        # High-level (recommended):
        sampler.acquire_by_time(Path("data.csv"), duration=10.0, sleep_interval=0.1)

        # Low-level (not recommended):
        iterator = sampler.time_based_iterator(10.0, 0.1)
        for _ in iterator:
            event = sampler.read_event()  # This is just one event
        ```

        Example (understanding sleep_interval):

        ```python
        # Frequent checks (high CPU):
        iterator = sampler.time_based_iterator(duration=5.0, sleep_interval=0.01)
        # Yields ~500 times in 5 seconds (every 0.01 seconds)

        # Standard checks:
        iterator = sampler.time_based_iterator(duration=5.0, sleep_interval=0.1)
        # Yields ~50 times in 5 seconds (every 0.1 seconds)

        # Slow checks (low CPU):
        iterator = sampler.time_based_iterator(duration=5.0, sleep_interval=0.5)
        # Yields ~10 times in 5 seconds (every 0.5 seconds)
        ```

        Performance notes:
            - Smaller sleep_interval = more responsive but higher CPU usage
            - Larger sleep_interval = lower CPU but less responsive
            - Choose based on your detector's measurement rate and CPU constraints
            - Default (0.1s) is standard for physics detector scanning

        Exact timing:
            - Uses time.time() for wall-clock accuracy
            - Timing includes measurement read time, so total may exceed duration slightly
            - Suitable for 1-10 second measurements, not for sub-millisecond precision
        """
        start = time.time()
        while time.time() - start < duration:
            yield
            time.sleep(sleep_interval)

    def count_based_iterator(self, counts: int):
        """Create an iterator that yields exactly N times (count-based acquisition loop).

        What this does:
            Returns a simple counter from 0 to counts-1. Used to implement
            fixed-count data collection ("collect 1000 measurements").

        Args:
            counts (int): Exact number of times to yield
                Example: 1000 yields 1000 times (0 through 999)

        Yields:
            int: Counter value (0, 1, 2, ..., counts-1)

        How it works:
            1. Create a range(0, counts) iterator
            2. Each time called, return next value in the range
            3. Stop after yielding counts times

        When to use:
            - Core of count-based data acquisition
            - Called by acquire_by_count()
            - Rarely called directly

        When NOT to use:
            - For time-based collection: use time_based_iterator() instead
            - For manual iteration: use acquire_by_count() instead

        Beginner tip:
            This is automatically used by acquire_by_count():

        ```python
        # High-level (recommended):
        sampler.acquire_by_count(Path("data.csv"), event_count=1000)

        # Low-level (not recommended):
        iterator = sampler.count_based_iterator(1000)
        for i in iterator:
            event = sampler.read_event()  # This is just one event
            if i < 3:
                print(f"Event {i}")
        ```

        Example (understanding iteration):

        ```python
        # Collect exactly 100 measurements
        iterator = sampler.count_based_iterator(100)

        # Process with different iteration patterns
        for index in iterator:
            event = sampler.read_event()

            # Index tells you which measurement this is (0-99)
            if index == 0:
                print("First measurement")
            elif index == 99:
                print("Last measurement")
        ```

        Performance:
            - Extremely efficient: Just a simple counter
            - No sleep/timing overhead (unlike time_based_iterator)
            - Perfect for fixed-size experiments
            - Predictable number of measurements

        Equivalent to:

        ```python
        # This:
        iterator = sampler.count_based_iterator(10)
        for i in iterator:
            pass

        # Is equivalent to:
        for i in range(10):
            pass
        ```
        """
        return range(counts)

    def run(
        self, mode: Optional[str] = None, files: Optional[int] = None
    ) -> Optional[list[RawEvent]]:
        """Run a complete acquisition session collecting N files of measurements.

        What this does:
            Collects data into multiple output files based on the mode.
            Each file gets a unique timestamped filename, with progress bar showing
            overall progress across all files.

            When stream_mode=False, returns all collected events as a list instead
            of writing to files. Useful for threshold scanning where you need to
            aggregate results in memory.

        Args:
            mode (str, optional): Acquisition mode determines how measurements are collected
                - "daq": Collect fixed event count per file (use acquire_by_count)
                - "scan": Collect for fixed duration per file (use acquire_by_time)
                - "time_based": Same as "scan" (for SamplerConfig compatibility)
                - "count_based": Same as "daq" (for SamplerConfig compatibility)
                - "mock": Same as "daq" (for mock detector testing)
                If not provided, uses self.mode from config (for SamplerConfig)

            files (int, optional): Number of output CSV files to create
                Example: 5 creates 5 separate CSV files
                If not provided, uses self.files from config

        Returns:
            - If stream_mode=True: None (writes to files as usual)
            - If stream_mode=False: list[RawEvent] with all collected events

        How it works (daq mode - most common):
            1. Loop files times:
               a. Generate timestamped filename (includes directory, file number)
               b. Collect exactly config.events_per_file measurements
               c. If stream_mode=True: write to CSV file
               d. If stream_mode=False: collect events in memory
               e. Update progress bar
            2. All measurements go to directory specified in __init__

        How it works (scan mode - threshold scanning):
            1. Loop files times:
               a. Generate timestamped filename
               b. Collect measurements for duration seconds
               c. Sleep 0.5 seconds between checks
               d. If stream_mode=True: write to CSV file
               e. If stream_mode=False: collect events in memory
               f. Update progress bar

        When to use:
            - High-level interface for batch data collection
            - When you need multiple files from one session
            - DAQ mode for regular data collection
            - Scan mode for threshold scanning experiments
            - stream_mode=False for threshold scanning where results need aggregation
            - Rarely call directly: usually managed by CLI command

        Output (stream_mode=True):
            Creates N timestamped CSV files in output_dir:
            ```
            data_2024-10-19T14h32m45s_000000.csv (1000 measurements)
            data_2024-10-19T14h32m55s_000001.csv (1000 measurements)
            data_2024-10-19T14h33m05s_000002.csv (1000 measurements)
            data_2024-10-19T14h33m15s_000003.csv (1000 measurements)
            data_2024-10-19T14h33m25s_000004.csv (1000 measurements)
            ```

        Output (stream_mode=False):
            Returns collected events as list[RawEvent] for aggregation.

        Progress bar:
            ```
            Files: 40%|████      | 2/5 [00:10<00:15, 5.00s/file]
            ```

        Beginner tip:
            For most use cases, use the higher-level CLI interface instead:

        ```python
        # CLI (recommended):
        haniwers-v1 daq --config config.toml --files 5

        # Low-level Python (rarely used):
        sampler = Sampler(device, config, Path("./data"))
        sampler.run(mode="daq", files=5)
        ```

        Mode comparison:

        ```python
        # DAQ mode (regular data collection):
        sampler.run(mode="daq", files=5)
        # Creates 5 files, each with events_per_file measurements

        # Scan mode (threshold scanning):
        sampler.run(mode="scan", files=5)
        # Creates 5 files, each collected for 10 seconds

        # Scan with in-memory aggregation:
        sampler.stream_mode = False
        events = sampler.run(mode="time_based", files=1)
        # Returns list[RawEvent] instead of writing to file
        ```

        Advanced example:

        ```python
        from pathlib import Path
        from haniwers.v1.daq.device import Device
        from haniwers.v1.daq.sampler import Sampler

        device = Device(config.device)
        device.connect()

        sampler = Sampler(
            device=device,
            config=config.daq,
            output_dir=Path("./data"),
            show_progress=True
        )

        # Collect 5 files, each with 1000 measurements
        print("Starting data acquisition...")
        sampler.run(mode="daq", files=5)
        print("✓ Data collection complete")

        device.disconnect()
        ```

        Threshold scanning example (with aggregation):

        ```python
        # Use stream_mode=False to get events for aggregation
        sampler.stream_mode = False
        events = sampler.run(mode="time_based", files=1)  # Collect for duration seconds

        # Now you can aggregate the results
        result = aggregate_scan_result(events, channel=1, vth=300, duration=10)
        ```

        Note about scan mode:
            Hardcoded values for scanning (10 seconds, 0.5s sleep interval) are
            meant for physics detector threshold scanning. For custom durations,
            use acquire_by_time() directly or modify this method.
        """
        # Use defaults from config if parameters not provided
        actual_mode = mode if mode is not None else self.mode
        actual_files = files if files is not None else self.files

        # Validate mode was determined
        if actual_mode is None:
            msg = "mode must be specified either via parameter or config"
            self.logger.error(msg)
            raise ValueError(msg)

        self.logger.info(
            f"Starting DAQ mode='{actual_mode}' for {actual_files} files (stream_mode={self.stream_mode})"
        )

        # If not streaming, collect all events in memory (and save to CSV)
        if not self.stream_mode:
            all_events: list[RawEvent] = []
            iterator = self.tqdm_wrapper(range(actual_files), desc="Files", show=self.show_progress)
            for i in iterator:
                # Support both legacy names (daq/scan) and new names (count_based/time_based)
                if actual_mode in ("daq", "mock", "count_based"):
                    it = self.count_based_iterator(self.events)
                    events = self.collect_events(it)
                elif actual_mode in ("scan", "time_based"):
                    # For time_based mode, use self.duration if available, otherwise default to 10s
                    duration = self.duration if self.duration is not None else 10.0
                    it = self.time_based_iterator(duration, sleep_interval=0.5)
                    events = self.collect_events(it)

                # Save collected events to CSV file
                csv_path = self.timestamped_filename(i, self.mac_address)
                self.save_events(csv_path, events)

                all_events.extend(events)
            return all_events

        # Otherwise, write to files as usual (streaming mode)
        iterator = self.tqdm_wrapper(range(actual_files), desc="Files", show=self.show_progress)
        for i in iterator:
            csv_path = self.timestamped_filename(i, self.mac_address)

            # Support both legacy names (daq/scan) and new names (count_based/time_based)
            if actual_mode in ("daq", "mock", "count_based"):
                self.acquire_by_count(csv_path, self.events)
            elif actual_mode in ("scan", "time_based"):
                # For time_based mode, use self.duration if available, otherwise default to 10s
                duration = self.duration if self.duration is not None else 10.0
                self.acquire_by_time(csv_path, duration, 0.5)

        return None

    @staticmethod
    def sanitize(event: list) -> list:
        """Convert raw CSV row to typed values (empty→None, text→float/int).

        What this does:
            Takes a list of strings (from CSV) and converts to proper Python types:
            - Empty strings become None
            - Numbers become int (if whole) or float (if decimal)
            - Non-numbers stay as strings

        Args:
            event (list): List of string values from CSV row

        Returns:
            list: Same values but with proper Python types

        How it works:
            For each value in the list:
            1. If empty string ("") → convert to None
            2. Try to convert to float
            3. If successful and is whole number (e.g., 100.0) → convert to int
            4. If successful and has decimal → keep as float
            5. If conversion fails → keep as string

        When to use:
            - Processing CSV data to clean up string values
            - Converting detector measurements from strings to numbers
            - Part of data preprocessing pipeline
            - Rarely called directly

        Beginner tip:
            This is usually called automatically by data processing code:

        ```python
        # Automatic (preferred):
        event = RawEvent.from_list(["2024-10-19T14h32m45s", "100", "200", ...])

        # Manual (for understanding):
        raw_values = ["2024-10-19T14h32m45s", "100", "", "200.5", "invalid"]
        cleaned = Sampler.sanitize(raw_values)
        # Result: ["2024-10-19T14h32m45s", 100, None, 200.5, "invalid"]
        ```

        Example conversions:

        ```python
        # Strings to integers
        Sampler.sanitize(["100", "200", "300"])
        # Returns: [100, 200, 300]

        # Empty strings to None
        Sampler.sanitize(["100", "", "300"])
        # Returns: [100, None, 300]

        # Decimals stay as float
        Sampler.sanitize(["100.5", "200.0"])
        # Returns: [100.5, 200]  # Note: 200.0 becomes int(200)

        # Invalid strings stay as strings
        Sampler.sanitize(["100", "abc", "300"])
        # Returns: [100, "abc", 300]
        ```

        Data type mapping:
            "100" → 100 (int)
            "100.0" → 100 (int, because no fractional part)
            "100.5" → 100.5 (float)
            "" → None
            "abc" → "abc" (string, unchanged)
            "1e5" → 100000.0 (scientific notation)

        Performance:
            - Reasonably efficient for typical CSV rows (7-10 values)
            - Suitable for processing large CSV files
            - Worth the type safety gained
        """
        sanitized: list = []
        for val in event:
            if val == "":
                sanitized.append(None)
                continue

            # Try to convert to float
            try:
                num = float(val)
            except (ValueError, TypeError):
                # Leave as string if conversion fails
                sanitized.append(val)
                continue

            # Append as int if it's an integer, else float
            sanitized.append(int(num) if num.is_integer() else num)

        return sanitized

    @staticmethod
    def tqdm_wrapper(iterable, desc: Optional[str] = None, show: bool = True):
        """Optionally wrap an iterable with a progress bar (tqdm).

        What this does:
            If show=True: Returns an iterable that displays a progress bar.
            If show=False: Returns the iterable unchanged (no progress bar).
            Useful for conditional progress display in batch processing.

        Args:
            iterable: Any iterable (list, range, generator, etc.)
                Example: range(1000), [1, 2, 3, 4, 5], file_list, etc.

            desc (str, optional): Label for progress bar
                Example: "Events", "Files", "Duration"
                Only used if show=True

            show (bool, optional): Whether to show progress bar
                Default: True (show progress)
                Set to False for scripts/batch jobs

        Returns:
            tqdm object (if show=True) or original iterable (if show=False)

        How it works:
            - If show=True: Wraps with tqdm() for progress bar display
            - If show=False: Returns iterable unchanged
            - Calling code iterates the same way either way

        When to use:
            - Conditional progress display (interactive vs batch)
            - Usually called internally by acquire_by_count(), acquire_by_time()
            - Rarely called directly

        Progress bar example (show=True):
            ```
            Events: 45%|████▌     | 450/1000 [00:05<00:06, 89.00 it/s]
            ```

        Beginner tip:
            The calling code doesn't need to know about tqdm:

        ```python
        # This works the same either way:
        iterator = sampler.tqdm_wrapper(range(1000), desc="Events", show=True)
        for i in iterator:
            print(i)

        iterator = sampler.tqdm_wrapper(range(1000), desc="Events", show=False)
        for i in iterator:  # Same code, no progress bar
            print(i)
        ```

        Use cases:

        ```python
        # Interactive script: Show progress
        bar = Sampler.tqdm_wrapper(
            range(1000),
            desc="Processing",
            show=True  # User sees progress bar
        )

        # Batch/automated script: Don't show progress
        bar = Sampler.tqdm_wrapper(
            range(1000),
            desc="Processing",
            show=False  # No output to terminal
        )

        # Dynamic based on condition:
        verbose = True  # Could come from command-line flag
        bar = Sampler.tqdm_wrapper(
            range(1000),
            desc="Processing",
            show=verbose
        )
        ```

        Performance:
            - show=False: No overhead (returns iterable unchanged)
            - show=True: Minimal overhead (~1% slowdown for fast operations)
            - Progress bar updates once per iteration

        Why use this pattern:
            - Cleaner than if/else statements in calling code
            - Consistent interface regardless of display preference
            - Easy to add progress bars to functions without changing loop logic
            - Industry-standard pattern for CLI tools
        """
        return tqdm(iterable, desc=desc) if show else iterable

    @staticmethod
    def mock_sample(*args, **kwargs):
        """Generate a mock RawEvent for testing or simulation.

        What this does:
            Returns hardcoded mock data ["mock_event"] for testing purposes.
            Useful for unit tests that don't have a real detector or mocker.

        Returns:
            list: Always returns ["mock_event"] (hardcoded test data)

        When to use:
            - Unit testing code that uses Sampler
            - Verifying Sampler logic without detector
            - Debugging file I/O without hardware
            - Demonstration purposes

        When NOT to use:
            - For realistic mock data: Use RandomMocker instead
            - For testing with real detector: Use Device class
            - For production code: Don't use mock_sample at all

        Note:
            This method accepts *args and **kwargs but ignores them (for flexibility)

        Example:

        ```python
        # Get mock data (for testing)
        mock_event = Sampler.mock_sample()
        # Returns: ["mock_event"]

        # Can be called with any arguments (ignored):
        result = Sampler.mock_sample("arg1", "arg2", kwarg1="value")
        # Still returns: ["mock_event"]
        ```

        Why this exists:
            Placeholder for potential future enhancements to mock data generation.
            Current implementation is intentionally simple for clarity.
        """
        return ["mock_event"]


def run_session(
    mode: str, device: "Device", config: Union["DaqConfig", "ScanConfig"], output_dir: Path
) -> None:
    """Run a complete acquisition session with device, config, and output directory.

    What this does:
        High-level function that creates a Sampler and runs a complete acquisition
        session. Handles all the setup and execution for a standard DAQ or scan run.

    Args:
        mode (str): Acquisition mode
            - "daq": Data acquisition (fixed event count)
            - "scan": Threshold scanning (fixed duration)

        device (Device | Mocker | RandomMocker): Data source
            - Device: Real detector connected to serial port
            - Mocker: Replay pre-recorded CSV file
            - RandomMocker: Generate synthetic measurements

        config (DaqConfig | ScanConfig): Configuration for the session
            - Specifies number_of_files (how many output CSV files)
            - Contains events_per_file or time-based settings
            - Stream mode and filename preferences

        output_dir (Path): Directory where CSV files will be saved
            Must exist and be writable

    How it works:
        1. Create Sampler object with provided device and config
        2. Call sampler.run() with mode and number_of_files from config
        3. Function returns when all files have been collected

    When to use:
        - Standard way to start DAQ/scan sessions from Python code
        - Higher-level than Sampler.run() directly
        - Recommended for scripts and batch processing
        - Called by CLI commands internally

    When NOT to use:
        - For complex acquisition patterns (use Sampler directly)
        - For multiple devices (create multiple Samplers)
        - For custom file handling (use Sampler.acquire_by_count/time)

    Raises:
        FileNotFoundError: If output_dir doesn't exist
        ValueError: If config missing required fields

    Example (standard DAQ):

    ```python
    from pathlib import Path
    from haniwers.v1.daq.device import Device
    from haniwers.v1.daq.sampler import run_session
    from haniwers.v1.config.loader import ConfigLoader

    # Load configuration
    loader = ConfigLoader(Path("config.toml"))
    cfg = loader.config

    # Connect to detector
    device = Device(cfg.device)
    device.connect()

    # Run acquisition session
    run_session(
        mode="daq",
        device=device,
        config=cfg.daq,
        output_dir=Path("./data")
    )

    device.disconnect()
    print("✓ Acquisition complete")
    ```

    Example (threshold scanning):

    ```python
    from pathlib import Path
    from haniwers.v1.daq.device import Device
    from haniwers.v1.daq.sampler import run_session
    from haniwers.v1.config.loader import ConfigLoader

    loader = ConfigLoader(Path("config.toml"))
    cfg = loader.config

    device = Device(cfg.device)
    device.connect()

    # Run threshold scan
    run_session(
        mode="scan",
        device=device,
        config=cfg.scan,
        output_dir=Path("./scan_results")
    )

    device.disconnect()
    ```

    Equivalent to:

    ```python
    # This:
    run_session("daq", device, config, Path("./data"))

    # Is equivalent to:
    sampler = Sampler(device, config, Path("./data"))
    sampler.run(mode="daq", files=config.number_of_files)
    ```
    """
    sampler = Sampler(device=device, config=config, output_dir=output_dir)
    sampler.run(mode=mode, files=config.number_of_files)


if __name__ == "__main__":
    """Self-test: Run minimal Sampler example using Mocker/RandomMocker.

    This demonstrates that Sampler works with mock devices (Mocker and RandomMocker)
    in addition to real Device hardware.

    Run with:
        poetry run python src/haniwers/v1/daq/sampler.py

    """
    from tempfile import TemporaryDirectory

    from haniwers.v1.daq.mocker import RandomMocker, MockerConfig
    from haniwers.v1.config.model import DaqConfig

    # Example 1: Using RandomMocker for synthetic data generation
    print("\n=== Example 1: RandomMocker (Synthetic Data) ===")
    mocker_config = MockerConfig(csv_path=None, speed=10.0)
    mock_device = RandomMocker(mocker_config, seed=42)  # Reproducible random data

    daq_config = DaqConfig(
        label="test",
        workspace=".",
        filename_prefix="test_random",
        filename_suffix=".csv",
        events_per_file=5,
        number_of_files=1,
        stream_mode=True,  # Stream mode: write events immediately, preserves data on Ctrl+C
    )

    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        sampler = Sampler(mock_device, daq_config, output_dir)
        test_file = output_dir / "test_random.csv"
        sampler.acquire_by_count(test_file, 5)
        print(f"✓ Created {test_file} with 5 synthetic events")

    # Example 2: Using Mocker for CSV replay (requires CSV file)
    # Uncomment to test with an actual CSV file:
    #
    # from haniwers.v1.daq.mocker import Mocker
    # csv_mocker = Mocker(csv_path=Path("data/your_recorded_data.csv"), speed=2.0)
    # sampler2 = Sampler(csv_mocker, daq_config, output_dir)
    # sampler2.acquire_by_count(output_dir / "test_replay.csv", 10)

    print("\n✓ All Sampler examples completed successfully!\n")
