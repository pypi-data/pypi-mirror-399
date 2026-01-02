"""Command Line Interface for the haniwers package.

This module provides various command-line tools for
data acquisition, processing, and analysis of
cosmic ray data collected with the OSECHI detector.

The CLI is built using Typer and provides the following commands:
- version: Display version information
- docs: Open online documentation
- ports: Search for available ports
- scan: Run threshold scanning
- fit: Calculate thresholds from scan data
- vth: Set threshold values
- daq: Run data acquisition
- raw2tmp: Quick parsing of raw data
- run2csv: Parse run data to CSV format
- mock_daq: Run simulated data acquisition (for debugging)
"""

import platform
import sys
import webbrowser
from pathlib import Path

import pandas as pd
import pendulum
import typer
from loguru import logger
from platformdirs import PlatformDirs
from typing_extensions import Annotated

from . import __version__

DOCS = {
    "home": "https://qumasan.gitlab.io/haniwers/docs/",
    "version": "https://qumasan.gitlab.io/haniwers/docs/command/version/",
    "scan": "https://qumasan.gitlab.io/haniwers/docs/command/scan/",
    "fit": "https://qumasan.gitlab.io/haniwers/docs/command/fit/",
    "vth": "https://qumasan.gitlab.io/haniwers/docs/command/vth/",
    "daq": "https://qumasan.gitlab.io/haniwers/docs/command/daq/",
    "raw2tmp": "https://qumasan.gitlab.io/haniwers/docs/command/raw2tmp/",
    "run2csv": "https://qumasan.gitlab.io/haniwers/docs/command/run2csv/",
}
"""URLs of online documents for each command."""


def _setup_logger(level="INFO") -> Path:
    """Configure loguru logger with appropriate formats and outputs.

    Sets up the logger with different formats depending on the log level:
    - For DEBUG level: Includes filename, function, and line number
    - For other levels: Simpler format with timestamp, level, and message

    Also configures a JSON file logger with DEBUG level for
    comprehensive logging.

    Parameters
    ----------
    level : str, default "INFO"
        Log level for stderr output.

    Returns
    -------
    Path
        Path to the log file.

    Notes
    -----
    DEBUG level: Includes filename, function, and line number
    Other levels: Simpler format with timestamp, level, and message
    """

    format_short = (" | ").join(
        ["{time:YYYY-MM-DDTHH:mm:ss}", "<level>{level:8}</level>", "<level>{message}</level>"]
    )
    format_long = (" | ").join(
        [
            "{time:YYYY-MM-DDTHH:mm:ss}",
            "<level>{level:8}</level>",
            "<cyan>{name}.{function}:{line}</cyan>",
            "<level>{message}</level>",
        ]
    )

    # ロガーをリセット
    logger.remove()

    # stderr用
    if level in ["DEBUG"]:
        logger.add(
            sys.stderr,
            format=format_long,
            level=level,
        )
    else:
        logger.add(
            sys.stderr,
            format=format_short,
            level=level,
        )

    # ファイル出力用
    p = PlatformDirs(appname="haniwers", version=__version__)
    fname = p.user_log_path / "haniwers_log.json"
    logger.add(
        sink=fname,
        format=format_long,
        level="DEBUG",
        serialize=True,
        retention="10 days",
        rotation="1 MB",
    )
    return fname


def _open_docs(value: bool, url: str) -> None:
    """Open documentation in default web browser.

    Private function used as a callback for the --docs option in commands.

    Parameters
    ----------
    value : bool
        Boolean flag indicating whether to open documentation.
    url : str
        URL of the documentation to open.

    Raises
    ------
    typer.Exit
        Exits the program after opening the documentation.

    Examples
    --------
    Used as callback function for --docs option in existing commands:

    >>> typer.Option(
    ...     "--docs",
    ...     help=f"Open online document. ({DOCS['version']})",
    ...     callback=lambda v: _open_docs(v, DOCS["version"]),
    ... )
    """
    if value:
        msg = f"Open docs with browser: {url}"
        logger.info(msg)
        webbrowser.open(url)
        raise typer.Exit()


app = typer.Typer(help="Haniwers v0 commands")


