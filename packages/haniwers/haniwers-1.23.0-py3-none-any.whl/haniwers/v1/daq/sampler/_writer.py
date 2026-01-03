"""Event writing functionality for Sampler data acquisition.

This module provides methods for writing events to CSV files. It handles
both streaming and buffered write modes.

Methods in this module:
- save_events(): Write measurements to CSV file
- acquire_by_count(): Collect and save fixed number of events
- acquire_by_time(): Collect and save events for fixed duration
"""

from pathlib import Path
from typing import Union, TYPE_CHECKING
from collections.abc import Iterator
import csv

from haniwers.v1.daq.model import RawEvent
from haniwers.v1.log.logger import logger as base_logger

if TYPE_CHECKING:
    from haniwers.v1.daq.sampler._reader import EventReader


class EventWriter:
    """Responsible for writing events to CSV files.

    This class handles:
    - Writing events from iterators or lists to CSV
    - Streaming mode (write as you go) vs buffered mode (collect then write)
    - Timestamped filename generation
    - High-level acquisition methods (by count, by time)

    These methods are extracted from the Sampler class to follow
    Single Responsibility Principle (SRP).
    """

    def __init__(
        self,
        reader: "EventReader",
        output_dir: Path,
        stream_mode: bool = True,
        show_progress: bool = True,
        logger=None,
    ):
        """Initialize EventWriter with reader and config.

        Args:
            reader: EventReader instance to get events from
            output_dir: Directory to save CSV files
            stream_mode: Write as you go (True) or collect first (False)
            show_progress: Show progress bar during acquisition
            logger: Logger instance (uses base logger if not provided)
        """
        self.reader = reader
        self.output_dir = output_dir
        self.stream_mode = stream_mode
        self.show_progress = show_progress
        self.logger = logger or base_logger

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
        writer.stream_mode = True  # Write as you go, memory-efficient

        # For small datasets (thousands of measurements):
        writer.stream_mode = False  # Collect first, then write once
        ```

        Example (low-level, for understanding):

        ```python
        writer = EventWriter(reader, Path("./data"), stream_mode=True)

        # Option 1: Save from iterator (streaming)
        from haniwers.v1.daq.sampler._iterators import count_based_iterator
        iterator = count_based_iterator(1000)
        writer.save_events(Path("./data/stream.csv"), iterator)

        # Option 2: Collect first, then save
        iterator = count_based_iterator(1000)
        events = reader.collect_events(iterator)
        writer.save_events(Path("./data/collected.csv"), events)

        # Option 3: Use higher-level acquire_by_count (recommended)
        writer.acquire_by_count(Path("./data/measurement.csv"), 1000)
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
                for event in self.reader.stream_events(source):
                    writer.writerow(event.to_list())
                    f.flush()  # Flush after each event for true streaming
            else:
                events = self.reader.collect_events(source)
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
        writer = EventWriter(reader, Path("./data"))

        # Collect 1000 measurements (simple and clear)
        writer.acquire_by_count(
            file_path=Path("./data/run.csv"),
            event_count=1000
        )

        # File is now saved at ./data/run.csv
        print("✓ Collection complete")
        ```

        Compare with time-based collection:

        ```python
        # Fixed count: Stop after 1000 measurements
        writer.acquire_by_count(Path("./data/fixed.csv"), 1000)

        # Fixed time: Stop after 10 seconds
        writer.acquire_by_time(Path("./data/timed.csv"), duration=10.0, sleep_interval=0.1)
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
        from haniwers.v1.daq.sampler._iterators import count_based_iterator
        from haniwers.v1.daq.sampler._helpers import tqdm_wrapper

        self.logger.debug(f"Saving to {file_path}")
        iterator = tqdm_wrapper(
            count_based_iterator(event_count), desc="Events", show=self.show_progress
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
        writer = EventWriter(reader, Path("./data"))

        # Collect for 10 seconds (standard for scanning)
        writer.acquire_by_time(
            file_path=Path("./data/threshold_scan.csv"),
            duration=10.0,          # 10 seconds
            sleep_interval=0.1      # Check 10 times per second
        )

        # File now contains all measurements collected during 10 seconds
        ```

        Compare with count-based collection:

        ```python
        # Fixed count: Stop after 1000 measurements
        writer.acquire_by_count(Path("./data/fixed.csv"), 1000)

        # Fixed time: Stop after 10 seconds (event count varies)
        writer.acquire_by_time(Path("./data/timed.csv"), 10.0, 0.1)
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
        from haniwers.v1.daq.sampler._iterators import time_based_iterator
        from haniwers.v1.daq.sampler._helpers import tqdm_wrapper

        iterator = tqdm_wrapper(
            time_based_iterator(duration, sleep_interval),
            desc="Duration",
            show=self.show_progress,
        )
        self.save_events(file_path, iterator)
