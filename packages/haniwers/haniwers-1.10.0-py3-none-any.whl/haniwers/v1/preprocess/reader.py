"""File I/O layer for loading raw detector CSV files.

This module handles reading detector data from CSV files using Polars for
high performance. It includes validation to ensure required columns are present.

Design (Principle IX - SRP):
- Single responsibility: Load CSV files and validate schema
- Used by converter to load raw data before transformation
- Returns polars DataFrame for fast I/O

References:
- FR-001: Load multiple CSV files and combine into single dataset
- ADR-012: Pure functions, easy to unit test
"""

from typing import List
from pathlib import Path
import polars as pl

from haniwers.v1 import schema


def load_csv_files(file_paths: List[Path]) -> pl.DataFrame:
    """Load multiple CSV files and combine into single DataFrame.

    Uses Polars for fast CSV parsing and combines all files into a single
    DataFrame for processing.

    Automatically detects whether CSV files have headers or not:
    - Files with headers: Reads normally with column names from first row
    - Files without headers: Applies RAW_COLUMNS as column names

    Args:
        file_paths: List of Path objects to CSV files containing detector data

    Returns:
        Combined polars DataFrame with all rows from input files

    Raises:
        ValueError: If any file is missing required columns

    Example:
        >>> from pathlib import Path
        >>> files = [Path("run93_001.csv"), Path("run93_002.csv")]
        >>> df = load_csv_files(files)
        >>> print(df.shape)
        (13856, 8)
    """
    dataframes = []

    for path in file_paths:
        # Try reading with headers first
        df = pl.read_csv(path)

        # Check if headers are valid (e.g., "datetime", "top", etc.)
        # If first row looks like data (numbers), re-read without headers
        if not _has_valid_headers(df):
            # Validate column count before re-reading
            if df.shape[1] != len(schema.RAW_COLUMNS):
                raise ValueError(
                    f"Missing columns: expected {len(schema.RAW_COLUMNS)} columns, "
                    f"but got {df.shape[1]}"
                )
            df = pl.read_csv(path, has_header=False, new_columns=schema.RAW_COLUMNS)

        validate_columns(df)  # Check required columns exist
        dataframes.append(df)

    # Combine all DataFrames
    if not dataframes:
        raise ValueError("No CSV files provided")

    return pl.concat(dataframes)


def _has_valid_headers(df: pl.DataFrame) -> bool:
    """Check if DataFrame has valid column headers.

    Validates that the first row contains expected column names
    rather than data values.

    Args:
        df: polars DataFrame to check

    Returns:
        True if columns match RAW_COLUMNS, False otherwise
    """
    expected = set(schema.RAW_COLUMNS)
    actual = set(df.columns)
    return expected == actual


def validate_columns(df: pl.DataFrame) -> None:
    """Check that all required columns exist in DataFrame.

    Validates that a polars DataFrame has all the columns expected from the
    OSECHI detector output before processing.

    Args:
        df: polars DataFrame to validate

    Raises:
        ValueError: If any required columns are missing
    """
    required = schema.RAW_COLUMNS
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