@app.command()
def version(
    env: Annotated[bool, typer.Option(help="Show environment information.")] = False,
    log_level: Annotated[
        str, typer.Option(help="Set log level (DEBUG, INFO, WARNING, ERROR).")
    ] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online documentation. ({DOCS['version']})",
            callback=lambda v: _open_docs(v, DOCS["version"]),
        ),
    ] = False,
):
    """Show haniwers version.

    Shows the current version of haniwers.
    With the --env flag, also displays detailed environment information
    such as Python version, platform details, and log file location.

    Parameters
    ----------
    env : bool, default False
        Show with environment details.
    log_level : str, default "INFO"
        Log level.

    Examples
    --------
    Basic version display:

    .. code-block:: console

        $ haniwers version
        haniwers 0.19.1

    With environment details:

    .. code-block:: console

        $ haniwers version --env
        haniwers 0.19.2

        Environments:

        Logs: ~/Library/Logs/haniwers/0.19.2/haniwers_log.json
        Executable: ~/.local/pipx/venvs/haniwers/bin/python
        Python: 3.12.5
        Implementation: CPython
        Compiler: Clang 15.0.0 (clang-1500.3.9.4)
        OS: macOS-14.6.1-arm64-arm-64bit
        System: darwin
        Platform: Darwin
        Kernel: 23.6.0
        Arch: arm64
    """

    fname = _setup_logger(level=log_level)

    msg = f"haniwers {__version__}"
    print(msg)
    logger.debug(msg)

    if env:
        _envs = {
            "Logs": fname,
            "Executable": sys.executable,
            "Python": platform.python_version(),
            "Implementation": platform.python_implementation(),
            "Compiler": platform.python_compiler(),
            "OS": platform.platform(),
            "System": sys.platform,
            "Platform": platform.system(),
            "Kernel": platform.release(),
            "Arch": platform.machine(),
        }

        print("\nEnvironments:\n")

        for k, v in _envs.items():
            msg = f"  {k}: {v}"
            print(msg)
            logger.debug(msg)

        print("\n")

    return


@app.command()
def docs(
    page: Annotated[
        str,
        typer.Option(
            help="Set page name.",
        ),
    ] = "home",
):
    """Open online documentation in the default web browser.

    Parameters
    ----------
    page : str, default "home"
        The name of the documentation to open.

    Examples
    --------
    Open home page:

    .. code-block:: console

        $ haniwers docs

    Open specific page:

    .. code-block:: console

        $ haniwers docs --page version
        $ haniwers docs --page scan
        $ haniwers docs --page fit
        $ haniwers docs --page vth
        $ haniwers docs --page daq
        $ haniwers docs --page raw2tmp
        $ haniwers docs --page run2csv

    Notes
    -----
    Added in version 0.19.0
    """
    url = DOCS[page]
    _open_docs(True, url)


@app.command()
def ports(log_level: Annotated[str, typer.Option(help="Change log level")] = "INFO") -> None:
    """Search available ports and show device names.

    Lists all available serial ports that can be used for
    connecting to OSECHI detector.

    Parameters
    ----------
    log_level : str, default "INFO"
        Set the logging level.

    Examples
    --------
    Run on macOS:

    .. code-block:: console

        $ haniwers ports
        | INFO     | Found 2 ports
        | INFO     | Port0: /dev/cu.Bluetooth-Incoming-Port - n/a
        | INFO     | Port1: /dev/cu.usbserial-140 - USB Serial

    Notes
    -----
    The name of USB port varies by operating system:
        - Linux: `/dev/ttyUSB0`
        - macOS: `/dev/cu.usbserial-*` (CP2102N USB to UART Bridge Controller)
        - Windows: `COM3`
    """

    _setup_logger(level=log_level)

    from serial.tools import list_ports

    ports = list_ports.comports()
    n = len(ports)

    if n == 0:
        logger.warning("No ports found")
        return

    logger.info(f"Found {n} ports")

    for i, port in enumerate(ports):
        logger.info(f"Port{i}: {port}")

        logger.debug(f"{port.device=}")
        logger.debug(f"{port.name=}")
        logger.debug(f"{port.description=}")
        logger.debug(f"{port.usb_description()=}")
        logger.debug(f"{port.hwid=}")
        logger.debug(f"{port.usb_info()=}")
        logger.debug(f"{port.pid=}")
        logger.debug(f"{port.vid=}")
        logger.debug(f"{port.interface=}")
        logger.debug(f"{port.manufacturer=}")
        logger.debug(f"{port.product=}")
        logger.debug(f"{port.serial_number=}")

    for port in ports:
        if "UART" in port.description:
            logger.info(f"Please use '{port.device}' as your device path")


