# -*- coding: utf-8 -*-
"""
GST Portal Automation Application - Windows Entry Point

This is a Windows-friendly entry point that runs without showing a console window.
Double-click this file to run the GST Automation application on Windows.

Author: Srinidhi B S
Version: 2.0.1 (Windows-compatible)
GitHub: https://github.com/srinidhi-bs/GST_Login
"""

import sys
import os

# Add the current directory to Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the main application
try:
    from main import run_application
    run_application()
except Exception as e:
    # If there's an error, show a simple message box
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        messagebox.showerror(
            "GST Automation Error",
            f"Failed to start the application:\n\n{str(e)}\n\n"
            "Try running 'run-app.bat' instead, which includes dependency setup."
        )
        
        root.destroy()
    except:
        # Last resort - write to a file
        error_file = os.path.join(current_dir, "error.txt")
        with open(error_file, "w") as f:
            f.write(f"GST Automation startup error:\n{str(e)}\n\n")
            f.write("Try running 'run-app.bat' instead.\n")