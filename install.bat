@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================
echo   YouTube Downloader - Instalador Windows
echo ============================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Executando sem privilegios de administrador.
    echo         Alguns recursos podem nao funcionar.
    echo.
)

:: ============================================
:: Check Python
:: ============================================
echo [1/4] Verificando Python...
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo       Python nao encontrado. Tentando instalar...
    
    :: Try winget first
    where winget >nul 2>&1
    if !errorLevel! equ 0 (
        echo       Instalando Python via winget...
        winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
        if !errorLevel! neq 0 (
            goto :install_python_manual
        )
        echo       Python instalado via winget!
        echo       [IMPORTANTE] Feche e abra novamente este terminal para continuar.
        pause
        exit /b 0
    ) else (
        goto :install_python_manual
    )
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
    echo       Python !PYVER! encontrado ✓
)

:: ============================================
:: Check/Install uv
:: ============================================
echo.
echo [2/4] Verificando uv (gerenciador de pacotes)...
where uv >nul 2>&1
if %errorLevel% neq 0 (
    echo       Instalando uv...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    if !errorLevel! neq 0 (
        echo       [ERRO] Falha ao instalar uv.
        echo       Tente instalar manualmente: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
    
    echo.
    echo       uv instalado com sucesso!
    echo       [IMPORTANTE] Feche e abra novamente este terminal,
    echo                    depois execute install.bat novamente.
    pause
    exit /b 0
) else (
    for /f "tokens=2" %%i in ('uv --version 2^>^&1') do set UVVER=%%i
    echo       uv !UVVER! encontrado ✓
)

:: ============================================
:: Install Python dependencies
:: ============================================
echo.
echo [3/4] Instalando dependencias Python...
cd /d "%~dp0"
uv sync
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias.
    echo        Verifique sua conexao com a internet.
    pause
    exit /b 1
)
echo       Dependencias instaladas ✓

:: ============================================
:: Check/Install FFmpeg
:: ============================================
echo.
echo [4/4] Verificando FFmpeg...
where ffmpeg >nul 2>&1
if %errorLevel% neq 0 (
    if exist "bin\ffmpeg.exe" (
        echo       FFmpeg local encontrado ✓
    ) else (
        echo       FFmpeg nao encontrado.
        echo.
        set /p INSTALL_FFMPEG="       Deseja instalar o FFmpeg agora? (S/N): "
        if /i "!INSTALL_FFMPEG!"=="S" (
            call :install_ffmpeg
        ) else (
            echo       [AVISO] FFmpeg sera instalado na primeira execucao do app.
        )
    )
) else (
    echo       FFmpeg encontrado ✓
)

echo.
echo ============================================
echo   Instalacao concluida!
echo ============================================
echo.
echo   Para executar o aplicativo, use:
echo   run.bat
echo.
pause
exit /b 0

:: ============================================
:: Function: Install Python manually
:: ============================================
:install_python_manual
echo.
echo       Winget nao disponivel. Baixando Python diretamente...
echo.

:: Download Python installer
set PYTHON_URL=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python_installer.exe

echo       Baixando Python 3.12...
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

if not exist "%PYTHON_INSTALLER%" (
    echo.
    echo       [ERRO] Falha no download do Python.
    echo       Por favor, instale manualmente em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo       Instalando Python (isso pode demorar)...
echo       [IMPORTANTE] Marque a opcao "Add Python to PATH" se aparecer!
"%PYTHON_INSTALLER%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0

if !errorLevel! neq 0 (
    echo       [ERRO] Falha na instalacao do Python.
    del "%PYTHON_INSTALLER%" 2>nul
    pause
    exit /b 1
)

del "%PYTHON_INSTALLER%" 2>nul

echo.
echo       Python instalado com sucesso!
echo       [IMPORTANTE] Feche e abra novamente este terminal,
echo                    depois execute install.bat novamente.
pause
exit /b 0

:: ============================================
:: Function: Install FFmpeg
:: ============================================
:install_ffmpeg
echo.
echo       Baixando FFmpeg...

:: Create bin directory
if not exist "bin" mkdir bin

:: Download using PowerShell
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'bin\ffmpeg.zip'}"

if not exist "bin\ffmpeg.zip" (
    echo       [ERRO] Falha no download do FFmpeg.
    echo       Verifique sua conexao com a internet.
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