@app.command()
def scan(
    ch: Annotated[int, typer.Option(help="Set channel ID.")] = 0,
    duration: Annotated[int, typer.Option(help="Set duration. Unit: [sec]")] = 10,
    step: Annotated[int, typer.Option(help="Set step interval. Unit: [step]")] = 1,
    vmin: Annotated[int, typer.Option(help="Set start point. Unit: [step]")] = 250,
    vmax: Annotated[int, typer.Option(help="Set end point. Unit: [step]")] = 311,
    vstarts: Annotated[
        str, typer.Option(help="Comma-separated start thresholds per channel.")
    ] = "250,250,250",
    nsteps: Annotated[int, typer.Option(help="Number of threshold steps.")] = 50,
    quiet: Annotated[bool, typer.Option(help="Quiet mode.")] = False,
    load_from: Annotated[str, typer.Option(help="Set filename.")] = "scan.toml",
    log_level: Annotated[str, typer.Option(help="Change log level.")] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online document. ({DOCS['scan']})",
            callback=lambda v: _open_docs(v, DOCS["scan"]),
        ),
    ] = False,
) -> None:
    """Start threshold scanning measurement.

    Performs threshold scanning by measuring the event rate at
    various threshold values. This is used to determine the
    optimal threshold settings for each channel.

    Parameters
    ----------
    ch : int, default 0
        Channel ID (1-3, or 0 for all channels).
    duration : int, default 10
        Measurement duration per point in seconds.
    step : int, default 1
        Step interval for threshold scanning.
    vmin : int, default 250
        Start point for scanning range (deprecated).
    vmax : int, default 311
        End point for scanning range (deprecated).
    nsteps : int, default 50
        Number of threshold steps to measure.
    vstarts : str, default "250,250,250"
        Comma-separated start thresholds per channel.
    quiet : bool, default False
        Suppress progress output.
    load_from : str, default "scan.toml"
        Configuration file path.
    log_level : str, default "INFO"
        Log level.
    docs : bool, default False
        Open online documentation.

    Examples
    --------
    Scan all channels with default settings:

    .. code-block:: console

        $ haniwers scan

    Scan specific channel with custom parameters:

    .. code-block:: console

        $ haniwers scan --ch 1 --duration=30 --step 5
        $ haniwers scan --vstarts="200,200,200" --nsteps=40

    Notes
    -----
    The --vmin and --vmax parameters are deprecated. Use --vstarts, --step, and --nsteps instead.
    """
    from .config import Daq
    from .threshold import scan_thresholds

    _setup_logger(level=log_level)

    # オプション解析

    # vminとvmaxが設定（＝初期値以外）の場合はエラーにする
    if vmin != 250 or vmax != 311:
        msg = "--vmin and --vmax are deprecated. Use --vstarts, --step, and --nsteps instead."
        logger.error(msg)
        raise typer.BadParameter(msg)

    if ch == 0:
        channels = [1, 2, 3]
    else:
        channels = [ch]

    # 開始点を取得
    try:
        vmins = [int(v.strip()) for v in vstarts.split(",")]
    except Exception:
        logger.error(f"Invalid format for --vstarts: {vstarts}")
        raise typer.BadParameter("Invalid format for --vstarts. Use comma-separated numbers.")

    # 開始点の数とチャンネル数が一致していない場合はエラーにする
    if (len(vmins)) != len(channels):
        logger.error("Number of vstart values must match the number of channels")
        raise typer.Exit(code=1)

    daq = Daq()
    daq.load_toml(load_from)
    daq.quiet = quiet

    now = pendulum.now().format("YYYYMMDD")
    daq.saved = str(Path(daq.saved) / now)

    for i, ch in enumerate(channels):
        start = vmins[i]
        stop = start + nsteps * step
        thresholds = list(range(start, stop, step))
        msg = f"Running threshold scan on ch{ch}."
        logger.info(msg)
        scan_thresholds(daq, duration, ch, thresholds)

    return


