"""Sampler orchestration layer - coordinates reading, writing, and configuration.

This module provides the main Sampler class that coordinates all data acquisition
operations by delegating to specialized modules:
- EventReader (_reader.py) for reading events from device
- EventWriter (_writer.py) for writing events to CSV
- Generators (_iterators.py) for iteration logic
- Utilities (_helpers.py) for helper functions

The Sampler class itself focuses on orchestration and public API.
"""

from pathlib import Path
from typing import Union, Optional, TYPE_CHECKING
from collections.abc import Iterator
from datetime import datetime

from haniwers.v1.log.logger import logger as base_logger
from haniwers.v1.daq.sampler._reader import EventReader
from haniwers.v1.daq.sampler._writer import EventWriter

if TYPE_CHECKING:
    from haniwers.v1.daq.device import Device
    from haniwers.v1.daq.mocker import Mocker, RandomMocker
    from haniwers.v1.config.model import DaqConfig, ScanConfig, SamplerConfig


class Sampler:
    """Orchestrate data acquisition from detector to CSV files.

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

    This class coordinates EventReader and EventWriter for all operations.

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
        - show_progress: Optional progress bar (rich.progress) during acquisition
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
        # Store configuration
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

        # Create reader and writer for delegation
        self.reader = EventReader(self.device, self.logger)
        self.writer = EventWriter(
            self.reader,
            self.output_dir,
            stream_mode=self.stream_mode,
            show_progress=self.show_progress,
            logger=self.logger,
        )

    def timestamped_filename(self, fid: int, mac_address: str = "unknown") -> Path:
        """Generate timestamped CSV filename with MAC address.

        What this does:
            Creates a unique filename for each CSV file, incorporating:
            - Filename prefix from config
            - MAC address for device identification
            - Timestamp (YYYY-MM-DD_HHhMMmSSs format) for session traceability
            - File ID (0000000, 0000001, etc.) to distinguish multiple files
            - .csv extension

        Args:
            fid (int): File ID number (incremented for each file in session)
                Example: 0 → "data_unknown_2025-12-30_14h30m45s_0000000.csv"
                Example: 1 → "data_unknown_2025-12-30_14h30m45s_0000001.csv"

            mac_address (str, optional): Device MAC address for traceability
                Default: "unknown" (fallback if MAC not available)
                Format: 12 lowercase hex characters (e.g., "aabbccddee00")

        Returns:
            Path: Full path to output file
                Example: Path("./data/data_unknown_2025-12-30_14h30m45s_0000000.csv")

        When to use:
            - Rarely called directly; used internally by acquire_by_count/time()
            - Useful for custom filename generation if needed

        Example:

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Generate filenames for files 0-2
        for i in range(3):
            filename = sampler.timestamped_filename(i, "aabbccddee00")
            print(filename)
            # Output:
            # ./data/data_aabbccddee00_2025-12-30_14h30m45s_0000000.csv
            # ./data/data_aabbccddee00_2025-12-30_14h30m45s_0000001.csv
            # ./data/data_aabbccddee00_2025-12-30_14h30m45s_0000002.csv
        ```
        """
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        fid_str = f"{fid:07d}"
        filename = f"{self.prefix}_{mac_address}_{timestamp_str}_{fid_str}{self.suffix}"
        return self.output_dir / filename

    def acquire_by_count(self, file_path: Path, event_count: int):
        """Collect exactly N measurements and save to CSV file (with progress bar).

        Delegates to EventWriter.acquire_by_count().
        See EventWriter documentation for details.
        """
        self.writer.acquire_by_count(file_path, event_count)

    def acquire_by_time(self, file_path: Path, duration: float, sleep_interval: float):
        """Collect measurements for a fixed duration and save to CSV file.

        Delegates to EventWriter.acquire_by_time().
        See EventWriter documentation for details.
        """
        self.writer.acquire_by_time(file_path, duration, sleep_interval)

    def run(self, mode: str = None, files: int = None):
        """High-level API for multi-file data acquisition.

        What this does:
            Collects data in multiple files using either count-based or time-based mode.
            Generates timestamped filenames automatically and coordinates all I/O.

        Args:
            mode (str, optional): "count_based" or "time_based"
                Default: Uses self.mode from config
                "count_based": Collect self.events measurements per file
                "time_based": Collect for self.duration seconds per file

            files (int, optional): Number of files to create
                Default: Uses self.files from config
                Example: files=5 creates 5 separate CSV files

        Example:

        ```python
        sampler = Sampler(device, config, Path("./data"))

        # Count-based: 5 files, 1000 events each
        sampler.run(mode="count_based", files=5)

        # Time-based: 5 files, 10 seconds each
        sampler.run(mode="time_based", files=5)
        ```
        """
        mode = mode or self.mode or "count_based"
        files = files or self.files

        for fid in range(files):
            file_path = self.timestamped_filename(fid, self.mac_address)
            self.logger.info(f"Acquiring to {file_path}")

            if mode == "count_based":
                self.acquire_by_count(file_path, self.events)
            elif mode == "time_based":
                self.acquire_by_time(file_path, self.duration, sleep_interval=0.1)
            else:
                raise ValueError(f"Unknown mode: {mode}")


def run_session(device, config, output_dir, mac_address="unknown", show_progress=True):
    """Convenience function for creating and running Sampler in one call.

    What this does:
        Creates a Sampler object and immediately runs acquisition with default settings.
        Useful for simple scripts that don't need advanced configuration.

    Args:
        device: Device or Mocker instance
        config: DaqConfig, ScanConfig, or SamplerConfig instance
        output_dir: Directory for CSV output files
        mac_address: Device MAC address (default: "unknown")
        show_progress: Whether to show progress bar (default: True)

    Example:

    ```python
    from haniwers.v1.daq.sampler import run_session

    device = Device(config.device)
    device.connect()

    # Quick one-liner for acquisition
    run_session(device, config.daq, Path("./data"), show_progress=True)

    device.disconnect()
    ```
    """
    sampler = Sampler(
        device=device,
        config=config,
        output_dir=output_dir,
        mac_address=mac_address,
        show_progress=show_progress,
    )
    sampler.run()
