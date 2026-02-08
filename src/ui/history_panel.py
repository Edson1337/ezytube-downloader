"""
History panel widget module.

This module provides a collapsible history panel that displays
downloaded videos organized by folder with buttons to open in explorer.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
import os

from .styles import COLORS, FONTS, SPACING
from ..core.history_repository import DownloadHistory
from ..core.file_utils import open_file_in_explorer, open_folder
from ..models import DownloadEntry


class HistoryPanel(tk.Frame):
    """A collapsible panel displaying download history organized by folders."""
    
    def __init__(self, parent, history: DownloadHistory, **kwargs):
        super().__init__(parent, bg=COLORS.BG_SECONDARY, **kwargs)
        
        self._history = history
        self._is_expanded = False  # Start collapsed
        self._content_frame = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the panel widgets."""
        # Toggle header (always visible)
        self._header_frame = tk.Frame(self, bg=COLORS.BG_TERTIARY, cursor="hand2")
        self._header_frame.pack(fill=tk.X)
        self._header_frame.bind("<Button-1>", lambda e: self.toggle())
        
        # Toggle arrow and title
        self._toggle_label = tk.Label(
            self._header_frame,
            text="▶ Histórico",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY, "bold"),
            bg=COLORS.BG_TERTIARY,
            fg=COLORS.TEXT_PRIMARY,
            cursor="hand2",
            padx=10,
            pady=8
        )
        self._toggle_label.pack(side=tk.LEFT)
        self._toggle_label.bind("<Button-1>", lambda e: self.toggle())
        
        # Count badge
        self._count_label = tk.Label(
            self._header_frame,
            text="",
            font=(FONTS.FAMILY, FONTS.SIZE_SMALL),
            bg=COLORS.ACCENT_PRIMARY,
            fg=COLORS.TEXT_PRIMARY,
            padx=6,
            pady=2
        )
        self._count_label.pack(side=tk.RIGHT, padx=10)
        
        # Content container (initially hidden)
        self._content_frame = tk.Frame(self, bg=COLORS.BG_SECONDARY)
        
        # Refresh button inside content
        controls_frame = tk.Frame(self._content_frame, bg=COLORS.BG_SECONDARY)
        controls_frame.pack(fill=tk.X, padx=SPACING.PADDING_SMALL, pady=SPACING.PADDING_SMALL)
        
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Atualizar",
            font=(FONTS.FAMILY, FONTS.SIZE_SMALL),
            bg=COLORS.BG_TERTIARY,
            fg=COLORS.TEXT_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.refresh
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Scrollable container
        self._canvas = tk.Canvas(
            self._content_frame,
            bg=COLORS.BG_SECONDARY,
            highlightthickness=0,
            height=400
        )
        
        scrollbar = ttk.Scrollbar(
            self._content_frame,
            orient=tk.VERTICAL,
            command=self._canvas.yview
        )
        
        self._scrollable_frame = tk.Frame(self._canvas, bg=COLORS.BG_SECONDARY)
        
        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        
        self._canvas_window = self._canvas.create_window((0, 0), window=self._scrollable_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind canvas resize to update scrollable frame width
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Enable mouse wheel scrolling
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update count
        self._update_count()
    
    def _on_canvas_configure(self, event):
        """Update scrollable frame width when canvas resizes."""
        self._canvas.itemconfig(self._canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _update_count(self):
        """Update the entry count badge."""
        count = len(self._history.get_entries())
        if count > 0:
            self._count_label.config(text=str(count))
            self._count_label.pack(side=tk.RIGHT, padx=10)
        else:
            self._count_label.pack_forget()
    
    def toggle(self):
        """Toggle the panel expanded/collapsed state."""
        self._is_expanded = not self._is_expanded
        
        if self._is_expanded:
            self._toggle_label.config(text="▼ Histórico")
            self._content_frame.pack(fill=tk.BOTH, expand=True)
            self.refresh()
        else:
            self._toggle_label.config(text="▶ Histórico")
            self._content_frame.pack_forget()
    
    def expand(self):
        """Expand the panel."""
        if not self._is_expanded:
            self.toggle()
    
    def collapse(self):
        """Collapse the panel."""
        if self._is_expanded:
            self.toggle()
    
    def refresh(self):
        """Refresh the history display."""
        # Validate entries - remove those for files that no longer exist
        self._history.validate_entries()
        
        # Clear existing widgets in scrollable frame
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()
        
        entries = self._history.get_entries()
        self._update_count()
        
        if not entries:
            empty_label = tk.Label(
                self._scrollable_frame,
                text="Nenhum download ainda",
                font=(FONTS.FAMILY, FONTS.SIZE_BODY),
                bg=COLORS.BG_SECONDARY,
                fg=COLORS.TEXT_MUTED
            )
            empty_label.pack(pady=SPACING.PADDING_LARGE)
            return
        
        # Group entries by folder
        folders: Dict[str, List[DownloadEntry]] = {}
        for entry in entries:
            folder = os.path.dirname(entry.file_path) if entry.file_path else "Unknown"
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(entry)
        
        # Create folder sections
        for folder_path, folder_entries in folders.items():
            self._create_folder_section(folder_path, folder_entries)
    
    def _create_folder_section(self, folder_path: str, entries: List[DownloadEntry]):
        """Create a collapsible folder section."""
        # Folder header
        folder_frame = tk.Frame(self._scrollable_frame, bg=COLORS.BG_TERTIARY)
        folder_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Folder name (shortened)
        folder_name = os.path.basename(folder_path) or folder_path
        if len(folder_name) > 25:
            folder_name = folder_name[:22] + "..."
        
        folder_header = tk.Frame(folder_frame, bg=COLORS.BG_TERTIARY)
        folder_header.pack(fill=tk.X, padx=4, pady=4)
        
        folder_label = tk.Label(
            folder_header,
            text=f"📁 {folder_name} ({len(entries)})",
            font=(FONTS.FAMILY, FONTS.SIZE_SMALL, "bold"),
            bg=COLORS.BG_TERTIARY,
            fg=COLORS.ACCENT_PRIMARY
        )
        folder_label.pack(side=tk.LEFT)
        
        # Open folder button
        open_folder_btn = tk.Button(
            folder_header,
            text="📂",
            font=(FONTS.FAMILY, 8),
            bg=COLORS.BG_TERTIARY,
            fg=COLORS.TEXT_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda p=folder_path: open_folder(p)
        )
        open_folder_btn.pack(side=tk.RIGHT)
        
        # Video entries
        entries_frame = tk.Frame(folder_frame, bg=COLORS.BG_SECONDARY)
        entries_frame.pack(fill=tk.X, padx=4, pady=(0, 4))
        
        for entry in entries[:10]:  # Limit to 10 per folder
            self._create_video_entry(entries_frame, entry)
    
    def _create_video_entry(self, parent: tk.Frame, entry: DownloadEntry):
        """Create a single video entry row."""
        entry_frame = tk.Frame(parent, bg=COLORS.BG_SECONDARY)
        entry_frame.pack(fill=tk.X, pady=1)
        
        # Video title (truncated)
        title = entry.title
        if len(title) > 35:
            title = title[:32] + "..."
        
        title_label = tk.Label(
            entry_frame,
            text=f"🎬 {title}",
            font=(FONTS.FAMILY, 9),
            bg=COLORS.BG_SECONDARY,
            fg=COLORS.TEXT_SECONDARY,
            anchor=tk.W
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Delete button (X character for better rendering)
        delete_btn = tk.Button(
            entry_frame,
            text="✕",
            font=(FONTS.FAMILY, 8),
            bg=COLORS.ERROR,
            fg=COLORS.TEXT_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            width=2,
            command=lambda fp=entry.file_path: self._delete_entry(fp)
        )
        delete_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Locate in explorer button (magnifying glass) - selects the file
        locate_btn = tk.Button(
            entry_frame,
            text="🔍",
            font=(FONTS.FAMILY, 8),
            bg=COLORS.BG_TERTIARY,
            fg=COLORS.TEXT_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            width=2,
            command=lambda fp=entry.file_path: open_file_in_explorer(fp)
        )
        locate_btn.pack(side=tk.RIGHT, padx=(1, 8))  # More padding on the right
    
    def _delete_entry(self, file_path: str):
        """Delete an entry from history and the actual file from disk."""
        from tkinter import messagebox
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir este vídeo?\n\nO arquivo será removido permanentemente do disco.",
            icon='warning'
        )
        
        if result:
            # Delete file from disk
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # File might already be deleted or inaccessible
            
            # Remove from history
            self._history.remove_entry(file_path)
            self.refresh()