@app.command()
def fit(
    read_from: Annotated[str, typer.Argument(help="Set directory.")],
    params: Annotated[
        str, typer.Option(help="Set initial fit parameters (commma separated string).")
    ] = "10,300,1,1",
    search_pattern: Annotated[str, typer.Option(help="Set filename.")] = "threshold_scan.csv",
    ch: Annotated[int, typer.Option(help="Set channel ID")] = 0,
    log_level: Annotated[str, typer.Option(help="Change log level")] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online document. ({DOCS['fit']})",
            callback=lambda v: _open_docs(v, DOCS["fit"]),
        ),
    ] = False,
):
    """Calculate thresholds from scan data using error function fitting.

    Analyzes threshold scan data to estimate optimal threshold values
    using error function fitting. Results are saved to both a historical
    record and a latest version file for use by other commands.

    Parameters
    ----------
    read_from : str
        Directory containing threshold scan data.
    params : str, default "10,300,1,1"
        Initial fit parameters as comma-separated string.
    search_pattern : str, default "threshold_scan.csv"
        Filename pattern for scan data files.
    ch : int, default 0
        Channel ID (1-3, or 0 for all channels).
    log_level : str, default "INFO"
        Log level.
    docs : bool, default False
        Open online documentation.

    Examples
    --------
    Calculate thresholds for all channels:

    .. code-block:: console

        $ haniwers fit path_data_directory

    With custom fit parameters:

    .. code-block:: console

        $ haniwers fit data_dir --params="5,250,2,0.5"

    Notes
    -----
    Results are saved to:
        - `threshold_history.csv`: Appends results with timestamps for historical tracking
        - `threshold_latest.csv`: Overwrites with most recent results for use by the `vth` command
    """
    import pandas as pd

    from .preprocess import get_fnames
    from .threshold import fit_thresholds

    _setup_logger(level=log_level)

    try:
        p0 = [float(x.strip()) for x in params.split(",")]
    except Exception:
        logger.error(f"Invalid format for --params: {params}")
        raise typer.BadParameter("Invalid format for --params. Use comma-separated numbers.")

    logger.info(f"Read data from {read_from}")
    fnames = get_fnames(
        read_from,
        search_pattern,
    )

    # ファイルが見つからない時は、なにもしない
    if len(fnames) == 0:
        logger.error("No files found.")
        return

    logger.debug(fnames)

    # チャンネル番号が範囲外のときは、なにもしない
    if ch > 3:
        logger.error(f"Out of range!: {ch}")
        return

    channels = [ch]
    if ch == 0:
        channels = [1, 2, 3]

    names = ["time", "duration", "ch", "vth", "events", "tmp", "atm", "hmd"]
    data = pd.read_csv(fnames[0], names=names, parse_dates=["time"])
    thresholds = fit_thresholds(data, channels, p0)

    # 実行した時刻を上書きする
    now = pendulum.now()
    thresholds["timestamp"] = now
    print(thresholds)

    fname = "thresholds_history.csv"
    thresholds.to_csv(fname, index=False, mode="a", header=None)
    logger.info(f"Saved to {fname}")
    fname = "thresholds_latest.csv"
    thresholds.to_csv(fname, index=False)
    logger.info(f"Saved to {fname}")

    return


