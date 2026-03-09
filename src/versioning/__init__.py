"""versioning: YAML-based config management for versioned data pipelines."""

__version__ = "0.2.0"

from versioning.config import Config
from versioning.autoread import autoread, get_file_reading_functions
from versioning.autowrite import autowrite, get_file_writing_functions
from versioning.utilities import pull_from_config

__all__ = [
    "Config",
    "autoread",
    "autowrite",
    "pull_from_config",
    "get_file_reading_functions",
    "get_file_writing_functions",
]
