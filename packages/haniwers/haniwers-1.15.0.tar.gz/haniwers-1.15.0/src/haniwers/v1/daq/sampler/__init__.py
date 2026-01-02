"""Modular Sampler package for data acquisition.

This module provides a refactored version of the Sampler class, split into
logically organized submodules while maintaining full backward compatibility
with the original monolithic implementation.

**Organization**:
    The original sampler.py (1,591 lines) has been reorganized into a package
    structure for better maintainability:

    - `_base.py`: Core Sampler class with complete functionality
    - Additional modules can be added for further decomposition (Reader, Writer, etc.)

**Backward Compatibility**:
    All imports continue to work as before:

    ```python
    # Old style (still works):
    from haniwers.v1.daq.sampler import Sampler

    # New style (also works):
    from haniwers.v1.daq.sampler import Sampler
    ```

**Usage**:
    No changes needed to existing code. The Sampler API remains identical.

    ```python
    from pathlib import Path
    from haniwers.v1.daq.sampler import Sampler
    from haniwers.v1.daq.device import Device
    from haniwers.v1.config.model import DaqConfig

    device = Device(config.device)
    device.connect()

    sampler = Sampler(
        device=device,
        config=config.daq,
        output_dir=Path("./data")
    )

    sampler.acquire_by_count(Path("./data/run.csv"), 1000)
    device.disconnect()
    ```

**Future Decomposition Plan**:
    Future versions may further split functionality into:
    - `_reader.py`: Event reading and data processing
    - `_writer.py`: CSV writing and file management
    - `_iterators.py`: Count-based and time-based iterators
    - `_helpers.py`: Static utility methods (sanitize, progress display with rich.progress)

    Each decomposition step will maintain backward compatibility through
    re-exports in this `__init__.py` file.
"""

from haniwers.v1.daq.sampler._base import Sampler, run_session

__all__ = ["Sampler", "run_session"]
