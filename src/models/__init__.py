"""
Models package.

Contains all data classes used across the application.
"""

from .download_entry import DownloadEntry
from .download_progress import DownloadProgress
from .download_result import DownloadResult
from .app_settings import AppSettings

__all__ = [
    'DownloadEntry',
    'DownloadProgress',
    'DownloadResult',
    'AppSettings',
]
