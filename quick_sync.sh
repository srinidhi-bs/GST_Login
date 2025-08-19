#!/bin/bash
# Quick sync script for rapid testing
# This is a lightweight version for frequent updates during development

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SOURCE_DIR="/home/srinidhibs/GST_Login"
DEST_DIR="/mnt/c/Users/srini/OneDrive/Desktop/PY Scripts/GST_Login"

echo -e "${YELLOW}Quick sync to Windows...${NC}"

# Sync only essential files (faster for testing iterations)
rsync -av --progress \
    --include='*.py' \
    --include='*.pyw' \
    --include='*.xlsx' \
    --include='*.csv' \
    --include='*.txt' \
    --include='*.bat' \
    --include='*.ps1' \
    --exclude='*' \
    "$SOURCE_DIR/" "$DEST_DIR/"

echo -e "${GREEN}✓ Quick sync complete!${NC}"
echo "Ready for testing in Windows!"