@app.command()
def vth(
    ch: Annotated[int, typer.Option(help="Set channel ID")] = 0,
    vth: Annotated[int, typer.Option(help="Set threshold value.")] = 0,
    max_retry: Annotated[int, typer.Option(help="Set numbers to retry.")] = 3,
    load_from: Annotated[str, typer.Option(help="Set filename.")] = "daq.toml",
    log_level: Annotated[str, typer.Option(help="Change log level.")] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online document. ({DOCS['vth']})",
            callback=lambda v: _open_docs(v, DOCS["vth"]),
        ),
    ] = False,
) -> None:
    """Set threshold values for detector channels.

    Sets threshold values for detector channels.
    Can set values individually by channel or apply optimal values
    calculated by the `fit` command to all channels.

    Each step corresponds to 4mV.
    For example, a value of 250 equals 1000mV.

    Parameters
    ----------
    ch : int, default 0
        Channel ID to set (1, 2, 3). Use 0 to set all channels.
    vth : int, default 0
        Threshold value to set. Use 0 to apply values from `threshold_latest.csv`.
    max_retry : int, default 3
        Maximum retry attempts if threshold setting fails.
    load_from : str, default "daq.toml"
        Configuration file path.
    log_level : str, default "INFO"
        Log level.
    docs : bool, default False
        Open online documentation.

    Examples
    --------
    Set thresholds for all channels using values from threshold_latest.csv:

    .. code-block:: console

        $ haniwers vth

    Set threshold for specific channel:

    .. code-block:: console

        $ haniwers vth --ch 1 --vth 278
        $ haniwers vth --ch 2 --vth 268
        $ haniwers vth --ch 3 --vth 300

    Notes
    -----
    - We still don't know the reason why threshold setting fails sometimes.
    - If threshold writing fails, it will retry up to `max_retry` times.
    - When setting all channels (ch=0 and vth=0), values are read from `threshold_latest.csv`.
    """

    from .config import Daq
    from .daq import set_vth_retry

    _setup_logger(level=log_level)

    daq = Daq()
    daq.load_toml(load_from)

    now = pendulum.now().format("YYYYMMDD")
    daq.saved = str(Path(daq.saved) / now)

    # 個別のチャンネルにスレッショルドを設定する
    if ch in range(1, 4) and vth > 0:
        logger.debug(f"Set threshold to each channel: {ch} -> {vth}")
        set_vth_retry(daq, ch, vth, max_retry)
        return

    # 引数を指定しない場合は
    # すべてのチャンネルに規定のスレッショルドを設定する
    if ch == 0 and vth == 0:
        # スレッショルド値をファイルから読み込む
        fname = Path("thresholds_latest.csv")
        if not fname.exists():
            logger.error(f"No file found. Please create {fname}")
            return

        names = ["ch", "3sigma"]
        thresholds = pd.read_csv(fname)[names]

        for _, row in thresholds.iterrows():
            ch = int(row["ch"])
            vth = int(row["3sigma"])
            logger.debug(f"Set threshold to channels: {ch} -> {vth}")
            set_vth_retry(daq, ch, vth, max_retry)
        return

    # オプション指定が間違っている
    logger.error("Invalid arguments")
    return


@app.command()
def scan_serial(
    ch: int = 0,
    duration: int = 10,
    step: int = 1,
    vmin: int = 250,
    vmax: int = 311,
    quiet: bool = False,
    load_from="daq.toml",
    log_level: str = "INFO",
) -> None:
    """Perform threshold scanning measurement per channel in serial mode.

    Parameters
    ----------
    ch : int, default 0
        Channel number (1-3, or 0 for all channels).
    duration : int, default 10
        Measurement time per point in seconds.
    step : int, default 1
        Step interval for scanning.
    vmin : int, default 250
        Minimum threshold value for scanning range.
    vmax : int, default 311
        Maximum threshold value for scanning range.
    quiet : bool, default False
        Suppress progress output.
    load_from : str, default "daq.toml"
        Configuration file path.
    log_level : str, default "INFO"
        Log level.
    """
    from .config import Daq
    from .threshold import scan_thresholds_in_serial

    _setup_logger(level=log_level)
    daq = Daq()
    daq.load_toml(load_from)

    # DAQ設定を変更
    daq.quiet = quiet
    daq.prefix = "scan_data_serial"
    daq.max_rows = 1000
    daq.max_files = 10
    daq.timeout = duration + 5
    daq.fname_scan = "thresholds_scan_serial.csv"

    # 保存先の設定
    now = pendulum.now().format("YYYYMMDD")
    daq.saved = str(Path(daq.saved) / now)

    if ch == 0:
        channels = [1, 2, 3]
    else:
        channels = [ch]

    thresholds = list(range(vmin, vmax, step))

    for ch in channels:
        msg = f"Running threshold scan on ch{ch}."
        logger.info(msg)
        scan_thresholds_in_serial(daq, duration, ch, thresholds)

    return


