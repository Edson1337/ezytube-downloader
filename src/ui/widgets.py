"""
Custom widgets module.

This module provides reusable styled widgets for the application UI,
following the Open/Closed Principle for extensibility.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from .styles import COLORS, FONTS, SPACING


class StyledButton(tk.Button):
    """A styled button with hover effects and modern appearance."""
    
    def __init__(
        self,
        parent,
        text: str,
        command: Optional[Callable] = None,
        width: int = 20,
        **kwargs
    ):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=(FONTS.FAMILY, FONTS.SIZE_BUTTON, "bold"),
            bg=COLORS.BUTTON_BG,
            fg=COLORS.TEXT_PRIMARY,
            activebackground=COLORS.BUTTON_ACTIVE,
            activeforeground=COLORS.TEXT_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            width=width,
            height=2,
            **kwargs
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        if self["state"] != tk.DISABLED:
            self.config(bg=COLORS.BUTTON_HOVER)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        if self["state"] != tk.DISABLED:
            self.config(bg=COLORS.BUTTON_BG)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button with appropriate styling."""
        if enabled:
            self.config(state=tk.NORMAL, bg=COLORS.BUTTON_BG)
        else:
            self.config(state=tk.DISABLED, bg=COLORS.BUTTON_DISABLED)


class StyledEntry(tk.Frame):
    """A styled entry widget with placeholder support."""
    
    def __init__(
        self,
        parent,
        placeholder: str = "",
        width: int = 50,
        **kwargs
    ):
        super().__init__(parent, bg=COLORS.BG_PRIMARY)
        
        self._placeholder = placeholder
        self._has_placeholder = True
        
        self._entry = tk.Entry(
            self,
            font=(FONTS.FAMILY, FONTS.SIZE_BODY),
            bg=COLORS.INPUT_BG,
            fg=COLORS.TEXT_MUTED,
            insertbackground=COLORS.TEXT_PRIMARY,
            relief=tk.FLAT,
            width=width,
            **kwargs
        )
        self._entry.pack(padx=2, pady=2, fill=tk.X, expand=True)
        
        # Set placeholder
        self._entry.insert(0, placeholder)
        
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Clear placeholder on focus."""
        if self._has_placeholder:
            self._entry.delete(0, tk.END)
            self._entry.config(fg=COLORS.TEXT_PRIMARY)
            self._has_placeholder = False
    
    def _on_focus_out(self, event):
        """Restore placeholder if empty."""
        if not self._entry.get():
            self._entry.insert(0, self._placeholder)
            self._entry.config(fg=COLORS.TEXT_MUTED)
            self._has_placeholder = True
    
    def get(self) -> str:
        """Get the entry value, returning empty string if placeholder is shown."""
        if self._has_placeholder:
            return ""
        return self._entry.get()
    
    def set(self, value: str):
        """Set the entry value."""
        self._has_placeholder = False
        self._entry.delete(0, tk.END)
        self._entry.insert(0, value)
        self._entry.config(fg=COLORS.TEXT_PRIMARY)
    
    def clear(self):
        """Clear the entry and show placeholder."""
        self._entry.delete(0, tk.END)
        self._entry.insert(0, self._placeholder)
        self._entry.config(fg=COLORS.TEXT_MUTED)
        self._has_placeholder = True


class StyledProgressBar(tk.Frame):
    """A styled progress bar with percentage display and animated fill."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS.BG_PRIMARY, **kwargs)
        
        # Progress info label (above bar)
        self._info_label = tk.Label(
            self,
            text="Pronto para download",
            font=(FONTS.FAMILY, FONTS.SIZE_SMALL),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_SECONDARY
        )
        self._info_label.pack(pady=(0, SPACING.PADDING_SMALL))
        
        # Outer container with border effect
        self._outer = tk.Frame(
            self,
            bg=COLORS.BG_TERTIARY,
            height=30,
            relief=tk.FLAT,
            bd=0
        )
        self._outer.pack(fill=tk.X, padx=2)
        self._outer.pack_propagate(False)
        
        # Container for progress bar
        self._container = tk.Frame(
            self._outer,
            bg=COLORS.PROGRESS_BG,
            height=26
        )
        self._container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self._container.pack_propagate(False)
        
        # Progress fill with gradient-like color
        self._fill = tk.Frame(
            self._container,
            bg=COLORS.PROGRESS_FILL,
            height=26
        )
        self._fill.place(x=0, y=0, relheight=1.0, relwidth=0)
        
        # Percentage label (centered on bar)
        self._percent_label = tk.Label(
            self._container,
            text="0%",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY, "bold"),
            bg=COLORS.PROGRESS_BG,
            fg=COLORS.TEXT_PRIMARY
        )
        self._percent_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self._percentage = 0.0
    
    def set_progress(self, percentage: float, info: str = None):
        """
        Set the progress percentage (0-100).
        
        Args:
            percentage: Progress value between 0 and 100.
            info: Optional info text to display above the bar.
        """
        self._percentage = max(0, min(100, percentage))
        
        # Update fill width
        self._fill.place(x=0, y=0, relheight=1.0, relwidth=self._percentage / 100)
        
        # Update percentage label
        self._percent_label.config(text=f"{self._percentage:.1f}%")
        
        # Change label background color when progress > 50%
        if self._percentage > 50:
            self._percent_label.config(bg=COLORS.PROGRESS_FILL)
        else:
            self._percent_label.config(bg=COLORS.PROGRESS_BG)
        
        # Update info label if provided
        if info:
            self._info_label.config(text=info)
        
        # Force UI update
        self.update_idletasks()
    
    def set_info(self, info: str):
        """Set the info text above the progress bar."""
        self._info_label.config(text=info)
        self.update_idletasks()
    
    def reset(self):
        """Reset the progress bar to 0%."""
        self._percentage = 0.0
        self._fill.place(x=0, y=0, relheight=1.0, relwidth=0)
        self._percent_label.config(text="0%", bg=COLORS.PROGRESS_BG)
        self._info_label.config(text="Pronto para download")
        self.update_idletasks()


class StatusLabel(tk.Label):
    """A label for displaying status messages with appropriate coloring."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            text="",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_SECONDARY,
            wraplength=500,
            justify=tk.CENTER,
            **kwargs
        )
    
    def set_status(self, message: str, status_type: str = "info"):
        """
        Set the status message with appropriate color.
        
        Args:
            message: The status message to display.
            status_type: One of 'info', 'success', 'warning', 'error'.
        """
        color_map = {
            "info": COLORS.TEXT_SECONDARY,
            "success": COLORS.SUCCESS,
            "warning": COLORS.WARNING,
            "error": COLORS.ERROR
        }
        self.config(text=message, fg=color_map.get(status_type, COLORS.TEXT_SECONDARY))
    
    def clear(self):
        """Clear the status message."""
        self.config(text="")
