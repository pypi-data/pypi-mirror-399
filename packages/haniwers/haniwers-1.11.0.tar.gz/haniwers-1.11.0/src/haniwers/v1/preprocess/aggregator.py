# -*- coding: utf-8 -*-
"""Aggregation layer for time-series statistics and resampling.

This module handles converting processed events into time-windowed statistics by:

1. Resampling to fixed time intervals (600s default)
2. Computing mean and standard deviation for numeric columns
3. Calculating event rates per time window

Design (Principle IX - SRP):

- Single responsibility: Aggregate processed data into statistics
- Pure functions, no side effects
- Each function adds one logical aggregation step

References:

- FR-005: Resample time-series data at variable intervals
- FR-006: Compute aggregated metrics (mean, std, rates)
- ADR-012: Pure functions, easy to unit test
"""

from typing import Dict, List
import pandas as pd
import numpy as np

from haniwers.v1 import schema


def resample_by_interval(df: pd.DataFrame, interval_seconds: int = 600) -> pd.DataFrame:
    """Group events into time windows and aggregate.

    Resamples a processed event DataFrame into fixed-size time windows,
    grouping by both time interval and hit_type for statistics aggregation.

    Args:
        df: DataFrame with 'datetime' column (timezone-aware datetime)
        interval_seconds: Window size in seconds (default 600s = 10 minutes)

    Returns:
        DataFrame with one row per interval per hit_type, containing counts

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "datetime": pd.date_range("2024-06-11 12:00:00", periods=3600, freq="1s"),
        ...     "hit_type": [0, 1, 6] * 1200
        ... })
        >>> resampled = resample_by_interval(df, interval_seconds=600)
        >>> resampled.shape
        (4, 3)  # 4 windows x 3 hit types
    """
    df_copy = df.copy()

    # Ensure datetime column is timezone-aware datetime
    if not isinstance(df_copy["datetime"].dtype, pd.DatetimeTZDtype):
        # If naive, try to localize to UTC first
        if pd.api.types.is_datetime64_any_dtype(df_copy["datetime"]):
            df_copy["datetime"] = df_copy["datetime"].dt.tz_localize("UTC")

    # Set datetime as index for resampling
    df_copy = df_copy.set_index("datetime")

    # Group by time interval AND hit_type
    grouped = df_copy.groupby([pd.Grouper(freq=f"{interval_seconds}s"), "hit_type"])

    # Create aggregation DataFrame
    result_list = []
    for (time_bin, hit_type), group in grouped:
        if len(group) > 0:  # Only include non-empty windows
            result_list.append(
                {
                    "time": time_bin,
                    "hit_type": hit_type,
                    "events": len(group),
                }
            )

    result = pd.DataFrame(result_list)
    return result


