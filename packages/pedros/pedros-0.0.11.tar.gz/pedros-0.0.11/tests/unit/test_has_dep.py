from pedros.has_dep import has_dep


def test_has_dep_available():
    """Test has_dep with an available module."""
    # Test with a module that should always be available
    result = has_dep("sys")
    assert result is True


def test_has_dep_unavailable():
    """Test has_dep with an unavailable module."""
    # Test with a module that should never be available
    result = has_dep("nonexistent_module_12345")
    assert result is False


def test_has_dep_case_sensitivity():
    """Test that has_dep is case-sensitive."""
    # This tests that the function respects Python's case-sensitive module names
    # Most standard library modules are lowercase
    result_lower = has_dep("sys")
    result_upper = has_dep("SYS")

    assert result_lower is True
    assert result_upper is False


def test_has_dep_with_dots():
    """Test has_dep with dotted module names."""
    # Test with a submodule
    result = has_dep("os.path")
    assert result is True
