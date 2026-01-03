from pedros.progbar import progbar


def test_progbar_no_backend():
    """Test progbar with no backend (returns original iterable)."""
    test_data = [1, 2, 3]

    # Test with backend="none" - should return original iterable
    result = progbar(test_data, backend="none")
    assert list(result) == test_data


def test_progbar_invalid_backend():
    """Test progbar with invalid backend (falls back to auto)."""
    test_data = [1, 2, 3]

    # Invalid backend should fall back to auto
    result = progbar(test_data, backend="invalid_backend")
    # Should still work, either with a backend or return original
    assert list(result) == test_data


def test_progbar_empty_iterable():
    """Test progbar with empty iterable."""
    empty_data = []

    result = progbar(empty_data)
    assert list(result) == []


def test_progbar_generator():
    """Test progbar with generator."""

    def test_generator():
        yield 1
        yield 2
        yield 3

    result = progbar(test_generator())
    assert list(result) == [1, 2, 3]


def test_progbar_list():
    """Test progbar with regular list."""
    test_data = [1, 2, 3, 4, 5]

    result = progbar(test_data)
    assert list(result) == test_data


def test_progbar_tuple():
    """Test progbar with tuple."""
    test_data = (1, 2, 3)

    result = progbar(test_data)
    assert list(result) == list(test_data)


def test_progbar_range():
    """Test progbar with range."""
    test_data = range(5)

    result = progbar(test_data)
    assert list(result) == [0, 1, 2, 3, 4]
