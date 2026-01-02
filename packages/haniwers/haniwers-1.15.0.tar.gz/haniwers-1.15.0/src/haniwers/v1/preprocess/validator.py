"""Error handling and logging setup for raw2csv data processing pipeline.

This module provides error handling and logging utilities following the
error handling strategy from FR-009:
- INFO level: Error summaries with counts
- DEBUG level: Row-level error details

The logger is configured in src/haniwers/v1/log/logger.py and imported here.

Design Pattern (Principle VIII - DRY):
- Centralized logging configuration in log module
- Used by all modules (reader, transformer, aggregator) for consistent error messages
- Two-tier approach prevents log spam while preserving debugging capability
"""

from haniwers.v1.log import logger


def log_error_summary(error_count: int, total_rows: int) -> None:
    """Log error count summary at INFO level.

    This function is called once per processing batch and provides high-level
    visibility into data quality issues without overwhelming logs with details.

    Args:
        error_count: Number of rows with errors/invalid data
        total_rows: Total number of rows processed

    Example:
        >>> log_error_summary(15, 13856)
        # Output: INFO | ...: Skipped 15/13856 invalid rows (0.11%)
    """
    if error_count > 0:
        percentage = (error_count / total_rows * 100) if total_rows > 0 else 0
        logger.info(f"Skipped {error_count}/{total_rows} invalid rows ({percentage:.2f}%)")


def log_error_detail(row_number: int, reason: str) -> None:
    """Log error detail at DEBUG level.

    This function is called for each invalid row during processing. Details are
    logged at DEBUG level to minimize output in normal operation while preserving
    full diagnostic information for troubleshooting.

    Args:
        row_number: Line number or row index with error
        reason: Human-readable explanation of why row was skipped

    Example:
        >>> log_error_detail(42, "Invalid ISO8601 timestamp: '2025-13-45T99:99:99'")
        # Output: DEBUG | ...: Row 42: Invalid ISO8601 timestamp: '2025-13-45T99:99:99'
    """
    logger.debug(f"Row {row_number}: {reason}")
