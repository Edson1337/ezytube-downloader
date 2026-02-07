#!/bin/bash

# YouTube Downloader - Installer for Linux/macOS

set -e

echo "============================================"
echo "  YouTube Downloader - Instalador"
echo "============================================"
echo

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="Linux";;
    Darwin*)    PLATFORM="macOS";;
    *)          PLATFORM="Unknown";;
esac

echo "Sistema detectado: $PLATFORM"
echo

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# [1/4] Check Python
echo "[1/4] Verificando Python..."
if command_exists python3; then
    PYVER=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "      Python $PYVER encontrado ✓"
else
    echo "      Python não encontrado. Instalando..."
    
    if [ "$PLATFORM" = "Linux" ]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-tk
        elif command_exists dnf; then
            sudo dnf install -y python3 python3-pip python3-tkinter
        elif command_exists pacman; then
            sudo pacman -S --noconfirm python python-pip tk
        else
            echo "[ERRO] Gerenciador de pacotes não suportado."
            echo "       Instale o Python 3 manualmente."
            exit 1
        fi
    elif [ "$PLATFORM" = "macOS" ]; then
        if command_exists brew; then
            brew install python3 python-tk
        else
            echo "[ERRO] Homebrew não encontrado."
            echo "       Instale em: https://brew.sh"
            exit 1
        fi
    fi
fi

# [2/4] Check/Install uv
echo
echo "[2/4] Verificando uv (gerenciador de pacotes)..."
if command_exists uv; then
    UVVER=$(uv --version 2>&1 | cut -d' ' -f2)
    echo "      uv $UVVER encontrado ✓"
else
    echo "      Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# [3/4] Install Python dependencies
echo
echo "[3/4] Instalando dependências Python..."
cd "$(dirname "$0")"
uv sync
echo "      Dependências instaladas ✓"

# [4/4] Check/Install FFmpeg
echo
echo "[4/4] Verificando FFmpeg..."
if command_exists ffmpeg; then
    FFVER=$(ffmpeg -version 2>&1 | head -n1 | cut -d' ' -f3)
    echo "      FFmpeg $FFVER encontrado ✓"
else
    echo "      FFmpeg não encontrado."
    read -p "      Deseja instalar o FFmpeg agora? (s/n): " INSTALL_FFMPEG
    
    if [ "$INSTALL_FFMPEG" = "s" ] || [ "$INSTALL_FFMPEG" = "S" ]; then
        if [ "$PLATFORM" = "Linux" ]; then
            if command_exists apt-get; then
                sudo apt-get install -y ffmpeg
            elif command_exists dnf; then
                sudo dnf install -y ffmpeg
            elif command_exists pacman; then
                sudo pacman -S --noconfirm ffmpeg
            fi
        elif [ "$PLATFORM" = "macOS" ]; then
            if command_exists brew; then
                brew install ffmpeg
            fi
        fi
        echo "      FFmpeg instalado ✓"
    else
        echo "      [AVISO] FFmpeg será solicitado na primeira execução."
    fi
fi

echo
echo "============================================"
echo "  Instalação concluída!"
echo "============================================"
echo
echo "  Para executar o aplicativo, use:"
echo "  uv run python src/main.py"
echo
echo "  Ou execute: ./run.sh"
echo