def compute_statistics(
    df: pd.DataFrame, processed_df: pd.DataFrame, interval_seconds: int = 600
) -> pd.DataFrame:
    """Calculate mean and std for numeric columns per time window.

    Computes aggregated statistics (mean, std) for environmental columns
    within each time window, grouped by hit_type.

    Args:
        df: Aggregated DataFrame from resample_by_interval()
        processed_df: Original processed DataFrame (for numeric columns)
        interval_seconds: Window size for binning (for reference)

    Returns:
        DataFrame with adc_mean, adc_std, tmp_mean, tmp_std, atm_mean, atm_std

    Example:
        >>> import pandas as pd
        >>> processed_df = pd.DataFrame({
        ...     "datetime": pd.date_range("2024-06-11 12:00:00", periods=100, freq="1s"),
        ...     "hit_type": [0, 1, 6] * 33 + [0],
        ...     "adc": range(100),
        ...     "tmp": [25.0 + i * 0.1 for i in range(100)],
        ...     "atm": [1013.25] * 100
        ... })
        >>> resampled = resample_by_interval(processed_df, 60)
        >>> stats = compute_statistics(resampled, processed_df, 60)
        >>> "adc_mean" in stats.columns
        True
    """
    df_copy = df.copy()

    # Numeric columns to aggregate
    numeric_cols = ["adc", "tmp", "atm", "hmd"]

    # For each numeric column, calculate mean and std
    for col in numeric_cols:
        df_copy[f"{col}_mean"] = np.nan
        df_copy[f"{col}_std"] = np.nan

        # Ensure processed_df datetime is comparable (using schema column name)
        processed_copy = processed_df.copy()
        datetime = schema.PROCESSED_COLUMNS[0]  # First column is "datetime"
        if not isinstance(processed_copy[datetime].dtype, pd.DatetimeTZDtype):
            if pd.api.types.is_datetime64_any_dtype(processed_copy[datetime]):
                processed_copy[datetime] = processed_copy[datetime].dt.tz_localize("UTC")

        # For each row in result, find matching events in processed_df
        for idx, row in df_copy.iterrows():
            time_bin = row["time"]
            hit_type = row["hit_type"]
            next_bin = time_bin + pd.Timedelta(seconds=interval_seconds)

            # Find events in this time window with this hit_type
            mask = (processed_copy[datetime] >= time_bin) & (processed_copy[datetime] < next_bin)
            mask = mask & (processed_copy["hit_type"] == hit_type)
            window_data = processed_copy[mask][col]

            if len(window_data) > 0:
                # Exclude NaN values for statistics
                valid_data = window_data.dropna()
                if len(valid_data) > 0:
                    df_copy.loc[idx, f"{col}_mean"] = valid_data.mean()
                    if len(valid_data) > 1:
                        df_copy.loc[idx, f"{col}_std"] = valid_data.std()
                    else:
                        df_copy.loc[idx, f"{col}_std"] = 0.0

    return df_copy


def compute_event_rates(df: pd.DataFrame, interval_seconds: int = 600) -> pd.DataFrame:
    """Calculate event rates (events per second) per time window.

    Computes overall and per-layer event rates by dividing event counts
    by the time interval. Rates represent frequency of events in Hz (events/sec).

    Args:
        df: Aggregated DataFrame with 'events' column
        interval_seconds: Window size for rate calculation

    Returns:
        DataFrame with event_rate, event_rate_top, event_rate_mid, event_rate_btm

    Formulas:
        event_rate = events / interval_seconds
        event_rate_top = sum(hit_top) / interval_seconds  (for hit_type 4,5,6,7)
        event_rate_mid = sum(hit_mid) / interval_seconds  (for hit_type 2,3,6,7)
        event_rate_btm = sum(hit_btm) / interval_seconds  (for hit_type 1,3,5,7)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "time": pd.date_range("2024-06-11", periods=2, freq="10min"),
        ...     "hit_type": [0, 6],
        ...     "events": [60, 120]
        ... })
        >>> rates = compute_event_rates(df, 600)
        >>> rates["event_rate"].tolist()
        [0.1, 0.2]
    """
    df_copy = df.copy()

    # Overall event rate
    df_copy["event_rate"] = df_copy["events"] / interval_seconds

    # Per-layer event rates (based on hit_type bit pattern)
    # hit_type = hit_top*4 + hit_mid*2 + hit_btm
    # Extract individual hit flags from hit_type
    df_copy["hit_top_count"] = (
        (df_copy["hit_type"] // 4) * df_copy["events"]
    ) / 3.0  # Approximate: assume uniform distribution
    df_copy["hit_mid_count"] = (((df_copy["hit_type"] % 4) // 2) * df_copy["events"]) / 3.0
    df_copy["hit_btm_count"] = ((df_copy["hit_type"] % 2) * df_copy["events"]) / 3.0

    df_copy["event_rate_top"] = df_copy["hit_top_count"] / interval_seconds
    df_copy["event_rate_mid"] = df_copy["hit_mid_count"] / interval_seconds
    df_copy["event_rate_btm"] = df_copy["hit_btm_count"] / interval_seconds

    # Clean up temporary columns
    df_copy = df_copy.drop(columns=["hit_top_count", "hit_mid_count", "hit_btm_count"])

    return df_copy
