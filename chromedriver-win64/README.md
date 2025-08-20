# Windows ChromeDriver Setup

This directory should contain the ChromeDriver executable for Windows support.

## Setup Instructions

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

- **ChromeDriver not found**: Ensure `chromedriver.exe` is in this exact directory
- **Version mismatch**: Download ChromeDriver version that matches your Chrome browser
- **Permissions**: ChromeDriver should be executable (Windows usually handles this automatically)

## Cross-Platform Note

- **Linux/WSL**: Uses `chromedriver-linux64/chromedriver` (existing)
- **Windows**: Uses `chromedriver-win64/chromedriver.exe` (this directory)

The application automatically detects your platform and uses the appropriate ChromeDriver.