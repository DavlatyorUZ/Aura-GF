@echo off
REM Run script for the Jarvis Desktop App on Windows
REM Usage: run_desktop_app.bat [--voice-debug]

REM Parse arguments
set "VOICE_DEBUG=0"
:parse_args
if "%~1"=="" goto done_args
if "%~1"=="--voice-debug" (
    set "VOICE_DEBUG=1"
    shift
    goto parse_args
)
shift
goto parse_args
:done_args

echo Testing Jarvis Desktop App locally...
if "%VOICE_DEBUG%"=="1" (
    echo    Voice debug: ENABLED
)
echo.

REM Navigate to project root
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"
set "PYTHONPATH=%PROJECT_ROOT%\src;%PYTHONPATH%"

REM Resolve Python environment (venv, .venv, or .mamba_env)
set "PYTHON_EXE="
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%PROJECT_ROOT%\.mamba_env\python.exe" set "PYTHON_EXE=%PROJECT_ROOT%\.mamba_env\python.exe"
if not defined PYTHON_EXE call :resolve_mamba_from_worktree

REM Check if environment exists
if not defined PYTHON_EXE (
    echo ERROR: Python environment not found.
    echo    Looked in: %PROJECT_ROOT%\venv, %PROJECT_ROOT%\.venv, %PROJECT_ROOT%\.mamba_env
    pause
    exit /b 1
)

REM Check Python version
echo Checking Python version...
"%PYTHON_EXE%" --version
echo.

REM Generate icons
echo Generating icons...
"%PYTHON_EXE%" src\desktop_app\desktop_assets\generate_icons.py
echo.

REM Run the desktop app
echo Starting desktop app...
echo    Click the system tray icon to open menu
echo    Select 'Start Listening' from menu to begin
echo    Or press Ctrl+C to quit
echo.

REM Set voice debug environment variable if requested
if "%VOICE_DEBUG%"=="1" (
    set "JARVIS_VOICE_DEBUG=1"
)

"%PYTHON_EXE%" -m desktop_app
goto :eof

:resolve_mamba_from_worktree
for /f "usebackq delims=" %%G in (`git -C "%PROJECT_ROOT%" rev-parse --git-common-dir 2^>nul`) do set "GIT_COMMON_DIR=%%G"
if not defined GIT_COMMON_DIR goto :eof
for %%I in ("%GIT_COMMON_DIR%\..") do set "MAIN_REPO=%%~fI"
if exist "%MAIN_REPO%\venv\Scripts\python.exe" set "PYTHON_EXE=%MAIN_REPO%\venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%MAIN_REPO%\.mamba_env\python.exe" set "PYTHON_EXE=%MAIN_REPO%\.mamba_env\python.exe"
goto :eof
