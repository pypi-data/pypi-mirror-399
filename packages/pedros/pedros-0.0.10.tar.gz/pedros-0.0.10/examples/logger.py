import logging
from unittest.mock import patch

from pedros import check_dependency, get_logger, setup_logging


def run_demo(label: str):
    print(f"\n--- DEMO: {label} ---")
    check_dependency.cache_clear()

    setup_logging(level=logging.DEBUG)
    logger = get_logger()

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")


if __name__ == "__main__":

    run_demo("native environment")

    with patch("importlib.util.find_spec", return_value=None):
        run_demo("without Rich")
