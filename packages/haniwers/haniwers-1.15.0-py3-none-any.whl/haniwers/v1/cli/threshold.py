"""Threshold management commands.

This module provides commands for writing threshold values to OSECHI detector
channels using a unified configuration interface.

Commands:
    write: Write threshold values to detector channels (single or multi-channel)
    fit: Placeholder for threshold fitting functionality
    optimize: Placeholder for optimal threshold optimization
    list: Placeholder for listing current threshold configurations

Dependencies:
    - ConfigLoader: Load configuration from TOML files
    - Device: Serial communication with detector
    - apply_thresholds: High-level batch threshold application with retry and logging
    - SensorConfig: Configuration model for detector channels
    - parse_thresholds: Parse and validate threshold configuration strings
"""

import typer
import pendulum
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
from serial import SerialException

from haniwers.v1.config.loader import ConfigLoader
from haniwers.v1.config.overrider import ConfigOverrider
from haniwers.v1.config.model import DeviceConfig, SamplerConfig, MockerConfig, SensorConfig
from haniwers.v1.daq.model import RawEvent
from haniwers.v1.daq.device import Device
from haniwers.v1.daq.mocker import RandomMocker
from haniwers.v1.helpers.parser import parse_thresholds
from haniwers.v1.helpers.validator import validate_threshold_ranges
from haniwers.v1.threshold.writer import apply_threshold, apply_thresholds
from haniwers.v1.threshold.model import ThresholdScanResult
from haniwers.v1.threshold.fitter import (
    fit_thresholds,
    verify_fit_quality,
    plot_fit_results,
)
from haniwers.v1.daq.sampler import Sampler
from haniwers.v1.log.logger import logger, configure_logging
from haniwers.v1.helpers.console import print_info, print_success, print_error, print_warning
from haniwers.v1.cli.options import (
    ConfigOptions,
    DeviceOptions,
    LoggerOptions,
    OutputOptions,
    SamplerOptions,
    ScanOptions,
    ThresholdOptions,
    TestingOptions,
)

app = typer.Typer(help="Threshold management commands")


def _apply_overrides(config, overrides: dict) -> None:
    """Apply overrides to configuration object

    Args:
        config: Configuration object to override (e.g. cfg.device)
        overrides: Dict of {attribute_name: value}
    """
    for key, value in overrides.items():
        if value is not None:
            logger.info(f"Overriding: {key} = {value}")
            setattr(config, key, value)


def count_hits_by_channel(events: list[RawEvent]) -> dict[str, int]:
    """Count events where each channel has value >0"""
    return {
        "top": sum(1 for e in events if e.top > 0),
        "mid": sum(1 for e in events if e.mid > 0),
        "btm": sum(1 for e in events if e.btm > 0),
    }


def get_all_thresholds(sensors: dict[str, SensorConfig]) -> dict[str, int | None]:
    """Get current threshold values for all channels."""

    return {sensor.name: sensor.threshold for sensor in sensors.values()}


