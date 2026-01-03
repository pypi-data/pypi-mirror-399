import pytest

from pedros.decorators.decorator_factory import CallContext, make_around_decorator


def test_make_around_decorator_sync():
    """Test make_around_decorator with synchronous functions."""

    def before_hook(ctx):
        ctx.extra["before_called"] = True

    def after_hook(ctx):
        ctx.extra["after_called"] = True

    @make_around_decorator(before=before_hook, after=after_hook)
    def test_func(x: int, y: int) -> int:
        return x + y

    result = test_func(2, 3)
    assert result == 5


def test_make_around_decorator_with_context():
    """Test that hooks receive proper CallContext."""

    def before_hook(ctx):
        assert isinstance(ctx, CallContext)
        assert ctx.wrapped.__name__ == "test_func"
        ctx.extra["before_called"] = True

    def after_hook(ctx):
        assert isinstance(ctx, CallContext)
        assert ctx.result == 42
        ctx.extra["after_called"] = True

    @make_around_decorator(before=before_hook, after=after_hook)
    def test_func() -> int:
        return 42

    result = test_func()
    assert result == 42


@pytest.mark.asyncio
async def test_make_around_decorator_async():
    """Test make_around_decorator with asynchronous functions."""

    def before_hook(ctx):
        ctx.extra["before_called"] = True

    def after_hook(ctx):
        ctx.extra["after_called"] = True

    @make_around_decorator(before=before_hook, after=after_hook)
    async def test_func(x: int, y: int) -> int:
        return x + y

    result = await test_func(2, 3)
    assert result == 5


@pytest.mark.asyncio
async def test_make_around_decorator_async_with_context():
    """Test that async hooks receive proper CallContext."""

    def before_hook(ctx):
        assert isinstance(ctx, CallContext)
        assert ctx.wrapped.__name__ == "test_func"
        ctx.extra["before_called"] = True

    def after_hook(ctx):
        assert isinstance(ctx, CallContext)
        # For async functions, result is a coroutine initially
        ctx.extra["after_called"] = True

    @make_around_decorator(before=before_hook, after=after_hook)
    async def test_func() -> int:
        return 42

    result = await test_func()
    assert result == 42


def test_make_around_decorator_error_handling():
    """Test that errors are properly captured in CallContext."""

    def before_hook(ctx):
        ctx.extra["before_called"] = True

    def after_hook(ctx):
        assert ctx.error is not None
        assert isinstance(ctx.error, ValueError)
        ctx.extra["after_called"] = True

    @make_around_decorator(before=before_hook, after=after_hook)
    def test_func() -> int:
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        test_func()


@pytest.mark.asyncio
async def test_make_around_decorator_async_error_handling():
    """Test that async errors are properly captured in CallContext."""

    def before_hook(ctx):
        ctx.extra["before_called"] = True

    def after_hook(ctx):
        assert ctx.error is not None
        assert isinstance(ctx.error, ValueError)
        ctx.extra["after_called"] = True

    @make_around_decorator(before=before_hook, after=after_hook)
    async def test_func() -> int:
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await test_func()


def test_make_around_decorator_preserves_metadata():
    """Test that decorator preserves function metadata."""

    @make_around_decorator()
    def test_func(x: int) -> int:
        """Test function docstring."""
        return x * 2

    # Check that function name and docstring are preserved
    assert test_func.__name__ == "test_func"
    assert test_func.__doc__ == "Test function docstring."


def test_call_context_attributes():
    """Test CallContext attributes and methods."""

    def before_hook(ctx):
        assert ctx.instance is None  # No instance for regular function
        assert ctx.args == (10,)
        assert ctx.kwargs == {}
        assert ctx.result is None
        assert ctx.error is None
        assert ctx.extra == {}

        # Set some extra data
        ctx.extra["test_key"] = "test_value"

    def after_hook(ctx):
        assert ctx.result == 20
        assert ctx.error is None
        assert ctx.extra["test_key"] == "test_value"

    @make_around_decorator(before=before_hook, after=after_hook)
    def test_func(x: int) -> int:
        return x * 2

    result = test_func(10)
    assert result == 20


def test_make_around_decorator_no_hooks():
    """Test decorator with no hooks (identity behavior)."""

    @make_around_decorator()
    def test_func(x: int) -> int:
        return x + 1

    result = test_func(5)
    assert result == 6


@pytest.mark.asyncio
async def test_make_around_decorator_async_no_hooks():
    """Test async decorator with no hooks (identity behavior)."""

    @make_around_decorator()
    async def test_func(x: int) -> int:
        return x + 1

    result = await test_func(5)
    assert result == 6
