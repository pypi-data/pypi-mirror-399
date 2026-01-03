"""
File Sanitizer – A tool to securely clean sensitive data from env, YAML, JSON, and CSV files.
"""

from .env_sanitizer import EnvSanitizer
from .yaml_sanitizer import YamlSanitizer
from .json_sanitizer import JsonSanitizer
from .csv_sanitizer import CsvSanitizer
from .utils import detect_file_type, load_rules

__version__ = "0.1.0"
__all__ = [
    "EnvSanitizer",
    "YamlSanitizer",
    "JsonSanitizer",
    "CsvSanitizer",
    "detect_file_type",
    "load_rules",
]