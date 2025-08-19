#!/usr/bin/env python3
"""
GST Portal Automation Application - Main Entry Point

This is the main entry point for the refactored GST automation application.
It handles application initialization, logging setup, and error handling.

Author: Srinidhi B S
Version: 2.0.0 (Refactored)
GitHub: https://github.com/srinidhi-bs/GST_Login
"""
import sys
import os
import argparse
import traceback
from typing import Optional

# Add the current directory to Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Import application components
    from gui.main_window import create_main_window
    from utils.logging_utils import setup_logging, get_logger
    from config.settings import APP_TITLE, APP_VERSION, AUTHOR_EMAIL, GITHUB_URL
    
except ImportError as e:
    print(f"Error: Failed to import required modules: {e}")
    print("Please ensure all dependencies are installed and the application structure is correct.")
    sys.exit(1)

def parse_command_line_args():
    """
    Parse command line arguments for the application.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="GST Portal Automation Application",
        epilog=f"Author: Srinidhi B S ({AUTHOR_EMAIL}) | GitHub: {GITHUB_URL}"
    )
    
    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (default: logs/gst_automation_YYYYMMDD.log)"
    )
    
    parser.add_argument(
        "--no-file-logging",
        action="store_true",
        help="Disable file logging (console only)"
    )
    
    # Application options
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI for browser)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"GST Automation {APP_VERSION}"
    )
    
    # Development/debug options
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (sets log level to DEBUG and enables additional features)"
    )
    
    return parser.parse_args()

def setup_application_logging(args: argparse.Namespace) -> None:
    """
    Set up application logging based on command line arguments.
    
    Args:
        args (argparse.Namespace): Parsed command line arguments
    """
    # Determine log level
    log_level = "DEBUG" if args.debug else args.log_level
    
    # Set up logging
    setup_logging(
        log_level=log_level,
        log_to_file=not args.no_file_logging,
        log_file_path=args.log_file
    )
    
    # Get logger for this module
    logger = get_logger(__name__)
    
    # Log application startup information
    logger.info(f"=== {APP_TITLE} v{APP_VERSION} Starting ===")
    logger.info(f"Author: Srinidhi B S")
    logger.info(f"Email: {AUTHOR_EMAIL}")
    logger.info(f"GitHub: {GITHUB_URL}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    if args.debug:
        logger.info("Debug mode enabled")
    
    if args.headless:
        logger.info("Headless mode enabled for browser automation")
    
    # Log system information
    try:
        import platform
        logger.info(f"Operating System: {platform.system()} {platform.release()}")
        logger.info(f"Machine: {platform.machine()}")
    except Exception:
        pass  # Not critical

def check_system_requirements() -> tuple[bool, Optional[str]]:
    """
    Check if system meets minimum requirements for the application.
    
    Returns:
        tuple[bool, Optional[str]]: (requirements_met, error_message)
    """
    logger = get_logger(__name__)
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            return False, "Python 3.8 or higher is required"
        
        # Check for required modules
        required_modules = [
            "tkinter", "pandas", "selenium"
        ]
        
        missing_modules = []
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                missing_modules.append(module_name)
        
        if missing_modules:
            return False, f"Missing required modules: {', '.join(missing_modules)}"
        
        # Check for ChromeDriver
        chromedriver_path = os.path.join(current_dir, "chromedriver-linux64", "chromedriver")
        if not os.path.exists(chromedriver_path):
            logger.warning(f"ChromeDriver not found at: {chromedriver_path}")
            logger.warning("Please ensure ChromeDriver is installed in the chromedriver-linux64 directory")
            # This is a warning, not an error, as the user might have ChromeDriver elsewhere
        
        # Check for GST_Downloads directory (create if needed)
        downloads_dir = os.path.join(current_dir, "GST_Downloads")
        if not os.path.exists(downloads_dir):
            try:
                os.makedirs(downloads_dir)
                logger.info(f"Created GST_Downloads directory: {downloads_dir}")
            except Exception as e:
                logger.warning(f"Could not create GST_Downloads directory: {e}")
        
        return True, None
        
    except Exception as e:
        return False, f"Error checking system requirements: {str(e)}"

def handle_application_error(error: Exception, logger: Optional[object] = None) -> None:
    """
    Handle critical application errors with user-friendly messages.
    
    Args:
        error (Exception): The exception that occurred
        logger (Optional[object]): Logger instance for error logging
    """
    error_message = str(error)
    
    if logger:
        logger.critical(f"Critical application error: {error_message}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
    
    # Show user-friendly error dialog if tkinter is available
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        messagebox.showerror(
            "Application Error",
            f"A critical error occurred:\n\n{error_message}\n\n"
            "Please check the log files for more details or contact the developer."
        )
        
        root.destroy()
        
    except Exception:
        # Fallback to console output if GUI is not available
        print(f"\n{'='*50}")
        print("CRITICAL ERROR:")
        print(f"{'='*50}")
        print(error_message)
        print(f"{'='*50}")
        print("Please check the log files for more details.")
        print(f"Contact: {AUTHOR_EMAIL}")

def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    logger = None
    
    try:
        # Parse command line arguments
        args = parse_command_line_args()
        
        # Set up logging
        setup_application_logging(args)
        logger = get_logger(__name__)
        
        # Check system requirements
        requirements_ok, error_message = check_system_requirements()
        if not requirements_ok:
            logger.error(f"System requirements not met: {error_message}")
            handle_application_error(Exception(error_message), logger)
            return 1
        
        # Create and run the main GUI application
        logger.info("Initializing GUI application...")
        
        try:
            main_window = create_main_window()
            
            logger.info("GUI application initialized successfully")
            logger.info("Starting main application loop...")
            
            # Run the application
            main_window.run()
            
            logger.info("Application closed normally")
            return 0
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user (Ctrl+C)")
            return 0
            
        except Exception as e:
            logger.error(f"Error in GUI application: {str(e)}")
            handle_application_error(e, logger)
            return 1
    
    except Exception as e:
        # Handle errors that occur before logging is set up
        if logger:
            handle_application_error(e, logger)
        else:
            handle_application_error(e, None)
        return 1

def run_application():
    """
    Convenience function to run the application with proper exit handling.
    
    This function is useful when the application is imported as a module.
    """
    try:
        exit_code = main()
        sys.exit(exit_code)
    except SystemExit:
        raise  # Re-raise SystemExit
    except Exception as e:
        handle_application_error(e, None)
        sys.exit(1)

if __name__ == "__main__":
    # Direct execution - run the application
    run_application()