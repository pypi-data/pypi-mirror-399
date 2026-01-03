"""Column definitions and schema constants for raw2csv data processing pipeline.

This module defines column names as constants to prevent duplication and ensure
consistency across reader, transformer, and aggregator modules.

Design Note (Principle VIII - DRY):
- All column names defined in one place
- Imported by other modules to maintain consistency
- Changes to schema only require updates here
"""

# RawEvent columns - direct from input CSV files
# These are the columns expected from the OSECHI detector output (raw, uncorrected)
RAW_COLUMNS = [
    "timestamp",  # ISO8601 timestamp string (raw, no timezone/offset corrections)
    "top",  # Top layer sensor ADC value
    "mid",  # Middle layer sensor ADC value
    "btm",  # Bottom layer sensor ADC value
    "adc",  # ADC (Analog-to-Digital Conversion) reading
    "tmp",  # Temperature sensor reading
    "atm",  # Atmospheric pressure reading
    "hmd",  # Humidity sensor reading
]

# ProcessedEvent columns - after transformer adds calculated columns
# Replaces raw "timestamp" with corrected "datetime" + adds hit detection columns
PROCESSED_COLUMNS = [
    "datetime",  # Timezone-aware datetime after transformation (with timezone/offset corrections)
    "top",  # Top layer sensor ADC value (from raw)
    "mid",  # Middle layer sensor ADC value (from raw)
    "btm",  # Bottom layer sensor ADC value (from raw)
    "adc",  # ADC (Analog-to-Digital Conversion) reading (from raw)
    "tmp",  # Temperature sensor reading (from raw)
    "atm",  # Atmospheric pressure reading (from raw)
    "hmd",  # Humidity sensor reading (from raw)
    "hit_top",  # Binary: 1 if top layer detected hit, 0 otherwise
    "hit_mid",  # Binary: 1 if middle layer detected hit, 0 otherwise
    "hit_btm",  # Binary: 1 if bottom layer detected hit, 0 otherwise
    "hit_type",  # Composite: 0-7 representing hit pattern (top*4 + mid*2 + btm)
]

# ResampledEvent columns - after aggregator creates time windows
# This represents the final output for time-series analysis
# Format follows v0 compatibility for resampled/aggregated data
RESAMPLED_COLUMNS = [
    "time",  # Window boundary time
    "events",  # Count of events in this window
    "hit_top",  # Sum of top layer hits in window
    "hit_mid",  # Sum of middle layer hits in window
    "hit_btm",  # Sum of bottom layer hits in window
    "hit_type",  # Hit type classification (0-7)
    "adc",  # Mean ADC value in window
    "tmp",  # Mean temperature in window
    "atm",  # Mean atmospheric pressure in window
    "hmd",  # Mean humidity in window
    "adc_std",  # Standard deviation of ADC in window
    "tmp_std",  # Standard deviation of temperature in window
    "atm_std",  # Standard deviation of atmospheric pressure in window
    "hmd_std",  # Standard deviation of humidity in window
    "interval",  # Aggregation interval in seconds
    "days",  # Days elapsed from measurement start
    "seconds",  # Seconds elapsed from measurement start
    "event_rate",  # Overall event rate: events / interval
    "event_rate_top",  # Top layer event rate: hit_top / interval
    "event_rate_mid",  # Middle layer event rate: hit_mid / interval
    "event_rate_btm",  # Bottom layer event rate: hit_btm / interval
]


def validate_dataframe_schema(df, expected_columns: list) -> bool:
    """Check if DataFrame has all expected columns.

    This function validates that a DataFrame contains all required columns,
    which is essential for ensuring data integrity through the processing pipeline.

    Args:
        df: pandas or polars DataFrame to validate
        expected_columns: list of column names to check for

    Returns:
        True if all columns present, False otherwise

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        >>> validate_dataframe_schema(df, ["a", "b"])
        True
        >>> validate_dataframe_schema(df, ["a", "c"])
        False
    """
    missing = set(expected_columns) - set(df.columns)
    if missing:
        print(f"ERROR: Missing columns: {missing}")
        return False
    return True
