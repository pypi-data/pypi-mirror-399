from pedros.check_dependency import check_dependency


def test_check_dependency_available():
    """Test check_dependency with an available module."""
    # Test with a module that should always be available
    result = check_dependency("sys")
    assert result is True


def test_check_dependency_unavailable():
    """Test check_dependency with an unavailable module."""
    # Test with a module that should never be available
    result = check_dependency("nonexistent_module_12345")
    assert result is False


def test_check_dependency_case_sensitivity():
    """Test that check_dependency is case-sensitive."""
    # This tests that the function respects Python's case-sensitive module names
    # Most standard library modules are lowercase
    result_lower = check_dependency("sys")
    result_upper = check_dependency("SYS")

    assert result_lower is True
    assert result_upper is False


def test_check_dependency_with_dots():
    """Test check_dependency with dotted module names."""
    # Test with a submodule
    result = check_dependency("os.path")
    assert result is True


def test_check_dependency_caching():
    """Test that check_dependency uses caching."""
    # Clear cache first
    check_dependency.cache_clear()

    # First call - should check the module
    result1 = check_dependency("sys")
    assert result1 is True

    # Second call - should use cache
    result2 = check_dependency("sys")
    assert result2 is True


def test_check_dependency_cache_clear():
    """Test that cache can be cleared."""
    # Clear cache
    check_dependency.cache_clear()

    # First call
    result1 = check_dependency("sys")
    assert result1 is True

    # Clear cache again
    check_dependency.cache_clear()

    # Second call should work the same
    result2 = check_dependency("sys")
    assert result2 is True
