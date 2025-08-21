@echo off
REM Simple Windows batch file for GST Automation
REM Author: Srinidhi B S

echo.
echo ========================================
echo    GST Automation - Windows Runner
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is installed
echo [INFO] Checking for Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Trying py command...
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python from https://python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
        echo [SUCCESS] Found Python using py command
    )
) else (
    set PYTHON_CMD=python
    echo [SUCCESS] Found Python using python command
)

REM Display Python version
echo.
echo [INFO] Python version:
%PYTHON_CMD% --version

REM Check if virtual environment exists
if not exist "gst_env\" (
    echo.
    echo [INFO] Virtual environment not found. Creating one...
    %PYTHON_CMD% -m venv gst_env
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
    
    echo [INFO] Installing dependencies...
    gst_env\Scripts\python.exe -m pip install --upgrade pip
    gst_env\Scripts\python.exe -m pip install selenium pandas
    
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
)

REM Check if ChromeDriver exists
if not exist "chromedriver-win64\chromedriver.exe" (
    echo.
    echo [WARNING] ChromeDriver not found!
    echo Please use the Update ChromeDriver button in the app
    echo or download manually from: https://chromedriver.chromium.org/downloads
    echo.
)

REM Run the application
echo.
echo [INFO] Starting GST Automation Application...
echo Working Directory: %CD%
echo.

if "%1"=="" (
    gst_env\Scripts\python.exe main.py
) else (
    gst_env\Scripts\python.exe main.py %1 %2 %3 %4 %5
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with error code: %errorlevel%
) else (
    echo.
    echo [SUCCESS] Application completed successfully!
)

echo.
echo ========================================
echo    Application Finished
echo ========================================
echo.
echo Press any key to close this window...
pause >nul