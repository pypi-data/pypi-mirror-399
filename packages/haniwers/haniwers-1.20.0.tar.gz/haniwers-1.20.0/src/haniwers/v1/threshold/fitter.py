"""Threshold fitting functionality for analysis of scan results.

This module provides threshold fitting analysis for ThresholdScanResult data,
calculating optimal threshold values using complementary error function fitting.

Functions:
    erfc_function: Complementary error function for threshold fitting
    fit_threshold_by_channel: Fit error function to threshold scan data for a single channel
    fit_thresholds: Calculate optimal thresholds for multiple channels

Examples:
    Basic threshold fitting workflow:

    >>> import pandas as pd
    >>> from haniwers.v1.threshold.fitter import fit_thresholds
    >>> data = pd.read_csv('scan_results.csv')
    >>> optimal_thresholds = fit_thresholds(data, channels=[1, 2, 3], params=[10, 300, 1, 1])
    >>> print(optimal_thresholds[['ch', '3sigma']])
"""

from typing import NamedTuple
from pathlib import Path

import numpy as np
import pandas as pd
import pendulum
from scipy.optimize import curve_fit
from scipy.special import erfc

from haniwers.v1.log.logger import logger as base_logger

# Bind context for all threshold fitting operations
logger = base_logger.bind(context="threshold.fitter")


class ThresholdFitResult(NamedTuple):
    """Result of threshold fitting for a single channel.

    Attributes:
        ch: Channel number (1-3)
        timestamp: ISO8601 timestamp of when fit was performed
        mean: Mean threshold value (b parameter from erfc fit)
        sigma: Sigma parameter (width of transition region)
        sigma_0: Optimal threshold at 0σ level (mean)
        sigma_1: Optimal threshold at 1σ level
        sigma_3: Optimal threshold at 3σ level (recommended)
        sigma_5: Optimal threshold at 5σ level
    """

    ch: int
    timestamp: str
    mean: float
    sigma: float
    sigma_0: float
    sigma_1: float
    sigma_3: float
    sigma_5: float


