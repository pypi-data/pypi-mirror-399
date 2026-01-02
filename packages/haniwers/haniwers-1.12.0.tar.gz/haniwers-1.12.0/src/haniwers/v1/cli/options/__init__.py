"""Common CLI option definitions for haniwers v1 commands.

This module provides reusable Typer Option definitions organized by functionality.
Instead of duplicating option definitions across multiple command files, this
centralized approach ensures consistency and reduces maintenance burden.

**Purpose**: Implement the DRY (Don't Repeat Yourself) principle by maintaining
a single source of truth for all common CLI options used by daq, threshold, and
scan commands.

**Usage Example**:
    Instead of defining options in each command file, import them:

    .. code-block:: python

        from haniwers.v1.cli.options import DeviceOptions, OutputOptions, SamplerOptions

        def my_command(
            port: Optional[str] = DeviceOptions.port,
            workspace: Optional[Path] = OutputOptions.workspace,
            label: Optional[str] = SamplerOptions.label,
        ) -> None:
            \"\"\"My CLI command using common options.\"\"\"
            pass

**Organization**: Options are grouped by functionality in separate modules
(ConfigOptions, DeviceOptions, OutputOptions, etc.). Each class uses Typer's
rich_help_panel to organize help text visually.

**Benefits**:
- Single source of truth: Change an option once, affects all commands
- Consistency: All commands show identical help text for common options
- Maintainability: No more duplicate option definitions
- Developer experience: IDE autocomplete works correctly with class attributes
- Backward compatible: No CLI interface changes, purely internal refactoring
"""

from haniwers.v1.cli.options.config import ConfigOptions
from haniwers.v1.cli.options.device import DeviceOptions
from haniwers.v1.cli.options.logger import LoggerOptions
from haniwers.v1.cli.options.output import OutputOptions
from haniwers.v1.cli.options.preprocess import PreprocessOptions
from haniwers.v1.cli.options.sampler import SamplerOptions
from haniwers.v1.cli.options.scan import ScanOptions
from haniwers.v1.cli.options.testing import TestingOptions
from haniwers.v1.cli.options.threshold import ThresholdOptions

__all__ = [
    "ConfigOptions",
    "DeviceOptions",
    "LoggerOptions",
    "OutputOptions",
    "PreprocessOptions",
    "SamplerOptions",
    "ScanOptions",
    "TestingOptions",
    "ThresholdOptions",
]
