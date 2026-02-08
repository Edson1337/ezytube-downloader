"""
Video format model.

Represents available video/audio formats for download.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoFormat:
    """Represents a video/audio format option."""
    format_id: str
    resolution: str  # e.g., "1080p", "720p", "audio"
    ext: str
    filesize: Optional[int] = None
    has_audio: bool = True
    has_video: bool = True
    description: str = ""  # Human readable description
    
    def size_str(self) -> str:
        """Return human readable file size."""
        if not self.filesize:
            return ""
        
        size = self.filesize
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
