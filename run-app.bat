@echo off
REM Windows batch file for GST Automation
REM Double-click this file to run the GST Automation application on Windows
REM
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
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Trying py command...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python from https://python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
        echo [SUCCESS] Found Python using 'py' command
    )
) else (
    set PYTHON_CMD=python
    echo [SUCCESS] Found Python using 'python' command
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
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
    
    echo [INFO] Installing dependencies...
    gst_env\Scripts\python.exe -m pip install --upgrade pip
    gst_env\Scripts\python.exe -m pip install selenium pandas
    
    if %errorlevel% neq 0 (
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
    echo Please download ChromeDriver for Windows and place it in:
    echo chromedriver-win64\chromedriver.exe
    echo.
    echo Download from: https://chromedriver.chromium.org/downloads
    echo Make sure the version matches your Chrome browser.
    echo.
    echo Press any key to continue anyway (you'll get an error during execution)...
    pause
)

REM Run the application
echo.
echo [INFO] Starting GST Automation Application...
echo Working Directory: %CD%
echo.

gst_env\Scripts\python.exe main.py %*

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Application completed successfully!
) else (
    echo.
    echo [ERROR] Application exited with error code: %errorlevel%
)

echo.
echo ========================================
echo    Application Finished
echo ========================================
echo.
echo Press any key to close this window...
pause >nul