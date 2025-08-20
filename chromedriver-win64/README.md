# Windows ChromeDriver Setup

This directory should contain the ChromeDriver executable for Windows support.

## 🚀 Easy Setup (Recommended)

**Use the app's auto-update feature:**
1. Run the GST Automation app
2. Click "Update ChromeDriver" button  
3. Wait for automatic download and installation
4. Done! ChromeDriver is ready to use

## Manual Setup (Alternative)

If auto-update doesn't work, you can install manually:

1. **Download ChromeDriver for Windows**:
   - Visit: https://chromedriver.chromium.org/downloads
   - Download the Windows version (chromedriver-win64.zip)
   - Ensure the version matches your installed Chrome browser

2. **Extract and Install**:
   - Extract `chromedriver.exe` from the downloaded ZIP file
   - Place `chromedriver.exe` in this directory (`chromedriver-win64/`)
   - The final path should be: `chromedriver-win64/chromedriver.exe`

3. **Verify Installation**:
   - The GST Automation application will automatically detect and use this ChromeDriver when running on Windows
   - You'll see "Running on Windows - using Windows ChromeDriver" in the status log

## File Structure
```
chromedriver-win64/
├── README.md                (this file)
└── chromedriver.exe         (place downloaded ChromeDriver here)
```

## Troubleshooting

- **ChromeDriver not found**: Try the "Update ChromeDriver" button first! If that fails, ensure `chromedriver.exe` is in this exact directory
- **Version mismatch**: Use "Update ChromeDriver" button for automatic version matching, or manually download ChromeDriver version that matches your Chrome browser
- **Permissions**: ChromeDriver should be executable (Windows usually handles this automatically)

## Cross-Platform Note

- **Linux/WSL**: Uses `chromedriver-linux64/chromedriver` (existing)
- **Windows**: Uses `chromedriver-win64/chromedriver.exe` (this directory)

The application automatically detects your platform and uses the appropriate ChromeDriver.