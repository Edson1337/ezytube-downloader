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
from ..models import DownloadProgress, DownloadResult, VideoFormat


def strip_ansi_codes(text: Optional[str]) -> Optional[str]:
    """Remove ANSI escape codes from a string."""
    if text is None:
        return None
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


ProgressCallback = Callable[[DownloadProgress], None]
VideoCompleteCallback = Callable[[str, str, str], None]  # title, url, file_path


class YouTubeDownloader:
    """
    Service class for downloading YouTube videos.
    
    Handles all interaction with yt-dlp library and provides a clean interface
    for downloading videos with progress tracking.
    """
    
    def __init__(self, output_dir: str, progress_callback: Optional[ProgressCallback] = None,
                 video_complete_callback: Optional[VideoCompleteCallback] = None):
        """
        Initialize the downloader with output directory and optional callbacks.
        
        Args:
            output_dir: Directory where downloaded videos will be saved.
            progress_callback: Optional callback function for progress updates.
            video_complete_callback: Optional callback for when each video completes (for playlists).
        """
        self._output_dir = output_dir
        self._progress_callback = progress_callback
        self._video_complete_callback = video_complete_callback
        self._current_title: Optional[str] = None
        self._current_url: Optional[str] = None
        self._noplaylist = True  # Default: download single video only
        self._cancelled = False
        self._temp_files: list[str] = []  # Track temp files for cleanup
    
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
    
    def cancel(self) -> None:
        """Cancel the current download and cleanup temp files."""
        self._cancelled = True
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self) -> None:
        """Remove all temporary files from the download."""
        import glob
        
        # Clean tracked temp files
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        
        # Clean ALL temp files in output dir (for playlists, current_title may not match)
        temp_patterns = [
            os.path.join(self._output_dir, "*.part"),
            os.path.join(self._output_dir, "*.ytdl"),
            os.path.join(self._output_dir, "*.temp"),
            os.path.join(self._output_dir, "*.f*.mp4"),
            os.path.join(self._output_dir, "*.f*.webm"),
            os.path.join(self._output_dir, "*.f*.m4a"),
        ]
        for pattern in temp_patterns:
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                except Exception:
                    pass
        
        self._temp_files.clear()
    
    def reset(self) -> None:
        """Reset the downloader state for a new download."""
        self._cancelled = False
        self._temp_files.clear()
        self._current_title = None
    
    def get_available_formats(self, url: str) -> list[VideoFormat]:
        """
        Get available video/audio formats for a URL.
        
        Args:
            url: The YouTube video URL.
            
        Returns:
            List of VideoFormat objects with available resolutions.
        """
        formats = []
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Add "Best available" option first
                formats.append(VideoFormat(
                    format_id='best',
                    resolution='Melhor disponivel',
                    ext='mp4',
                    description='Melhor qualidade de video + audio'
                ))
                
                # Collect unique resolutions
                seen_resolutions = set()
                available_formats = info.get('formats', [])
                
                for fmt in available_formats:
                    height = fmt.get('height')
                    if not height or height in seen_resolutions:
                        continue
                    
                    # Only include common resolutions
                    if height not in [2160, 1440, 1080, 720, 480, 360]:
                        continue
                    
                    seen_resolutions.add(height)
                    resolution = f"{height}p"
                    
                    formats.append(VideoFormat(
                        format_id=f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
                        resolution=resolution,
                        ext='mp4',
                        filesize=fmt.get('filesize'),
                        description=f'Video {resolution}'
                    ))
                
                # Sort by resolution (descending)
                formats[1:] = sorted(formats[1:], key=lambda f: int(f.resolution.replace('p', '')), reverse=True)
                
                # Add audio-only option at the end
                formats.append(VideoFormat(
                    format_id='bestaudio/best',
                    resolution='Apenas audio',
                    ext='mp3',
                    has_video=False,
                    description='MP3 audio'
                ))
                
        except Exception:
            # Return default options on error
            formats = [
                VideoFormat(format_id='best', resolution='Melhor disponivel', ext='mp4'),
            ]
        
        return formats
    
    def download(self, url: str, format_id: str = 'best', audio_only: bool = False) -> DownloadResult:
        """
        Download a video from the given YouTube URL.
        
        Args:
            url: The YouTube video URL.
            format_id: The format string to download (default: 'best')
            audio_only: If True, download only audio as MP3.
            
        Returns:
            DownloadResult with success status, file path, and any error message.
        """
        # Reset state
        self.reset()
        
        try:
            os.makedirs(self._output_dir, exist_ok=True)
            
            ydl_opts = self._build_options(format_id, audio_only)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First get info to track title
                info_dict = ydl.extract_info(url, download=False)
                self._current_title = info_dict.get('title', 'video')
                
                # Check if cancelled before downloading
                if self._cancelled:
                    self._cleanup_temp_files()
                    return DownloadResult(
                        success=False,
                        error_message="Download cancelado"
                    )
                
                # Now download
                info_dict = ydl.extract_info(url, download=True)
                title = info_dict.get('title', 'video')
                
                # Check if cancelled during download
                if self._cancelled:
                    self._cleanup_temp_files()
                    return DownloadResult(
                        success=False,
                        error_message="Download cancelado"
                    )
                
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
            if self._cancelled:
                self._cleanup_temp_files()
                return DownloadResult(
                    success=False,
                    error_message="Download cancelado"
                )
            return DownloadResult(
                success=False,
                error_message=str(e)
            )
    
    def _build_options(self, format_id: str = 'best', audio_only: bool = False) -> dict:
        """Build yt-dlp options dictionary."""
        
        # Determine format string
        if format_id == 'best':
            format_str = 'bestvideo+bestaudio/best'
        else:
            format_str = format_id
        
        opts = {
            'format': format_str,
            'outtmpl': os.path.join(self._output_dir, '%(title)s.%(ext)s'),
            'noplaylist': self._noplaylist,
            'quiet': False,
            'no_warnings': False,
            'noprogress': True,
            'progress_hooks': [self._on_progress],
        }
        
        if audio_only:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opts['merge_output_format'] = 'mp4'
            opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        
        # Add postprocessor hook for per-video callbacks
        opts['postprocessor_hooks'] = [self._on_postprocess]
        
        return opts
    
    def _on_postprocess(self, data: dict) -> None:
        """Postprocessor hook called when video processing is complete."""
        if data.get('status') == 'finished' and self._video_complete_callback:
            info_dict = data.get('info_dict', {})
            title = info_dict.get('title', 'Unknown')
            url = info_dict.get('webpage_url', self._current_url or '')
            filepath = data.get('filepath') or info_dict.get('filepath', '')
            
            if filepath and os.path.exists(filepath):
                self._video_complete_callback(title, url, filepath)
    
    def _on_progress(self, data: dict) -> None:
        """Internal progress hook that delegates to the callback."""
        # Check for cancellation and raise to interrupt yt-dlp
        if self._cancelled:
            raise yt_dlp.utils.DownloadError("Download cancelado")
        
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
