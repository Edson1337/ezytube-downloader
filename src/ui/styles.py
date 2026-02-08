"""
UI styles module.

This module defines the visual styling constants for the application,
including colors, fonts, and spacing following modern design principles.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:
    """Color palette for the application using a modern dark theme."""
    
    # Background colors
    BG_PRIMARY = "#1a1a2e"
    BG_SECONDARY = "#16213e"
    BG_TERTIARY = "#0f3460"
    
    # Accent colors
    ACCENT_PRIMARY = "#e94560"
    ACCENT_SECONDARY = "#ff6b6b"
    ACCENT_GRADIENT_START = "#e94560"
    ACCENT_GRADIENT_END = "#ff6b6b"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b8b8b8"
    TEXT_MUTED = "#6c6c6c"
    
    # Status colors
    SUCCESS = "#4ecca3"
    WARNING = "#ffd93d"
    ERROR = "#ff6b6b"
    
    # Button colors
    BUTTON_BG = "#e94560"
    BUTTON_HOVER = "#ff6b6b"
    BUTTON_ACTIVE = "#c73e54"
    BUTTON_DISABLED = "#4a4a5a"
    
    # Input colors
    INPUT_BG = "#0f3460"
    INPUT_BORDER = "#1a1a2e"
    INPUT_FOCUS_BORDER = "#e94560"
    
    # Progress bar
    PROGRESS_BG = "#1a1a2e"
    PROGRESS_FILL = "#4ecca3"


@dataclass(frozen=True)
class Fonts:
    """Font configurations for the application."""
    
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    SIZE_TITLE = 24
    SIZE_HEADING = 18
    SIZE_BODY = 12
    SIZE_SMALL = 10
    SIZE_BUTTON = 11


@dataclass(frozen=True)
class Spacing:
    """Spacing and sizing constants."""
    
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    PADDING_XLARGE = 30
    
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 15
    
    BORDER_RADIUS = 8
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 40
    
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 650


# Create singleton instances
COLORS = Colors()
FONTS = Fonts()
SPACING = Spacing()
