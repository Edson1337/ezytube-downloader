"""
Main window module.

This module provides the main application window with all UI components
for the YouTube downloader application.
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional, List

from .styles import COLORS, FONTS, SPACING
from .widgets import StyledButton, StyledEntry, StyledProgressBar, StatusLabel
from ..core.downloader import YouTubeDownloader
from ..core.file_utils import open_file_in_explorer, get_default_download_dir
from ..core.history_repository import DownloadHistory
from ..models import AppSettings, DownloadProgress, DownloadResult, VideoFormat


class MainWindow:
    """
    Main application window for the YouTube downloader.
    
    This class orchestrates the UI components and handles user interactions,
    following the Interface Segregation Principle by exposing only necessary methods.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: The Tkinter root window.
        """
        self._root = root
        
        # Load settings
        self._settings = AppSettings.load()
        self._history = DownloadHistory()
        
        # Use saved directory or default
        self._output_dir = self._settings.download_dir or get_default_download_dir()
        
        self._downloader: Optional[YouTubeDownloader] = None
        self._last_downloaded_file: Optional[str] = None
        self._download_thread: Optional[threading.Thread] = None
        
        # Format selection
        self._available_formats: List[VideoFormat] = []
        self._selected_format: Optional[VideoFormat] = None
        
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure the main window properties."""
        self._root.title("YouTube Downloader")
        self._root.geometry(f"{SPACING.WINDOW_WIDTH}x{SPACING.WINDOW_HEIGHT}")
        self._root.configure(bg=COLORS.BG_PRIMARY)
        self._root.resizable(False, False)
        
        # Center the window
        self._root.update_idletasks()
        x = (self._root.winfo_screenwidth() - SPACING.WINDOW_WIDTH) // 2
        y = (self._root.winfo_screenheight() - SPACING.WINDOW_HEIGHT) // 2
        self._root.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create and layout all UI widgets."""
        # Main container
        main_container = tk.Frame(self._root, bg=COLORS.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=SPACING.PADDING_LARGE, pady=SPACING.PADDING_LARGE)
        
        # Two-column layout
        left_panel = tk.Frame(main_container, bg=COLORS.BG_PRIMARY)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, SPACING.PADDING_MEDIUM))
        
        right_panel = tk.Frame(main_container, bg=COLORS.BG_SECONDARY, width=380)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # === LEFT PANEL: Download Section ===
        container = left_panel
        
        # Title
        title = tk.Label(
            container,
            text="🎬 YouTube Downloader",
            font=(FONTS.FAMILY, FONTS.SIZE_TITLE, "bold"),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.ACCENT_PRIMARY
        )
        title.pack(pady=(0, SPACING.PADDING_MEDIUM))
        
        # Subtitle
        subtitle = tk.Label(
            container,
            text="Download videos from YouTube in high quality",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, SPACING.PADDING_LARGE))
        
        # === RIGHT PANEL: History ===
        from .history_panel import HistoryPanel
        self._history_panel = HistoryPanel(right_panel, self._history)
        self._history_panel.pack(fill=tk.BOTH, expand=True)
        
        # URL input section
        url_frame = tk.Frame(container, bg=COLORS.BG_PRIMARY)
        url_frame.pack(fill=tk.X, pady=SPACING.PADDING_MEDIUM)
        
        url_label = tk.Label(
            url_frame,
            text="Video URL:",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY, "bold"),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_PRIMARY
        )
        url_label.pack(anchor=tk.W)
        
        self._url_entry = StyledEntry(url_frame, placeholder="Paste YouTube URL here...")
        self._url_entry.pack(fill=tk.X, pady=SPACING.PADDING_SMALL)
        
        # Bind events to fetch formats when URL changes
        self._url_entry._entry.bind('<FocusOut>', self._on_url_changed)
        self._url_entry._entry.bind('<Return>', self._on_url_changed)
        self._url_entry._entry.bind('<KeyRelease>', self._on_url_key_release)
        self._url_entry._entry.bind('<<Paste>>', lambda e: self._root.after(100, self._on_url_changed))
        
        # Directory selection section
        dir_frame = tk.Frame(container, bg=COLORS.BG_PRIMARY)
        dir_frame.pack(fill=tk.X, pady=SPACING.PADDING_MEDIUM)
        
        dir_label = tk.Label(
            dir_frame,
            text="Save to:",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY, "bold"),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_PRIMARY
        )
        dir_label.pack(anchor=tk.W)
        
        dir_input_frame = tk.Frame(dir_frame, bg=COLORS.BG_PRIMARY)
        dir_input_frame.pack(fill=tk.X, pady=SPACING.PADDING_SMALL)
        
        self._dir_entry = StyledEntry(dir_input_frame, placeholder="", width=40)
        self._dir_entry.set(self._output_dir)
        self._dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = StyledButton(
            dir_input_frame,
            text="📁 Browse",
            command=self._browse_directory,
            width=12
        )
        browse_btn.pack(side=tk.RIGHT, padx=(SPACING.PADDING_SMALL, 0))
        
        # === Settings section ===
        settings_frame = tk.Frame(container, bg=COLORS.BG_PRIMARY)
        settings_frame.pack(fill=tk.X, pady=SPACING.PADDING_MEDIUM)
        
        settings_label = tk.Label(
            settings_frame,
            text="Configuracoes:",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY, "bold"),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_PRIMARY
        )
        settings_label.pack(anchor=tk.W)
        
        # Settings row container
        settings_row = tk.Frame(settings_frame, bg=COLORS.BG_PRIMARY)
        settings_row.pack(fill=tk.X, pady=SPACING.PADDING_SMALL)
        
        # Resolution dropdown
        resolution_label = tk.Label(
            settings_row,
            text="Qualidade:",
            font=(FONTS.FAMILY, FONTS.SIZE_BODY),
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_SECONDARY
        )
        resolution_label.pack(side=tk.LEFT)
        
        self._format_var = tk.StringVar(value="Melhor disponivel")
        self._format_combo = ttk.Combobox(
            settings_row,
            textvariable=self._format_var,
            state="readonly",
            width=20
        )
        self._format_combo['values'] = ["Melhor disponivel"]
        self._format_combo.pack(side=tk.LEFT, padx=(SPACING.PADDING_SMALL, SPACING.PADDING_LARGE))
        self._format_combo.bind('<<ComboboxSelected>>', self._on_format_selected)
        
        # Playlist checkbox (disabled by default, enabled when URL has playlist)
        self._playlist_var = tk.BooleanVar(value=False)
        self._playlist_check = tk.Checkbutton(
            settings_row,
            text="Baixar playlist completa",
            variable=self._playlist_var,
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_SECONDARY,
            disabledforeground=COLORS.TEXT_SECONDARY,
            selectcolor=COLORS.BG_TERTIARY,
            activebackground=COLORS.BG_PRIMARY,
            activeforeground=COLORS.TEXT_PRIMARY,
            font=(FONTS.FAMILY, FONTS.SIZE_BODY),
            state=tk.DISABLED
        )
        self._playlist_check.pack(side=tk.LEFT)
        
        # Audio-only checkbox
        self._audio_only_var = tk.BooleanVar(value=False)
        self._audio_only_check = tk.Checkbutton(
            settings_row,
            text="Apenas audio (MP3)",
            variable=self._audio_only_var,
            bg=COLORS.BG_PRIMARY,
            fg=COLORS.TEXT_SECONDARY,
            selectcolor=COLORS.BG_TERTIARY,
            activebackground=COLORS.BG_PRIMARY,
            activeforeground=COLORS.TEXT_PRIMARY,
            font=(FONTS.FAMILY, FONTS.SIZE_BODY)
        )
        self._audio_only_check.pack(side=tk.LEFT, padx=(SPACING.PADDING_MEDIUM, 0))
        
        # Download button
        btn_frame = tk.Frame(container, bg=COLORS.BG_PRIMARY)
        btn_frame.pack(fill=tk.X, pady=SPACING.PADDING_LARGE)
        
        self._download_btn = StyledButton(
            btn_frame,
            text="⬇️  Download Video",
            command=self._start_download,
            width=25
        )
        self._download_btn.pack(side=tk.LEFT)
        
        # Cancel button (hidden by default)
        self._cancel_btn = StyledButton(
            btn_frame,
            text="❌ Cancelar",
            command=self._cancel_download,
            width=15
        )
        # Don't pack yet - will show when download starts
        
        # Progress section (initially hidden)
        self._progress_bar = StyledProgressBar(container)
        # Don't pack yet - will show when download starts
        
        # Status label
        self._status_label = StatusLabel(container)
        self._status_label.pack(fill=tk.X, pady=SPACING.PADDING_SMALL)
        
        # Open folder button (initially hidden)
        self._open_folder_btn = StyledButton(
            container,
            text="📂 Open Folder",
            command=self._open_download_folder,
            width=20
        )
        # Don't pack yet - will show after successful download
    
    def _browse_directory(self):
        """Open directory selection dialog."""
        directory = filedialog.askdirectory(
            initialdir=self._output_dir,
            title="Selecionar Pasta de Download"
        )
        if directory:
            self._output_dir = directory
            self._dir_entry.set(directory)
            
            # Save preference
            self._settings.download_dir = directory
            self._settings.save()
    
    def _on_format_selected(self, event=None):
        """Handle format selection from combobox."""
        selected_text = self._format_var.get()
        for fmt in self._available_formats:
            if fmt.resolution == selected_text:
                self._selected_format = fmt
                break
    
    def _on_url_key_release(self, event=None):
        """Handle key release in URL entry - debounced fetch."""
        # Cancel any pending fetch
        if hasattr(self, '_url_fetch_timer') and self._url_fetch_timer:
            self._root.after_cancel(self._url_fetch_timer)
        
        # Schedule fetch after 500ms of no typing
        self._url_fetch_timer = self._root.after(500, self._on_url_changed)
    
    def _on_url_changed(self, event=None):
        """Fetch available formats when URL is entered."""
        url = self._url_entry.get().strip()
        
        if not url or not url.startswith(("http://", "https://")):
            return
        
        # Don't refetch if same URL
        if hasattr(self, '_last_fetched_url') and self._last_fetched_url == url:
            return
        
        self._last_fetched_url = url
        self._status_label.set_status("Buscando qualidades disponiveis...", "info")
        
        # Check if URL is from a playlist
        is_playlist = 'list=' in url
        self._update_playlist_checkbox(is_playlist)
        
        self._root.update()
        
        # Fetch formats in background thread
        def fetch_formats():
            try:
                temp_downloader = YouTubeDownloader(
                    output_dir=self._output_dir
                )
                formats = temp_downloader.get_available_formats(url)
                self._root.after(0, lambda: self._update_format_combo(formats))
            except Exception:
                self._root.after(0, lambda: self._update_format_combo([]))
        
        thread = threading.Thread(target=fetch_formats)
        thread.daemon = True
        thread.start()
    
    def _update_playlist_checkbox(self, is_playlist: bool):
        """Enable or disable playlist checkbox based on URL type."""
        if is_playlist:
            self._playlist_check.config(state=tk.NORMAL)
            self._playlist_var.set(False)  # Reset to unchecked
        else:
            self._playlist_var.set(False)
            self._playlist_check.config(state=tk.DISABLED)
    
    def _update_format_combo(self, formats: List[VideoFormat]):
        """Update the format combobox with available formats."""
        self._available_formats = formats
        
        if formats:
            values = [f.resolution for f in formats]
            self._format_combo['values'] = values
            self._format_combo.current(0)
            self._selected_format = formats[0]
            self._status_label.set_status("Pronto para download", "success")
        else:
            self._format_combo['values'] = ["Melhor disponivel"]
            self._format_combo.current(0)
            self._status_label.set_status("", "info")
    
    def _start_download(self):
        """Start the download process in a separate thread."""
        url = self._url_entry.get().strip()
        
        if not url:
            self._status_label.set_status("Please enter a YouTube URL", "error")
            return
        
        if not url.startswith(("http://", "https://")):
            self._status_label.set_status("Please enter a valid URL", "error")
            return
        
        # Update output directory from entry
        self._output_dir = self._dir_entry.get() or get_default_download_dir()
        
        # Create downloader to check for existing file
        self._downloader = YouTubeDownloader(
            output_dir=self._output_dir,
            progress_callback=self._on_progress,
            video_complete_callback=self._on_video_complete
        )
        
        # Check if video already exists
        self._status_label.set_status("Verificando video...", "info")
        self._download_btn.set_enabled(False)
        self._root.update()
        
        # Get video info first (in separate thread to avoid freezing)
        def check_and_download():
            video_info = self._downloader.get_video_info(url)
            
            if video_info:
                existing_file = self._downloader.check_file_exists(video_info['title'])
                if existing_file:
                    # File exists - ask user on main thread
                    self._root.after(0, lambda: self._ask_overwrite(url, video_info['title'], existing_file))
                    return
            
            # No existing file or couldn't get info - proceed with download
            self._root.after(0, lambda: self._proceed_download(url))
        
        thread = threading.Thread(target=check_and_download)
        thread.daemon = True
        thread.start()
    
    def _ask_overwrite(self, url: str, title: str, existing_file: str):
        """Ask user if they want to overwrite existing file."""
        result = messagebox.askyesnocancel(
            "Arquivo ja existe",
            f"O video '{title}' ja existe nesta pasta.\n\n"
            "Deseja baixar novamente?\n\n"
            "Sim = Sobrescrever\n"
            "Nao = Abrir arquivo existente\n"
            "Cancelar = Cancelar download"
        )
        
        if result is True:  # Yes - overwrite
            self._proceed_download(url)
        elif result is False:  # No - open existing
            self._download_btn.set_enabled(True)
            self._status_label.set_status("Abrindo arquivo existente...", "info")
            open_file_in_explorer(existing_file)
        else:  # Cancel
            self._download_btn.set_enabled(True)
            self._status_label.set_status("Download cancelado", "info")
    
    def _proceed_download(self, url: str):
        """Proceed with the actual download."""
        # Hide open folder button, show progress bar and cancel button
        self._open_folder_btn.pack_forget()
        self._progress_bar.pack(fill=tk.X, pady=SPACING.PADDING_MEDIUM)
        self._progress_bar.reset()
        self._cancel_btn.pack(side=tk.LEFT, padx=(SPACING.PADDING_SMALL, 0))
        self._status_label.set_status("Iniciando download...", "info")
        
        # Start download in separate thread
        self._download_thread = threading.Thread(target=self._download_video, args=(url,))
        self._download_thread.daemon = True
        self._download_thread.start()
    
    def _download_video(self, url: str):
        """Download video in separate thread."""
        # Determine format settings
        format_id = 'best'
        audio_only = False
        
        if self._selected_format:
            format_id = self._selected_format.format_id
        
        # Check audio-only setting from checkbox
        audio_only = self._audio_only_var.get()
        
        # Check playlist setting
        if self._playlist_var.get():
            # Override noplaylist in downloader
            self._downloader._noplaylist = False
        
        result = self._downloader.download(url, format_id=format_id, audio_only=audio_only)
        
        # Update UI from main thread
        self._root.after(0, lambda: self._on_download_complete(result))
    
    def _on_progress(self, progress: DownloadProgress):
        """Handle progress updates from downloader."""
        # Create a copy of progress data to avoid closure issues
        pct = progress.percentage
        status = progress.status
        speed = progress.speed
        eta = progress.eta
        
        # Schedule UI update on main thread
        self._root.after(0, lambda: self._update_progress_ui(pct, status, speed, eta))
    
    def _on_video_complete(self, title: str, url: str, file_path: str):
        """Handle individual video completion (for playlists)."""
        # Add to history and refresh panel on main thread
        def add_to_history():
            self._history.add_entry(
                title=title,
                url=url,
                file_path=file_path
            )
            self._history_panel.refresh()
        
        self._root.after(0, add_to_history)
    
    def _update_progress_ui(self, percentage: float, status: str, speed: str, eta: str):
        """Update progress UI elements with explicit parameters."""
        if status == 'downloading':
            # Build info string with speed and ETA
            info_parts = ["Baixando..."]
            if speed:
                info_parts.append(f"Velocidade: {speed}")
            if eta:
                info_parts.append(f"Tempo restante: {eta}")
            
            info_text = " | ".join(info_parts)
            self._progress_bar.set_progress(percentage, info_text)
            
            self._status_label.set_status(
                f"Baixando: {percentage:.1f}%",
                "info"
            )
        elif status == 'finished':
            self._progress_bar.set_progress(100, "Processando vídeo...")
            self._status_label.set_status("Processando vídeo...", "info")
        
        # Force immediate UI refresh
        self._root.update_idletasks()
    
    def _on_download_complete(self, result: DownloadResult):
        """Handle download completion."""
        self._download_btn.set_enabled(True)
        
        # Hide progress bar and cancel button after download completes
        self._progress_bar.pack_forget()
        self._cancel_btn.pack_forget()
        
        if result.success:
            self._last_downloaded_file = result.file_path
            self._status_label.set_status(
                f"✅ Download concluído: {result.title}",
                "success"
            )
            
            # Save to download history
            if result.file_path:
                self._history.add_entry(
                    title=result.title or "Unknown",
                    url=self._url_entry.get(),
                    file_path=result.file_path
                )
                # Refresh history panel
                self._history_panel.refresh()
            
            # Show open folder button
            self._open_folder_btn.pack(pady=SPACING.PADDING_MEDIUM)
        else:
            # Check if it was a cancellation (not an error)
            if result.error_message and "cancelado" in result.error_message.lower():
                self._status_label.set_status(
                    "✅ Download cancelado com sucesso!",
                    "info"
                )
            else:
                self._status_label.set_status(
                    f"❌ Erro: {result.error_message}",
                    "error"
                )
    
    def _cancel_download(self):
        """Cancel the current download."""
        if self._downloader:
            self._downloader.cancel()
            self._status_label.set_status("Cancelando download...", "info")
            self._cancel_btn.set_enabled(False)
    
    def _open_download_folder(self):
        """Open the folder containing the downloaded file."""
        if self._last_downloaded_file:
            if not open_file_in_explorer(self._last_downloaded_file):
                messagebox.showerror(
                    "Error",
                    "Could not open the folder. Please navigate manually."
                )
        elif self._output_dir:
            import os
            os.startfile(self._output_dir) if os.name == 'nt' else None
