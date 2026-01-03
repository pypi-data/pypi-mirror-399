"""Data transformation layer for processing raw detector events.

This module handles converting raw detector data into processed events by:
1. Parsing ISO8601 timestamps and applying timezone/offset
2. Detecting hit events (sensor > 0)
3. Computing composite hit classification (0-7)

Design (Principle IX - SRP):
- Single responsibility: Add calculated columns to raw data
- Pure functions, no side effects
- Each function adds one logical transformation

References:
- FR-002: Parse ISO8601 timestamps with timezone handling
- FR-003: Detect hits by checking sensor values
- FR-004: Calculate hit_type composite classification
- ADR-012: Pure functions, easy to unit test
"""

from typing import Optional
import pandas as pd
import pendulum

from haniwers.v1 import schema


def add_time_column(
    df: pd.DataFrame, tz_string: str = "UTC+09:00", offset_seconds: int = 0
) -> pd.DataFrame:
    """Parse timestamp column and add timezone-localized 'datetime' column.

    Converts ISO8601 timestamp strings to timezone-aware datetime with optional
    time offset correction. Used for FR-002 timestamp handling.

    Args:
        df: DataFrame with 'timestamp' column (ISO8601 strings)
        tz_string: Timezone string (e.g., "UTC+09:00")
        offset_seconds: Time offset correction in seconds (e.g., 0)

    Returns:
        DataFrame with new 'datetime' column (timezone-aware datetime)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"timestamp": ["2024-06-11T12:34:56Z"]})
        >>> result = add_time_column(df, "UTC+09:00", 0)
        >>> result['datetime'].dtype
        datetime64[ns, UTC+09:00]
    """
    df_copy = df.copy()

    # Parse ISO8601 timestamps (assumes UTC if no timezone specified)
    # Specify format to suppress UserWarning and enable strict parsing
    try:
        df_copy["datetime"] = pd.to_datetime(df_copy["timestamp"], utc=True, format="ISO8601")
    except (ValueError, TypeError) as e:
        # Re-raise with clearer message on parsing failure
        raise ValueError(f"Invalid timestamp format in 'timestamp' column: {e}") from e

    # Add offset (convert seconds to timedelta)
    if offset_seconds != 0:
        df_copy["datetime"] += pd.Timedelta(seconds=offset_seconds)

    # Apply timezone conversion
    df_copy["datetime"] = df_copy["datetime"].dt.tz_convert(tz_string)

    return df_copy


def add_hit_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect hits: create binary columns (1 if sensor > 0, else 0).

    Creates three binary columns (hit_top, hit_mid, hit_btm) by checking if
    corresponding sensor values exceed 0. Used for FR-003 hit detection.

    Args:
        df: DataFrame with 'top', 'mid', 'btm' sensor columns

    Returns:
        DataFrame with new binary columns: hit_top, hit_mid, hit_btm (each 0 or 1)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"top": [10, 0], "mid": [5, 0], "btm": [0, 0]})
        >>> result = add_hit_columns(df)
        >>> result[['hit_top', 'hit_mid', 'hit_btm']].values.tolist()
        [[1, 1, 0], [0, 0, 0]]
    """
    df_copy = df.copy()

    df_copy["hit_top"] = (df_copy["top"] > 0).astype(int)
    df_copy["hit_mid"] = (df_copy["mid"] > 0).astype(int)
    df_copy["hit_btm"] = (df_copy["btm"] > 0).astype(int)

    return df_copy


def compute_hit_type(df: pd.DataFrame) -> pd.DataFrame:
    """Compute composite hit_type (0-7) from binary hit columns.

    Combines three binary hit columns into a single composite classification
    using the formula: hit_type = hit_top*4 + hit_mid*2 + hit_btm.
    Used for FR-004 composite classification.

    Hit Type Meanings (0-7):
        0: No hits (noise/background)
        1: Bottom only
        2: Middle only
        3: Middle + Bottom
        4: Top only
        5: Top + Bottom
        6: Top + Middle (typical cosmic ray signature)
        7: All three (rare multi-layer event)

    Args:
        df: DataFrame with 'hit_top', 'hit_mid', 'hit_btm' binary columns

    Returns:
        DataFrame with new 'hit_type' column (0-7)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "hit_top": [1, 1, 0, 0],
        ...     "hit_mid": [1, 0, 1, 0],
        ...     "hit_btm": [0, 0, 0, 0]
        ... })
        >>> result = compute_hit_type(df)
        >>> result['hit_type'].tolist()
        [6, 4, 2, 0]
    """
    df_copy = df.copy()

    df_copy["hit_type"] = df_copy["hit_top"] * 4 + df_copy["hit_mid"] * 2 + df_copy["hit_btm"] * 1

    return df_copy


def process_raw_data(
    df: pd.DataFrame,
    tz_string: str = "UTC+09:00",
    offset_seconds: int = 0,
) -> pd.DataFrame:
    """Apply all transformations to convert raw events to processed events.

    Orchestrates all transformer functions in sequence to convert raw detector
    data into processed events with timestamps and hit classifications.

    Args:
        df: Raw DataFrame from reader
        tz_string: Timezone string (default Japan timezone)
        offset_seconds: Time offset correction in seconds

    Returns:
        Processed DataFrame with all calculated columns

    Example:
        >>> import pandas as pd
        >>> raw_df = pd.DataFrame({
        ...     "timestamp": ["2024-06-11T12:34:56Z"],
        ...     "top": [10], "mid": [5], "btm": [0],
        ...     "adc": [100], "tmp": [25.5], "atm": [1013.25], "hmd": [60]
        ... })
        >>> result = process_raw_data(raw_df)
        >>> list(result.columns)
        ['timestamp', 'top', 'mid', 'btm', 'adc', 'tmp', 'atm', 'hmd',
         'datetime', 'hit_top', 'hit_mid', 'hit_btm', 'hit_type']
    """
    df_processed = df.copy()
    df_processed = add_time_column(df_processed, tz_string, offset_seconds)
    df_processed = add_hit_columns(df_processed)
    df_processed = compute_hit_type(df_processed)
    return df_processed
