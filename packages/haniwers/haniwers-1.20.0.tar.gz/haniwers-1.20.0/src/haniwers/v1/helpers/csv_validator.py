"""Unified CSV column validation for OSECHI detector data.

Consolidates CSV column validation patterns across the codebase (P1-8) to:
- Eliminate duplicate column discovery logic
- Provide consistent error handling
- Support flexible column name variants
- Work with both pandas and polars DataFrames

This module is the single source of truth for CSV schema validation, replacing
scattered column checks across preprocess/reader.py, cli/preprocess.py, and
other data layer modules.

Design (Principle VIII - DRY):
- Single responsibility: Validate CSV schemas and find columns
- Consolidates ~50 lines of duplicated column discovery code
- Provides flexible column matching with name variants
- Raises InvalidCSVError with clear error messages
"""

from typing import Union, Dict, List, Any, TYPE_CHECKING
from loguru import logger

from haniwers.v1.helpers.exceptions import InvalidCSVError
from haniwers.v1 import schema

if TYPE_CHECKING:
    from pandas import DataFrame as PandasDataFrame
    import polars as pl
else:
    PandasDataFrame = Any
    pl = Any

# Type alias for either pandas or polars DataFrames
# Any covers polars.DataFrame
DataFrameType = Union[PandasDataFrame, Any]


def validate_raw_csv_columns(df: DataFrameType) -> None:
    """Validate that a raw detector CSV has all required columns.

    Raw detector CSVs from OSECHI detector must have 8 columns with specific names.
    This validator ensures data integrity before processing.

    Args:
        df: pandas or polars DataFrame to validate

    Raises:
        InvalidCSVError: If any required columns are missing

    Example:
        >>> import polars as pl
        >>> df = pl.read_csv("run93_001.csv")
        >>> validate_raw_csv_columns(df)  # OK if all 8 columns present
        >>> # Raises InvalidCSVError if columns missing
    """
    required = schema.RAW_COLUMNS
    actual = set(df.columns) if hasattr(df, "columns") else set(df.columns)
    missing = set(required) - actual

    if missing:
        msg = (
            f"Raw CSV missing required columns: {sorted(missing)}. "
            f"Expected columns: {required}. "
            f"Found columns: {list(df.columns)}"  # noqa: E501
        )
        logger.error(msg)
        raise InvalidCSVError(msg)


def validate_processed_csv_columns(df: DataFrameType) -> None:
    """Validate that a processed detector CSV has all required columns.

    Processed CSVs must include original raw columns plus computed columns
    (hit_top, hit_mid, hit_btm, hit_type).

    Args:
        df: pandas or polars DataFrame to validate

    Raises:
        InvalidCSVError: If any required columns are missing

    Example:
        >>> df = load_processed_csv("processed.csv")
        >>> validate_processed_csv_columns(df)  # OK if all columns present
    """
    required = set(schema.RAW_COLUMNS) | {"hit_top", "hit_mid", "hit_btm", "hit_type"}
    actual = set(df.columns) if hasattr(df, "columns") else set(df.columns)
    missing = required - actual

    if missing:
        msg = (
            f"Processed CSV missing required columns: {sorted(missing)}. "
            f"Expected columns: {sorted(required)}. "
            f"Found columns: {list(df.columns)}"  # noqa: E501
        )
        logger.error(msg)
        raise InvalidCSVError(msg)


def validate_resampled_csv_columns(df: DataFrameType) -> None:
    """Validate that a resampled detector CSV has all required columns.

    Resampled CSVs contain aggregated statistics per time interval.

    Args:
        df: pandas or polars DataFrame to validate

    Raises:
        InvalidCSVError: If any required columns are missing

    Example:
        >>> df = load_resampled_csv("resampled.csv")
        >>> validate_resampled_csv_columns(df)  # OK if all columns present
    """
    required = {"datetime", "interval", "adc_mean", "tmp_mean", "atm_mean", "hmd_mean"}
    actual = set(df.columns) if hasattr(df, "columns") else set(df.columns)
    missing = required - actual

    if missing:
        msg = (
            f"Resampled CSV missing required columns: {sorted(missing)}. "
            f"Expected columns: {sorted(required)}. "
            f"Found columns: {list(df.columns)}"  # noqa: E501
        )
        logger.error(msg)
        raise InvalidCSVError(msg)


