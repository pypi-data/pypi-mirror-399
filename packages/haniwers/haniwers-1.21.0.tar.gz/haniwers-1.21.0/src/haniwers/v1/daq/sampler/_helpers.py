"""Helper functions for Sampler data processing and progress display.

This module provides static utility functions used by the Sampler class:
- sanitize(): Type conversion for CSV data
- tqdm_wrapper(): Conditional progress bar display (using rich.progress)
- mock_sample(): Test data generation

These functions are independent utilities that can be used standalone or
integrated into other modules.
"""

from typing import Optional

from rich.progress import track


def sanitize(event: list) -> list:
    """Convert raw CSV row to typed values (empty→None, text→float/int).

    What this does:
        Takes a list of strings (from CSV) and converts to proper Python types:
        - Empty strings become None
        - Numbers become int (if whole) or float (if decimal)
        - Non-numbers stay as strings

    Args:
        event (list): List of string values from CSV row

    Returns:
        list: Same values but with proper Python types

    How it works:
        For each value in the list:
        1. If empty string ("") → convert to None
        2. Try to convert to float
        3. If successful and is whole number (e.g., 100.0) → convert to int
        4. If successful and has decimal → keep as float
        5. If conversion fails → keep as string

    When to use:
        - Processing CSV data to clean up string values
        - Converting detector measurements from strings to numbers
        - Part of data preprocessing pipeline
        - Rarely called directly

    Example conversions:

    ```python
    # Strings to integers
    sanitize(["100", "200", "300"])
    # Returns: [100, 200, 300]

    # Empty strings to None
    sanitize(["100", "", "300"])
    # Returns: [100, None, 300]

    # Decimals stay as float
    sanitize(["100.5", "200.0"])
    # Returns: [100.5, 200]  # Note: 200.0 becomes int(200)

    # Invalid strings stay as strings
    sanitize(["100", "abc", "300"])
    # Returns: [100, "abc", 300]
    ```

    Data type mapping:
        "100" → 100 (int)
        "100.0" → 100 (int, because no fractional part)
        "100.5" → 100.5 (float)
        "" → None
        "abc" → "abc" (string, unchanged)
        "1e5" → 100000.0 (scientific notation)

    Performance:
        - Reasonably efficient for typical CSV rows (7-10 values)
        - Suitable for processing large CSV files
        - Worth the type safety gained
    """
    sanitized: list = []
    for val in event:
        if val == "":
            sanitized.append(None)
            continue

        # Try to convert to float
        try:
            num = float(val)
        except (ValueError, TypeError):
            # Leave as string if conversion fails
            sanitized.append(val)
            continue

        # Append as int if it's an integer, else float
        sanitized.append(int(num) if num.is_integer() else num)

    return sanitized


def tqdm_wrapper(iterable, desc: Optional[str] = None, show: bool = True):
    """Optionally wrap an iterable with a progress bar (rich.progress).

    What this does:
        If show=True: Returns an iterable that displays a progress bar.
        If show=False: Returns the iterable unchanged (no progress bar).
        Useful for conditional progress display in batch processing.

    Args:
        iterable: Any iterable (list, range, generator, etc.)
            Example: range(1000), [1, 2, 3, 4, 5], file_list, etc.

        desc (str, optional): Label for progress bar
            Example: "Events", "Files", "Duration"
            Only used if show=True

        show (bool, optional): Whether to show progress bar
            Default: True (show progress)
            Set to False for scripts/batch jobs

    Returns:
        Generator (if show=True) or original iterable (if show=False)

    How it works:
        - If show=True: Wraps with rich.progress.track() for progress bar display
        - If show=False: Returns iterable unchanged
        - Calling code iterates the same way either way

    When to use:
        - Conditional progress display (interactive vs batch)
        - Usually called internally by acquire_by_count(), acquire_by_time()
        - Rarely called directly

    Progress bar example (show=True):
        ```
        Events ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45% 450/1000 [00:05<00:06]
        ```

    Use cases:

    ```python
    # Interactive script: Show progress
    bar = tqdm_wrapper(
        range(1000),
        desc="Processing",
        show=True  # User sees progress bar
    )

    # Batch/automated script: Don't show progress
    bar = tqdm_wrapper(
        range(1000),
        desc="Processing",
        show=False  # No output to terminal
    )

    # Dynamic based on condition:
    verbose = True  # Could come from command-line flag
    bar = tqdm_wrapper(
        range(1000),
        desc="Processing",
        show=verbose
    )
    ```

    Performance:
        - show=False: No overhead (returns iterable unchanged)
        - show=True: Minimal overhead (~1% slowdown for fast operations)
        - Progress bar updates once per iteration

    Why use this pattern:
        - Cleaner than if/else statements in calling code
        - Consistent interface regardless of display preference
        - Easy to add progress bars to functions without changing loop logic
        - Industry-standard pattern for CLI tools
    """
    return track(iterable, description=desc) if show else iterable


def mock_sample(*args, **kwargs):
    """Generate a mock RawEvent for testing or simulation.

    What this does:
        Returns hardcoded mock data ["mock_event"] for testing purposes.
        Useful for unit tests that don't have a real detector or mocker.

    Returns:
        list: Always returns ["mock_event"] (hardcoded test data)

    When to use:
        - Unit testing code that uses Sampler
        - Verifying Sampler logic without detector
        - Debugging file I/O without hardware
        - Demonstration purposes

    When NOT to use:
        - For realistic mock data: Use RandomMocker instead
        - For testing with real detector: Use Device class
        - For production code: Don't use mock_sample at all

    Note:
        This method accepts *args and **kwargs but ignores them (for flexibility)

    Example:

    ```python
    # Get mock data (for testing)
    mock_event = mock_sample()
    # Returns: ["mock_event"]

    # Can be called with any arguments (ignored):
    result = mock_sample("arg1", "arg2", kwarg1="value")
    # Still returns: ["mock_event"]
    ```

    Why this exists:
        Placeholder for potential future enhancements to mock data generation.
        Current implementation is intentionally simple for clarity.
    """
    return ["mock_event"]
