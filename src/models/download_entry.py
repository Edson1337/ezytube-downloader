"""
Download entry model.

Represents a single download history entry.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DownloadEntry:
    """Represents a single download history entry."""
    title: str
    url: str
    file_path: str
    download_date: str
    file_size: Optional[int] = None