def find_csv_column(
    df: DataFrameType,
    name_variants: List[str],
    column_description: str = "column",
) -> str:
    """Find a CSV column by trying multiple name variants.

    Useful for handling CSV files from different sources that may use
    different column naming conventions (e.g., "run_id", "run id",
    "runid"). This consolidates the repetitive column-finding pattern
    used in cli/preprocess.py (P1-8 consolidation).

    Args:
        df: pandas or polars DataFrame to search
        name_variants: List of column names to try (in order of preference)
        column_description: Human-readable description of column (for error messages)

    Returns:
        str: The actual column name found in the DataFrame

    Raises:
        InvalidCSVError: If none of the variants match any column

    Example:
        >>> import pandas as pd
        >>> df = pd.read_csv("runs.csv")
        >>> run_id_col = find_csv_column(df, ["run_id", "run id", "runid"])
        >>> # Returns "run_id" if it exists, else "run id", else "runid"
        >>> # Raises InvalidCSVError if none exist
    """
    columns = list(df.columns) if hasattr(df, "columns") else list(df.columns)
    columns_lower = {col.lower().strip(): col for col in columns}

    # Try exact matches first (case-sensitive)
    for variant in name_variants:
        if variant in columns:
            return variant

    # Try case-insensitive matches
    for variant in name_variants:
        variant_lower = variant.lower().strip()
        if variant_lower in columns_lower:
            return columns_lower[variant_lower]

    # No match found - raise error with helpful message
    msg = (
        f"No '{column_description}' column found in CSV. "
        f"Tried column names: {name_variants}. "
        f"Available columns: {columns}"  # noqa: E501
    )
    logger.error(msg)
    raise InvalidCSVError(msg)


def find_required_columns(
    df: DataFrameType,
    column_requirements: Dict[str, List[str]],
) -> Dict[str, str]:
    """Find multiple CSV columns using flexible name matching.

    This consolidates the repetitive column-finding pattern in cli/preprocess.py
    (P1-8 consolidation #2) where 5 separate column searches were performed
    with identical logic.

    Args:
        df: pandas or polars DataFrame to search
        column_requirements: Dict mapping logical names to variant lists:
            {
                "run_id": ["run_id", "run id", "runid"],
                "raw_data": ["path_raw_data", "raw_data_path", "data_dir"],
                ...
            }

    Returns:
        Dict[str, str]: Mapping of logical names to actual column names:
            {
                "run_id": "run_id",
                "raw_data": "path_raw_data",
                ...
            }

    Raises:
        InvalidCSVError: If any required column cannot be found

    Example:
        >>> import pandas as pd
        >>> df = pd.read_csv("runs.csv")
        >>> columns = find_required_columns(df, {
        ...     "run_id": ["run_id", "run id", "runid"],
        ...     "raw_data": ["path_raw_data", "raw_data_path", "data_dir"],
        ...     "pattern": ["search_pattern", "pattern", "file_pattern"],
        ... })
        >>> # Returns {"run_id": "run_id", "raw_data": "path_raw_data", ...}
    """
    found_columns = {}

    for logical_name, variants in column_requirements.items():
        try:
            actual_col = find_csv_column(df, variants, logical_name)
            found_columns[logical_name] = actual_col
        except InvalidCSVError as e:
            # Re-raise with more context about which column we
            # were looking for
            msg = f"Failed to find '{logical_name}' column: {e}"
            logger.error(msg)
            raise InvalidCSVError(msg) from e

    return found_columns


def get_column_safe(
    df: DataFrameType,
    column_name: str,
    operation: str = "access",
) -> Any:
    """Safely access a DataFrame column with clear error handling.

    Provides explicit validation before column access to prevent silent
    KeyErrors. Used by transformer.py and aggregator.py (P1-8 consolidation #3).

    Args:
        df: pandas or polars DataFrame
        column_name: Name of column to access
        operation: Description of operation (for error messages)

    Returns:
        The DataFrame column

    Raises:
        InvalidCSVError: If column doesn't exist

    Example:
        >>> import pandas as pd
        >>> df = pd.read_csv("data.csv")
        >>> col = get_column_safe(df, "datetime", "resampling")
        >>> # Returns df["datetime"] if it exists
        >>> # Raises InvalidCSVError if it doesn't
    """
    try:
        return df[column_name]
    except KeyError as e:
        msg = (
            f"Column '{column_name}' not found during {operation}. "
            f"Available columns: {list(df.columns)}"  # noqa: E501
        )
        logger.error(msg)
        raise InvalidCSVError(msg) from e
