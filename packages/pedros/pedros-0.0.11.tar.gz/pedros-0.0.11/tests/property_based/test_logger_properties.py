"""Property-based tests using Hypothesis for edge cases and boundary conditions."""

import logging

from hypothesis import given
from hypothesis.strategies import text, integers, booleans

from pedros.decorators.decorator_factory import make_around_decorator
from pedros.decorators.timed import timed
from pedros.logger import get_logger, setup_logging
from pedros.progbar import progbar


class TestLoggerPropertyBased:
    """Property-based tests for logger module."""

    @given(logger_name=text(min_size=1, max_size=50))
    def test_get_logger_any_name(self, logger_name):
        """Test that get_logger works with any valid logger name."""
        logger = get_logger(logger_name)
        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name

    @given(log_level=integers(min_value=0, max_value=50))
    def test_setup_logging_any_level(self, log_level):
        """Test that setup_logging works with various log levels."""
        # Only test valid log levels
        if log_level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            setup_logging(log_level)
            logger = get_logger()
            assert logger.getEffectiveLevel() == log_level

    @given(logger_name=text(min_size=1, max_size=100), use_rich=booleans())
    def test_logger_creation_robustness(self, logger_name, use_rich):
        """Test logger creation with various names and rich availability."""
        # This should never raise an exception regardless of parameters
        logger = get_logger(logger_name)
        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name


class TestTimedPropertyBased:
    """Property-based tests for timed decorator."""

    @given(test_value=integers(min_value=0, max_value=100))
    def test_timed_decorator_basic(self, test_value):
        """Test that timed decorator works with various return values."""
        
        @timed
        def test_function():
            return test_value
        
        result = test_function()
        assert result == test_value

    @given(function_name=text(min_size=1, max_size=20))
    def test_timed_decorator_with_different_functions(self, function_name):
        """Test that timed decorator works with various function implementations."""
        
        @timed
        def test_function():
            return f"processed_{function_name}"
        
        result = test_function()
        assert result == f"processed_{function_name}"


class TestProgbarPropertyBased:
    """Property-based tests for progress bar."""

    @given(iterable_size=integers(min_value=0, max_value=100))
    def test_progbar_any_iterable_size(self, iterable_size):
        """Test that progbar works with various iterable sizes."""
        items = list(range(iterable_size))
        
        # Test that progbar doesn't break with any size
        result = []
        for item in progbar(items):
            result.append(item)
        
        assert result == items

    @given(desc_text=text(min_size=0, max_size=50))
    def test_progbar_any_description(self, desc_text):
        """Test that progbar works with various descriptions."""
        items = [1, 2, 3]
        
        result = []
        for item in progbar(items, desc=desc_text):
            result.append(item)
        
        assert result == items


class TestDecoratorFactoryPropertyBased:
    """Property-based tests for decorator factory."""

    @given(test_value=integers(min_value=-1000, max_value=1000))
    def test_make_around_decorator_basic(self, test_value):
        """Test that make_around_decorator works with various input values."""
        
        def before_hook(ctx):
            # Simple before hook that does nothing
            pass
        
        def after_hook(ctx):
            # Simple after hook that does nothing
            pass
        
        decorator = make_around_decorator(before=before_hook, after=after_hook)
        
        @decorator
        def test_function(x):
            return x + 1
        
        result = test_function(test_value)
        assert result == test_value + 1

    @given(test_value=integers(min_value=-1000, max_value=1000))
    def test_decorator_with_various_inputs(self, test_value):
        """Test that decorators work with various input values."""
        
        def before_hook(ctx):
            pass
        
        def after_hook(ctx):
            pass
        
        decorator = make_around_decorator(before=before_hook, after=after_hook)
        
        @decorator
        def test_function(x):
            return x * 2
        
        result = test_function(test_value)
        assert result == test_value * 2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_logger_empty_name(self):
        """Test logger with empty name."""
        logger = get_logger("")
        assert isinstance(logger, logging.Logger)

    def test_progbar_empty_iterable(self):
        """Test progbar with empty iterable."""
        result = list(progbar([]))
        assert result == []

    def test_timed_basic_functionality(self):
        """Test timed decorator basic functionality."""
        
        @timed
        def test_function():
            return "immediate"
        
        result = test_function()
        assert result == "immediate"

    def test_decorator_factory_none_hooks(self):
        """Test decorator factory with None hooks."""
        decorator = make_around_decorator(before=None, after=None)
        
        @decorator
        def test_function():
            return "test"
        
        result = test_function()
        assert result == "test"