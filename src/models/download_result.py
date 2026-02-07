"""
Download result model.

Represents the result of a download operation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DownloadResult:
    """Data class representing the result of a download operation."""
    success: bool
    file_path: Optional[str] = None
    title: Optional[str] = None
    error_message: Optional[str] = None
