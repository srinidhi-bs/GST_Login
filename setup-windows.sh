#!/bin/bash
# One-time Windows setup script for GST Automation
# This script sets up the Windows environment from WSL
#
# Usage: ./setup-windows.sh

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛠️  GST Automation - Windows Setup${NC}"
echo "=========================================="
echo "This script will set up the Windows environment for GST Automation"
echo ""

# Get paths
WINDOWS_PATH="C:\\Development\\GST_Login"
WSL_PATH="/mnt/c/Development/GST_Login"

# Check if we're in the right directory
if [[ "$PWD" != "$WSL_PATH" ]]; then
    echo -e "${RED}❌ Error: Please run this script from $WSL_PATH${NC}"
    echo "Current directory: $PWD"
    exit 1
fi

# Step 1: Check Windows Python
echo -e "${YELLOW}Step 1: Checking Windows Python installation...${NC}"
if command -v python.exe &> /dev/null; then
    PYTHON_CMD="python.exe"
    echo -e "${GREEN}✅ Found python.exe${NC}"
elif command -v py.exe &> /dev/null; then
    PYTHON_CMD="py.exe"
    echo -e "${GREEN}✅ Found py.exe${NC}"
else
    echo -e "${RED}❌ Windows Python not found${NC}"
    echo ""
    echo "Please install Python on Windows:"
    echo "1. Go to: https://python.org/downloads/"
    echo "2. Download the latest Python for Windows"
    echo "3. During installation, check 'Add Python to PATH'"
    echo "4. Restart WSL and run this script again"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "Windows Python version: $PYTHON_VERSION"

# Step 2: Create virtual environment
echo -e "\n${YELLOW}Step 2: Setting up virtual environment...${NC}"
WINDOWS_VENV_PATH="$WINDOWS_PATH\\gst_env"
WSL_VENV_CHECK="/mnt/c/Development/GST_Login/gst_env"

if [[ -d "$WSL_VENV_CHECK" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf "$WSL_VENV_CHECK"
    else
        echo "Skipping virtual environment creation"
        echo -e "${GREEN}✅ Using existing virtual environment${NC}"
    fi
fi

if [[ ! -d "$WSL_VENV_CHECK" ]]; then
    echo "Creating Windows virtual environment..."
    cd "$WINDOWS_PATH" 2>/dev/null || {
        echo -e "${RED}❌ Failed to access Windows directory${NC}"
        exit 1
    }
    
    $PYTHON_CMD -m venv gst_env
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Step 3: Install dependencies
echo -e "\n${YELLOW}Step 3: Installing Python dependencies...${NC}"
cd "$WINDOWS_PATH" 2>/dev/null
"$WINDOWS_PATH\\gst_env\\Scripts\\python.exe" -m pip install --upgrade pip
"$WINDOWS_PATH\\gst_env\\Scripts\\python.exe" -m pip install selenium pandas

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Step 4: ChromeDriver check
echo -e "\n${YELLOW}Step 4: Checking ChromeDriver...${NC}"
CHROMEDRIVER_PATH="/mnt/c/Development/GST_Login/chromedriver-win64/chromedriver.exe"

if [[ -f "$CHROMEDRIVER_PATH" ]]; then
    echo -e "${GREEN}✅ ChromeDriver found${NC}"
else
    echo -e "${YELLOW}⚠️  ChromeDriver not found${NC}"
    echo ""
    echo "To complete setup, you need to download ChromeDriver:"
    echo "1. Go to: https://chromedriver.chromium.org/downloads"
    echo "2. Download the Windows version (chromedriver-win64.zip)"
    echo "3. Extract chromedriver.exe to: chromedriver-win64/"
    echo "4. Make sure the version matches your Chrome browser"
    echo ""
    echo "The application will show an error if ChromeDriver is missing."
fi

# Step 5: Test installation
echo -e "\n${YELLOW}Step 5: Testing installation...${NC}"
cd "$WINDOWS_PATH" 2>/dev/null
TEST_OUTPUT=$("$WINDOWS_PATH\\gst_env\\Scripts\\python.exe" -c "import sys; print('Python:', sys.version); import selenium; import pandas; print('Dependencies: OK')" 2>&1)

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Installation test passed${NC}"
    echo "$TEST_OUTPUT"
else
    echo -e "${RED}❌ Installation test failed${NC}"
    echo "$TEST_OUTPUT"
    exit 1
fi

# Final summary
echo -e "\n${BLUE}=========================================="
echo -e "🎉 Windows Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Your GST Automation is now ready to run on Windows!"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. From WSL: Run './run-on-windows.sh' to test on Windows"
echo "2. From Windows: Double-click 'run-app.bat' to run natively"
echo "3. Don't forget to download ChromeDriver if you haven't already"
echo ""
echo -e "${BLUE}Happy automating! 🚀${NC}"