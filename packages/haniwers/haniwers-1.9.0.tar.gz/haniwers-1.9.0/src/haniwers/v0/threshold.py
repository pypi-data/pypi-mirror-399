"""Threshold measurement and analysis.

This module provides functionality for threshold scanning measurements
by varying threshold values and obtaining S-curves of event counts versus threshold.
The S-curves are fitted with complementary error functions to estimate
optimal threshold values for cosmic ray detection.

The module performs the following operations:
- Channel selection and threshold setting
- Data acquisition (DAQ) execution and data collection
- Statistical analysis of collected events
- Error function fitting for threshold estimation
- Calculation of optimal threshold values (1σ, 3σ, 5σ)

Classes
-------
Count : BaseModel
    Data model for threshold measurement results containing event counts,
    environmental data, and measurement metadata.

Functions
---------
scan_threshold_by_channel : Perform threshold scan for a specific channel
scan_thresholds_in_serial : Sequential threshold scanning across multiple points
scan_thresholds_in_parallel : Parallel threshold scanning for all channels
fit_threshold_by_channel : Fit error function to threshold scan data
fit_thresholds : Calculate optimal thresholds for multiple channels
erfc_function : Complementary error function for fitting

Examples
--------
Basic threshold scanning workflow:

>>> from haniwers.config import Daq
>>> daq = Daq()
>>> thresholds = list(range(250, 350, 5))
>>> results = scan_thresholds_in_serial(daq, duration=10, ch=1, thresholds=thresholds)

Fitting threshold data:

>>> import pandas as pd
>>> data = pd.read_csv('threshold_scan.csv')
>>> optimal_thresholds = fit_thresholds(data, channels=[1, 2, 3], params=[10, 300, 1, 1])
"""

import csv
from pathlib import Path

import numpy as np
import pandas as pd
import pendulum
from datetime import datetime

from loguru import logger
from scipy.optimize import curve_fit
from scipy.special import erfc
from pydantic import BaseModel

from .config import Daq
from .daq import (
    events_to_dataframe,
    get_savef_with_timestamp,
    mkdir_saved,
    scan_daq,
    set_vth_retry,
)


class Count(BaseModel):
    """Data model for threshold measurement results.

    This class stores the results of a single threshold measurement,
    including event counts, detector hit information, and environmental
    conditions during the measurement.

    Attributes
    ----------
    timestamp : datetime
        Timestamp when the measurement was taken.
    duration : int
        Measurement duration in seconds.
    ch : int
        Channel number (1-3) used for the measurement.
    vth : int
        Threshold value used for the measurement.
    counts : int
        Total number of events detected.
    hit_top : int
        Number of hits in the top detector layer.
    hit_mid : int
        Number of hits in the middle detector layer.
    hit_btm : int
        Number of hits in the bottom detector layer.
    tmp : float
        Temperature in degrees Celsius during measurement.
    atm : float
        Atmospheric pressure in hPa during measurement.
    hmd : float
        Humidity percentage during measurement.

    Examples
    --------
    Create a Count instance with measurement data:

    >>> import pendulum
    >>> count = Count(
    ...     timestamp=pendulum.now(),
    ...     duration=10,
    ...     ch=1,
    ...     vth=280,
    ...     counts=150,
    ...     hit_top=50,
    ...     hit_mid=60,
    ...     hit_btm=40,
    ...     tmp=25.3,
    ...     atm=1013.2,
    ...     hmd=45.6
    ... )
    """

    timestamp: datetime = pendulum.now()
    duration: int = 0
    ch: int = 0
    vth: int = 0
    counts: int = 0
    hit_top: int = 0
    hit_mid: int = 0
    hit_btm: int = 0
    tmp: float = 0
    atm: float = 0
    hmd: float = 0

    def to_list_string(self) -> list[str]:
        """Convert all attributes to a list of strings.

        This method converts all model attributes to string format,
        which is useful for CSV export and data serialization.

        Returns
        -------
        list[str]
            List of all attribute values converted to strings,
            in the order they are defined in the model.

        Examples
        --------
        >>> count = Count(duration=10, ch=1, vth=280, counts=50)
        >>> strings = count.to_list_string()
        >>> len(strings)
        11
        >>> strings[1:4]  # duration, ch, vth
        ['10', '1', '280']
        """
        data = self.model_dump()
        values = [str(v) for v in data.values()]
        return values