@app.command()
def write(
    ctx: typer.Context,
    # Configuration file
    config: Optional[Path] = ConfigOptions.config,
    # Device options
    port: Optional[str] = DeviceOptions.port,
    baudrate: Optional[int] = DeviceOptions.baudrate,
    timeout: Optional[float] = DeviceOptions.timeout,
    # Threshold options
    thresholds: str = ThresholdOptions.thresholds,
    max_retry: int = ThresholdOptions.max_retry,
    history: Path = ThresholdOptions.history,
    # Output options
    workspace: Path = OutputOptions.workspace,
    filename_prefix: Optional[str] = OutputOptions.filename_prefix,
    filename_suffix: Optional[str] = OutputOptions.filename_suffix,
    # Sampler options
    events_per_file: Optional[int] = SamplerOptions.events_per_file,
    number_of_files: Optional[int] = SamplerOptions.number_of_files,
    stream_mode: bool = SamplerOptions.stream_mode,
    mode: Optional[str] = SamplerOptions.mode,
    duration: Optional[float] = SamplerOptions.duration,
    # Testing options
    mock: bool = TestingOptions.mock,
    load_from: Optional[Path] = TestingOptions.load_from,
    speed: float = TestingOptions.speed,
    shuffle: bool = TestingOptions.shuffle,
    jitter: float = TestingOptions.jitter,
    loop: bool = TestingOptions.loop,
    # Logging options
    verbose: bool = LoggerOptions.verbose,
    logfile: str = LoggerOptions.logfile,
) -> None:
    """Write threshold values to detector channels.

    This command writes threshold values to the three detector layers
    (top, middle, bottom). The threshold determines the detector's sensitivity
    to cosmic ray signals.

    Supports single-channel or multi-channel configuration using the unified
    --thresholds option. Includes automatic retry logic on communication failures
    and audit trail logging to CSV file.

    Args:
        thresholds: Threshold configuration as 'channel:value;channel:value;...'
            Examples:
            - Single channel: '1:280'
            - All channels: '1:290;2:320;3:298'

    Output:
        For each channel, displays:
        - Status icon: ✓ (success) or ✗ (failed)
        - Channel number and status
        - Threshold value written (vth)
        - Number of attempts (1 = immediate success, >1 = retried)

    Examples:
        Write to single channel:
            $ haniwers-v1 threshold write --port /dev/tty.usbserial --thresholds 1:280

        Write to multiple channels:
            $ haniwers-v1 threshold write --port /dev/tty.usbserial --thresholds '1:290;2:320;3:298'

        With custom workspace and max retries:
            $ haniwers-v1 threshold write --port /dev/tty.usbserial --thresholds '1:280' \\
                --workspace data --max-retry 5

    Note:
        The device must be powered on and connected before running this command.
        Logs are automatically created in YYYYMMDD directory matching DAQ structure.
        Each threshold write is logged to CSV with timestamp for audit trail.
    """

    # Step 1: Configure logging with verbose option
    configure_logging(verbose=verbose, logfile=logfile)

    # Step 2: Determine config path (command-level --config takes precedence over global --config)
    config_path = config or ctx.obj.get("config_path")

    # Step 3: Load configuration file (or use defaults if no file specified)
    try:
        loader = ConfigLoader(config_path)
        cfg = loader.config

        overrider = ConfigOverrider(cfg)
        overrider.apply_device_overrides(port=port, baudrate=baudrate, timeout=timeout)

        # Timestamped subdirectory under workspace
        today = datetime.now().strftime("%Y%m%d")
        overrider.apply_sampler_overrides(
            workspace=workspace / today,
            filename_prefix=filename_prefix,
            events_per_file=events_per_file,
            number_of_files=1,
            stream_mode=False,
            mode=mode,
            duration=duration,
        )

        overrider.apply_mocker_overrides(
            csv_path=load_from,
            shuffle=shuffle,
            speed=speed,
            jitter=jitter,
            loop=loop,
        )

        if thresholds is not None:
            threshold_dict = parse_thresholds(thresholds)
            overrider.apply_sensor_overrides(
                thresholds=threshold_dict,
            )

        overrider.validate("device", "sampler", "mocker", "sensors")
    except (FileNotFoundError, ValueError, AttributeError) as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        raise typer.Exit(code=1)

    # Step 4: Create device (real or mock)
    if mock:
        # Use RandomMocker for testing without hardware
        device = RandomMocker(cfg.mocker)
        logger.debug("Using RandomMocker for testing (--mock enabled)")
        # Force change filename_prefix for distinction
        cfg.sampler.filename_prefix = "mock_data"
    else:
        # Create real Device from DeviceConfig
        device = Device(cfg.device)
        logger.debug("Create real Device from DeviceConfig")

    # Main: Connect device and write thresholds
    try:
        device.connect()

        # Create workspace directory (and its subdirectories)
        workspace = Path(cfg.sampler.workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        print_info(f"Saving files to {workspace.absolute()}")
        history_path = workspace / history

        # Filter to only sensors with configured thresholds (threshold != None)
        sensors_to_write = [s for s in cfg.sensors.values() if s.threshold is not None]

        results = apply_thresholds(
            device,
            sensors_to_write,
            max_retry=max_retry,
            history_path=history_path,
        )
        logger.debug(f"Threshold application complete: {len(results)} results received")

        # Display results to user
        all_success = True
        print_info("\nThreshold Write Results:")

        for result in results:
            if result.success:
                print_success(
                    f"Channel {result.id}: Success (vth={result.vth}, attempts={result.attempts})"
                )
            else:
                print_error(
                    f"Channel {result.id}: Failed (vth={result.vth}, attempts={result.attempts})"
                )
                all_success = False

    except SerialException as e:
        print_error(f"Cannot connect to the device: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Threshold write failed: {e}")
        raise typer.Exit(code=1)

    finally:
        # Clean up: disconnect device
        device.disconnect()

        if not all_success:
            raise typer.Exit(code=1)


@app.command()
def serial(
    ctx: typer.Context,
    # Configuration file
    config: Optional[Path] = ConfigOptions.config,
    # Device options
    port: Optional[str] = DeviceOptions.port,
    baudrate: Optional[int] = DeviceOptions.baudrate,
    timeout: Optional[float] = DeviceOptions.timeout,
    # Threshold options
    thresholds: str = ThresholdOptions.thresholds,
    suppress_threshold: int = ThresholdOptions.suppress_threshold,
    max_retry: int = ThresholdOptions.max_retry,
    history: Path = ThresholdOptions.history,
    # Output options
    workspace: Optional[Path] = OutputOptions.workspace,
    filename_prefix: Optional[str] = OutputOptions.filename_prefix,
    filename_suffix: Optional[str] = OutputOptions.filename_suffix,
    # Sampler options
    events_per_file: Optional[int] = SamplerOptions.events_per_file,
    number_of_files: Optional[int] = SamplerOptions.number_of_files,
    stream_mode: bool = SamplerOptions.stream_mode,
    mode: Optional[str] = SamplerOptions.mode,
    duration: Optional[float] = SamplerOptions.duration,
    # Threshold parameters
    nsteps: int = ScanOptions.nsteps,
    step: int = ScanOptions.step,
    # Testing options
    mock: bool = TestingOptions.mock,
    load_from: Optional[Path] = TestingOptions.load_from,
    speed: float = TestingOptions.speed,
    shuffle: bool = TestingOptions.shuffle,
    jitter: float = TestingOptions.jitter,
    loop: bool = TestingOptions.loop,
    # Logging options
    verbose: bool = LoggerOptions.verbose,
    logfile: str = LoggerOptions.logfile,
) -> None:
    """Run serial threshold scanning for detector characterization.

    Scans one or more detector channels across a range of threshold values,
    collecting cosmic ray event data at each threshold level. Results are
    saved to CSV files for analysis.

    Threshold operations are logged to threshold_operations.csv in the workspace
    directory for complete audit trail and reproducibility. Each threshold write
    (suppress and measurement) is recorded with timestamp, channel, value, success
    status, and retry count.

    This command is useful for:
    - Measuring detector sensitivity curves
    - Comparing channel responses
    - Characterizing detector behavior

    Example commands:

        Single-channel scan with mock device:
        $ haniwers-v1 threshold serial --thresholds "1:250" \\
            --nsteps 5 --step 10 --duration 2 --mock

        Multi-channel scan with TOML config:
        $ haniwers-v1 threshold serial --config config.toml

        Override TOML parameters with CLI:
        $ haniwers-v1 threshold serial --config config.toml \\
            --thresholds "1:300;2:320" --duration 3

    Output files (saved in workspace/YYYYMMDD/):
    - scan_results_ch1.csv, scan_results_ch2.csv, ...: Threshold scan data
    - threshold_operations.csv: Audit log of all threshold changes (timestamp,
      id, vth, success, attempts)

    Note:
        Requires a TOML configuration file with sensor definitions, unless all
        parameters are provided via CLI options.
    """

    # Step 1: Configure logging with verbose option
    configure_logging(verbose=verbose, logfile=logfile)

    # Step 2: Determine config path
    config_path = config or ctx.obj.get("config_path")

    # Step 3: Load configuration file (or use defaults if no file specified)
    try:
        loader = ConfigLoader(config_path)
        cfg = loader.config

        overrider = ConfigOverrider(cfg)
        overrider.apply_device_overrides(port=port, baudrate=baudrate, timeout=timeout)

        # Timestamped subdirectory under workspace
        today = datetime.now().strftime("%Y%m%d")
        overrider.apply_sampler_overrides(
            workspace=workspace / today,
            filename_prefix=filename_prefix,
            events_per_file=events_per_file,
            number_of_files=1,
            stream_mode=False,
            mode=mode,
            duration=duration,
        )

        overrider.apply_mocker_overrides(
            csv_path=load_from,
            shuffle=shuffle,
            speed=speed,
            jitter=jitter,
            loop=loop,
        )

        if thresholds is not None:
            threshold_dict = parse_thresholds(thresholds)
            overrider.apply_sensor_overrides(
                centers=threshold_dict,
                nsteps=nsteps,
                step_size=step,
                threshold=suppress_threshold,
            )

        overrider.validate("device", "sampler", "mocker", "sensors")

    except (FileNotFoundError, ValueError, AttributeError) as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        raise typer.Exit(code=1)

    # Step 4: Create device (real or mock)
    if mock:
        # Use RandomMocker for testing without hardware
        device = RandomMocker(cfg.mocker)
        logger.debug("Using RandomMocker for testing (--mock enabled)")
        # Force change filename_prefix for distinction
        cfg.sampler.filename_prefix = "mock_data"
    else:
        # Create real Device from DeviceConfig
        device = Device(cfg.device)
        logger.debug("Create real Device from DeviceConfig")

    # Main: Connect device and start scanning
    try:
        device.connect()

        # Create workspace directory (and its subdirectories)
        workspace = Path(cfg.sampler.workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        print_info(f"Saving files to {workspace.absolute()}")
        history_path = workspace / history
        result_csv = workspace / "serial.csv"

        logger.debug("STEP8.3: Build Sampler instance")
        cfg.sampler.stream_mode = False
        sampler = Sampler(device, cfg.sampler)

        # Applying suppress thresholds to sensors")
        logger.debug("STEP8.4: Scan each sensor sequentially")
        for sensor in cfg.sensors.values():
            logger.info("Apply suppress thresholds to all sensors before measuring new sensor")
            overrider.apply_sensor_overrides(threshold=cfg.sampler.suppress_threshold)
            overrider.validate("sensors")

            results = apply_thresholds(
                device,
                cfg.sensors.values(),
                max_retry=max_retry,
                history_path=history_path,
            )

            logger.debug(f"Threshold application complete: {len(results)} results received")

            logger.info(f"Applying measure thresholds to {sensor.name}")
            scan_range = sensor.threshold_range()

            for vth in scan_range:
                check = get_all_thresholds(cfg.sensors)
                logger.debug(f"{check=}")
                sensor.threshold = vth
                apply_threshold(device, sensor, history_path=history_path)
                check = get_all_thresholds(cfg.sensors)
                logger.debug(f"{check=}")

                events = sampler.run(mode="time_based", files=1)
                thresholds = get_all_thresholds(cfg.sensors)
                hits = count_hits_by_channel(events)

                # Create ThresholdScanResult for this measurement point
                result = ThresholdScanResult(
                    timestamp=pendulum.now().to_iso8601_string(),
                    event_count=len(events),
                    ch1=thresholds.get("ch1", 0),
                    ch2=thresholds.get("ch2", 0),
                    ch3=thresholds.get("ch3", 0),
                    top=hits.get("top", 0),
                    mid=hits.get("mid", 0),
                    btm=hits.get("btm", 0),
                )
                logger.debug(f"{events=}")
                logger.debug(f"{len(events)=}")
                logger.success(f"{result=}")

                # Convert result to CSV format and write
                result_dict = result._asdict()
                with result_csv.open(mode="a", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(result_dict.keys()))
                    writer.writerow(result_dict)
    except SerialException as e:
        print_error(f"Cannot connect to the device: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Threshold write failed: {e}")
        raise typer.Exit(code=1)
    finally:
        device.disconnect()
        raise typer.Exit(code=0)


@app.command()
def parallel(
    ctx: typer.Context,
    # Configuration file
    config: Optional[Path] = ConfigOptions.config,
    # Device options
    port: Optional[str] = DeviceOptions.port,
    baudrate: Optional[int] = DeviceOptions.baudrate,
    timeout: Optional[float] = DeviceOptions.timeout,
    device_label: Optional[str] = DeviceOptions.device_label,
    # Threshold options
    thresholds: str = ThresholdOptions.thresholds,
    max_retry: int = ThresholdOptions.max_retry,
    history: Path = ThresholdOptions.history,
    # Scan parameters
    nsteps: int = ScanOptions.nsteps,
    step: int = ScanOptions.step,
    # Duration is shared with SamplerOptions for consistency across commands
    duration: Optional[float] = SamplerOptions.duration,
    # Output options
    workspace: Optional[Path] = OutputOptions.workspace,
    filename_prefix: Optional[str] = OutputOptions.filename_prefix,
    filename_suffix: Optional[str] = OutputOptions.filename_suffix,
    # Sampler options
    events_per_file: Optional[int] = SamplerOptions.events_per_file,
    number_of_files: Optional[int] = SamplerOptions.number_of_files,
    stream_mode: bool = SamplerOptions.stream_mode,
    # Testing options
    mock: bool = TestingOptions.mock,
    # Logging options
    verbose: bool = LoggerOptions.verbose,
    logfile: str = LoggerOptions.logfile,
) -> None:
    """Run parallel threshold scanning for detector characterization.

    Scans all detector channels across a range of threshold values in parallel.
    All channels step together at each measurement point, with all active during
    data collection (unlike serial mode). This provides 3x speedup vs serial scan.

    Threshold operations are logged to threshold_operations.csv in the workspace
    directory for complete audit trail and reproducibility. Each threshold write
    is recorded with timestamp, channel, value, success status, and retry count.
    Unlike serial mode, parallel mode has no suppress phase.

    Results are saved to CSV files for analysis, one per channel.

    This command is useful for:
    - Fast threshold characterization of all channels simultaneously
    - Collecting synchronized measurements from multiple channels
    - Comparing detector responses in parallel

    Example commands:

        Parallel scan with mock device (all channels step together):
        $ haniwers-v1 threshold parallel --nsteps 5 --step 10 --duration 2 --mock

        Multi-channel parallel scan with TOML config:
        $ haniwers-v1 threshold parallel --config config.toml

        Override TOML parameters with CLI:
        $ haniwers-v1 threshold parallel --config config.toml \\
            --thresholds "1:300;2:320;3:298" --duration 3

    Output files (saved in workspace/YYYYMMDD/):
    - scan_results_ch1.csv, scan_results_ch2.csv, ...: Threshold scan data
    - threshold_operations.csv: Audit log of all threshold changes (timestamp,
      id, vth, success, attempts)

    Note:
        Requires a TOML configuration file with sensor definitions, unless all
        parameters are provided via CLI options. All channels must have matching
        nsteps and step_size values.
    """

    # Step 1: Configure logging with verbose option
    configure_logging(verbose=verbose, logfile=logfile)
    logger.debug("STEP1: Configure logging")
    logger.debug(f"|--{verbose=}")
    logger.debug(f"|--{logfile=}")

    # Step 2: Determine config path
    logger.debug("STEP2: Determine config path")
    config_path = config or ctx.obj.get("config_path")
    logger.debug(f"|--{config=}")

    # Step 3: Load configuration file (or use defaults if no file specified)
    logger.debug("STEP3: Load configuration")
    try:
        loader = ConfigLoader(config_path)
        cfg = loader.config
    except FileNotFoundError as e:
        print_error(f"Config file not found: {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        print_error(f"Invalid configuration: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        raise typer.Exit(code=1)

    # Step 4: Apply CLI option overrides
    logger.debug("STEP4: Apply CLI options")
    try:
        # Device overrides
        logger.debug("STEP4.1: Override DeviceOptions")
        logger.debug(f"|--{port=}")
        logger.debug(f"|--{baudrate=}")
        logger.debug(f"|--{timeout=}")
        logger.debug(f"|--{device_label=}")
        device_overrides = {
            "port": port,
            "baudrate": baudrate,
            "timeout": timeout,
            "label": device_label,
        }
        _apply_overrides(cfg.device, device_overrides)

        # Sampler/Output overrides
        logger.debug("STEP4.2: Override OutputOptions")
        logger.debug(f"|--{workspace=}")
        logger.debug(f"|--{filename_prefix=}")
        logger.debug(f"|--{filename_suffix=}")
        logger.debug(f"|--{events_per_file=}")
        logger.debug(f"|--{number_of_files=}")
        logger.debug(f"|--{duration=}")
        logger.debug(f"|--{stream_mode=}")
        sampler_overrides = {
            "workspace": str(workspace) if workspace else None,
            "filename_prefix": filename_prefix,
            "filename_suffix": filename_suffix,
            "events_per_file": events_per_file,
            "number_of_files": number_of_files,
            "stream_mode": False,
            "duration": duration,
        }
        _apply_overrides(cfg.sampler, sampler_overrides)

        # Validation
        logger.debug("STEP4.3: Validate configuration overrides")
        DeviceConfig.model_validate(cfg.device.model_dump())
        SamplerConfig.model_validate(cfg.sampler.model_dump())
    except (ValueError, AttributeError) as e:
        logger.error(str(e))
        print_error(str(e))
        raise typer.Exit(code=1)

    # Create device (real or mock based on --mock flag)
    if mock:
        logger.debug("Create RandomMocker from MockerConfig")
        logger.debug(f"|--{cfg.mocker.csv_path=}")
        logger.debug(f"|--{cfg.mocker.jitter=}")
        logger.debug(f"|--{cfg.mocker.speed=}")
        # Use RandomMocker for testing without hardware
        device = RandomMocker(cfg.mocker)
        logger.debug("Using RandomMocker for testing (--mock enabled)")
    else:
        # Create real Device from DeviceConfig and establish connection
        logger.debug("Create real Device from DeviceConfig and establish connection")
        device = Device(cfg.device)

    # Step 5: Connect device and apply thresholds
    logger.debug("STEP5: Connect device and apply thresholds")
    try:
        device.connect()
    except SerialException as e:
        print_error(f"Cannot connect to the device: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Threshold write failed: {e}")
        raise typer.Exit(code=1)

    # STEP6: Build SensorConfig for each threshold
    logger.debug("STEP6: Build SensorConfig for each threshold")

    # STEP6.1: Parse and validate threshold configuration
    logger.debug("STEP6.1: Parse and validate threshold configuration")
    logger.debug(f"|--{thresholds=}")
    logger.debug(f"|--{max_retry=}")
    try:
        threshold_dict = parse_thresholds(thresholds)
    except ValueError as e:
        logger.error(str(e))
        print_error(str(e))
        raise typer.Exit(code=1)

    if threshold_dict:
        for ch, vth in sorted(threshold_dict.items()):
            logger.debug(f"|--{ch=}")
            logger.debug(f"|--{vth=}")
            for sensor in cfg.sensors.values():
                if sensor.id == ch:
                    sensor.threshold = int(vth)
                    sensor.center = int(vth)

    # STEP6.2: Override ScanOptions
    logger.debug(f"STEP6.2: Applying scan parameters to {len(cfg.sensors)} sensors")
    for sensor in cfg.sensors.values():
        logger.debug(f"|--{nsteps=}")
        logger.debug(f"|--{step=}")
        sensor.nsteps = nsteps
        sensor.step_size = step

    # STEP7: Create timestamped subdirectory under workspace
    logger.debug("STEP7: Create timestamped subdirectory")
    today = datetime.now().strftime("%Y%m%d")
    timestamped_workspace = Path(cfg.sampler.workspace) / today
    timestamped_workspace.mkdir(parents=True, exist_ok=True)
    logger.debug(f"|--{timestamped_workspace}")

    # Apply all thresholds using batch API with retry and logging
    history_path = timestamped_workspace / history
    logger.debug(f"History log path: {history_path}")
    logger.debug(f"Applying thresholds with max_retry={max_retry}")

    # STEP8: Build Sampler
    cfg.sampler.stream_mode = False
    sampler = Sampler(device, cfg.sampler, timestamped_workspace)
    p = timestamped_workspace / "parallel.csv"

    # STEP9:
    sensors = cfg.sensors
    range1 = sensors["ch1"].threshold_range()
    range2 = sensors["ch2"].threshold_range()
    range3 = sensors["ch3"].threshold_range()

    n = len(range1)
    for i in range(n):
        sensors["ch1"].threshold = range1[i]
        sensors["ch2"].threshold = range2[i]
        sensors["ch3"].threshold = range3[i]

        apply_thresholds(
            device, cfg.sensors.values(), max_retry=max_retry, history_path=history_path
        )
        events = sampler.run(mode="time_based", files=1)
        thresholds = get_all_thresholds(cfg.sensors)
        hits = count_hits_by_channel(events)

        # Create ThresholdScanResult for this measurement point
        result = ThresholdScanResult(
            timestamp=pendulum.now().to_iso8601_string(),
            event_count=len(events),
            ch1=thresholds.get("ch1", 0),
            ch2=thresholds.get("ch2", 0),
            ch3=thresholds.get("ch3", 0),
            top=hits.get("top", 0),
            mid=hits.get("mid", 0),
            btm=hits.get("btm", 0),
        )
        logger.debug(f"{events=}")
        logger.debug(f"{len(events)=}")
        logger.success(f"{result=}")

        # Convert result to CSV format and write
        result_dict = result._asdict()
        with p.open(mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(result_dict.keys()))
            writer.writerow(result_dict)


def _parse_fit_parameters(parameters: Optional[str]) -> dict:
    """Parse fit parameters in global or per-channel format.

    Supports two formats:
    1. Global: "10,300,1,1" (height,mean,sigma,offset for all channels)
    2. Per-channel: "1:10,300,1,1;2:10,300,1,1"

    Args:
        parameters: Parameter string in one of the two formats above.
                   If None, uses default global parameters.

    Returns:
        Dictionary with channel number as key and parameter list as value.
        Example: {1: [10, 300, 1, 1], 2: [10, 300, 1, 1], 3: [10, 300, 1, 1]}

    Raises:
        ValueError: If parameters format is invalid or values are out of range.
    """
    # Default parameters if not specified
    if parameters is None:
        default_params = [10.0, 300.0, 1.0, 1.0]
        return {1: default_params, 2: default_params, 3: default_params}

    # Check if per-channel format (contains ':')
    if ":" in parameters:
        # Per-channel format: "1:10,300,1,1;2:10,300,1,1"
        params_dict = {}
        channel_params = parameters.split(";")

        for ch_spec in channel_params:
            ch_spec = ch_spec.strip()
            if not ch_spec:
                continue

            try:
                ch_str, params_str = ch_spec.split(":", 1)
                ch = int(ch_str.strip())
                params = [float(p.strip()) for p in params_str.split(",")]

                if ch not in [1, 2, 3]:
                    raise ValueError(f"Invalid channel: {ch}. Must be 1-3")
                if len(params) != 4:
                    raise ValueError(f"Channel {ch}: expected 4 parameters, got {len(params)}")

                params_dict[ch] = params
            except ValueError as e:
                raise ValueError(f"Invalid per-channel format '{ch_spec}': {e}")

        # Fill missing channels with defaults
        default_params = [10.0, 300.0, 1.0, 1.0]
        for ch in [1, 2, 3]:
            if ch not in params_dict:
                params_dict[ch] = default_params

        return params_dict
    else:
        # Global format: "10,300,1,1"
        try:
            params = [float(p.strip()) for p in parameters.split(",")]
            if len(params) != 4:
                raise ValueError(f"Expected 4 parameters, got {len(params)}")
            return {1: params, 2: params, 3: params}
        except ValueError as e:
            raise ValueError(f"Invalid global format: {e}")


@app.command()
def fit(
    read_from: Path = typer.Argument(
        ..., help="Directory containing threshold scan result CSV files"
    ),
    pattern: str = typer.Option(
        "*.csv", "--pattern", "-p", help="Filename pattern to search for scan data"
    ),
    parameters: Optional[str] = typer.Option(
        None,
        "--parameters",
        help="Initial fit parameters. Two formats supported:\n"
        "  1. Global: '10,300,1,1' (height,mean,sigma,offset for all channels)\n"
        "  2. Per-channel: '1:10,300,1,1;2:10,300,1,1' (channel:height,mean,sigma,offset)",
    ),
    verify: bool = typer.Option(
        False,
        "--verify",
        help="Perform verification checks on fit results (data quality, reasonableness)",
    ),
    plot: bool = typer.Option(
        False,
        "--plot",
        help="Generate and save interactive hvplot visualizations of fit results",
    ),
    workspace: Optional[Path] = OutputOptions.workspace,
    verbose: bool = LoggerOptions.verbose,
    logfile: str = LoggerOptions.logfile,
) -> None:
    """Calculate optimal thresholds from scan data using error function fitting.

    Analyzes threshold scan result data to estimate optimal threshold values
    using complementary error function (erfc) fitting. Results are saved to
    CSV files for use by other commands.

    The fitting process:
    1. Reads ThresholdScanResult CSV files from the specified directory
    2. Fits error function curves to event rate vs threshold data for each channel
    3. Calculates optimal thresholds at multiple sigma levels (0σ, 1σ, 3σ, 5σ)
    4. Saves results to CSV files for analysis and use by threshold write command

    Args:
        read_from: Directory containing threshold scan result CSV files
        pattern: Filename pattern for scan result files (default: "*.csv")
        parameters: Initial fit parameters in two formats:
                   - Global: "10,300,1,1" for all channels
                   - Per-channel: "1:10,300,1,1;2:10,300,1,1"
                   (default: "10,300,1,1" for all channels)
        workspace: Output directory for results (default: current directory)
        verbose: Enable verbose logging
        logfile: Log file path

    Output files:
        - `threshold_fit_results.csv`: Latest fit results for use by other commands

    Examples:
        Fit scan results with default settings:

            $ haniwers-v1 threshold fit ./scan_data

        With custom filename pattern:

            $ haniwers-v1 threshold fit ./scan_data --pattern "serial_*.csv"

        With per-channel fit parameters:

            $ haniwers-v1 threshold fit ./scan_data \\
                --parameters "1:5,280,2,0.5;2:5,310,2,0.5"

        Save to specific workspace:

            $ haniwers-v1 threshold fit ./scan_data --workspace ./results

    Notes:
        - Scan data must be in ThresholdScanResult CSV format
        - The 3σ level is typically used as the optimal threshold value
        - Results are saved with ISO8601 timestamps for audit trail
    """

    # Configure logging
    configure_logging(verbose=verbose, logfile=logfile)
    logger.debug(f"fit command started with read_from={read_from}, pattern={pattern}")

    # Parse fit parameters (global or per-channel)
    try:
        params_dict = _parse_fit_parameters(parameters)
        logger.debug(f"Parsed fit parameters: {params_dict}")
    except ValueError as e:
        print_error(f"Invalid fit parameters: {e}")
        raise typer.Exit(code=1)

    # Convert read_from to Path and check if it exists
    read_from = Path(read_from)
    if not read_from.is_dir():
        print_error(f"Directory not found: {read_from}")
        raise typer.Exit(code=1)

    # Set up workspace (use current directory if not specified)
    if workspace is None:
        workspace = Path.cwd()
    else:
        workspace = Path(workspace)

    workspace.mkdir(parents=True, exist_ok=True)

    # Find scan result files
    logger.debug(f"Searching for files matching pattern: {pattern}")
    scan_files = list(read_from.glob(pattern))

    if not scan_files:
        print_error(f"No files matching pattern '{pattern}' found in {read_from}")
        raise typer.Exit(code=1)

    print_info(f"Found {len(scan_files)} scan result file(s)")
    logger.debug(f"Scan files: {[f.name for f in scan_files]}")

    # Read and combine all scan data
    try:
        dfs = []
        for fname in scan_files:
            logger.debug(f"Reading {fname}")
            df = pd.read_csv(fname)
            dfs.append(df)

        if not dfs:
            print_error("No data could be read from scan files")
            raise typer.Exit(code=1)

        data = pd.concat(dfs, ignore_index=True)
        print_info(f"Loaded {len(data)} scan points from {len(scan_files)} file(s)")
        logger.debug(f"Data shape: {data.shape}")
        logger.debug(f"Data columns: {list(data.columns)}")

    except Exception as e:
        print_error(f"Failed to read scan data: {e}")
        logger.error(f"Exception: {str(e)}", exc_info=True)
        raise typer.Exit(code=1)

    # Perform fitting for each channel using per-channel parameters
    try:
        all_results = []
        for ch in [1, 2, 3]:
            ch_params = params_dict.get(ch, [10.0, 300.0, 1.0, 1.0])
            logger.debug(f"Fitting channel {ch} with parameters {ch_params}")
            result = fit_thresholds(data, channels=[ch], params=ch_params)
            all_results.append(result)

        thresholds = pd.concat(all_results, ignore_index=True)
        print_info("\nFitted Threshold Values:")
        print_info(thresholds.to_string(index=False))

    except Exception as e:
        print_error(f"Threshold fitting failed: {e}")
        logger.error(f"Exception: {str(e)}", exc_info=True)
        raise typer.Exit(code=1)

    # Save results
    try:
        # Save to history file (append mode)
        history_file = workspace / "thresholds_history.csv"
        if history_file.exists():
            thresholds.to_csv(history_file, mode="a", index=False, header=False)
            logger.debug(f"Appended to {history_file}")
        else:
            thresholds.to_csv(history_file, index=False)
            logger.debug(f"Created {history_file}")

        print_success(f"Saved to {history_file.absolute()}")

        # Save to latest file (overwrite mode)
        latest_file = workspace / "thresholds_latest.csv"
        thresholds.to_csv(latest_file, index=False)
        logger.debug(f"Created {latest_file}")
        print_success(f"Saved to {latest_file.absolute()}")

    except Exception as e:
        print_error(f"Failed to save results: {e}")
        logger.error(f"Exception: {str(e)}", exc_info=True)
        raise typer.Exit(code=1)

    # Perform verification if requested
    if verify:
        try:
            print_info("\nPerforming verification checks...")
            verification_results = verify_fit_quality(data, thresholds, verbose=True)

            # Check for any errors
            has_errors = any("error" in result for result in verification_results.values())
            if has_errors:
                print_warning("\nSome verification checks encountered errors")
                raise typer.Exit(code=1)

            # Check for warnings
            has_warnings = any(result.get("warnings") for result in verification_results.values())
            if has_warnings:
                print_warning("\nVerification completed with warnings (see above)")

        except Exception as e:
            print_error(f"Verification failed: {e}")
            logger.error(f"Exception: {str(e)}", exc_info=True)
            raise typer.Exit(code=1)

    # Generate visualizations if requested
    if plot:
        try:
            print_info("\nGenerating visualizations...")
            plot_output_dir = workspace / "threshold_plots"
            plot_metadata = plot_fit_results(
                data, thresholds, output_dir=plot_output_dir, verbose=verbose
            )

            print_success("Visualizations created:")
            for ch, metadata in sorted(plot_metadata.items()):
                plot_file = metadata["plot_file"]
                threshold_3sigma = metadata["threshold_3sigma"]
                data_points = metadata["data_points"]
                print_info(
                    f"  Channel {ch}: {plot_file.name} ({data_points} data points, "
                    f"3σ threshold: {threshold_3sigma})"
                )

        except Exception as e:
            print_error(f"Visualization generation failed: {e}")
            logger.error(f"Exception: {str(e)}", exc_info=True)
            raise typer.Exit(code=1)
