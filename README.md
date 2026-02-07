# YouTube Downloader

A modern desktop application for downloading YouTube videos in high quality.

## Features

- **Simple Interface**: Clean, dark-themed UI for easy video downloads
- **High Quality**: Downloads best available video and audio quality
- **Download History**: Track downloaded videos organized by folder
- **Auto FFmpeg Install**: Automatically installs FFmpeg if not present
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Requirements

- Python 3.10 or higher
- FFmpeg (auto-installed if missing)

## Installation

### Windows

1. Double-click `install.bat`
2. Follow the on-screen instructions

Or manually:
```batch
powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
uv sync
```

### Linux / macOS

```bash
chmod +x install.sh
./install.sh
```

Or manually:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

## Usage

### Windows
```batch
run.bat
```
Or:
```batch
uv run python src/main.py
```

### Linux / macOS
```bash
./run.sh
```
Or:
```bash
uv run python src/main.py
```

## How to Download Videos

1. Copy the YouTube video URL
2. Paste it in the "Video URL" field
3. Choose a destination folder (or use the default)
4. Click "Download Video"
5. Wait for the download to complete

## Project Structure

```
yt-vids-download/
├── src/
│   ├── core/
│   │   ├── downloader.py      # YouTube download logic using yt-dlp
│   │   ├── file_utils.py      # File and folder utilities
│   │   ├── settings.py        # User preferences and history
│   │   └── dependencies.py    # FFmpeg auto-installer
│   ├── ui/
│   │   ├── main_window.py     # Main application window
│   │   ├── history_panel.py   # Download history sidebar
│   │   ├── widgets.py         # Reusable styled widgets
│   │   └── styles.py          # Theme and styling constants
│   └── main.py                # Application entry point
├── data/                      # Settings and history (auto-created)
├── bin/                       # FFmpeg binaries (auto-created)
├── install.bat                # Windows installer
├── install.sh                 # Linux/macOS installer
├── run.bat                    # Windows launcher
├── run.sh                     # Linux/macOS launcher
└── pyproject.toml             # Project dependencies
```

## Configuration

Settings are stored in `data/settings.json`:
- `download_dir`: Default download directory

Download history is stored in `data/history.json`.

## Dependencies

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video download engine
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing

## Troubleshooting

### FFmpeg not found
The application will automatically download FFmpeg on first run. If this fails:
- **Windows**: Download from https://ffmpeg.org/download.html and place in the `bin/` folder
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

### Download fails
- Check if the video is available in your region
- Try updating yt-dlp: `uv pip install --upgrade yt-dlp`

## License

MIT License
