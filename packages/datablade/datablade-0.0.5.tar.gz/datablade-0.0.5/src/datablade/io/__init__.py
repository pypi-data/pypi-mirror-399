"""
Input/output operations for fetching and processing external data.

This module provides functions for:
- JSON data retrieval from URLs
- ZIP file downloading and extraction
"""

from .json import get as get_json
from .zip import get as get_zip

__all__ = [
    "get_json",
    "get_zip",
]
