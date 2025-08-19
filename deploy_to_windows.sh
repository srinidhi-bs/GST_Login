#!/bin/bash
# GST Login Project - Windows Deployment Script
# This script syncs the WSL project to Windows PY Scripts folder for testing

# Color codes for better output visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Define source and destination paths
SOURCE_DIR="/home/srinidhibs/GST_Login"
DEST_DIR="/mnt/c/Users/srini/OneDrive/Desktop/PY Scripts/GST_Login"

echo -e "${YELLOW}=== GST Login Project - Windows Deployment ===${NC}"
echo "Source: $SOURCE_DIR"
echo "Destination: $DEST_DIR"
echo ""

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo -e "${YELLOW}Creating destination directory...${NC}"
    mkdir -p "$DEST_DIR"
fi

# Sync files (excluding git files, __pycache__, and virtual environment)
echo -e "${YELLOW}Syncing project files...${NC}"
rsync -av --progress \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='gst_env/' \
    --exclude='.vscode/' \
    --exclude='*.log' \
    "$SOURCE_DIR/" "$DEST_DIR/"

# Check if sync was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Open Windows Explorer and navigate to: C:\\Users\\srini\\OneDrive\\Desktop\\PY Scripts\\GST_Login"
    echo "2. Create a Python virtual environment if needed"
    echo "3. Install dependencies from requirements.txt (if present)"
    echo "4. Run your Python application for testing"
    echo ""
    echo -e "${YELLOW}Quick commands for Windows testing:${NC}"
    echo "- Open Command Prompt in the GST_Login folder"
    echo "- Run: python gst_automation_app.pyw"
    echo "- Or double-click the .pyw file to run silently"
else
    echo -e "${RED}✗ Deployment failed!${NC}"
    exit 1
fi