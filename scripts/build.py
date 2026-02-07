"""
Build script for creating standalone executables.

This script uses PyInstaller to create a standalone executable
for the YouTube Downloader application.
"""

import os
import platform
import subprocess
import sys


def get_project_root() -> str:
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_executable():
    """Build the executable using PyInstaller."""
    project_root = get_project_root()
    src_dir = os.path.join(project_root, "src")
    main_script = os.path.join(src_dir, "main.py")
    dist_dir = os.path.join(project_root, "dist")
    
    # Determine the executable name based on OS
    system = platform.system()
    exe_name = "YTDownloader" if system == "Windows" else "yt-downloader"
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={exe_name}",
        f"--distpath={dist_dir}",
        "--clean",
        "--noconfirm",
        # Add hidden imports for yt-dlp
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--hidden-import=yt_dlp.postprocessor",
        # Collect all yt-dlp data
        "--collect-all=yt_dlp",
        main_script
    ]
    
    # Add icon on Windows if available
    icon_path = os.path.join(src_dir, "assets", "icon.ico")
    if system == "Windows" and os.path.exists(icon_path):
        cmd.insert(-1, f"--icon={icon_path}")
    
    print(f"Building {exe_name} for {system}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, cwd=project_root)
        
        # Success message
        exe_ext = ".exe" if system == "Windows" else ""
        exe_path = os.path.join(dist_dir, f"{exe_name}{exe_ext}")
        print(f"\n✅ Build successful!")
        print(f"📁 Executable: {exe_path}")
        
        return exe_path
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return None


def create_windows_shortcut(exe_path: str):
    """Create a Windows shortcut on the Desktop."""
    if platform.system() != "Windows":
        return
    
    try:
        import winreg
        
        # Get Desktop path
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
        winreg.CloseKey(key)
        
        shortcut_path = os.path.join(desktop_path, "YouTube Downloader.lnk")
        
        # Create shortcut using PowerShell
        ps_script = f'''
        $WScriptShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{exe_path}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
        $Shortcut.Description = "YouTube Downloader"
        $Shortcut.Save()
        '''
        
        subprocess.run(
            ["powershell", "-Command", ps_script],
            check=True,
            capture_output=True
        )
        
        print(f"🔗 Shortcut created: {shortcut_path}")
        
    except Exception as e:
        print(f"⚠️ Could not create shortcut: {e}")


def main():
    """Main entry point for the build script."""
    print("=" * 50)
    print("YouTube Downloader - Build Script")
    print("=" * 50)
    
    exe_path = build_executable()
    
    if exe_path and platform.system() == "Windows":
        print("\nCreating Windows shortcut...")
        create_windows_shortcut(exe_path)
    
    print("\n" + "=" * 50)
    print("Build process complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
