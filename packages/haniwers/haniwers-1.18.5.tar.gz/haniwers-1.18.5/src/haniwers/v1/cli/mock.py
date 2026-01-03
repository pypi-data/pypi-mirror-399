"""Mock data acquisition command.

This module provides the 'mock' command for testing DAQ functionality without
physical hardware. It supports CSV replay (Mocker) and random data generation
(RandomMocker).

Examples:
    Replay from CSV file:
        $ haniwers-v1 mock --load-from data/recorded.csv --events 100

    Generate random data:
        $ haniwers-v1 mock --random --events 500 --seed 42

    Fast replay with custom output:
        $ haniwers-v1 mock --load-from data.csv --speed 10.0 --output-dir test/
"""

import typer
from typing import Optional
from pathlib import Path

from haniwers.v1.config.model import MockerConfig, SamplerConfig
from haniwers.v1.daq.mocker import Mocker, RandomMocker
from haniwers.v1.daq.sampler import run_session
from haniwers.v1.log.logger import logger as base_logger
from haniwers.v1.helpers.validator import (
    validate_file_path,
    validate_numeric_range,
)
from haniwers.v1.cli.options import (
    LoggerOptions,
    OutputOptions,
    SamplerOptions,
    TestingOptions,
)


# Bind logger context
log = base_logger.bind(context="cli.mock")


def validate_speed(speed: float) -> float:
    """Validate speed multiplier is within valid range.

    CLI wrapper around unified validate_numeric_range() (P1-6 consolidation).

    Args:
        speed: Speed multiplier to validate

    Returns:
        speed if valid

    Raises:
        typer.BadParameter: If speed is outside valid range [0.1, 100.0]
    """
    try:
        return validate_numeric_range(speed, 0.1, 100.0, "speed")
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def validate_file_exists(path: Optional[Path]) -> Optional[Path]:
    """Validate that file exists if path is provided.

    CLI wrapper around unified validate_file_path() (P1-6 consolidation).

    Args:
        path: File path to validate (None is valid)

    Returns:
        path if valid or None

    Raises:
        typer.BadParameter: If file does not exist or is not a file
    """
    if path is None:
        return None

    try:
        return validate_file_path(path, must_exist=True)
    except (FileNotFoundError, IsADirectoryError) as e:
        raise typer.BadParameter(str(e)) from e


def validate_mutual_exclusivity(
    load_from: Optional[Path], random: bool
) -> tuple[Optional[Path], bool]:
    """Validate that --load-from and --random are mutually exclusive.

    Args:
        load_from: CSV file path for replay mode
        random: Random generation mode flag

    Returns:
        Tuple of validated (load_from, random)

    Raises:
        typer.BadParameter: If both options are provided
    """
    if load_from and random:
        msg = "Cannot use both --load-from and --random. Choose one mode."
        raise typer.BadParameter(msg)

    if not load_from and not random:
        msg = "Must specify either --load-from (replay mode) or --random (generation mode)"
        raise typer.BadParameter(msg)

    return load_from, random