@app.command()
def scan_parallel(
    ch: int = 0,
    duration: int = 10,
    step: int = 1,
    vmin: int = 250,
    vmax: int = 311,
    quiet: bool = False,
    load_from="daq.toml",
    log_level: str = "INFO",
) -> None:
    """Perform threshold scanning measurement in parallel mode.

    Parameters
    ----------
    ch : int, default 0
        Channel number (1-3, or 0 for all channels).
    duration : int, default 10
        Measurement time per point in seconds.
    step : int, default 1
        Step interval for scanning.
    vmin : int, default 250
        Minimum threshold value for scanning range.
    vmax : int, default 311
        Maximum threshold value for scanning range.
    quiet : bool, default False
        Suppress progress output.
    load_from : str, default "daq.toml"
        Configuration file path.
    log_level : str, default "INFO"
        Log level.
    """
    from .config import Daq
    from .threshold import scan_thresholds_in_parallel

    _setup_logger(level=log_level)
    daq = Daq()
    daq.load_toml(load_from)

    # DAQ設定を変更
    daq.prefix = "scan_data_parallel"
    daq.max_rows = 1000
    daq.max_files = 10
    daq.timeout = duration + 5
    daq.fname_scan = "thresholds_scan_parallel.csv"

    # 保存先の設定
    now = pendulum.now().format("YYYYMMDD")
    daq.saved = str(Path(daq.saved) / now)

    # スキャンする範囲を設定
    thresholds = list(range(vmin, vmax, step))
    scan_thresholds_in_parallel(daq, duration=duration, thresholds=thresholds)

    return


@app.command()
def scan(
    ch: int = 0,
    duration: int = 10,
    step: int = 1,
    vmin: int = 250,
    vmax: int = 311,
    quiet: bool = False,
    load_from="scan.toml",
    log_level: str = "INFO",
) -> None:
    """Alias for scan_serial command.

    This is a wrapper function that calls scan_serial with the same parameters.
    Provides backward compatibility for the legacy scan command.

    Parameters
    ----------
    ch : int, default 0
        Channel number (1-3, or 0 for all channels).
    duration : int, default 10
        Measurement time per point in seconds.
    step : int, default 1
        Step interval for scanning.
    vmin : int, default 250
        Minimum threshold value for scanning range.
    vmax : int, default 311
        Maximum threshold value for scanning range.
    quiet : bool, default False
        Suppress progress output.
    load_from : str, default "scan.toml"
        Configuration file path.
    log_level : str, default "INFO"
        Log level.

    See Also
    --------
    scan_serial : The actual implementation of serial threshold scanning.
    scan_parallel : Parallel threshold scanning implementation.
    """
    return scan_serial(ch, duration, step, vmin, vmax, quiet, load_from, log_level)


@app.command()
def daq(
    quiet: Annotated[bool, typer.Option(help="Quiet mode.")] = False,
    load_from: Annotated[str, typer.Option(help="Set filename.")] = "daq.toml",
    log_level: Annotated[str, typer.Option(help="Change log level")] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online document. ({DOCS['daq']})",
            callback=lambda v: _open_docs(v, DOCS["daq"]),
        ),
    ] = False,
) -> None:
    """Start data acquisition with configured settings.

    Starts the data acquisition process using settings
    from the configuration file. Collects cosmic ray events
    and environmental data from the OSECHI detector.

    Parameters
    ----------
    quiet : bool, default False
        Suppress progress output.
    load_from : str, default "daq.toml"
        Configuration file path.
    log_level : str, default "INFO"
        Log level.
    docs : bool, default False
        Open online documentation.

    Examples
    --------
    Start data acquisition with default settings:

    .. code-block:: console

        $ haniwers daq

    Start in quiet mode:

    .. code-block:: console

        $ haniwers daq --quiet

    Notes
    -----
    - Data is saved to the directory specified in the configuration file,
      organized by date in YYYYMMDD format.
    - Press Ctrl+c to stop data acquisition.
    - The program automatically creates directories if they don't exist.
    """
    from .config import Daq
    from .daq import open_serial_connection, run

    # ログレベルを設定
    _setup_logger(level=log_level)

    # DAQの初期設定
    args = Daq()
    args.load_toml(load_from)
    args.quiet = quiet

    # データの保存先をymdに変更
    now = pendulum.now().format("YYYYMMDD")
    args.saved = str(Path(args.saved) / now)

    with open_serial_connection(args) as port:
        run(port, args)

    return


