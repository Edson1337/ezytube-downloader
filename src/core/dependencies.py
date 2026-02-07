"""
Dependency checker module.

This module checks for and installs required external dependencies
like FFmpeg that are not Python packages.
"""

import os
import platform
import shutil
import subprocess
import urllib.request
import zipfile
import tempfile
from typing import Optional, Callable


def get_app_bin_dir() -> str:
    """Get the bin directory inside the app folder."""
    current_file = os.path.abspath(__file__)
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    bin_dir = os.path.join(app_root, 'bin')
    os.makedirs(bin_dir, exist_ok=True)
    return bin_dir


def find_ffmpeg() -> Optional[str]:
    """Find FFmpeg executable. Returns path if found, None otherwise."""
    # Check in app's bin directory first
    bin_dir = get_app_bin_dir()
    
    if platform.system() == 'Windows':
        local_ffmpeg = os.path.join(bin_dir, 'ffmpeg.exe')
    else:
        local_ffmpeg = os.path.join(bin_dir, 'ffmpeg')
    
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    
    # Check system PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    return None


def is_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed and working."""
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        return False
    
    try:
        result = subprocess.run(
            [ffmpeg_path, '-version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def download_ffmpeg(progress_callback: Optional[Callable[[str, float], None]] = None) -> bool:
    """
    Download and install FFmpeg to the app's bin directory.
    
    Args:
        progress_callback: Optional callback(status: str, percentage: float)
    
    Returns:
        True if successful, False otherwise.
    """
    if progress_callback:
        progress_callback("Verificando FFmpeg...", 0)
    
    system = platform.system()
    bin_dir = get_app_bin_dir()
    
    try:
        if system == 'Windows':
            return _download_ffmpeg_windows(bin_dir, progress_callback)
        elif system == 'Linux':
            return _download_ffmpeg_linux(bin_dir, progress_callback)
        elif system == 'Darwin':
            return _download_ffmpeg_macos(bin_dir, progress_callback)
        else:
            return False
    except Exception as e:
        if progress_callback:
            progress_callback(f"Erro: {str(e)}", 0)
        return False


def _download_ffmpeg_windows(bin_dir: str, callback: Optional[Callable] = None) -> bool:
    """Download FFmpeg for Windows."""
    # Use a pre-built FFmpeg release from GitHub
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    if callback:
        callback("Baixando FFmpeg...", 10)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, 'ffmpeg.zip')
        
        # Download with progress
        def _report_progress(block_num, block_size, total_size):
            if callback and total_size > 0:
                percent = min(10 + (block_num * block_size / total_size) * 70, 80)
                callback(f"Baixando FFmpeg... {percent:.0f}%", percent)
        
        urllib.request.urlretrieve(url, zip_path, _report_progress)
        
        if callback:
            callback("Extraindo FFmpeg...", 85)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        
        if callback:
            callback("Instalando FFmpeg...", 95)
        
        # Find and copy ffmpeg.exe
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file == 'ffmpeg.exe':
                    src = os.path.join(root, file)
                    dst = os.path.join(bin_dir, 'ffmpeg.exe')
                    shutil.copy2(src, dst)
                    
                    # Also copy ffprobe if available
                    ffprobe_src = os.path.join(root, 'ffprobe.exe')
                    if os.path.exists(ffprobe_src):
                        shutil.copy2(ffprobe_src, os.path.join(bin_dir, 'ffprobe.exe'))
                    
                    if callback:
                        callback("FFmpeg instalado!", 100)
                    return True
    
    return False


def _download_ffmpeg_linux(bin_dir: str, callback: Optional[Callable] = None) -> bool:
    """Download FFmpeg for Linux."""
    # On Linux, suggest using package manager
    if callback:
        callback("No Linux, instale via: sudo apt install ffmpeg", 0)
    
    # Try to use static build
    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    
    # For simplicity, we'll just return False and let user install via apt
    return False


def _download_ffmpeg_macos(bin_dir: str, callback: Optional[Callable] = None) -> bool:
    """Download FFmpeg for macOS."""
    if callback:
        callback("No macOS, instale via: brew install ffmpeg", 0)
    return False


def ensure_ffmpeg(progress_callback: Optional[Callable[[str, float], None]] = None) -> bool:
    """
    Ensure FFmpeg is available. Download if necessary.
    
    Args:
        progress_callback: Optional callback(status: str, percentage: float)
    
    Returns:
        True if FFmpeg is available, False otherwise.
    """
    if is_ffmpeg_installed():
        return True
    
    return download_ffmpeg(progress_callback)


def get_ffmpeg_path() -> Optional[str]:
    """Get the path to FFmpeg executable."""
    return find_ffmpeg()


def add_ffmpeg_to_path():
    """Add the app's bin directory to PATH for subprocess calls."""
    bin_dir = get_app_bin_dir()
    current_path = os.environ.get('PATH', '')
    
    if bin_dir not in current_path:
        os.environ['PATH'] = bin_dir + os.pathsep + current_path
