"""
YouTube Downloader - Main Entry Point

A modern desktop application for downloading YouTube videos.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add src to path for proper imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import MainWindow
from src.core.dependencies import is_ffmpeg_installed, ensure_ffmpeg, add_ffmpeg_to_path


def check_dependencies(root: tk.Tk) -> bool:
    """Check and install dependencies. Returns True if all ok."""
    if is_ffmpeg_installed():
        add_ffmpeg_to_path()
        return True
    
    # Show installing message
    result = messagebox.askyesno(
        "FFmpeg Necessário",
        "O FFmpeg é necessário para baixar vídeos.\n\n"
        "Deseja instalar automaticamente?\n\n"
        "(~80MB de download)",
        icon='question'
    )
    
    if not result:
        messagebox.showwarning(
            "Aviso",
            "Sem o FFmpeg, alguns vídeos podem não ser baixados corretamente."
        )
        return True  # Continue anyway
    
    # Create progress window
    progress_win = tk.Toplevel(root)
    progress_win.title("Instalando FFmpeg")
    progress_win.geometry("400x100")
    progress_win.resizable(False, False)
    progress_win.transient(root)
    progress_win.grab_set()
    
    # Center window
    progress_win.update_idletasks()
    x = (progress_win.winfo_screenwidth() - 400) // 2
    y = (progress_win.winfo_screenheight() - 100) // 2
    progress_win.geometry(f"+{x}+{y}")
    
    status_label = tk.Label(progress_win, text="Preparando...", font=("Segoe UI", 11))
    status_label.pack(pady=20)
    
    progress_bar = tk.ttk.Progressbar(progress_win, length=350, mode='determinate')
    progress_bar.pack(pady=10)
    
    def update_progress(status: str, percent: float):
        status_label.config(text=status)
        progress_bar['value'] = percent
        progress_win.update()
    
    # Run installation
    import threading
    install_result = [False]
    
    def do_install():
        install_result[0] = ensure_ffmpeg(update_progress)
    
    thread = threading.Thread(target=do_install)
    thread.start()
    
    # Wait for thread
    while thread.is_alive():
        root.update()
        progress_win.update()
    
    progress_win.destroy()
    
    if install_result[0]:
        add_ffmpeg_to_path()
        messagebox.showinfo("Sucesso", "FFmpeg instalado com sucesso!")
    else:
        messagebox.showwarning(
            "Aviso",
            "Não foi possível instalar o FFmpeg automaticamente.\n"
            "Alguns vídeos podem não ser baixados corretamente."
        )
    
    return True


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    root.withdraw()  # Hide main window during setup
    
    # Set app icon if available
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass
    
    # Check dependencies
    check_dependencies(root)
    
    # Show main window
    root.deiconify()
    
    # Create main window
    app = MainWindow(root)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