def get_count(data: pd.DataFrame) -> Count:
    """Process threshold measurement results and create Count object.

    Processes raw event data from a threshold measurement and calculates
    statistical summaries including event counts, detector hit counts,
    and environmental conditions.

    Parameters
    ----------
    data : pd.DataFrame
        Raw event data containing columns: 'hit_top', 'hit_mid', 'hit_btm',
        'tmp', 'atm', 'hmd'. Empty DataFrame is handled gracefully.

    Returns
    -------
    Count
        Count object containing processed measurement results:
        - counts: Total number of events
        - hit_top/mid/btm: Sum of hits in each detector layer
        - tmp/atm/hmd: Mean environmental conditions

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'hit_top': [1, 0, 1],
    ...     'hit_mid': [1, 1, 0],
    ...     'hit_btm': [0, 1, 1],
    ...     'tmp': [25.1, 25.2, 25.0],
    ...     'atm': [1013.2, 1013.1, 1013.3],
    ...     'hmd': [45.0, 45.5, 44.8]
    ... })
    >>> result = get_count(data)
    >>> result.counts
    3
    >>> result.hit_top
    2
    """
    count = Count()

    if data.empty:
        return count

    count.counts = len(data)
    count.hit_top = int(data["hit_top"].sum())
    count.hit_mid = int(data["hit_mid"].sum())
    count.hit_btm = int(data["hit_btm"].sum())
    count.tmp = float(data["tmp"].mean())
    count.atm = float(data["atm"].mean())
    count.hmd = float(data["hmd"].mean())

    logger.debug(count)
    logger.debug(f"{count.counts=}")
    logger.debug(f"{count.hit_top=}")
    logger.debug(f"{count.hit_mid=}")
    logger.debug(f"{count.hit_btm=}")
    logger.debug(f"{count.tmp=}")
    logger.debug(f"{count.atm=}")
    logger.debug(f"{count.hmd=}")

    return count


def write_count(count: Count, fname: Path) -> None:
    """Write Count object to CSV file.

    Appends the Count object's data as a new row to the specified CSV file.
    Creates the file if it doesn't exist.

    Parameters
    ----------
    count : Count
        Count object containing measurement results to write.
    fname : Path
        Path to the CSV file where data will be appended.

    Examples
    --------
    >>> from pathlib import Path
    >>> count = Count(duration=10, ch=1, vth=280, counts=50)
    >>> write_count(count, Path("results.csv"))
    """
    row = count
    with fname.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row.to_list_string())
        msg = f"Added data to: {fname}"
        logger.success(msg)


def get_data(daq: Daq, duration: int, ch: int, vth: int) -> Count:
    """Execute threshold measurement and collect event data.

    Performs a data acquisition run with specified parameters,
    collects cosmic ray events, and processes them into a Count object.
    Handles exceptions gracefully by returning empty Count on failure.

    Parameters
    ----------
    daq : Daq
        Data acquisition configuration object containing device settings.
    duration : int
        Measurement duration in seconds.
    ch : int
        Channel number (1-3) for threshold measurement.
    vth : int
        Threshold value to be applied during measurement.

    Returns
    -------
    Count
        Count object containing processed measurement results with
        timestamp, measurement parameters, and event statistics.

    Examples
    --------
    >>> from haniwers.config import Daq
    >>> daq = Daq()
    >>> result = get_data(daq, duration=30, ch=1, vth=280)
    >>> result.duration
    30
    >>> result.ch
    1
    >>> result.vth
    280

    Notes
    -----
    - File ID (fid) is generated as "{ch:02}_{vth:04}" format (max 7 digits)
    - Returns Count with zero counts if data acquisition fails
    - All exceptions are caught and logged as errors
    """
    try:
        # fidは7ケタまで使える
        fid = f"{ch:02}_{vth:04}"
        fname = get_savef_with_timestamp(daq, fid)
        events = scan_daq(daq, str(fname), duration)
        data = events_to_dataframe(events)
    except Exception as e:
        data = pd.DataFrame()
        msg = f"Failed to collect data due to: {str(e)}"
        logger.error(msg)

    # Save Summary
    row = get_count(data)
    now = pendulum.now()
    row.timestamp = now
    row.duration = duration
    row.ch = ch
    row.vth = vth

    return row


