"""
pedros - A collection of reusable Python utilities.

Public API:
- has_dep: Check if a dependency is available
- setup_logging: Configure logging with optional Rich support
- get_logger: Get a configured logger instance
- progbar: Progress bar for iterables with multiple backend support
- timed: Decorator to measure execution time
"""

from pedros.decorators.timed import timed
from pedros.has_dep import has_dep
from pedros.logger import setup_logging, get_logger
from pedros.progbar import progbar

setup_logging()

__all__ = [
    "has_dep",
    "setup_logging",
    "get_logger",
    "progbar",
    "timed"
]
