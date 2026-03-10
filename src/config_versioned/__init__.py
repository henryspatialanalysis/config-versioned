"""config_versioned: YAML-based config management for versioned data pipelines."""

__version__ = "0.2.0"

from config_versioned.config import Config
from config_versioned.autoread import autoread, get_file_reading_functions
from config_versioned.autowrite import autowrite, get_file_writing_functions
from config_versioned.utilities import pull_from_config

__all__ = [
    "Config",
    "autoread",
    "autowrite",
    "pull_from_config",
    "get_file_reading_functions",
    "get_file_writing_functions",
]
