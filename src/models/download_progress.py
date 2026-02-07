"""
Download progress model.

Represents download progress information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DownloadProgress:
    """Data class representing download progress information."""
    status: str
    percentage: float
    downloaded_bytes: int
    total_bytes: int
    speed: Optional[str] = None
    eta: Optional[str] = None
