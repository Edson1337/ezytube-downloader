"""
Download history repository.

Manages persistence of download history entries.
"""

import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional

from ..models import DownloadEntry


def _get_data_dir() -> str:
    """Get the data directory path (inside app directory)."""
    current_file = os.path.abspath(__file__)
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    data_dir = os.path.join(app_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def _get_history_file() -> str:
    """Get the download history file path."""
    return os.path.join(_get_data_dir(), 'history.json')


class DownloadHistory:
    """Repository for managing download history."""
    
    def __init__(self):
        self._entries: List[DownloadEntry] = []
        self._load()
        self._remove_duplicates()
    
    def _load(self):
        """Load history from file."""
        try:
            history_file = _get_history_file()
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._entries = [DownloadEntry(**entry) for entry in data]
        except Exception:
            self._entries = []
    
    def _remove_duplicates(self):
        """Remove duplicate entries based on file_path, keeping most recent."""
        seen_paths = set()
        unique_entries = []
        for entry in self._entries:
            if entry.file_path not in seen_paths:
                seen_paths.add(entry.file_path)
                unique_entries.append(entry)
        
        if len(unique_entries) != len(self._entries):
            self._entries = unique_entries
            self._save()
    
    def _save(self):
        """Save history to file."""
        try:
            with open(_get_history_file(), 'w', encoding='utf-8') as f:
                data = [asdict(entry) for entry in self._entries]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def add_entry(self, title: str, url: str, file_path: str, file_size: Optional[int] = None):
        """Add a new download entry. Removes duplicate if same file exists."""
        self._entries = [e for e in self._entries if e.file_path != file_path]
        
        entry = DownloadEntry(
            title=title,
            url=url,
            file_path=file_path,
            download_date=datetime.now().isoformat(),
            file_size=file_size
        )
        self._entries.insert(0, entry)
        self._entries = self._entries[:100]
        self._save()
    
    def get_entries(self) -> List[DownloadEntry]:
        """Get all history entries."""
        return self._entries.copy()
    
    def get_last_file_path(self) -> Optional[str]:
        """Get the file path of the most recent download."""
        if self._entries:
            return self._entries[0].file_path
        return None
    
    def remove_entry(self, file_path: str):
        """Remove a specific entry by file path."""
        self._entries = [e for e in self._entries if e.file_path != file_path]
        self._save()
    
    def clear(self):
        """Clear all history."""
        self._entries = []
        self._save()
