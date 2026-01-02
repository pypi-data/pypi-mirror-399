"""Data preprocessing commands for raw2csv functionality.

Provides commands for converting raw detector CSV files to processed format.
Supports v0 compatibility mode and configurable preprocessing parameters.

Commands:
    raw2csv: Full processing pipeline with statistics
    raw2tmp: Quick conversion for temporary analysis (v0 compatible)
    run2csv: Process raw data from a specific run using metadata from Google Sheets export

Dependencies:
    - haniwers.v1.preprocess: Core preprocessing functions
    - typer: CLI framework
    - loguru: Structured logging
    - pandas: Data frame manipulation
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from haniwers.v1.helpers.exceptions import InvalidCSVError, InvalidIDError
from haniwers.v1.helpers.validator import validate_directory_exists, validate_file_exists
from haniwers.v1.log.logger import logger
from haniwers.v1.preprocess import convert_files
from haniwers.v1.cli.options import LoggerOptions, PreprocessOptions

app = typer.Typer(help="Data preprocessing utilities")


def _validate_input_directory(read_from: str) -> Path:
    """Validate input directory exists and is accessible.

    Args:
        read_from: Directory path to validate

    Returns:
        Path: Validated Path object

    Raises:
        typer.Exit: If directory doesn't exist or is not a directory
    """
    try:
        return validate_directory_exists(read_from)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(str(e))
        raise typer.Exit(code=1)


def _discover_files(input_dir: Path, pattern: str, verbose: bool = False) -> list[Path]:
    """Discover files matching pattern in input directory.

    Args:
        input_dir: Directory to search
        pattern: Glob pattern for matching files
        verbose: Enable detailed logging

    Returns:
        list[Path]: Sorted list of matching file paths

    Raises:
        typer.Exit: If no files matching pattern are found
    """
    file_paths = sorted(input_dir.glob(pattern))

    if not file_paths:
        logger.error(f"No files matching pattern '{pattern}' found in {input_dir}")
        raise typer.Exit(code=1)

    logger.info(f"Found {len(file_paths)} file(s) matching '{pattern}'")
    if verbose:
        for fpath in file_paths:
            logger.debug(f"  - {fpath.name}")

    return file_paths


def _validate_runs_csv(runs_csv_path: str) -> Path:
    """Validate runs.csv file exists and is readable.

    Args:
        runs_csv_path: Path to runs.csv file

    Returns:
        Path: Validated Path object

    Raises:
        typer.Exit: If file doesn't exist or is not readable
    """
    try:
        return validate_file_exists(runs_csv_path)
    except (FileNotFoundError, IsADirectoryError) as e:
        logger.error(str(e))
        raise typer.Exit(code=1)


def _get_run_info(runs_csv_path: Path, run_id: str, workspace: str) -> dict:
    """Get run metadata from runs.csv using run_id.

    Extracts raw data directory, search pattern, and output paths from runs.csv.
    Handles Google Sheets exports with type hint rows.

    Expected CSV columns:
    - run_id: Run ID
    - path_raw_data: Directory containing raw data files
    - search_pattern: Glob pattern for raw data files
    - path_preprocessed_data: Output path for preprocessed data
    - path_resampled_data: Output path for resampled data

    Args:
        runs_csv_path: Path to runs.csv exported from Google Sheets
        run_id: Run ID to lookup
        workspace: Base workspace directory to construct full paths

    Returns:
        dict: Run metadata with keys:
            - data_dir: Full path to raw data directory
            - pattern: Search pattern for raw data files
            - preprocessed_path: Relative path for preprocessed output
            - resampled_path: Relative path for resampled output

    Raises:
        InvalidCSVError: If CSV columns are invalid or file cannot be read
        InvalidIDError: If run_id not found in runs.csv
        FileNotFoundError: If data directory doesn't exist
        NotADirectoryError: If data path exists but is not a directory
    """
    try:
        # Google Sheets export: row 1=types, row 2=headers, row 3+=data
        # Use skiprows=[0,1] to skip type hints and first header row, making row 3 the header
        df = pd.read_csv(runs_csv_path, skiprows=[0, 1])
        if df.empty:
            # Fallback: try standard read
            df = pd.read_csv(runs_csv_path)
    except Exception as e:
        raise InvalidCSVError(f"Failed to read runs.csv: {e}")

    # Find run_id column
    run_id_col = None
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in ["run_id", "run id", "runid"]:
            run_id_col = col
            break

    if run_id_col is None:
        raise InvalidCSVError(
            f"No 'run_id' column found in runs.csv. Available columns: {list(df.columns)}"
        )

    # Find raw data directory column
    raw_data_col = None
    for name in ["path_raw_data", "raw_data_path", "data_dir"]:
        if name in df.columns:
            raw_data_col = name
            break

    if raw_data_col is None:
        raise InvalidCSVError(
            f"No 'path_raw_data' column found in runs.csv. Available columns: {list(df.columns)}"
        )

    # Find search pattern column
    pattern_col = None
    for name in ["search_pattern", "pattern", "file_pattern"]:
        if name in df.columns:
            pattern_col = name
            break

    if pattern_col is None:
        raise InvalidCSVError(
            f"No 'search_pattern' column found in runs.csv. Available columns: {list(df.columns)}"
        )

    # Find preprocessed data output path column
    preprocessed_col = None
    for name in ["path_preprocessed_data", "preprocessed_path", "processed_output"]:
        if name in df.columns:
            preprocessed_col = name
            break

    # Find resampled data output path column
    resampled_col = None
    for name in ["path_resampled_data", "resampled_path", "resampled_output"]:
        if name in df.columns:
            resampled_col = name
            break

    # Find matching run
    run_row = df[df[run_id_col].astype(str).str.strip() == str(run_id).strip()]

    if run_row.empty:
        available_ids = sorted(df[run_id_col].astype(str).str.strip().unique())
        raise InvalidIDError(f"Run ID '{run_id}' not found in runs.csv. Available: {available_ids}")

    # Extract values from row
    raw_data_rel = run_row[raw_data_col].iloc[0]
    pattern = run_row[pattern_col].iloc[0]
    preprocessed_path = run_row[preprocessed_col].iloc[0] if preprocessed_col else None
    resampled_path = run_row[resampled_col].iloc[0] if resampled_col else None

    # Handle NaN values
    if pd.isna(pattern):
        pattern = "*data*.csv"  # Default fallback
    else:
        pattern = str(pattern).strip()

    # Construct full data directory path
    full_data_dir = Path(workspace) / str(raw_data_rel).strip()

    if not full_data_dir.exists():
        logger.error(f"Data directory does not exist: {full_data_dir}")
        logger.info(f"(Workspace: {workspace}, Relative: {raw_data_rel})")
        raise typer.Exit(code=1)

    if not full_data_dir.is_dir():
        logger.error(f"Not a directory: {full_data_dir}")
        raise typer.Exit(code=1)

    logger.info(f"Found run '{run_id}' in runs.csv")
    logger.debug(f"Data directory: {full_data_dir}")
    logger.debug(f"Search pattern: {pattern}")

    return {
        "data_dir": full_data_dir,
        "pattern": pattern,
        "preprocessed_path": preprocessed_path if not pd.isna(preprocessed_path) else None,
        "resampled_path": resampled_path if not pd.isna(resampled_path) else None,
        "preprocessed_filename": Path(preprocessed_path).name
        if preprocessed_path and not pd.isna(preprocessed_path)
        else None,
        "resampled_filename": Path(resampled_path).name
        if resampled_path and not pd.isna(resampled_path)
        else None,
    }


@app.command(name="raw2csv")
def raw2csv(
    read_from: str = typer.Argument(..., help="Directory containing raw CSV files from detector"),
    save: bool = typer.Option(False, "--save", help="Save processed data to files"),
    interval: int = PreprocessOptions.interval,
    offset: int = PreprocessOptions.offset,
    tz: str = typer.Option(
        "UTC+09:00",
        "--tz",
        help="Timezone string for timestamp parsing (e.g., UTC+09:00, Asia/Tokyo)",
        rich_help_panel="Processing Options",
    ),
    pattern: str = typer.Option(
        "*data*.csv",
        "--pattern",
        help="Glob pattern for matching input files",
        rich_help_panel="Processing Options",
    ),
    verbose: bool = LoggerOptions.verbose,
) -> None:
    """Convert raw detector data to processed CSV format.

    Performs full preprocessing pipeline:
    1. Load raw CSV files from detector
    2. Parse timestamps and apply timezone/offset
    3. Compute hit classifications (per-layer and composite)
    4. Resample data into time windows
    5. Calculate statistics (mean, std, event rates)

    Output files (when --save is used):
    - processed.csv.gz: Full processed data with all columns
    - resampled.csv: Resampled data with statistical aggregates

    Example:
        $ haniwers-v1 preprocess raw2csv sandbox/test_data/20240611_run93 --save
        $ haniwers-v1 preprocess raw2csv data/ --interval 300 --tz Asia/Tokyo
        $ haniwers-v1 preprocess raw2csv data/ --pattern "run*.csv" --verbose

    Args:
        read_from: Directory path containing raw CSV files
        save: Save output files (processed.csv.gz, resampled.csv)
        interval: Time window size in seconds for resampling
        offset: Timestamp offset in seconds
        tz: Timezone for timestamp interpretation
        pattern: File glob pattern (default: "*.csv")
        verbose: Enable detailed logging
    """
    try:
        # Validate and discover files
        input_dir = _validate_input_directory(read_from)
        file_paths = _discover_files(input_dir, pattern, verbose)

        # Process files
        logger.info(f"Processing: interval={interval}s, offset={offset}s, tz={tz}")

        processed_df, resampled_df = convert_files(
            file_paths,
            tz_string=tz,
            offset_seconds=offset,
            resample_interval=interval,
        )

        logger.info(f"✓ Processed: {len(processed_df)} rows")
        logger.info(f"✓ Resampled: {len(resampled_df)} rows (into {interval}s windows)")

        if verbose:
            logger.debug(f"Processed columns: {list(processed_df.columns)}")
            logger.debug(f"Resampled columns: {list(resampled_df.columns)}")

        # Save if requested
        if save:
            processed_path = Path("processed.csv.gz")
            resampled_path = Path("resampled.csv")

            processed_df.to_csv(processed_path, compression="gzip", index=False)
            resampled_df.to_csv(resampled_path, index=False)

            logger.info(
                f"✓ Saved: {processed_path} ({processed_path.stat().st_size / 1024:.1f} KB)"
            )
            logger.info(
                f"✓ Saved: {resampled_path} ({resampled_path.stat().st_size / 1024:.1f} KB)"
            )
        else:
            logger.info("(Use --save flag to save output files)")

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        if verbose:
            import traceback

            logger.debug(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command(name="raw2tmp")
def raw2tmp(
    read_from: str = typer.Argument(..., help="Directory containing raw CSV files"),
    interval: int = PreprocessOptions.interval,
    pattern: str = typer.Option(
        "*data*.csv",
        "--pattern",
        help="Glob pattern for matching input files",
        rich_help_panel="Processing Options",
    ),
) -> None:
    """Quick conversion for temporary analysis (v0 compatible output).

    Faster alternative to raw2csv for quick data exploration.
    Always saves output with v0-compatible filenames:

    - tmp_raw2tmp.csv.gz: Processed data (compressed)
    - tmp_raw2tmp.csv: Resampled data

    This command uses default timezone (UTC+09:00) and no time offset.
    For advanced options, use 'raw2csv' command.

    Example:
        $ haniwers-v1 preprocess raw2tmp sandbox/test_data/20240611_run93
        $ haniwers-v1 preprocess raw2tmp data/ --interval 300

    Args:
        read_from: Directory path containing raw CSV files
        interval: Time window size in seconds for resampling
        pattern: File glob pattern (default: "*.csv")
    """
    try:
        # Validate and discover files
        input_dir = _validate_input_directory(read_from)
        file_paths = _discover_files(input_dir, pattern, verbose=False)

        # Process with defaults
        logger.info(f"Processing with {interval}s resampling...")

        processed_df, resampled_df = convert_files(
            file_paths,
            tz_string="UTC+09:00",  # Default v0 timezone
            offset_seconds=0,  # No offset
            resample_interval=interval,
        )

        # Save with v0-compatible names
        processed_path = Path("tmp_raw2tmp.csv.gz")
        resampled_path = Path("tmp_raw2tmp.csv")

        processed_df.to_csv(processed_path, compression="gzip", index=False)
        resampled_df.to_csv(resampled_path, index=False)

        logger.info(f"✓ Saved: {processed_path} ({processed_path.stat().st_size / 1024:.1f} KB)")
        logger.info(f"✓ Saved: {resampled_path} ({resampled_path.stat().st_size / 1024:.1f} KB)")

    except Exception as e:
        logger.error(f"Quick conversion failed: {e}")
        raise typer.Exit(code=1)


@app.command(name="run2csv")
def run2csv(
    run_id: str = typer.Argument(..., help="Run ID from runs.csv"),
    load_from: str = typer.Option(
        "runs.csv",
        "--load_from",
        help="Path to runs.csv configuration exported from Google Sheets",
        rich_help_panel="Input Options",
    ),
    workspace: str = typer.Option(
        ".",
        "--workspace",
        help="Base workspace directory (root for relative paths in runs.csv)",
        rich_help_panel="Input Options",
    ),
    preprocessed: str = typer.Option(
        ".",
        "--preprocessed",
        help="Directory to save preprocessed (processed.csv.gz) files",
        rich_help_panel="Output Options",
    ),
    resampled: str = typer.Option(
        ".",
        "--resampled",
        help="Directory to save resampled (resampled.csv) files",
        rich_help_panel="Output Options",
    ),
    save: bool = typer.Option(False, "--save", help="Save processed data to files"),
    interval: int = PreprocessOptions.interval,
    offset: int = PreprocessOptions.offset,
    tz: str = typer.Option(
        "UTC+09:00",
        "--tz",
        help="Timezone string for timestamp parsing (e.g., UTC+09:00, Asia/Tokyo)",
        rich_help_panel="Processing Options",
    ),
    verbose: bool = LoggerOptions.verbose,
) -> None:
    """Convert raw detector data for a specific run using metadata from runs.csv.

    This command reads run information from a Google Sheets export (runs.csv),
    looks up the raw data directory and search pattern, then processes the raw
    detector data through the full preprocessing pipeline.

    The runs.csv file should have:
    - run_id: Run ID column
    - path_raw_data: Directory containing raw data files
    - search_pattern: Glob pattern for raw data files (e.g., "*.dat")
    - path_preprocessed_data: Output path for preprocessed data
    - path_resampled_data: Output path for resampled data

    If --save is used with --preprocessed and --resampled options, output files
    are saved to those directories; otherwise paths from runs.csv are used relative
    to the base workspace.

    Example:
        $ haniwers-v1 preprocess run2csv 1 --load_from runs.csv --workspace ./data --save
        $ haniwers-v1 preprocess run2csv 100 --load_from runs.csv --preprocessed ./output/processed --resampled ./output/resampled --save
        $ haniwers-v1 preprocess run2csv 85 --workspace /mnt/data --interval 300 --save --verbose

    Args:
        run_id: Run ID to process (from runs.csv)
        load_from: Path to runs.csv configuration file exported from Google Sheets
        workspace: Base directory for relative paths in runs.csv
        preprocessed: Directory for preprocessed output (overrides runs.csv path)
        resampled: Directory for resampled output (overrides runs.csv path)
        save: Save output files
        interval: Time window size in seconds for resampling
        offset: Timestamp offset in seconds
        tz: Timezone for timestamp interpretation
        verbose: Enable detailed logging
    """
    try:
        # Validate runs.csv and lookup run metadata
        runs_csv_path = _validate_runs_csv(load_from)
        run_info = _get_run_info(runs_csv_path, run_id, workspace)

        # Discover and process files
        logger.info(f"Processing run '{run_id}': interval={interval}s, offset={offset}s, tz={tz}")
        file_paths = _discover_files(run_info["data_dir"], run_info["pattern"], verbose)

        processed_df, resampled_df = convert_files(
            file_paths,
            tz_string=tz,
            offset_seconds=offset,
            resample_interval=interval,
        )

        logger.info(f"✓ Processed: {len(processed_df)} rows")
        logger.info(f"✓ Resampled: {len(resampled_df)} rows (into {interval}s windows)")

        if verbose:
            logger.debug(f"Processed columns: {list(processed_df.columns)}")
            logger.debug(f"Resampled columns: {list(resampled_df.columns)}")

        # Save if requested
        if save:
            # Determine output paths
            if preprocessed != ".":
                processed_dir = Path(preprocessed)
                processed_dir.mkdir(parents=True, exist_ok=True)
                processed_filename = run_info.get(
                    "preprocessed_filename", f"{run_id}_processed.csv.gz"
                )
                processed_path = processed_dir / processed_filename
            else:
                # Use path from runs.csv
                processed_path = Path(workspace) / run_info.get(
                    "preprocessed_path", f"{run_id}_processed.csv.gz"
                )
                processed_path.parent.mkdir(parents=True, exist_ok=True)

            if resampled != ".":
                resampled_dir = Path(resampled)
                resampled_dir.mkdir(parents=True, exist_ok=True)
                resampled_filename = run_info.get("resampled_filename", f"{run_id}_resampled.csv")
                resampled_path = resampled_dir / resampled_filename
            else:
                # Use path from runs.csv
                resampled_path = Path(workspace) / run_info.get(
                    "resampled_path", f"{run_id}_resampled.csv"
                )
                resampled_path.parent.mkdir(parents=True, exist_ok=True)

            processed_df.to_csv(processed_path, compression="gzip", index=False)
            resampled_df.to_csv(resampled_path, index=False)

            logger.info(
                f"✓ Saved: {processed_path} ({processed_path.stat().st_size / 1024:.1f} KB)"
            )
            logger.info(
                f"✓ Saved: {resampled_path} ({resampled_path.stat().st_size / 1024:.1f} KB)"
            )
        else:
            logger.info("(Use --save flag to save output files)")

    except InvalidCSVError as e:
        logger.error(f"Invalid runs.csv format: {e}")
        raise typer.Exit(code=1)
    except InvalidIDError as e:
        logger.error(f"Invalid run ID: {e}")
        raise typer.Exit(code=1)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(f"Data directory error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Run processing failed: {e}")
        if verbose:
            import traceback

            logger.debug(traceback.format_exc())
        raise typer.Exit(code=1)
