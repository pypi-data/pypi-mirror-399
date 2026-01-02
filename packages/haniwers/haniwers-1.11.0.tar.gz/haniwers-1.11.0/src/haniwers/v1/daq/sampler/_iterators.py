"""Iterator implementations for count-based and time-based acquisition loops.

This module provides generator functions that control the acquisition loop timing:
- count_based_iterator(): Yield N times for fixed event count
- time_based_iterator(): Yield for a fixed duration in seconds

These iterators are used internally by acquire_by_count() and acquire_by_time()
to implement the core data acquisition timing logic.
"""

import time
from collections.abc import Generator


def count_based_iterator(counts: int):
    """Create an iterator that yields exactly N times (count-based acquisition loop).

    What this does:
        Returns a simple counter from 0 to counts-1. Used to implement
        fixed-count data collection ("collect 1000 measurements").

    Args:
        counts (int): Exact number of times to yield
            Example: 1000 yields 1000 times (0 through 999)

    Yields:
        int: Counter value (0, 1, 2, ..., counts-1)

    How it works:
        1. Create a range(0, counts) iterator
        2. Each time called, return next value in the range
        3. Stop after yielding counts times

    When to use:
        - Core of count-based data acquisition
        - Called by acquire_by_count()
        - Rarely called directly

    When NOT to use:
        - For time-based collection: use time_based_iterator() instead
        - For manual iteration: use acquire_by_count() instead

    Example (understanding iteration):

    ```python
    # Collect exactly 100 measurements
    iterator = count_based_iterator(100)

    # Process with different iteration patterns
    for index in iterator:
        event = read_event()

        # Index tells you which measurement this is (0-99)
        if index == 0:
            print("First measurement")
        elif index == 99:
            print("Last measurement")
    ```

    Performance:
        - Extremely efficient: Just a simple counter
        - No sleep/timing overhead (unlike time_based_iterator)
        - Perfect for fixed-size experiments
        - Predictable number of measurements

    Equivalent to:

    ```python
    # This:
    iterator = count_based_iterator(10)
    for i in iterator:
        pass

    # Is equivalent to:
    for i in range(10):
        pass
    ```
    """
    return range(counts)


def time_based_iterator(duration: float, sleep_interval: float) -> Generator[None, None, None]:
    """Generator that yields for a fixed duration (time-based acquisition loop).

    What this does:
        Yields control back to the caller (which reads one measurement) until
        the specified duration has elapsed. Used to implement time-limited
        data collection ("collect for 10 seconds").

    Args:
        duration (float): Total time to yield for (in seconds)
            Example: 10.0 yields for 10 seconds total

        sleep_interval (float): Time to sleep between yields (in seconds)
            Example: 0.1 means "check every 0.1 seconds"
            Smaller intervals = more frequent checks but higher CPU usage
            Larger intervals = less frequent checks but lower CPU usage

    Yields:
        None: Each yield means "read one measurement, then continue"

    How it works:
        1. Record start time at first yield
        2. Loop:
           a. Yield None (signal to caller to read one event)
           b. Sleep for sleep_interval seconds
           c. Check if total elapsed_time >= duration
        3. Stop yielding when duration exceeded

    When to use:
        - Core of time-based data acquisition
        - Called by acquire_by_time()
        - Rarely called directly

    When NOT to use:
        - For fixed event counts: use count_based_iterator() instead
        - For manual iteration: Too low-level, use acquire_by_time()

    Beginner tip:
        This is automatically used by acquire_by_time():

    ```python
    # High-level (recommended):
    sampler.acquire_by_time(Path("data.csv"), duration=10.0, sleep_interval=0.1)

    # Low-level (not recommended):
    iterator = time_based_iterator(10.0, 0.1)
    for _ in iterator:
        event = read_event()  # This is just one event
    ```

    Example (understanding sleep_interval):

    ```python
    # Frequent checks (high CPU):
    iterator = time_based_iterator(duration=5.0, sleep_interval=0.01)
    # Yields ~500 times in 5 seconds (every 0.01 seconds)

    # Standard checks:
    iterator = time_based_iterator(duration=5.0, sleep_interval=0.1)
    # Yields ~50 times in 5 seconds (every 0.1 seconds)

    # Slow checks (low CPU):
    iterator = time_based_iterator(duration=5.0, sleep_interval=0.5)
    # Yields ~10 times in 5 seconds (every 0.5 seconds)
    ```

    Performance notes:
        - Smaller sleep_interval = more responsive but higher CPU usage
        - Larger sleep_interval = lower CPU but less responsive
        - Choose based on your detector's measurement rate and CPU constraints
        - Default (0.1s) is standard for physics detector scanning

    Exact timing:
        - Uses time.time() for wall-clock accuracy
        - Timing includes measurement read time, so total may exceed duration slightly
        - Suitable for 1-10 second measurements, not for sub-millisecond precision
    """
    start = time.time()
    while time.time() - start < duration:
        yield
        time.sleep(sleep_interval)