def erfc_function(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """Complementary error function for threshold fitting.

    Mathematical function used to fit threshold scan data S-curves.
    This function models the probability distribution of detector
    response as a function of threshold voltage.

    The function is defined as:
        f(x) = a * erfc((x - b) / c) + d

    where erfc(x) = 1 - erf(x) is the complementary error function.

    Parameters
    ----------
    x : np.ndarray
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
    np.ndarray
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
    2. Calculates event rates (events/event_count)
    3. Performs curve fitting with provided initial parameters
    4. Repeats fitting using optimized parameters for better convergence
    5. Generates fit curve and calculates threshold recommendations

    Parameters
    ----------
    data : pd.DataFrame
        Threshold scan data with columns for channel thresholds and hit counts.
        Expected to contain columns: 'ch1', 'ch2', 'ch3' for thresholds
        and 'top', 'mid', 'btm' for hit counts.
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
        Data subset for the specified channel with added 'event_rate' column.
    fit_curve : pd.DataFrame
        Fitted curve data points for plotting with columns ['vth', 'event_rate', 'ch'].

    Examples
    --------
    >>> import pandas as pd
    >>> from haniwers.v1.threshold.fitter import fit_threshold_by_channel, erfc_function
    >>> data = pd.read_csv('scan_results.csv')
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
    # Get current timestamp
    now = pendulum.now()

    # Map channel number to column names
    channel_col = f"ch{ch}"
    if ch == 1:
        hit_col = "top"
    elif ch == 2:
        hit_col = "mid"
    elif ch == 3:
        hit_col = "btm"
    else:
        raise ValueError(f"Invalid channel: {ch}. Must be 1, 2, or 3")

    # Extract data for the specified channel
    data_q = data.copy()
    data_q["vth"] = data_q[channel_col]
    data_q["hits"] = data_q[hit_col]

    # Calculate event rate (hits / event_count)
    # Handle case where event_count is 0 to avoid division by zero
    data_q["event_rate"] = data_q["hits"] / data_q["event_count"].replace(0, 1)

    x_data = data_q["vth"].values
    y_data = data_q["event_rate"].values

    # TODO: Improve curve_fit stability with real detector data
    # Current OptimizeWarning occurs with demo data due to limited signal variation.
    # When testing with real cosmic ray data, the natural variation in event counts
    # may eliminate this warning. If issues persist with real data, consider:
    # - Implementing better initial parameter estimation from data characteristics
    # - Adding data quality checks before fitting (sufficient variation, outliers)
    # - Using alternative fitting methods (robust fitting) for edge cases
    # Perform fitting: Stage 1
    popt, pcov = curve_fit(func, x_data, y_data, p0=params, maxfev=10000)

    # Perform fitting: Stage 2 (refine with optimized parameters)
    popt, pcov = curve_fit(func, x_data, y_data, p0=popt, maxfev=10000)

    # Generate fit curve using optimized parameters
    xmin = x_data.min()
    xmax = x_data.max()
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

    # Calculate threshold values at different sigma levels
    mean, sigma = popt[1], popt[2]
    _thresholds = {
        "timestamp": [now],
        "ch": [ch],
        "0sigma": [round(mean)],
        "1sigma": [round(mean + 1 * sigma)],
        "3sigma": [round(mean + 3 * sigma)],
        "5sigma": [round(mean + 5 * sigma)],
    }
    thresholds = pd.DataFrame(_thresholds)

    logger.debug(f"Fitted channel {ch}: mean={mean:.2f}, sigma={sigma:.2f}")
    logger.debug(f"  0σ: {thresholds['0sigma'].iloc[0]}")
    logger.debug(f"  1σ: {thresholds['1sigma'].iloc[0]}")
    logger.debug(f"  3σ: {thresholds['3sigma'].iloc[0]}")
    logger.debug(f"  5σ: {thresholds['5sigma'].iloc[0]}")

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
        Complete threshold scan data containing measurements for all channels.
        Expected to have columns: 'event_count', 'ch1', 'ch2', 'ch3', 'top', 'mid', 'btm'.
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
    >>> from haniwers.v1.threshold.fitter import fit_thresholds
    >>> data = pd.read_csv('scan_results.csv')
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
    threshold_results = []

    for ch in channels:
        try:
            _threshold, _, _ = fit_threshold_by_channel(
                data, ch=ch, func=erfc_function, params=params
            )
            threshold_results.append(_threshold)
        except Exception as e:
            logger.error(f"Failed to fit channel {ch}: {str(e)}")
            continue

    if not threshold_results:
        raise ValueError("No channels were successfully fitted")

    thresholds = pd.concat(threshold_results, ignore_index=True)
    return thresholds


def verify_fit_quality(
    scan_data: pd.DataFrame, fit_results: pd.DataFrame, verbose: bool = True
) -> dict:
    """Verify threshold fit quality and reasonableness.

    Performs statistical and physical validation of fitting results,
    checking for data completeness, reasonable threshold values,
    event distribution, and potential fitting issues.

    Parameters
    ----------
    scan_data : pd.DataFrame
        Threshold scan data with columns: timestamp, event_count, ch1, ch2, ch3, top, mid, btm
    fit_results : pd.DataFrame
        Fit results with columns: timestamp, ch, 0sigma, 1sigma, 3sigma, 5sigma
    verbose : bool
        Print verification results to console

    Returns
    -------
    dict
        Verification results for all channels with keys:
        - channel: Channel number
        - sigma_0: 0σ threshold value
        - sigma_3: 3σ threshold value (recommended)
        - data_points: Number of data points for fitting
        - x_range: (min, max) of threshold values in scan
        - y_range: (min, max) of event counts
        - warnings: List of warning messages (if any)

    Example
    -------
    >>> results = verify_fit_quality(scan_data, fit_results)
    >>> for ch, info in results.items():
    ...     if info['warnings']:
    ...         print(f"Channel {ch}: {info['warnings']}")
    """
    all_results = {}

    for ch in [1, 2, 3]:
        col_name = f"ch{ch}"

        if col_name not in scan_data.columns:
            all_results[ch] = {"error": f"Column '{col_name}' not found in scan data"}
            continue

        # Extract data for this channel
        x_data = scan_data[col_name].values
        y_data = scan_data["event_count"].values

        # Get fitted thresholds
        ch_matches = fit_results[fit_results["ch"] == ch]
        if len(ch_matches) == 0:
            all_results[ch] = {"error": f"No fit results found for channel {ch}"}
            continue

        ch_result = ch_matches.iloc[0]
        sigma_0 = int(ch_result["0sigma"])
        sigma_3 = int(ch_result["3sigma"])

        # Perform checks
        warnings = []
        x_min, x_max = float(x_data.min()), float(x_data.max())
        y_min, y_max = float(y_data.min()), float(y_data.max())

        # Check 1: Threshold range
        if not (x_min <= sigma_3 <= x_max):
            warnings.append(f"3σ={sigma_3} outside scan range [{x_min:.0f}-{x_max:.0f}]")

        # Check 2: Reasonable threshold value
        if not (100 <= sigma_3 <= 1000):
            warnings.append(f"3σ={sigma_3} outside typical range [100-1000]")

        # Check 3: Event distribution
        center_mask = np.abs(x_data - sigma_0) < 10
        sigma3_mask = np.abs(x_data - sigma_3) < 10

        if center_mask.sum() > 0 and sigma3_mask.sum() > 0:
            events_at_center = y_data[center_mask].mean()
            events_at_3sigma = y_data[sigma3_mask].mean()

            if events_at_center > 0:
                reduction = (1 - events_at_3sigma / events_at_center) * 100
                if reduction < 5:
                    warnings.append(f"Low event reduction ({reduction:.1f}%) - flat response")
                elif reduction > 98:
                    warnings.append(f"High event reduction ({reduction:.1f}%) - sharp cutoff")

        # Check 4: Data quality
        if len(x_data) < 20:
            warnings.append(f"Limited data ({len(x_data)} points) - may affect fit")

        result = {
            "channel": ch,
            "sigma_0": sigma_0,
            "sigma_3": sigma_3,
            "data_points": len(x_data),
            "x_range": (x_min, x_max),
            "y_range": (y_min, y_max),
            "warnings": warnings,
        }

        if verbose:
            print(f"\n{'=' * 70}")
            print(f"Channel {ch}: σ0={sigma_0}, σ3={sigma_3}")
            print(f"{'=' * 70}")
            print(
                f"Data: {len(x_data)} points, threshold=[{x_min:.0f}-{x_max:.0f}], events=[{y_min:.0f}-{y_max:.0f}]"
            )

            if warnings:
                print(f"⚠ Warnings:")
                for w in warnings:
                    print(f"  - {w}")
            else:
                print(f"✓ All checks passed")

        all_results[ch] = result

    return all_results


def plot_fit_results(
    scan_data: pd.DataFrame,
    fit_results: pd.DataFrame,
    output_dir: Path = None,
    verbose: bool = False,
) -> dict:
    """Create and save interactive hvplot visualizations of fit results.

    Generates per-channel plots showing:
    - Scan data points (actual threshold measurements)
    - Fitted curve (complementary error function)
    - Threshold recommendations at different sigma levels (0σ, 1σ, 3σ, 5σ)
    - Event rate vs threshold voltage

    Each channel gets its own interactive HTML visualization saved to disk.

    NOTE: This function requires hvplot and holoviews packages.
    Install with: pip install haniwers[analysis]

    Parameters
    ----------
    scan_data : pd.DataFrame
        Original threshold scan data with columns: timestamp, event_count,
        ch1, ch2, ch3, top, mid, btm
    fit_results : pd.DataFrame
        Fitted threshold values with columns: timestamp, ch, 0sigma, 1sigma,
        3sigma, 5sigma (output from fit_thresholds)
    output_dir : Path, optional
        Directory to save visualization HTML files. If None, creates
        'threshold_plots' subdirectory in current working directory.
    verbose : bool
        Print status messages during visualization creation

    Returns
    -------
    dict
        Visualization metadata with keys:
        - channel: Channel number
        - plot_file: Path to saved HTML file
        - data_points: Number of scan data points
        - threshold_3sigma: Recommended threshold (3σ level)

    Raises
    ------
    ImportError
        If hvplot or holoviews packages are not installed.

    Example
    -------
    >>> import pandas as pd
    >>> from haniwers.v1.threshold.fitter import fit_thresholds, plot_fit_results
    >>> scan_data = pd.read_csv('scan_results.csv')
    >>> fit_results = fit_thresholds(scan_data, channels=[1, 2, 3], params=[10, 300, 1, 1])
    >>> plot_results = plot_fit_results(scan_data, fit_results, output_dir=Path('./plots'))
    >>> print(plot_results[1]['plot_file'])  # Path to channel 1 plot

    Notes
    -----
    - Requires hvplot and bokeh for interactive HTML generation
    - Each plot includes interactive legend, zoom, pan, and hover tools
    - Threshold lines (0σ, 1σ, 3σ, 5σ) are color-coded for easy interpretation
    - Output files are named: threshold_fit_ch{N}.html (where N is channel number)
    """
    # Lazy import: load hvplot and holoviews only when needed
    try:
        import hvplot.pandas  # noqa: F401
        import holoviews as hv
    except ImportError as e:
        raise ImportError(
            "plot_fit_results() requires hvplot and holoviews packages.\n"
            "Install with: pip install haniwers[analysis]"
        ) from e

    if output_dir is None:
        output_dir = Path.cwd() / "threshold_plots"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_metadata = {}

    for ch in [1, 2, 3]:
        try:
            if verbose:
                logger.info(f"Creating visualization for channel {ch}...")

            # Get fit data for this channel
            ch_fit = fit_results[fit_results["ch"] == ch]
            if ch_fit.empty:
                logger.warning(f"No fit results for channel {ch}, skipping plot")
                continue

            # Re-fit to get raw data and fitted curve
            thresholds, data_q, data_f = fit_threshold_by_channel(
                scan_data, ch=ch, func=erfc_function, params=[10, 300, 1, 1]
            )

            # Prepare data for plotting
            # Raw scan data
            plot_data = data_q[["vth", "event_rate"]].copy()
            plot_data["type"] = "scan"
            plot_data["ch"] = ch

            # Fitted curve
            curve_data = data_f[["vth", "event_rate"]].copy()
            curve_data["type"] = "fit"
            curve_data["ch"] = ch

            # Combine data
            plot_df = pd.concat([plot_data, curve_data], ignore_index=True)

            # Get threshold values
            sig_0 = ch_fit["0sigma"].iloc[0]
            sig_1 = ch_fit["1sigma"].iloc[0]
            sig_3 = ch_fit["3sigma"].iloc[0]
            sig_5 = ch_fit["5sigma"].iloc[0]

            # Create hvplot visualization
            plot = plot_df[plot_df["type"] == "scan"].hvplot.scatter(
                x="vth",
                y="event_rate",
                label="Scan Data",
                size=100,
                color="steelblue",
                alpha=0.7,
                title=f"Threshold Fit - Channel {ch}",
                xlabel="Threshold (mV)",
                ylabel="Event Rate (events/count)",
                width=900,
                height=600,
            ) * plot_df[plot_df["type"] == "fit"].hvplot.line(
                x="vth",
                y="event_rate",
                label="Fitted Curve",
                color="red",
                line_width=2,
            )

            # Add vertical lines for threshold recommendations
            # Using hlines to add threshold reference lines
            import holoviews as hv

            # Create threshold reference lines as separate curves
            y_min = plot_df["event_rate"].min()
            y_max = plot_df["event_rate"].max()
            x_range = plot_df["vth"].max() - plot_df["vth"].min()

            # Add threshold lines as overlays
            for threshold_val, threshold_name, color in [
                (sig_0, "0σ", "orange"),
                (sig_1, "1σ", "gold"),
                (sig_3, "3σ", "green"),
                (sig_5, "5σ", "purple"),
            ]:
                # Create a small vertical line at each threshold
                threshold_line_df = pd.DataFrame(
                    {"vth": [threshold_val, threshold_val], "event_rate": [y_min, y_max]}
                )
                line = threshold_line_df.hvplot.line(
                    x="vth",
                    y="event_rate",
                    label=f"{threshold_name} ({threshold_val})",
                    color=color,
                    line_width=1.5,
                    line_dash="dashed",
                )
                plot = plot * line

            # Save to HTML file
            output_file = output_dir / f"threshold_fit_ch{ch}.html"
            hv.save(plot, str(output_file))

            if verbose:
                logger.info(f"Saved plot to {output_file}")

            plot_metadata[ch] = {
                "channel": ch,
                "plot_file": output_file,
                "data_points": len(data_q),
                "threshold_3sigma": sig_3,
            }

        except Exception as e:
            logger.error(f"Failed to create plot for channel {ch}: {str(e)}")
            if verbose:
                logger.exception(e)
            continue

    if not plot_metadata:
        raise ValueError("Failed to create visualizations for any channels")

    return plot_metadata
