"""
Status logger GUI component for GST Automation Application.

This module provides a reusable status logging widget that displays
automation progress and messages to the user.

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional
import datetime

class StatusLogger:
    """
    GUI component for displaying status messages and automation progress.
    
    This component provides a text widget with auto-scrolling capability
    for displaying status messages during automation runs.
    """
    
    def __init__(self, parent: tk.Widget, height: int = 8):
        """
        Initialize the status logger component.
        
        Args:
            parent (tk.Widget): Parent widget to contain this component
            height (int): Height of the text widget in lines (default: 8)
        """
        self.parent = parent
        
        # Create frame to contain the status logger
        self.frame = ttk.LabelFrame(parent, text="Status")
        
        # Create text widget for status messages
        # State is disabled to prevent user editing
        self.text_widget = tk.Text(
            self.frame, 
            height=height, 
            wrap="word", 
            state="disabled",
            font=("Consolas", 9)  # Monospace font for better formatting
        )
        
        # Add scrollbar for long status logs
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack text widget and scrollbar
        self.text_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configuration options
        self.show_timestamps = True
        self.max_lines = 1000  # Limit to prevent memory issues with long runs
        self.line_count = 0
    
    def pack(self, **kwargs) -> None:
        """Pack the status logger frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the status logger frame."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the status logger frame."""
        self.frame.place(**kwargs)
    
    def log_message(self, message: str, level: str = "INFO") -> None:
        """
        Add a status message to the log display.
        
        Args:
            message (str): The message to log
            level (str): Message level (INFO, WARNING, ERROR) for potential formatting
        """
        # Format message with timestamp if enabled
        if self.show_timestamps:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
        else:
            formatted_message = message
        
        # Temporarily enable text widget to add new message
        self.text_widget.config(state="normal")
        
        # Add message to text widget
        self.text_widget.insert(tk.END, formatted_message + "\n")
        self.line_count += 1
        
        # Auto-scroll to latest message
        self.text_widget.see(tk.END)
        
        # Apply formatting based on level
        if level.upper() == "ERROR":
            # Color error messages in red
            start_line = f"{self.line_count}.0"
            end_line = f"{self.line_count}.end"
            self.text_widget.tag_add("error", start_line, end_line)
            self.text_widget.tag_config("error", foreground="red")
        elif level.upper() == "WARNING":
            # Color warning messages in orange
            start_line = f"{self.line_count}.0"
            end_line = f"{self.line_count}.end"
            self.text_widget.tag_add("warning", start_line, end_line)
            self.text_widget.tag_config("warning", foreground="orange")
        elif level.upper() == "SUCCESS":
            # Color success messages in green
            start_line = f"{self.line_count}.0"
            end_line = f"{self.line_count}.end"
            self.text_widget.tag_add("success", start_line, end_line)
            self.text_widget.tag_config("success", foreground="green")
        
        # Disable text widget to prevent user editing
        self.text_widget.config(state="disabled")
        
        # Force GUI update
        self.parent.update_idletasks()
        
        # Manage memory by limiting number of lines
        if self.line_count > self.max_lines:
            self._trim_old_messages()
    
    def _trim_old_messages(self) -> None:
        """Remove old messages to prevent memory issues."""
        lines_to_remove = self.line_count - self.max_lines + 100  # Keep some buffer
        
        if lines_to_remove > 0:
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", f"{lines_to_remove}.0")
            self.line_count -= lines_to_remove
            self.text_widget.config(state="disabled")
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.log_message(message, "INFO")
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.log_message(message, "WARNING")
    
    def log_error(self, message: str) -> None:
        """Log an error message."""
        self.log_message(message, "ERROR")
    
    def log_success(self, message: str) -> None:
        """Log a success message."""
        self.log_message(message, "SUCCESS")
    
    def clear_log(self) -> None:
        """Clear all messages from the log."""
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.line_count = 0
        self.text_widget.config(state="disabled")
    
    def save_log_to_file(self, filename: str) -> bool:
        """
        Save the current log contents to a file.
        
        Args:
            filename (str): Path to save the log file
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            content = self.text_widget.get("1.0", tk.END)
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            return True
        except Exception:
            return False
    
    def get_log_content(self) -> str:
        """
        Get the current log content as a string.
        
        Returns:
            str: All log messages as a single string
        """
        return self.text_widget.get("1.0", tk.END)
    
    def set_timestamp_display(self, show_timestamps: bool) -> None:
        """
        Enable or disable timestamp display for new messages.
        
        Args:
            show_timestamps (bool): Whether to show timestamps
        """
        self.show_timestamps = show_timestamps
    
    def set_max_lines(self, max_lines: int) -> None:
        """
        Set the maximum number of lines to keep in memory.
        
        Args:
            max_lines (int): Maximum number of lines
        """
        self.max_lines = max_lines
    
    def get_line_count(self) -> int:
        """
        Get the current number of lines in the log.
        
        Returns:
            int: Number of lines currently displayed
        """
        return self.line_count