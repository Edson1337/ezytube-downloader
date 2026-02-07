"""
File utilities module.

This module provides cross-platform file operations including filename sanitization
and opening folders in the system file explorer.
"""

import os
import platform
import re
import subprocess
import unicodedata


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing special characters and normalizing.
    
    Args:
        filename: The original filename to sanitize.
        
    Returns:
        A sanitized filename safe for use on any filesystem.
    """
    # Remove accents and special unicode characters
    nfkd_form = unicodedata.normalize('NFKD', filename)
    filename = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Replace special characters with spaces
    filename = re.sub(r'[^\w\s]', ' ', filename)
    
    # Replace multiple spaces with single underscore
    filename = re.sub(r'\s+', '_', filename)
    
    # Convert to lowercase
    return filename.lower()


def open_folder(path: str) -> bool:
    """
    Open a folder in the system's file explorer.
    
    Works on Windows, macOS, and Linux.
    
    Args:
        path: The path to the folder to open.
        
    Returns:
        True if the folder was opened successfully, False otherwise.
    """
    if not os.path.exists(path):
        return False
    
    # Get the directory if path is a file
    if os.path.isfile(path):
        path = os.path.dirname(path)
    
    try:
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', path], check=True)
        else:  # Linux and other Unix-like
            subprocess.run(['xdg-open', path], check=True)
        
        return True
    except Exception:
        return False


def open_file_in_explorer(file_path: str) -> bool:
    """
    Open file explorer and select/highlight a specific file.
    
    Args:
        file_path: The path to the file to highlight.
        
    Returns:
        True if successful, False otherwise.
    """
    if not file_path:
        return False
    
    # If file doesn't exist, try opening the folder instead
    if not os.path.exists(file_path):
        folder = os.path.dirname(file_path)
        if os.path.exists(folder):
            return open_folder(folder)
        return False
    
    try:
        system = platform.system()
        
        if system == 'Windows':
            # Windows explorer returns non-zero even on success, so don't use check=True
            subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
            return True
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', '-R', file_path], check=True)
        else:  # Linux
            # Most Linux file managers don't support selecting a file directly
            # So we just open the containing folder
            folder = os.path.dirname(file_path)
            subprocess.run(['xdg-open', folder], check=True)
        
        return True
    except Exception:
        return False


def validate_directory(path: str) -> bool:
    """
    Validate if a path is a valid directory or can be created.
    
    Args:
        path: The directory path to validate.
        
    Returns:
        True if the directory exists or can be created, False otherwise.
    """
    if os.path.isdir(path):
        return True
    
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def get_default_download_dir() -> str:
    """
    Get the default download directory based on the operating system.
    
    Returns:
        The path to the user's Downloads folder or home directory.
    """
    # Try to get the Downloads folder
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    
    if os.path.isdir(downloads):
        return downloads
    
    # Fallback to home directory
    return home
