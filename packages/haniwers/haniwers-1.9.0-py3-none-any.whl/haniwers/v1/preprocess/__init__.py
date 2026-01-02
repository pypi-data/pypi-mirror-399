"""Preprocessing module for haniwers.

Handles:
- Conversion from RawEvent to ProcessedEvent
- CSV loading and cleaning
"""

from haniwers.v1.preprocess.converter import convert_files

__all__ = ["convert_files"]
