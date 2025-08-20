#!/bin/bash
# WSL to Windows execution script for GST Automation
# This script allows you to run the GST automation app on Windows from WSL
#
# Usage: ./run-on-windows.sh [arguments]
# Example: ./run-on-windows.sh --debug

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GST Automation - WSL to Windows Runner${NC}"
echo "=============================================="

# Get the Windows path of current directory
WINDOWS_PATH="C:\\Development\\GST_Login"
WSL_PATH="/mnt/c/Development/GST_Login"

# Check if we're in the right directory
if [[ "$PWD" != "$WSL_PATH" ]]; then
    echo -e "${RED}❌ Error: Please run this script from $WSL_PATH${NC}"
    echo "Current directory: $PWD"
    exit 1
fi

# Check if Windows Python is available
echo -e "${YELLOW}🔍 Checking for Windows Python...${NC}"
if command -v python.exe &> /dev/null; then
    PYTHON_CMD="python.exe"
    echo -e "${GREEN}✅ Found python.exe${NC}"
elif command -v py.exe &> /dev/null; then
    PYTHON_CMD="py.exe"
    echo -e "${GREEN}✅ Found py.exe${NC}"
else
    echo -e "${RED}❌ Error: Windows Python not found${NC}"
    echo "Please ensure Python is installed on Windows and available in PATH"
    echo "You can download Python from: https://python.org/downloads/"
    echo ""
    echo "After installation, restart WSL and try again."
    exit 1
fi

# Check Python version
echo -e "${YELLOW}🐍 Checking Python version...${NC}"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "Windows Python: $PYTHON_VERSION"

# Check if virtual environment exists on Windows
WINDOWS_VENV_PATH="$WINDOWS_PATH\\gst_env"
WSL_VENV_CHECK="/mnt/c/Development/GST_Login/gst_env"

if [[ ! -d "$WSL_VENV_CHECK" ]]; then
    echo -e "${YELLOW}⚠️  Windows virtual environment not found${NC}"
    echo "Setting up virtual environment on Windows..."
    
    # Create virtual environment on Windows
    echo -e "${BLUE}📦 Creating Windows virtual environment...${NC}"
    cd "$WINDOWS_PATH" 2>/dev/null
    $PYTHON_CMD -m venv gst_env
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Virtual environment created${NC}"
        
        # Install dependencies
        echo -e "${BLUE}📚 Installing dependencies...${NC}"
        "$WINDOWS_PATH\\gst_env\\Scripts\\python.exe" -m pip install selenium pandas
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Dependencies installed${NC}"
        else
            echo -e "${RED}❌ Failed to install dependencies${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Run the application with Windows Python
echo -e "${BLUE}🎯 Running GST Automation on Windows...${NC}"
echo "Arguments: $@"
echo "Working Directory: $WINDOWS_PATH"
echo ""

# Set environment to force Windows execution mode
export GST_FORCE_WINDOWS_MODE=1

# Execute the application using Windows Python in the Windows environment
# Use WSL path for execution since we're running from WSL
cd "$WSL_PATH"
/mnt/c/Development/GST_Login/gst_env/Scripts/python.exe main.py "$@"

# Check exit code
EXIT_CODE=$?
echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Application completed successfully${NC}"
else
    echo -e "${RED}❌ Application exited with code: $EXIT_CODE${NC}"
fi

echo -e "${BLUE}=============================================="
echo -e "🏁 WSL to Windows execution complete${NC}"