"""
YouTube video downloader service module.

This module provides the core functionality for downloading videos from YouTube
using yt-dlp library, following the Single Responsibility Principle.
"""

import os
import re
from typing import Callable, Optional

import yt_dlp

from .file_utils import sanitize_filename
from ..models import DownloadProgress, DownloadResult


def strip_ansi_codes(text: Optional[str]) -> Optional[str]:
    """Remove ANSI escape codes from a string."""
    if text is None:
        return None
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


ProgressCallback = Callable[[DownloadProgress], None]


class YouTubeDownloader:
    """
    Service class for downloading YouTube videos.
    
    This class encapsulates all download logic and provides a clean interface
    for the UI layer, following the Dependency Inversion Principle.
    """
    
    def __init__(self, output_dir: str, progress_callback: Optional[ProgressCallback] = None):
        """
        Initialize the downloader with output directory and optional progress callback.
        
        Args:
            output_dir: Directory where downloaded videos will be saved.
            progress_callback: Optional callback function for progress updates.
        """
        self._output_dir = output_dir
        self._progress_callback = progress_callback
        self._current_title: Optional[str] = None
    
    @property
    def output_dir(self) -> str:
        """Get the current output directory."""
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self, value: str) -> None:
        """Set the output directory."""
        self._output_dir = value
    
    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Get video information without downloading.
        
        Args:
            url: The YouTube video URL.
            
        Returns:
            Dictionary with video info (title, etc.) or None if failed.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,  # Get info for single video only
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'video'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                }
        except Exception:
            return None
    
    def check_file_exists(self, title: str) -> Optional[str]:
        """
        Check if a file with the given title already exists.
        
        Args:
            title: The video title.
            
        Returns:
            File path if exists, None otherwise.
        """
        expected_path = os.path.join(self._output_dir, f"{title}.mp4")
        if os.path.exists(expected_path):
            return expected_path
        return None
    
    def download(self, url: str) -> DownloadResult:
        """
        Download a video from the given YouTube URL.
        
        Args:
            url: The YouTube video URL.
            
        Returns:
            DownloadResult with success status, file path, and any error message.
        """
        try:
            os.makedirs(self._output_dir, exist_ok=True)
            
            ydl_opts = self._build_options()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                title = info_dict.get('title', 'video')
                
                if 'requested_downloads' in info_dict and info_dict['requested_downloads']:
                    file_path = info_dict['requested_downloads'][0].get('filepath')
                else:
                    ext = info_dict.get('ext', 'mp4')
                    file_path = os.path.join(self._output_dir, f"{title}.{ext}")
                
                if not file_path or not os.path.exists(file_path):
                    file_path = self._find_most_recent_file()
                
                return DownloadResult(
                    success=True,
                    file_path=file_path,
                    title=title
                )
                
        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=str(e)
            )
    
    def _build_options(self) -> dict:
        """Build yt-dlp options dictionary."""
        return {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self._output_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'noplaylist': True,  # Download only the video, not the playlist
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'quiet': False,
            'no_warnings': False,
            'noprogress': True,
            'progress_hooks': [self._on_progress],
        }
    
    def _on_progress(self, data: dict) -> None:
        """Internal progress hook that delegates to the callback."""
        if self._progress_callback is None:
            return
            
        if data['status'] == 'downloading':
            total_bytes = data.get('total_bytes') or data.get('total_bytes_estimate', 0)
            downloaded_bytes = data.get('downloaded_bytes', 0)
            percentage = (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
            
            progress = DownloadProgress(
                status='downloading',
                percentage=percentage,
                downloaded_bytes=downloaded_bytes,
                total_bytes=total_bytes,
                speed=strip_ansi_codes(data.get('_speed_str')),
                eta=strip_ansi_codes(data.get('_eta_str'))
            )
            self._progress_callback(progress)
            
        elif data['status'] == 'finished':
            progress = DownloadProgress(
                status='finished',
                percentage=100.0,
                downloaded_bytes=data.get('downloaded_bytes', 0),
                total_bytes=data.get('total_bytes', 0)
            )
            self._progress_callback(progress)
    
    def _find_most_recent_file(self) -> Optional[str]:
        """Find the most recently modified mp4 file in the output directory."""
        try:
            mp4_files = []
            for file in os.listdir(self._output_dir):
                if file.endswith('.mp4'):
                    full_path = os.path.join(self._output_dir, file)
                    mp4_files.append((full_path, os.path.getmtime(full_path)))
            
            if mp4_files:
                mp4_files.sort(key=lambda x: x[1], reverse=True)
                return mp4_files[0][0]
        except Exception:
            pass
        
        return None