def mock(
    # Mock data acquisition options (from TestingOptions)
    load_from: Optional[Path] = TestingOptions.load_from,
    random: bool = TestingOptions.random,
    events: Optional[int] = TestingOptions.events,
    speed: float = TestingOptions.speed,
    shuffle: bool = TestingOptions.shuffle,
    seed: Optional[int] = TestingOptions.seed,
    # Output options
    workspace: Optional[Path] = OutputOptions.workspace,
    filename_prefix: Optional[str] = OutputOptions.filename_prefix,
    # Logging options
    verbose: bool = LoggerOptions.verbose,
    logfile: str = LoggerOptions.logfile,
) -> None:
    """Run mock data acquisition for testing without hardware.

    This command allows developers to test DAQ functionality by either:
    1. Replaying events from a recorded CSV file (--load-from)
    2. Generating synthetic random events (--random)

    The mock device (Mocker or RandomMocker) behaves like a real Device,
    allowing the Sampler to work identically in both mock and real modes.

    Examples:
        Replay from CSV:
            $ haniwers-v1 mock --load-from data/run.csv --events 100

        Generate random data:
            $ haniwers-v1 mock --random --events 500

        Fast replay with shuffling:
            $ haniwers-v1 mock --load-from data.csv --speed 10.0 --shuffle

        Reproducible random generation:
            $ haniwers-v1 mock --random --events 1000 --seed 42

    Note:
        - Speed range: 0.1 (10x slower) to 100.0 (100x faster)
        - Output files go to sandbox/mock/ by default (clearly separated from real data)
        - Use Ctrl+C to stop acquisition early
    """
    # === Validation Phase (T019-T021) ===
    log.info("Starting mock DAQ acquisition")

    # Validate speed range (T020)
    try:
        speed = validate_speed(speed)
    except typer.BadParameter as e:
        log.error(f"Invalid speed: {e}")
        raise

    # Validate file existence (T019)
    try:
        load_from = validate_file_exists(load_from)
    except typer.BadParameter as e:
        log.error(f"File validation failed: {e}")
        raise

    # Validate mutual exclusivity (T021)
    try:
        load_from, random = validate_mutual_exclusivity(load_from, random)
    except typer.BadParameter as e:
        log.error(f"Mode selection error: {e}")
        raise

    # === Output Directory Handling (T022-T023) ===
    # Default output directory: sandbox/mock/
    output_path = Path(workspace) if workspace else Path("sandbox/mock")

    # Validate output path is not an existing file
    if output_path.exists() and not output_path.is_dir():
        raise typer.BadParameter(f"Output path exists but is not a directory: {output_path}")

    # Create directory if it doesn't exist
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        log.info(f"Created output directory: {output_path}")
    else:
        log.debug(f"Using existing output directory: {output_path}")

    # === Mock Device Initialization (T025) ===
    try:
        if load_from:
            # Replay mode with Mocker
            log.info(f"Loading events from CSV: {load_from}")
            mocker_config = MockerConfig(
                csv_path=load_from,
                shuffle=shuffle,
                speed=speed,
                jitter=0.0,  # No jitter for now (can be added later)
                loop=False,  # Don't loop in CLI mode
            )
            device = Mocker(mocker_config)
            log.info(f"Initialized Mocker with {len(device.events)} events")

        else:  # random mode
            # Random generation with RandomMocker
            log.info("Initializing random data generation")
            mocker_config = MockerConfig(
                csv_path=None,
                shuffle=False,  # Not applicable for random
                speed=speed,
                jitter=0.0,
                loop=False,
            )
            device = RandomMocker(mocker_config, seed=seed)
            if seed is not None:
                log.info(f"Using random seed: {seed} (reproducible mode)")
            else:
                log.info("Using random seed: None (non-reproducible mode)")

    except Exception as e:
        log.error(f"Failed to initialize mock device: {e}")
        raise typer.Exit(code=1)

    # === DAQ Configuration (T023) ===
    try:
        # Determine event count
        if events:
            event_count = events
        else:
            # For replay mode without --events, use all available events
            if load_from:
                event_count = len(device.events)
                log.info(f"No --events specified, using all {event_count} events from CSV")
            else:
                # For random mode, must specify --events
                msg = "Must specify --events for random generation mode"
                log.error(msg)
                raise typer.BadParameter(msg)

        # Create Sampler configuration
        # Use filename_prefix from OutputOptions, default to "mock_data"
        prefix = filename_prefix or "mock_data"
        sampler_config = SamplerConfig(
            label="mock",
            workspace=str(output_path),
            filename_prefix=prefix,  # T023: Custom prefix
            filename_suffix=".csv",
            events_per_file=event_count,
            number_of_files=1,
            stream_mode=True,  # real-time output
            mode="count_based",
        )
        log.debug(f"Sampler config: {sampler_config.label}, events={event_count}, prefix={prefix}")

    except Exception as e:
        log.error(f"Failed to create DAQ configuration: {e}")
        raise typer.Exit(code=1)

    # === Data Acquisition (T025) ===
    try:
        log.info(f"Starting acquisition of {event_count} events")

        # Run acquisition session (handles Sampler initialization and data collection)
        run_session("mock", device, sampler_config, output_path)

        log.info(f"Successfully completed mock DAQ acquisition")

        # Report output file location (T024)
        # Sampler creates files with run numbers, so we need to find the latest
        output_files = list(output_path.glob(f"{prefix}_*.csv"))
        if output_files:
            latest_file = max(output_files, key=lambda p: p.stat().st_mtime)
            log.info(f"Saved events to: {latest_file}")
        else:
            log.warning("No output file found (this should not happen)")

    except KeyboardInterrupt:
        log.info("Mock acquisition interrupted by user (Ctrl+C)")
        raise typer.Exit(code=0)

    except Exception as e:
        log.error(f"Mock acquisition failed: {e}")
        raise typer.Exit(code=1)
