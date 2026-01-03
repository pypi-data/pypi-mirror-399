"""Data acquisition command.

This module provides the 'daq' command for collecting cosmic ray event data
from the OSECHI detector. It handles configuration loading, CLI option overrides,
validation, directory creation, and initiates the data acquisition session.

Features:
    - Load configuration from TOML files or environment variables
    - Override config settings via CLI options (precedence: CLI > env > config)
    - Validate all settings before starting DAQ
    - Support CLI-only mode (no config file required)
    - Support config file mode with partial CLI overrides

Architecture: Clear & Unified Flow

  ┌─────────────────────────────────────┐
  │  Config File (TOML)                 │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  ConfigLoader                       │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  cfg = HaniwersConfig               │
  │  ├── device → DeviceConfig          │
  │  └── sampler → SamplerConfig ◄──────┼─── PRIMARY FOR DAQ
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  CLI Overrides (only cfg.sampler)   │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  Validation                         │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  Device.connect()                   │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  Create timestamped workspace       │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  Sampler(device, cfg.sampler)       │
  │  sampler.run(files=...)             │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │  Device.disconnect()                │
  └─────────────────────────────────────┘


"""

import typer
from pathlib import Path
from datetime import datetime
from typing import Optional

from haniwers.v1.config.loader import ConfigLoader
from haniwers.v1.config.overrider import ConfigOverrider
from haniwers.v1.config.model import DeviceConfig, SamplerConfig, MockerConfig
from haniwers.v1.log.logger import configure_logging, logger
from haniwers.v1.daq.device import Device
from haniwers.v1.daq.mocker import RandomMocker
from haniwers.v1.daq.sampler import Sampler
from haniwers.v1.helpers.console import print_info, print_error
from haniwers.v1.cli.options import (
    ConfigOptions,
    DeviceOptions,
    LoggerOptions,
    OutputOptions,
    SamplerOptions,
    TestingOptions,
)


def daq(
    ctx: typer.Context,
    # Configuration file
    config: Optional[Path] = ConfigOptions.config,
    # Device options
    port: Optional[str] = DeviceOptions.port,
    baudrate: Optional[int] = DeviceOptions.baudrate,
    timeout: Optional[float] = DeviceOptions.timeout,
    # Output options
    workspace: Path = OutputOptions.workspace,
    filename_prefix: Optional[str] = OutputOptions.filename_prefix,
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
    """Run data acquisition to collect cosmic ray events.

    Supports three usage modes:

    **CLI-only** (no config file):
        $ haniwers-v1 daq --port /dev/ttyUSB0 --workspace ./output \\
          --filename-prefix run001 --events-per-file 1000

    **Config file** (all settings from TOML):
        $ haniwers-v1 daq --config daq.toml

    **Config with CLI overrides** (mix of both):
        $ haniwers-v1 daq --config daq.toml --port /dev/ttyUSB1 --workspace ./exp02

    **Mode Resolution** (determines count_based vs time_based acquisition):

    The command determines the acquisition mode through the following precedence
    (highest to lowest priority):

    1. **Explicit --mode flag**: Direct specification wins
        Example: `haniwers-v1 daq --config config.toml --mode time_based`

    2. **Implicit --duration flag**: Automatically switches to time_based mode
        Example: `haniwers-v1 daq --config config.toml --duration 60`
        (mode is set to time_based even if config says count_based)

    3. **Config [sampler] section**: Uses configured mode
        Example: `haniwers-v1 daq --config config.toml`
        (uses mode from [sampler] mode = "count_based" or "time_based")

    4. **Default fallback**: count_based mode
        (used when no mode specified anywhere)

    Configuration precedence (highest to lowest):
    1. CLI options (--port, --workspace, etc.)
    2. Environment variables (HANIWERS_DEVICE_PORT, etc.)
    3. TOML configuration file
    4. Built-in defaults

    Exit codes:
        0: Success
        1: Configuration error, validation failure, or DAQ runtime error
        2: Serial port permission error (rare)
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
        overrider.apply_device_overrides(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
        )

        # Timestamped subdirectory under workspace
        today = datetime.now().strftime("%Y%m%d")
        overrider.apply_sampler_overrides(
            workspace=workspace / today,
            filename_prefix=filename_prefix,
            events_per_file=events_per_file,
            number_of_files=number_of_files,
            stream_mode=stream_mode,
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
        overrider.validate("device", "sampler", "mocker")
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
        # Create real Device from DeviceConfig and establish connection
        device = Device(cfg.device)
        logger.debug("Create real Device from DeviceConfig")

    # Main: Connect device and start taking data
    try:
        # Connect device
        device.connect()

        # Retrieve device MAC address for filename traceability
        mac_address = device.get_mac_address()
        logger.debug(f"Device MAC address: {mac_address}")

        # Create workspace directory (and its subdirectories)
        workspace = Path(cfg.sampler.workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        print_info(f"Saving files to {workspace.absolute()}")

        # Run DAQ session with connected device using SamplerConfig
        print_info("Press Ctrl-c to stop")
        sampler = Sampler(device=device, config=cfg.sampler, mac_address=mac_address)
        sampler.run(files=cfg.sampler.number_of_files)
    except KeyboardInterrupt as e:
        print_info(f"DAQ stopped: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"DAQ failed: {e}")
        raise typer.Exit(code=1)
    finally:
        # Clean up: disconnect device
        device.disconnect()
        # Display summary of skipped invalid lines if any
        invalid_count = sampler.reader.get_invalid_count()
        if invalid_count > 0:
            print_info(f"Skipped {invalid_count} invalid/empty detector lines during acquisition")
        print_info(f"Files saved to {workspace.absolute()}.")
        print_info("Rename the directory if you start another run.")
