# Pedros

[![PyPI](https://img.shields.io/pypi/v/pedros)](https://pypi.org/project/pedros/)  

A small package of reusable Python utilities for Python projects.

## Features

- **Dependency Management**: Smart detection of optional dependencies
- **Logging**: Configure logging with optional Rich support
- **Progress Bars**: Multiple backend support (rich, tqdm, auto)
- **Timing**: Measure and log function execution time
- **Type Safe**: Comprehensive type hints throughout

## Installation

```bash
pip install pedros
```

## Quickstart

```python
from pedros import has_dep, setup_logging, get_logger, progbar, timed

# Configure logging
setup_logging()
logger = get_logger()

# Check dependencies
if has_dep("rich"):
    logger.info("Rich is available!")

# Use progress bar
for item in progbar(range(10)):
    # Process item
    pass


# Time function execution
@timed
def process_data():
    return "result"

result = process_data()  # Automatically logs execution time
```

### Advanced Progress Bar Usage

```python
from pedros import progbar

# Different backend options
for item in progbar(range(50), backend="rich", description="Rich progress"):
    pass

for item in progbar(range(50), backend="tqdm", desc="TQDM progress"):
    pass

# Disable progress bar
for item in progbar(range(50), backend="none"):
    pass
```

### Logging Configuration

```python
import logging
from pedros import setup_logging, get_logger

# Different logging levels
setup_logging(logging.WARNING)  # Only warnings and errors
logger = get_logger("production")

setup_logging(logging.DEBUG)   # All messages including debug
debug_logger = get_logger("development")

# Logger hierarchy
parent_logger = get_logger("app")
child_logger = get_logger("app.module")
```

## Installation

### Basic Installation

```bash
pip install pedros
```

### With Optional Dependencies

For enhanced functionality, install with optional dependencies:

```bash
pip install pedros[rich]    # For rich logging and progress bars
pip install pedros[tqdm]    # For tqdm progress bars
pip install pedros[all]     # All optional dependencies
```

## License

This project is licensed under the MIT [License](LICENSE).

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.

## Support

For questions or support, please open a GitHub issue.