def scan_threshold_by_channel(daq: Daq, duration: int, ch: int, vth: int) -> Count:
    """Perform threshold scan measurement for a specific channel.

    Sets the threshold value for the specified channel and performs
    a data acquisition measurement. The results are processed and
    saved to the scan data file.

    Parameters
    ----------
    daq : Daq
        Data acquisition configuration object containing device settings
        and file paths.
    duration : int
        Measurement duration in seconds.
    ch : int
        Channel number (1-3) to measure.
    vth : int
        Threshold value to set for the measurement.

    Returns
    -------
    Count
        Count object containing measurement results including timestamp,
        measurement parameters, event counts, and environmental data.

    Examples
    --------
    >>> from haniwers.config import Daq
    >>> daq = Daq()
    >>> result = scan_threshold_by_channel(daq, duration=10, ch=1, vth=280)
    >>> result.ch
    1
    >>> result.vth
    280
    >>> result.duration
    10

    Notes
    -----
    - Attempts to set threshold with up to 3 retries
    - Returns Count with zero counts if threshold setting fails
    - Results are automatically appended to the scan data file
    """

    # Try to set the threshold
    if not set_vth_retry(daq, ch, vth, 3):
        msg = f"Failed to set threshold: ch{ch} - {vth}"
        logger.error(msg)
        # Return empty Count instead of empty list
        count = Count()
        count.timestamp = pendulum.now()
        count.duration = duration
        count.ch = ch
        count.vth = vth
        return count

    # スレッショルド測定を実行
    row = get_data(daq, duration, ch, vth)
    fname = Path(daq.saved) / daq.fname_scan
    write_count(row, fname)
    return row


def scan_thresholds_in_serial(
    daq: Daq, duration: int, ch: int, thresholds: list[int]
) -> list[Count]:
    """Perform threshold scanning measurements in serial mode.

    Executes threshold scan measurements sequentially across a range
    of threshold values for a specified channel. All other channels
    are set to high thresholds (500) to minimize interference.

    Parameters
    ----------
    daq : Daq
        Data acquisition configuration object containing device settings
        and file paths.
    duration : int
        Measurement duration in seconds for each threshold point.
    ch : int
        Channel number (1-3) to scan. Other channels are disabled.
    thresholds : list[int]
        List of threshold values to measure sequentially.

    Returns
    -------
    list[Count]
        List of Count objects, one for each successful measurement.
        Failed measurements are excluded from the results.

    Examples
    --------
    >>> from haniwers.config import Daq
    >>> daq = Daq()
    >>> thresholds = [250, 260, 270, 280, 290]
    >>> results = scan_thresholds_in_serial(daq, duration=10, ch=1, thresholds=thresholds)
    >>> len(results)
    5
    >>> results[0].ch
    1
    >>> results[0].vth
    250

    Notes
    -----
    - Channels 1, 2, 3 are initially set to high threshold (500)
    - Only the specified channel is varied during the scan
    - Estimated time and progress are logged during execution
    - Results are automatically saved to the scan data file
    """

    # Estimated time for scan
    msg = f"Number of points: {len(thresholds)}"
    logger.info(msg)
    estimated_time = len(thresholds) * duration
    msg = f"Estimated time: {estimated_time} sec."
    logger.info(msg)

    # すべてのチャンネルの閾値を高くする
    set_vth_retry(daq, 1, 500, 5)
    set_vth_retry(daq, 2, 500, 5)
    set_vth_retry(daq, 3, 500, 5)

    rows = []
    n = len(thresholds)
    for i, vth in enumerate(thresholds):
        msg = "-" * 40 + f"[{i + 1:2d}/{n:2d}: {vth}]"
        logger.info(msg)
        row = scan_threshold_by_channel(daq, duration, ch, vth)
        if row:
            rows.append(row)

    return rows


def scan_thresholds_in_parallel(daq: Daq, duration: int, thresholds: list[int]) -> Count:
    """Perform threshold scanning measurements in parallel mode.

    Executes threshold scan measurements where all channels (1, 2, 3)
    are set to the same threshold value simultaneously. This mode is useful
    for measuring the collective response of all detector channels.

    Parameters
    ----------
    daq : Daq
        Data acquisition configuration object containing device settings
        and file paths.
    duration : int
        Measurement duration in seconds for each threshold point.
    thresholds : list[int]
        List of threshold values to apply to all channels simultaneously.

    Returns
    -------
    Count
        Count object from the last measurement. Note that this function
        returns only the final result, not a list of all measurements.

    Examples
    --------
    >>> from haniwers.config import Daq
    >>> daq = Daq()
    >>> thresholds = [250, 260, 270, 280, 290]
    >>> result = scan_thresholds_in_parallel(daq, duration=10, thresholds=thresholds)
    >>> result.vth  # Last threshold value
    290

    Notes
    -----
    - All channels (1, 2, 3) are set to the same threshold value
    - Channel ID is set to 0 in the results to indicate parallel mode
    - Each measurement overwrites the previous result
    - Results are automatically saved to the scan data file
    - Creates save directory if it doesn't exist
    """
    mkdir_saved(daq)

    # Estimated time for scan
    msg = f"Number of points: {len(thresholds)}"
    logger.info(msg)
    estimated_time = len(thresholds) * duration
    msg = f"Estimated time: {estimated_time} sec."
    logger.info(msg)

    # チャンネルは0にする
    ch = 0

    n = len(thresholds)
    for i, vth in enumerate(thresholds):
        msg = "-" * 40 + f"[{i + 1:2d}/{n:2d}: {vth}]"
        logger.info(msg)

        # すべてのチャンネルの閾値を設定
        set_vth_retry(daq, 1, vth, 5)
        set_vth_retry(daq, 2, vth, 5)
        set_vth_retry(daq, 3, vth, 5)

        # スレッショルド測定を実行
        row = get_data(daq, duration, ch, vth)
        fname = Path(daq.saved) / daq.fname_scan
        write_count(row, fname)

    return row


