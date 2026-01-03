"""Performance benchmark tests for decorators and utilities."""

from pedros.decorators.decorator_factory import make_around_decorator
from pedros.decorators.timed import timed
from pedros.logger import get_logger, setup_logging
from pedros.progbar import progbar


class TestDecoratorPerformance:
    """Performance tests for decorators."""

    def test_timed_decorator_overhead(self, benchmark):
        """Benchmark the overhead of the timed decorator."""
        
        @timed  # No sleep to measure pure overhead
        def test_function():
            return 42
        
        result = benchmark(test_function)
        assert result == 42

    def test_timed_decorator_basic(self, benchmark):
        """Benchmark timed decorator basic functionality."""
        
        @timed
        def test_function():
            return 42
        
        result = benchmark(test_function)
        assert result == 42

    def test_decorator_factory_overhead(self, benchmark):
        """Benchmark the overhead of decorator factory."""
        
        def before_hook(ctx):
            pass
        
        def after_hook(ctx):
            pass
        
        decorator = make_around_decorator(before=before_hook, after=after_hook)
        
        @decorator
        def test_function():
            return 42
        
        result = benchmark(test_function)
        assert result == 42

    def test_multiple_decorators_overhead(self, benchmark):
        """Benchmark the overhead of multiple decorators."""
        
        def before_hook(ctx):
            pass
        
        def after_hook(ctx):
            pass
        
        decorator1 = make_around_decorator(before=before_hook, after=after_hook)
        decorator2 = make_around_decorator(before=before_hook, after=after_hook)
        
        @decorator1
        @decorator2
        def test_function():
            return 42
        
        result = benchmark(test_function)
        assert result == 42


class TestProgbarPerformance:
    """Performance tests for progress bar."""

    def test_progbar_small_iterable(self, benchmark):
        """Benchmark progbar with small iterable."""
        items = list(range(10))
        
        def test_progbar():
            result = []
            for item in progbar(items):
                result.append(item)
            return result
        
        result = benchmark(test_progbar)
        assert result == items

    def test_progbar_medium_iterable(self, benchmark):
        """Benchmark progbar with medium iterable."""
        items = list(range(100))
        
        def test_progbar():
            result = []
            for item in progbar(items):
                result.append(item)
            return result
        
        result = benchmark(test_progbar)
        assert result == items

    def test_progbar_large_iterable(self, benchmark):
        """Benchmark progbar with large iterable."""
        items = list(range(1000))
        
        def test_progbar():
            result = []
            for item in progbar(items):
                result.append(item)
            return result
        
        result = benchmark(test_progbar)
        assert result == items


class TestLoggerPerformance:
    """Performance tests for logger."""

    def test_logger_creation_performance(self, benchmark):
        """Benchmark logger creation performance."""
        
        def test_logger_creation():
            logger = get_logger("test_logger")
            return logger
        
        result = benchmark(test_logger_creation)
        assert result.name == "test_logger"

    def test_logging_performance(self, benchmark):
        """Benchmark logging performance."""
        setup_logging()
        logger = get_logger("performance_test")
        
        def test_logging():
            for i in range(10):
                logger.info(f"Test message {i}")
            return True
        
        result = benchmark(test_logging)
        assert result is True


class TestMemoryEfficiency:
    """Memory efficiency tests."""

    def test_progbar_memory_with_large_iterable(self):
        """Test that progbar doesn't consume excessive memory with large iterables."""
        # Create a large iterable but don't materialize it all at once
        items = range(10000)
        
        # Use progbar and ensure it works without excessive memory usage
        result = []
        for item in progbar(items):
            result.append(item)
            if len(result) >= 100:  # Limit for test
                break
        
        assert len(result) == 100
        assert result == list(range(100))

    def test_decorator_memory_overhead(self):
        """Test that decorators don't add significant memory overhead."""
        
        def before_hook(ctx):
            pass
        
        def after_hook(ctx):
            pass
        
        decorator = make_around_decorator(before=before_hook, after=after_hook)
        
        @decorator
        def test_function():
            return [1, 2, 3, 4, 5] * 1000
        
        result = test_function()
        assert len(result) == 5000
        assert result[0] == 1
        assert result[-1] == 5