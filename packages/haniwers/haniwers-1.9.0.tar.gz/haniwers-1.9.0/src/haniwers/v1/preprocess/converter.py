# -*- coding: utf-8 -*-
"""High-level API orchestrating the data processing pipeline.

This module provides the main entry point convert_files() that coordinates
the reader, transformer, and aggregator modules to process detector data.

Design (Principle IX - SRP):
- Single responsibility: Orchestrate pipeline stages
- Pure function, no side effects
- Returns DataFrames for downstream processing

References:
- FR-007: Return two datasets (raw processed + resampled events)
- ADR-005: Layered data processing pipeline
- ADR-012: Pure orchestration function
"""

from typing import List, Tuple, Optional
from pathlib import Path
import pandas as pd

from haniwers.v1.preprocess import reader, transformer, aggregator
from haniwers.v1 import schema


def convert_files(
    file_paths: List[Path],
    tz_string: str = "UTC+09:00",
    offset_seconds: int = 0,
    resample_interval: int = 600,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """Convert raw detector CSV files to processed and resampled DataFrames.

    Main entry point for the v1 preprocess module.
    Orchestrates:

    1. Load raw CSV files (reader layer)
    2. Add calculated columns (transformer layer)
    3. Optionally resample to time windows (aggregator layer - Phase 2)

    Phase 1 (User Story 1) returns only processed events.
    Phase 2 (User Story 2) will also return resampled aggregations.

    Args:
        file_paths: List of Path objects to raw CSV files from detector
        tz_string: Timezone for datetime parsing (default: UTC+09:00)
        offset_seconds: Time offset correction in seconds (default: 0)
        resample_interval: Interval in seconds for aggregation (default: 600)

    Returns:
        Tuple of (processed_df, resampled_df):
        - processed_df: All events with calculated columns (datetime -> time, hit_* columns)
        - resampled_df: None in Phase 1, time-windowed aggregations in Phase 2+

    Raises:
        ValueError: If no files provided or files missing required columns

    Example:
        >>> from pathlib import Path
        >>> files = [Path("run93_001.csv"), Path("run93_002.csv")]
        >>> raw_df, resampled_df = convert_files(files)
        >>> print(raw_df.shape, resampled_df)
        (13856, 13) None  # Phase 1: no resampling yet
    """
    # Step 1: Load raw CSV files using Polars (fast I/O)
    raw_polars = reader.load_csv_files(file_paths)

    # Convert to pandas for transformer operations
    raw_df = raw_polars.to_pandas()

    # Step 2: Apply transformations (add timestamp, hit detection, etc.)
    processed_df = transformer.process_raw_data(raw_df, tz_string, offset_seconds)

    # Step 3: Resample to time windows (User Story 2)
    resampled_df = aggregator.resample_by_interval(processed_df, resample_interval)
    resampled_df = aggregator.compute_statistics(resampled_df, processed_df, resample_interval)
    resampled_df = aggregator.compute_event_rates(resampled_df, resample_interval)

    return processed_df, resampled_df