@app.command()
def raw2tmp(
    read_from: Annotated[str, typer.Argument(help="Directory containing raw data.")],
    search_pattern: Annotated[str, typer.Option(help="Filename pattern for raw data.")] = "*.csv",
    interval: Annotated[int, typer.Option(help="Resampling interval in seconds.")] = 600,
    offset: Annotated[int, typer.Option(help="Datetime offset in seconds")] = 0,
    tz: Annotated[str, typer.Option(help="Timezone for data.")] = "UTC+09:00",
    log_level: Annotated[
        str, typer.Option(help="Set log level (DEBUG, INFO, WARNING, ERROR).")
    ] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online documentation. ({DOCS['raw2tmp']})",
            callback=lambda v: _open_docs(v, DOCS["raw2tmp"]),
        ),
    ] = False,
) -> None:
    """Quick conversion of raw data for temporary analysis.

    Converts raw cosmic ray data into a simplified CSV format for quick analysis.
    This is intended for temporary use to quickly check data during measurement.
    For thorough analysis, use the `run2csv` command instead.

    Parameters
    ----------
    read_from : str
        Path to the directory containing raw data files.
    search_pattern : str, default "*.csv"
        Pattern to match raw data files.
    interval : int, default 600
        Resampling interval in seconds (10 minutes).
    offset : int, default 0
        Time offset correction in seconds.
    tz : str, default "UTC+09:00"
        Timezone for data timestamps.
    log_level : str, default "INFO"
        Log level.
    docs : bool, default False
        Open online documentation.

    Examples
    --------
    Quick convert data with default settings:

    .. code-block:: console

        $ haniwers raw2tmp path_data_directory

    With custom parameters:

    .. code-block:: console

        $ haniwers raw2tmp data_dir --search-pattern="*.dat"
        $ haniwers raw2tmp data_dir --interval=10
        $ haniwers raw2tmp data_dir --offset=36480
        $ haniwers raw2tmp data_dir --tz="UTC+09:00"

    Notes
    -----
    Output files:
        - `tmp_raw2tmp.csv.gz`: Raw data with all events
        - `tmp_raw2tmp.csv`: Resampled data at specified interval

    The time offset option is useful for correcting clock drift on Raspberry Pi devices that lack a real-time clock.
    """
    from .preprocess import get_fnames, raw2csv

    _setup_logger(level=log_level)

    logger.info(f"Read data from {read_from}")
    fnames = get_fnames(read_from, search_pattern)
    gzip, csv = raw2csv(fnames, interval, offset, tz)
    logger.debug(f"raw2gz = {len(gzip)}")
    logger.debug(f"raw2csv = {len(csv)}")

    fname = "tmp_raw2tmp.csv.gz"
    gzip.to_csv(fname, index=False, compression="gzip")
    logger.info(f"Save data to: {fname} ({len(gzip)} rows).")

    fname = "tmp_raw2tmp.csv"
    csv.to_csv(fname, index=False)
    logger.info(f"Save data to: {fname} ({len(csv)} rows).")


