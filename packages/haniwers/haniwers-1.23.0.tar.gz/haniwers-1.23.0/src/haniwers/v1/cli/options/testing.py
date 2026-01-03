"""Testing options group."""

from pathlib import Path
from typing import Optional

import typer


class TestingOptions:
    """Testing option group.

    Contains options for testing without physical hardware, including mock data
    acquisition mode and synthetic data generation. Use with OutputOptions for
    filename_prefix and workspace settings. Options correspond to MockerConfig
    in config.model.MockerConfig for full CLI-to-config symmetry.
    """

    mock = typer.Option(
        False,
        "--mock",
        help="Use RandomMocker instead of real device for testing (no hardware required).",
        rich_help_panel="Testing",
    )
    """Mock mode option.

    When enabled, uses a simulated random detector instead of real hardware.
    Useful for testing without the physical OSECHI detector connected.

    Type: bool
    Default: False (use real device)
    """

    label = typer.Option(
        None,
        "--mocker-label",
        help="Label for mock configuration (e.g., 'replay-demo', 'stress-test'). "
        "Used for logging and documentation of mock runs.",
        rich_help_panel="Testing",
    )
    """Mock configuration label.

    Human-readable identifier for this mock/mocker configuration. Useful for
    organizing multiple test scenarios and tracking test results. Examples:
    'replay-demo', 'stress-test', 'validation-run'.

    Corresponds to: MockerConfig.label

    Type: Optional[str]
    Default: None (use config file value)
    """

    load_from = typer.Option(
        None,
        "--load-from",
        help="CSV file to replay (mutually exclusive with --random)",
        rich_help_panel="Testing",
    )
    """CSV file to replay.

    Path to a CSV file containing previously recorded detector data. When
    specified, the mock command replays events from this file instead of
    generating random data. Mutually exclusive with --random.

    Corresponds to: MockerConfig.csv_path

    Type: Optional[Path]
    Default: None (must specify --random or --load-from)
    """

    random = typer.Option(
        False,
        "--random",
        help="Generate random synthetic data (mutually exclusive with --load-from)",
        rich_help_panel="Testing",
    )
    """Random data generation mode.

    When enabled, generates synthetic random detector events instead of
    replaying from a file. Mutually exclusive with --load-from.

    Type: bool
    Default: False (use --load-from to replay file)
    """

    events = typer.Option(
        None,
        "--events",
        help="Number of events to acquire (default: all events in CSV for replay)",
        rich_help_panel="Testing",
    )
    """Event count option.

    Limit the number of events to process. For replay mode, defaults to all
    events in the CSV file. For random mode, generates this many events.

    Type: Optional[int]
    Default: None (all events for replay, or unlimited for generation)
    """

    speed = typer.Option(
        1.0,
        "--speed",
        help="Speed multiplier for replay/generation (0.1 to 100.0, default: 1.0)",
        rich_help_panel="Testing",
    )
    """Replay/generation speed multiplier.

    Scales the speed of event processing. Values > 1.0 speed up playback,
    values < 1.0 slow it down. Useful for testing with different data rates.

    Corresponds to: MockerConfig.speed

    Type: float
    Default: 1.0 (normal speed)
    Valid range: 0.1 to 100.0
    """

    shuffle = typer.Option(
        False,
        "--shuffle",
        help="Shuffle event order (replay mode only)",
        rich_help_panel="Testing",
    )
    """Event order shuffling option.

    When enabled, randomizes the order of events during replay. Useful for
    testing code that should be order-independent. Only applies to replay mode.

    Corresponds to: MockerConfig.shuffle

    Type: bool
    Default: False (preserve original event order)
    """

    jitter = typer.Option(
        0.0,
        "--jitter",
        min=0.0,
        help="Random timing variation in seconds (Gaussian noise std dev, default: 0.0). "
        "Adds realistic timing jitter to mock events.",
        rich_help_panel="Testing",
    )
    """Timing jitter for mock events.

    Amount of random timing variation (in seconds) to add to mock-generated
    events. Uses Gaussian (normal) distribution with this value as standard
    deviation. Useful for simulating realistic detector timing variations.
    Examples: 0.001 for 1ms jitter, 0.01 for 10ms jitter.

    Corresponds to: MockerConfig.jitter

    Type: float
    Default: 0.0 (no jitter)
    Valid range: >= 0.0
    """

    loop = typer.Option(
        True,
        "--loop/--no-loop",
        help="Loop back to start when CSV replay ends (default: --loop). "
        "When disabled (--no-loop), stop after reaching end of file.",
        rich_help_panel="Testing",
    )
    """Loop flag for CSV replay.

    When enabled, replay mode loops back to the beginning of the CSV file when
    reaching the end. When disabled, stops after all events are replayed once.
    This option only applies to CSV replay mode (--load-from), not random
    generation mode.

    Corresponds to: MockerConfig.loop

    Type: bool
    Default: True (loop enabled)
    """

    seed = typer.Option(
        None,
        "--seed",
        help="Random seed for reproducibility (random mode only)",
        rich_help_panel="Testing",
    )
    """Random seed for reproducibility.

    Sets the random seed for deterministic event generation. Use the same seed
    to reproduce identical random event sequences. Only applies to random mode.

    Type: Optional[int]
    Default: None (random seed each run)
    """