def erfc_function(x, a, b, c, d):
    """Complementary error function for threshold fitting.

    Mathematical function used to fit threshold scan data S-curves.
    This function models the probability distribution of detector
    response as a function of threshold voltage.

    The function is defined as:
        f(x) = a * erfc((x - b) / c) + d

    where erfc(x) = 1 - erf(x) is the complementary error function.

    Parameters
    ----------
    x : array_like
        Input values (threshold voltages).
    a : float
        Height parameter (amplitude of the S-curve).
    b : float
        Mean parameter (center position of the transition).
    c : float
        Sigma parameter (width of the transition region).
    d : float
        Offset parameter (baseline level).

    Returns
    -------
    ndarray
        Fitted function values at input points.

    Examples
    --------
    >>> import numpy as np
    >>> x = np.array([250, 260, 270, 280, 290])
    >>> result = erfc_function(x, a=10, b=275, c=5, d=1)
    >>> len(result)
    5

    Notes
    -----
    This function is typically used with scipy.optimize.curve_fit
    to determine optimal threshold values from scan data.
    """
    return a * erfc((x - b) / c) + d


def fit_threshold_by_channel(
    data: pd.DataFrame, ch: int, func, params: list[float]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Determine optimal threshold values using error function fitting.

    Analyzes threshold scan data for a specific channel by fitting a
    complementary error function to the event rate vs threshold curve.
    Calculates multiple sigma levels (0σ, 1σ, 3σ, 5σ) for threshold selection.

    The fitting process:
    1. Extracts data for the specified channel
    2. Calculates event rates (events/duration)
    3. Performs curve fitting with provided initial parameters
    4. Repeats fitting using optimized parameters for better convergence
    5. Generates fit curve and calculates threshold recommendations

    Parameters
    ----------
    data : pd.DataFrame
        Threshold scan data with columns: ['time', 'duration', 'ch', 'vth', 'events',
        'tmp', 'atm', 'hmd'].
    ch : int
        Channel number (1-3) to analyze for threshold determination.
    func : callable
        Fitting function, typically erfc_function for threshold analysis.
    params : list[float]
        Initial parameters for curve fitting [height, mean, sigma, offset].

    Returns
    -------
    thresholds : pd.DataFrame
        DataFrame with calculated threshold values at different sigma levels:
        columns ['timestamp', 'ch', '0sigma', '1sigma', '3sigma', '5sigma'].
    data_fitted : pd.DataFrame
        Original data subset with added 'event_rate' column for the specified channel.
    fit_curve : pd.DataFrame
        Fitted curve data points for plotting with columns ['vth', 'event_rate', 'ch'].

    Examples
    --------
    >>> import pandas as pd
    >>> from haniwers.threshold import erfc_function
    >>> data = pd.read_csv('threshold_scan.csv',
    ...                    names=['time', 'duration', 'ch', 'vth', 'events', 'tmp', 'atm', 'hmd'])
    >>> thresholds, fitted_data, curve = fit_threshold_by_channel(
    ...     data, ch=1, func=erfc_function, params=[10, 300, 1, 1]
    ... )
    >>> thresholds['3sigma'].iloc[0]  # Recommended threshold
    283

    Notes
    -----
    - Performs two-stage fitting for improved convergence
    - Sigma levels represent: mean + N*sigma threshold recommendations
    - 3σ level is typically used as the optimal threshold
    - Fit curve spans the full range of input threshold values
    """

    # 実行した時刻を取得する
    now = pendulum.now()

    # データフレームのカラム名を確認する
    expected_names = ["time", "duration", "ch", "vth", "events", "tmp", "atm", "hmd"]
    names = list(data.columns)
    # assert names == expected_names

    # フィットの準備
    # 1. 該当するチャンネル番号のデータを抽出
    # 2. イベントレートの計算
    # 3. numpy配列に変換
    q = f"ch == {ch}"
    # print(f"----- Query: {q} -----")
    data_q = data.query(q).copy()
    data_q["event_rate"] = data_q["events"] / data_q["duration"]
    x_data = data_q["vth"]
    y_data = data_q["event_rate"]

    # フィットの初期パラメータ
    # TODO: 初期パラメータを外から調整できるようにする
    # params = [10.0, 300.0, 1.0, 1.0]

    # フィット：1回目
    popt, pcov = curve_fit(func, x_data, y_data, p0=params)
    # std = np.sqrt(np.diag(pcov))

    # logger.debug("フィット（1回目）")
    # logger.debug(f"Parameter Optimized  (popt) = {popt}")
    # logger.debug(f"Parameter Covariance (pcov) = {pcov}")
    # logger.debug(f"Parameter Std. Dev.  (std) = {std}")

    # フィット：2回目
    popt, pcov = curve_fit(func, x_data, y_data, p0=popt)
    # std = np.sqrt(np.diag(pcov))
    # logger.debug("フィット（2回目）")
    # logger.debug(f"Parameter Optimized  (popt) = {popt}")
    # logger.debug(f"Parameter Covariance (pcov) = {pcov}")
    # logger.debug(f"Parameter Std. Dev.  (std) = {std}")

    # フィット曲線
    # 1. フィットで得られた値を使って関数（numpy.array）を作成する
    # 2. データフレームに変換して返り値にする
    xmin = x_data.min()
    xmax = x_data.max()

    # logger.debug(xmin)
    # logger.debug(xmax)
    x_fit = np.arange(xmin, xmax, 0.1)
    a, b, c, d = popt
    y_fit = func(x_fit, a, b, c, d)
    data_f = pd.DataFrame(
        {
            "vth": x_fit,
            "event_rate": y_fit,
            "ch": f"fit{ch}",
        }
    )

    # フィット結果を使って閾値を計算する
    # 例：1sigma, 3sigma, 5sigma
    # pd.DataFrameに変換する
    mean, sigma = popt[1], popt[2]
    _thresholds = {
        "timestamp": now,
        "ch": ch,
        "0sigma": [round(mean)],
        "1sigma": [round(mean + 1 * sigma)],
        "3sigma": [round(mean + 3 * sigma)],
        "5sigma": [round(mean + 5 * sigma)],
    }
    thresholds = pd.DataFrame(_thresholds)

    return thresholds, data_q, data_f


def fit_thresholds(data: pd.DataFrame, channels: list[int], params: list[float]) -> pd.DataFrame:
    """Calculate optimal threshold values for multiple channels.

    Processes threshold scan data for multiple channels and determines
    optimal threshold values using complementary error function fitting.
    Returns a consolidated DataFrame with threshold recommendations
    for all specified channels.

    Parameters
    ----------
    data : pd.DataFrame
        Complete threshold scan data containing measurements for all channels
        with columns: ['time', 'duration', 'ch', 'vth', 'events', 'tmp', 'atm', 'hmd'].
    channels : list[int]
        List of channel numbers (1-3) to calculate thresholds for.
    params : list[float]
        Initial parameters for curve fitting [height, mean, sigma, offset].

    Returns
    -------
    pd.DataFrame
        Consolidated DataFrame with threshold values for all channels.
        Contains columns: ['timestamp', 'ch', '0sigma', '1sigma', '3sigma', '5sigma'].
        Each row represents one channel's calculated thresholds.

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.read_csv('threshold_scan.csv',
    ...                    names=['time', 'duration', 'ch', 'vth', 'events', 'tmp', 'atm', 'hmd'])
    >>> channels = [1, 2, 3]
    >>> params = [10, 300, 1, 1]  # [height, mean, sigma, offset]
    >>> thresholds = fit_thresholds(data, channels, params)
    >>> thresholds[['ch', '3sigma']]  # Show recommended thresholds
       ch  3sigma
    0   1     283
    1   2     278
    2   3     285

    Notes
    -----
    - Calls fit_threshold_by_channel() for each specified channel
    - Only returns threshold DataFrames, discards fitted data and curves
    - Results are concatenated with reset index for clean output
    - 3σ level is typically used as the optimal threshold value
    """
    threshold = []
    erfc = erfc_function
    for c in channels:
        _threshold, _, _ = fit_threshold_by_channel(data, ch=c, func=erfc, params=params)
        threshold.append(_threshold)

    thresholds = pd.concat(threshold, ignore_index=True)
    return thresholds
