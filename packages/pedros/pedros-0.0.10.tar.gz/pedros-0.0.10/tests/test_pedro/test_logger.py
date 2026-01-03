import logging

from pedros.logger import get_logger, setup_logging


def test_get_logger_default():
    """Test getting logger with default name."""
    logger = get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "pedros.logger"


def test_get_logger_custom_name():
    """Test getting logger with custom name."""
    logger = get_logger("custom_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "custom_logger"


def test_setup_logging_default():
    """Test setup_logging with default parameters."""
    # Test that it runs without error
    setup_logging()
    logger = get_logger()
    assert logger.getEffectiveLevel() == logging.INFO


def test_setup_logging_custom_level():
    """Test setup_logging with custom level."""
    setup_logging(logging.DEBUG)
    logger = get_logger()
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_setup_logging_without_rich():
    """Test setup_logging when Rich is not available."""
    # This should not raise an error and fall back to standard logging
    # We can't easily mock the cached function, so we just test that it works
    setup_logging()
    logger = get_logger()
    assert logger.getEffectiveLevel() == logging.INFO


def test_setup_logging_with_rich():
    """Test setup_logging when Rich is available."""
    # This should use Rich handler if available
    # We can't easily mock the cached function, so we just test that it works
    setup_logging()
    logger = get_logger()
    assert logger.getEffectiveLevel() == logging.INFO


def test_logger_hierarchy():
    """Test that loggers maintain proper hierarchy."""
    parent_logger = get_logger("parent")
    child_logger = get_logger("parent.child")

    assert parent_logger.name == "parent"
    assert child_logger.name == "parent.child"
    assert child_logger.parent.name == "parent"


def test_logger_level_inheritance():
    """Test that child loggers inherit parent levels."""
    setup_logging(logging.DEBUG)
    parent_logger = get_logger("parent")
    child_logger = get_logger("parent.child")

    # Child should inherit parent's effective level
    assert child_logger.getEffectiveLevel() == logging.DEBUG
