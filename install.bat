@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================
echo   YouTube Downloader - Instalador Windows
echo ============================================
echo.

:: Check if running as admin for winget
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Executando sem privilégios de administrador.
    echo         Alguns recursos podem não funcionar.
    echo.
)

:: Check Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo       Python não encontrado. Tentando instalar...
    
    :: Try winget first
    winget --version >nul 2>&1
    if %errorLevel% equ 0 (
        echo       Instalando Python via winget...
        winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
    ) else (
        echo.
        echo [ERRO] Não foi possível instalar o Python automaticamente.
        echo        Por favor, instale manualmente em: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
    echo       Python !PYVER! encontrado ✓
)

:: Check/Install uv
echo.
echo [2/4] Verificando uv (gerenciador de pacotes)...
uv --version >nul 2>&1
if %errorLevel% neq 0 (
    echo       Instalando uv...
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    
    :: Refresh PATH
    set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
) else (
    for /f "tokens=2" %%i in ('uv --version 2^>^&1') do set UVVER=%%i
    echo       uv !UVVER! encontrado ✓
)

:: Install Python dependencies
echo.
echo [3/4] Instalando dependências Python...
cd /d "%~dp0"
uv sync
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar dependências.
    pause
    exit /b 1
)
echo       Dependências instaladas ✓

:: Check/Install FFmpeg
echo.
echo [4/4] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if %errorLevel% neq 0 (
    if exist "bin\ffmpeg.exe" (
        echo       FFmpeg local encontrado ✓
    ) else (
        echo       FFmpeg não encontrado.
        echo.
        set /p INSTALL_FFMPEG="       Deseja instalar o FFmpeg agora? (S/N): "
        if /i "!INSTALL_FFMPEG!"=="S" (
            call :install_ffmpeg
        ) else (
            echo       [AVISO] FFmpeg será instalado na primeira execução do app.
        )
    )
) else (
    echo       FFmpeg encontrado ✓
)

echo.
echo ============================================
echo   Instalação concluída!
echo ============================================
echo.
echo   Para executar o aplicativo, use:
echo   uv run python src/main.py
echo.
echo   Ou execute: run.bat
echo.
pause
exit /b 0

:install_ffmpeg
echo.
echo       Baixando FFmpeg...

:: Create bin directory
if not exist "bin" mkdir bin

:: Download using PowerShell
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'bin\ffmpeg.zip'}"

if not exist "bin\ffmpeg.zip" (
    echo       [ERRO] Falha no download do FFmpeg.
    exit /b 1
)

echo       Extraindo FFmpeg...
powershell -Command "Expand-Archive -Path 'bin\ffmpeg.zip' -DestinationPath 'bin\temp' -Force"

:: Find and move ffmpeg.exe
for /r "bin\temp" %%f in (ffmpeg.exe) do (
    copy "%%f" "bin\ffmpeg.exe" > nul
)
for /r "bin\temp" %%f in (ffprobe.exe) do (
    copy "%%f" "bin\ffprobe.exe" > nul
)

:: Cleanup
rmdir /s /q "bin\temp"
del "bin\ffmpeg.zip"

echo       FFmpeg instalado ✓
exit /b 0
