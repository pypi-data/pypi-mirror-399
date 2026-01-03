"""
pedros - A collection of reusable Python utilities.

Public API:
- check_dependency: Check if a dependency is available
- setup_logging: Configure logging with optional Rich support
- get_logger: Get a configured logger instance
- progbar: Progress bar for iterables with multiple backend support
- timed: Decorator to measure execution time
"""

from pedros.check_dependency import check_dependency
from pedros.logger import setup_logging, get_logger
from pedros.progbar import progbar
from pedros.timed import timed

setup_logging()

__all__ = [
    "check_dependency",
    "setup_logging",
    "get_logger",
    "progbar",
    "timed"
]
