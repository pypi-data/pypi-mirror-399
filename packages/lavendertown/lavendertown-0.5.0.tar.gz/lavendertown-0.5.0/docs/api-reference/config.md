# Configuration

Configuration management for LavenderTown using environment variables and `.env` files.

## Overview

LavenderTown automatically loads configuration from `.env` files when the package is imported. Configuration is searched in the following order:

1. Current directory (`.env`)
2. Parent directories (up to project root)
3. Home directory (`.lavendertown.env`)

## Functions

::: lavendertown.config.load_config

::: lavendertown.config.get_config

::: lavendertown.config.get_config_bool

::: lavendertown.config.get_config_int

## Usage Example

```python
from lavendertown.config import get_config, get_config_bool, get_config_int

# Get string configuration
log_level = get_config("LAVENDERTOWN_LOG_LEVEL", "WARNING")

# Get boolean configuration
debug_mode = get_config_bool("LAVENDERTOWN_DEBUG", False)

# Get integer configuration
max_rows = get_config_int("LAVENDERTOWN_MAX_ROWS", 1000000)
```

## Environment Variables

Common environment variables:

- `LAVENDERTOWN_LOG_LEVEL`: Logging level (e.g., "INFO", "WARNING", "DEBUG")
- `LAVENDERTOWN_DEBUG`: Enable debug mode (boolean)
- `LAVENDERTOWN_OUTPUT_DIR`: Default output directory for exports

Configuration is automatically loaded when you import LavenderTown:

```python
import lavendertown  # Configuration is loaded automatically

# Your code here
```

