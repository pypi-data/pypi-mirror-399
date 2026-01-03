"""Integration tests for module interactions and real-world scenarios."""

import logging

from pedros.decorators.decorator_factory import make_around_decorator
from pedros.decorators.timed import timed
from pedros.logger import get_logger, setup_logging
from pedros.progbar import progbar


class TestLoggerProgbarIntegration:
    """Test integration between logger and progress bar."""

    def test_logger_with_progbar(self, caplog):
        """Test that logger works correctly with progress bar operations."""
        # Use caplog to capture logs instead of setup_logging
        logger = get_logger("integration_test")
        logger.setLevel(logging.INFO)
        
        items = [1, 2, 3, 4, 5]
        results = []
        
        logger.info("Starting progress bar operation")
        
        for item in progbar(items, desc="Processing items"):
            logger.debug(f"Processing item: {item}")
            results.append(item * 2)
        
        logger.info("Completed progress bar operation")
        
        assert results == [2, 4, 6, 8, 10]
        # Check that we have at least the info messages (debug messages won't be captured at INFO level)
        info_messages = [record for record in caplog.records if record.levelno == logging.INFO]
        assert len(info_messages) >= 2  # At least the info messages

    def test_logger_progbar_error_handling(self, caplog):
        """Test error handling in logger + progbar integration."""
        setup_logging(logging.WARNING)
        logger = get_logger("error_test")
        
        items = [1, 2, 3, 2, 1]  # Includes potential division by zero
        results = []
        
        for item in progbar(items, desc="Processing with potential errors"):
            try:
                result = 10 / item
                results.append(result)
            except ZeroDivisionError:
                logger.warning(f"Skipping item {item} due to division by zero")
                results.append(float('inf'))
        
        assert len(results) == 5
        assert results[0] == 10.0
        assert results[2] == 10.0 / 3


class TestTimedLoggerIntegration:
    """Test integration between timed decorator and logger."""

    def test_timed_with_logging(self, caplog):
        """Test that timed decorator works with logging."""
        # Don't use setup_logging as it bypasses caplog
        logger = get_logger("timed_test")
        logger.setLevel(logging.INFO)
        
        @timed
        def process_data(data):
            logger.info(f"Processing data: {data}")
            return data.upper()
        
        result = process_data("test data")
        assert result == "TEST DATA"
        
        # Should have logged the function execution
        assert any("Processing data: test data" in record.message for record in caplog.records)

    def test_timed_logger_error_handling(self, caplog):
        """Test error handling in timed + logger integration."""
        # Don't use setup_logging as it bypasses caplog
        logger = get_logger("timed_error_test")
        logger.setLevel(logging.ERROR)
        
        @timed
        def failing_function():
            logger.error("About to fail")
            raise ValueError("Test error")
        
        try:
            failing_function()
        except ValueError:
            pass  # Expected
        
        # Should have logged the error
        assert any("About to fail" in record.message for record in caplog.records)


class TestDecoratorFactoryIntegration:
    """Test integration of decorator factory with other modules."""

    def test_decorator_factory_with_logger(self, caplog):
        """Test decorator factory integration with logger."""
        # Don't use setup_logging as it bypasses caplog
        logger = get_logger("decorator_test")
        logger.setLevel(logging.INFO)
        
        def before_hook(ctx):
            logger.info("Before function execution")
        
        def after_hook(ctx):
            logger.info("After function execution")
        
        logging_decorator = make_around_decorator(before=before_hook, after=after_hook)
        
        @logging_decorator
        def process_item(item):
            return item * 2
        
        result = process_item(5)
        assert result == 10
        
        # Should have logged before and after
        assert any("Before function execution" in record.message for record in caplog.records)
        assert any("After function execution" in record.message for record in caplog.records)

    def test_decorator_factory_with_progbar(self):
        """Test decorator factory integration with progress bar."""
        
        def before_hook(ctx):
            print("Starting iteration")
        
        def after_hook(ctx):
            print("Completed iteration")
        
        iteration_decorator = make_around_decorator(before=before_hook, after=after_hook)
        
        @iteration_decorator
        def process_item(item):
            return item * 2
        
        items = [1, 2, 3]
        results = []
        
        for item in progbar(items, desc="Processing with decorator"):
            results.append(process_item(item))
        
        assert results == [2, 4, 6]


class TestComplexIntegrationScenarios:
    """Test complex real-world integration scenarios."""

    def test_data_processing_pipeline(self, caplog):
        """Test a complete data processing pipeline with all modules."""
        # Don't use setup_logging as it bypasses caplog
        logger = get_logger("pipeline_test")
        logger.setLevel(logging.INFO)
        
        # Define processing functions with decorators
        @timed
        def validate_data(data):
            logger.info(f"Validating: {data}")
            return data.strip() if isinstance(data, str) else data
        
        @timed
        def transform_data(data):
            logger.info(f"Transforming: {data}")
            return data.upper() if isinstance(data, str) else data * 2
        
        # Process multiple items with progress bar
        raw_data = ["  hello  ", "world", "test", 42, "data"]
        processed_data = []
        
        logger.info("Starting data processing pipeline")
        
        for item in progbar(raw_data, desc="Processing data pipeline"):
            validated = validate_data(item)
            transformed = transform_data(validated)
            processed_data.append(transformed)
        
        logger.info("Completed data processing pipeline")
        
        expected = ["HELLO", "WORLD", "TEST", 84, "DATA"]
        assert processed_data == expected
        
        # Should have logged all operations (excluding timed decorator logs)
        info_messages = [record for record in caplog.records if record.levelno == logging.INFO]
        assert len(info_messages) >= 7  # Pipeline start + 5 items + pipeline end

    def test_error_recovery_scenario(self, caplog):
        """Test error recovery in integrated scenario."""
        # Don't use setup_logging as it bypasses caplog
        logger = get_logger("error_recovery_test")
        logger.setLevel(logging.WARNING)
        
        def safe_processor(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Error in {func.__name__}: {e}")
                    return None
            return wrapper
        
        @timed
        @safe_processor
        def risky_operation(data):
            if data == 2:
                raise ValueError("Invalid data")
            return data * 2
        
        items = [1, 2, 3, 4]
        results = []
        
        for item in progbar(items, desc="Risky operations"):
            result = risky_operation(item)
            results.append(result)
        
        expected = [2, None, 6, 8]  # Item 2 fails and returns None
        assert results == expected
        
        # Should have logged the error
        assert any("Error in risky_operation" in record.message for record in caplog.records)


class TestModuleInteractionEdgeCases:
    """Test edge cases in module interactions."""

    def test_empty_operations(self):
        """Test integration with empty operations."""
        setup_logging(logging.INFO)
        logger = get_logger("empty_test")
        
        @timed
        def empty_function():
            return None
        
        # Test with empty progress bar
        results = []
        for item in progbar([], desc="Empty operation"):
            results.append(empty_function())
        
        assert results == []

    def test_nested_decorators_integration(self):
        """Test nested decorators with other modules."""
        # Don't use setup_logging as it bypasses caplog
        logger = get_logger("nested_test")
        logger.setLevel(logging.DEBUG)
        
        def logging_before(ctx):
            logger.debug("Before outer decorator")
        
        def logging_after(ctx):
            logger.debug("After outer decorator")
        
        outer_decorator = make_around_decorator(before=logging_before, after=logging_after)
        
        @outer_decorator
        @timed
        def nested_function(x):
            return x * 3
        
        items = [1, 2, 3]
        results = []
        
        for item in progbar(items, desc="Nested decorators"):
            results.append(nested_function(item))
        
        assert results == [3, 6, 9]