@app.command()
def run2csv(
    run_id: Annotated[int, typer.Argument(help="Run ID")],
    save: Annotated[bool, typer.Option(help="Save results to files.")] = False,
    load_from: Annotated[str, typer.Option(help="Run configuration files.")] = "runs.csv",
    drive: Annotated[str, typer.Option(help="Data directory.")] = "../data",
    log_level: Annotated[
        str, typer.Option(help="Set log level (DEBUG, INFO, WARNING, ERROR).")
    ] = "INFO",
    docs: Annotated[
        bool,
        typer.Option(
            "--docs",
            help=f"Open online documentation. ({DOCS['run2csv']})",
            callback=lambda v: _open_docs(v, DOCS["run2csv"]),
        ),
    ] = False,
) -> None:
    """Convert run data to CSV format for analysis.

    Processes raw data from a specific run and converts it to
    CSV format for analysis. Uses run configuration information
    from `runs.csv` to determine proper processing parameters.

    Parameters
    ----------
    run_id : int
        Run identifier number to process.
    save : bool, default False
        Save processed data to files.
    load_from : str, default "runs.csv"
        Run configuration file path.
    drive : str, default "../data"
        Base directory containing data.
    log_level : str, default "INFO"
        Log level.
    docs : bool, default False
        Open online documentation.

    Examples
    --------
    Process run #98 without saving (preview mode):

    .. code-block:: console

        $ haniwers run2csv 98

    Process run #98 and save results:

    .. code-block:: console

        $ haniwers run2csv 98 --save

    With custom configuration location:

    .. code-block:: console

        $ haniwers run2csv 98 --drive="../data" --load_from="runs.csv"

    Notes
    -----
    - If `run_id` is invalid or not found in the configuration,
      the program will exit with an error message.
    - When `--save` is not specified, the command will process data but
      not save any files, acting as a preview mode.
    - Output files are determined by the run configuration and include:
        - A compressed raw data file (`.csv.gz`)
        - A resampled data file (`.csv`)
    """

    from .config import RunManager
    from .preprocess import run2csv

    _setup_logger(level="INFO")
    rm = RunManager(load_from=load_from, drive=drive)
    msg = f"Load config from: {load_from}."
    logger.info(msg)

    msg = f"Get RunData: {run_id}."
    logger.info(msg)

    run = rm.get_run(run_id)
    logger.info(f"description: {run.description}")
    logger.info(f"read_from: {run.read_from}")
    logger.debug(f"srcf: {run.srcf}")

    gzip, csv = run2csv(run)
    if save:
        fname = run.raw2gz
        gzip.to_csv(fname, index=False, compression="gzip")
        logger.info(f"Save data to: {fname} ({len(gzip)} rows).")
        fname = run.raw2csv
        csv.to_csv(fname, index=False)
        logger.info(f"Save data to: {fname} ({len(csv)} rows).")
    else:
        logger.warning("No data saved. Add --save to save data.")
        logger.debug(f"gzip: {len(gzip)}.")
        logger.debug(f"csv:  {len(csv)}.")


@app.command()
def mock_daq(
    quiet: Annotated[bool, typer.Option(help="Quiet mode.")] = False,
    load_from: Annotated[str, typer.Option(help="Set filename")] = "daq.toml",
    log_level: Annotated[str, typer.Option(help="Change log level")] = "DEBUG",
):
    """Run simulated data acquisition for testing and debugging.

    Creates simulated cosmic ray events without requiring actual OSECHI hardware.
    This command is useful for development, testing, and debugging purposes.

    Parameters
    ----------
    quiet : bool, default False
        Suppress progress output.
    load_from : str, default "daq.toml"
        Configuration file path.
    log_level : str, default "DEBUG"
        Log level.

    Examples
    --------
    Run simulated data acquisition:

    .. code-block:: console

        $ haniwers mock_daq

    With custom configuration:

    .. code-block:: console

        $ haniwers mock_daq --load_from="test_config.toml"

    Notes
    -----
    - Generated data follows the same format as real data but uses random values.
    - The mock DAQ uses reduced file counts and row counts for quicker execution.
    - Data is saved to the directory specified in the configuration file,
      organized by date in YYYYMMDD format, just like the real `daq` command.
    """
    from unittest.mock import MagicMock, patch

    import serial

    from .config import Daq
    from .daq import run
    from .mimic import FakeEvent

    # ログレベルを設定
    _setup_logger(level=log_level)
    logger.debug("mock-daq")

    # DAQの初期設定
    args = Daq()
    args.load_toml(load_from)
    args.quiet = quiet

    # データの保存先をymdに変更
    now = pendulum.now().format("YYYYMMDD")
    args.saved = str(Path(args.saved) / now)
    args.max_rows = 10
    args.max_files = 5
    logger.debug(args)

    # シリアル通信をモック
    mock_port = MagicMock()
    mock_port.readline().decode.return_value = FakeEvent().to_mock_string()
    mock_port.name.return_value = "mock"

    with patch("serial.Serial", return_value=mock_port):
        with serial.Serial() as port:
            logger.debug(f"Port opened: {port.name}")
            run(port, args)
    logger.debug(f"Port closed: {port.name}")


if __name__ == "__main__":
    app()
