# GST Automation - Streamlined Development Workflow

## 🚀 **Overview**

This document describes the streamlined development workflow for the GST Automation project, designed to make it easy to develop in WSL while running and testing on Windows.

## 📁 **Project Location**

The project is now located in a **shared directory** accessible from both WSL and Windows:
- **WSL Path**: `/mnt/c/Development/GST_Login/`
- **Windows Path**: `C:\Development\GST_Login\`

This single location eliminates the need for copying or syncing files between environments.

## 🛠️ **Development Workflow**

### **Primary Development (WSL)**
```bash
# Navigate to project
cd /mnt/c/Development/GST_Login

# Make your code changes using your favorite tools
code .        # VS Code
vim main.py   # Vim
nano config/settings.py  # Nano

# Git operations (as usual)
git add .
git commit -m "Your changes"
git push
```

### **Testing on Windows (from WSL)**
```bash
# One-time setup (only needed once)
./setup-windows.sh

# Test on Windows instantly
./run-on-windows.sh

# Test with debug mode
./run-on-windows.sh --debug

# Test with other options
./run-on-windows.sh --headless
```

### **Running Natively on Windows**
For Windows users or when you want to run directly on Windows:
1. Navigate to `C:\Development\GST_Login\` in Windows
2. Double-click `run-app.bat`

## 📋 **Setup Scripts**

### **1. `setup-windows.sh` - One-Time Setup**
- **Purpose**: Sets up the Windows environment from WSL
- **Usage**: `./setup-windows.sh`
- **What it does**:
  - Checks for Windows Python installation
  - Creates Windows virtual environment
  - Installs Python dependencies
  - Validates ChromeDriver setup
  - Tests the installation

### **2. `run-on-windows.sh` - WSL to Windows Runner**
- **Purpose**: Run the app on Windows from WSL
- **Usage**: `./run-on-windows.sh [arguments]`
- **What it does**:
  - Detects Windows Python
  - Sets up environment variables for Windows mode
  - Executes the app using Windows Python
  - Provides colored, informative output

### **3. `run-app.bat` - Windows Native Runner**
- **Purpose**: Easy double-click execution for Windows users
- **Usage**: Double-click the file in Windows Explorer
- **What it does**:
  - Checks Python installation
  - Creates virtual environment if needed
  - Installs dependencies automatically
  - Runs the application
  - Provides user-friendly error messages

## 🔧 **Platform Detection**

The application automatically detects the execution environment:

### **Normal WSL Execution**
```bash
python3 main.py
# Shows: "Running on WSL - using WSL ChromeDriver"
```

### **Windows Mode (via WSL)**
```bash
./run-on-windows.sh
# Shows: "Running on Windows (via WSL) - using Windows ChromeDriver"
```

### **Native Windows Execution**
```cmd
run-app.bat
# Shows: "Running on Windows - using Windows ChromeDriver"
```

## 📂 **Directory Structure**
```
/mnt/c/Development/GST_Login/  (accessible as C:\Development\GST_Login\ from Windows)
├── main.py                    # Main application
├── config/                    # Configuration
├── gui/                       # GUI components
├── services/                  # Automation services
├── utils/                     # Utilities
├── models/                    # Data models
├── chromedriver-linux64/      # Linux ChromeDriver
├── chromedriver-win64/        # Windows ChromeDriver (you need to add this)
├── gst_env/                   # Python virtual environment (auto-created)
├── run-on-windows.sh         # WSL → Windows runner
├── run-app.bat               # Windows native runner
├── setup-windows.sh          # One-time Windows setup
└── DEVELOPMENT_WORKFLOW.md   # This file
```

## 🐛 **Troubleshooting**

### **Windows Python Not Found**
```bash
# Error: Windows Python not found
# Solution: Install Python on Windows from python.org
# Make sure to check "Add Python to PATH" during installation
```

### **ChromeDriver Missing**
```bash
# Error: ChromeDriver not found for Windows
# Solution: Download ChromeDriver for Windows
# 1. Go to: https://chromedriver.chromium.org/downloads
# 2. Download chromedriver-win64.zip
# 3. Extract chromedriver.exe to chromedriver-win64/
```

### **Virtual Environment Issues**
```bash
# If you get virtual environment errors, recreate it:
rm -rf gst_env
./setup-windows.sh
```

### **Permission Issues**
- Ensure you're running WSL as the same user who owns the Windows files
- Make sure Windows Defender isn't blocking ChromeDriver
- Try running Windows Command Prompt as Administrator

## 🎯 **Benefits**

### ✅ **For Developers**
- **Single Codebase**: No more copying or syncing files
- **WSL Comfort**: Keep using your familiar WSL development environment
- **Instant Testing**: Test on Windows with one command
- **Git Simplicity**: All git operations from WSL as usual

### ✅ **For Users**
- **Easy Setup**: One-time setup script handles everything
- **Multiple Options**: WSL→Windows or native Windows execution
- **User-Friendly**: Double-click batch file for Windows users
- **Automatic Environment**: Virtual environment and dependencies handled automatically

## 🔄 **Migration from Old Setup**

If you were using the old `/home/srinidhibs/GST_Login` location:

1. **The project has been moved** to `/mnt/c/Development/GST_Login/`
2. **Update your bookmarks** to the new location
3. **Git operations** continue to work the same way
4. **Use the new scripts** for Windows testing

## 📝 **Quick Reference**

| Task | Command | Location |
|------|---------|----------|
| Setup Windows (once) | `./setup-windows.sh` | WSL |
| Test on Windows | `./run-on-windows.sh` | WSL |
| Run on Windows | Double-click `run-app.bat` | Windows |
| Develop | `code .` or `vim main.py` | WSL |
| Git operations | `git add/commit/push` | WSL |
| Debug mode | `./run-on-windows.sh --debug` | WSL |

---

**Happy coding! 🚀** The streamlined workflow makes cross-platform development effortless while maintaining the power and flexibility you need.