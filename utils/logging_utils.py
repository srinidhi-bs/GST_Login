"""
Logging utilities for GST Automation Application.

This module provides enhanced logging configuration and utilities
for the GST automation application.

Author: Srinidhi B S
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

from config.settings import LOG_FORMAT, LOG_DATE_FORMAT

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log messages in terminal.
    
    This formatter adds ANSI color codes to log messages based on their level
    for better readability in terminal output.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'  # Reset color
    
    def format(self, record):
        """Format log record with colors if outputting to terminal."""
        # Get the original formatted message
        original_format = super().format(record)
        
        # Add colors if we're outputting to a terminal
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            level_name = record.levelname
            color = self.COLORS.get(level_name, '')
            if color:
                # Color only the level name part
                original_format = original_format.replace(
                    level_name, 
                    f"{color}{level_name}{self.RESET}"
                )
        
        return original_format

def setup_logging(log_level: str = "INFO", 
                 log_to_file: bool = True,
                 log_file_path: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Set up comprehensive logging for the application.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file (bool): Whether to log to file
        log_file_path (Optional[str]): Path to log file, None for default
        max_file_size (int): Maximum size of log file before rotation
        backup_count (int): Number of backup files to keep
        
    Returns:
        logging.Logger: Configured root logger
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set root logger level
    root_logger.setLevel(numeric_level)
    
    # Create console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = ColoredFormatter(LOG_FORMAT, LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if requested
    if log_to_file:
        if log_file_path is None:
            # Create default log file path
            log_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file_path = os.path.join(log_dir, f"gst_automation_{timestamp}.log")
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Log the setup
        root_logger.info(f"Logging initialized - Level: {log_level}, File: {log_file_path}")
    else:
        root_logger.info(f"Logging initialized - Level: {log_level}, Console only")
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

def log_exception(logger: logging.Logger, message: str = "An exception occurred") -> None:
    """
    Log an exception with full traceback.
    
    Args:
        logger (logging.Logger): Logger instance to use
        message (str): Custom message to include with the exception
    """
    logger.exception(message)

def log_function_entry(logger: logging.Logger, function_name: str, *args, **kwargs) -> None:
    """
    Log function entry with parameters (for debugging).
    
    Args:
        logger (logging.Logger): Logger instance to use
        function_name (str): Name of the function being entered
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    if logger.isEnabledFor(logging.DEBUG):
        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        params = ", ".join(filter(None, [args_str, kwargs_str]))
        logger.debug(f"Entering {function_name}({params})")

def log_function_exit(logger: logging.Logger, function_name: str, result=None) -> None:
    """
    Log function exit with return value (for debugging).
    
    Args:
        logger (logging.Logger): Logger instance to use
        function_name (str): Name of the function being exited
        result: Return value of the function
    """
    if logger.isEnabledFor(logging.DEBUG):
        if result is not None:
            logger.debug(f"Exiting {function_name} -> {result}")
        else:
            logger.debug(f"Exiting {function_name}")

def log_timing(logger: logging.Logger, message: str, start_time: float, end_time: float) -> None:
    """
    Log timing information for operations.
    
    Args:
        logger (logging.Logger): Logger instance to use
        message (str): Description of the operation
        start_time (float): Start time (from time.time())
        end_time (float): End time (from time.time())
    """
    duration = end_time - start_time
    logger.info(f"{message} completed in {duration:.2f} seconds")

class ContextLogger:
    """
    Context manager that logs entry and exit of code blocks.
    
    This is useful for logging the execution of specific operations
    or methods with automatic timing.
    """
    
    def __init__(self, logger: logging.Logger, operation_name: str, log_level: int = logging.INFO):
        """
        Initialize the context logger.
        
        Args:
            logger (logging.Logger): Logger instance to use
            operation_name (str): Name of the operation being logged
            log_level (int): Log level to use for messages
        """
        self.logger = logger
        self.operation_name = operation_name
        self.log_level = log_level
        self.start_time = None
    
    def __enter__(self):
        """Enter the context and log the start."""
        import time
        self.start_time = time.time()
        self.logger.log(self.log_level, f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and log the completion or error."""
        import time
        end_time = time.time()
        
        if exc_type is None:
            # Successful completion
            duration = end_time - self.start_time
            self.logger.log(self.log_level, f"Completed {self.operation_name} in {duration:.2f} seconds")
        else:
            # Exception occurred
            self.logger.error(f"Failed {self.operation_name}: {exc_val}")

def create_module_logger(module_name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Create a logger for a specific module with optional level override.
    
    Args:
        module_name (str): Name of the module (usually __name__)
        level (Optional[str]): Override log level for this logger
        
    Returns:
        logging.Logger: Configured logger for the module
    """
    logger = logging.getLogger(module_name)
    
    if level:
        numeric_level = getattr(logging, level.upper(), None)
        if isinstance(numeric_level, int):
            logger.setLevel(numeric_level)
    
    return logger

class LogCapture:
    """
    Utility class for capturing log messages during testing or debugging.
    
    This can be used as a context manager to capture log messages
    for analysis or testing purposes.
    """
    
    def __init__(self, logger_name: str = "", level: int = logging.DEBUG):
        """
        Initialize log capture.
        
        Args:
            logger_name (str): Name of logger to capture (empty for root)
            level (int): Minimum level to capture
        """
        self.logger_name = logger_name
        self.level = level
        self.handler = None
        self.records = []
    
    def __enter__(self):
        """Start capturing log messages."""
        class ListHandler(logging.Handler):
            def __init__(self, records_list):
                super().__init__()
                self.records = records_list
            
            def emit(self, record):
                self.records.append(record)
        
        self.handler = ListHandler(self.records)
        self.handler.setLevel(self.level)
        
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(self.handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing log messages."""
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
    
    def get_messages(self, level: Optional[int] = None) -> list:
        """
        Get captured log messages.
        
        Args:
            level (Optional[int]): Filter by minimum level
            
        Returns:
            list: List of log message strings
        """
        if level is None:
            return [record.getMessage() for record in self.records]
        else:
            return [record.getMessage() for record in self.records if record.levelno >= level]
    
    def get_records(self, level: Optional[int] = None) -> list:
        """
        Get captured log records.
        
        Args:
            level (Optional[int]): Filter by minimum level
            
        Returns:
            list: List of LogRecord objects
        """
        if level is None:
            return self.records[:]
        else:
            return [record for record in self.records if record.levelno >= level]
    
    def clear(self) -> None:
        """Clear captured messages."""
        self.records.clear()

# Convenience functions for common logging tasks
def debug(message: str, logger_name: str = "") -> None:
    """Log a debug message."""
    logging.getLogger(logger_name).debug(message)

def info(message: str, logger_name: str = "") -> None:
    """Log an info message."""
    logging.getLogger(logger_name).info(message)

def warning(message: str, logger_name: str = "") -> None:
    """Log a warning message."""
    logging.getLogger(logger_name).warning(message)

def error(message: str, logger_name: str = "") -> None:
    """Log an error message."""
    logging.getLogger(logger_name).error(message)

def critical(message: str, logger_name: str = "") -> None:
    """Log a critical message."""
    logging.getLogger(logger_name).critical(message)