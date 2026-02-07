"""
Application settings model.

Stores user preferences with save/load functionality.
"""

import json
import os
from dataclasses import dataclass, asdict


def _get_settings_dir() -> str:
    """Get the settings directory path (inside app directory)."""
    current_file = os.path.abspath(__file__)
    # Go up from src/models to app root
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    settings_dir = os.path.join(app_root, 'data')
    os.makedirs(settings_dir, exist_ok=True)
    return settings_dir


def _get_settings_file() -> str:
    """Get the settings file path."""
    return os.path.join(_get_settings_dir(), 'settings.json')


@dataclass
class AppSettings:
    """Application settings."""
    download_dir: str = ""
    last_url: str = ""
    
    def save(self):
        """Save settings to file."""
        try:
            with open(_get_settings_file(), 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    @classmethod
    def load(cls) -> 'AppSettings':
        """Load settings from file."""
        try:
            settings_file = _get_settings_file()
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return cls(**data)
        except Exception:
            pass
        return cls()
