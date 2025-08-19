"""
Credit Ledger options GUI component for GST Automation Application.

This module provides a reusable component for configuring Electronic Credit
Ledger date range options for querying credit ledger data.

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk
import time
import datetime
from typing import Optional, Callable
import re

from config.settings import DEFAULT_DATE_FORMAT
from models.client_data import CreditLedgerOptions

class CreditLedgerOptionsComponent:
    """
    GUI component for Electronic Credit Ledger date range options.
    
    This component provides date input fields for specifying the date range
    for Electronic Credit Ledger queries.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_options_changed: Optional[Callable[[CreditLedgerOptions], None]] = None):
        """
        Initialize the credit ledger options component.
        
        Args:
            parent (tk.Widget): Parent widget to contain this component
            on_options_changed (Optional[Callable]): Callback when options change
        """
        self.parent = parent
        self.on_options_changed = on_options_changed
        
        # Create StringVar instances for date fields
        self.from_date_var = tk.StringVar()
        self.to_date_var = tk.StringVar()
        
        # Create the UI components
        self._create_ui()
        
        # Set default values (current date)
        self._set_default_dates()
        
        # Bind change events
        self._bind_change_events()
    
    def _create_ui(self) -> None:
        """Create the user interface components."""
        # Main frame for credit ledger options
        self.frame = ttk.LabelFrame(self.parent, text="Credit Ledger Options")
        
        # From Date field
        ttk.Label(self.frame, text="From Date (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_date_entry = ttk.Entry(self.frame, textvariable=self.from_date_var, width=15)
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Add "Today" button for From Date
        self.from_date_today_btn = ttk.Button(
            self.frame,
            text="Today",
            command=lambda: self._set_date_to_today(self.from_date_var),
            width=8
        )
        self.from_date_today_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # To Date field
        ttk.Label(self.frame, text="To Date (DD-MM-YYYY):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.to_date_entry = ttk.Entry(self.frame, textvariable=self.to_date_var, width=15)
        self.to_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Add "Today" button for To Date
        self.to_date_today_btn = ttk.Button(
            self.frame,
            text="Today",
            command=lambda: self._set_date_to_today(self.to_date_var),
            width=8
        )
        self.to_date_today_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Quick date range buttons frame
        quick_dates_frame = ttk.Frame(self.frame)
        quick_dates_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="w")
        
        # Quick date range buttons
        ttk.Label(quick_dates_frame, text="Quick ranges:", font=("TkDefaultFont", 8)).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            quick_dates_frame,
            text="This Month",
            command=self._set_current_month_range,
            width=12
        ).pack(side="left", padx=2)
        
        ttk.Button(
            quick_dates_frame,
            text="Last Month",
            command=self._set_last_month_range,
            width=12
        ).pack(side="left", padx=2)
        
        ttk.Button(
            quick_dates_frame,
            text="This Quarter",
            command=self._set_current_quarter_range,
            width=12
        ).pack(side="left", padx=2)
        
        # Add helpful information
        info_label = ttk.Label(
            self.frame,
            text="Date format: DD-MM-YYYY (e.g., 15-03-2025). Use Quick ranges for common periods.",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        info_label.grid(row=3, column=0, columnspan=3, padx=5, pady=(5, 10), sticky="w")
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
    
    def _set_default_dates(self) -> None:
        """Set default dates to current date."""
        current_date = time.strftime(DEFAULT_DATE_FORMAT)
        self.from_date_var.set(current_date)
        self.to_date_var.set(current_date)
    
    def _bind_change_events(self) -> None:
        """Bind change events to date fields."""
        self.from_date_var.trace('w', self._on_option_changed)
        self.to_date_var.trace('w', self._on_option_changed)
    
    def _on_option_changed(self, *args) -> None:
        """Handle changes to any option and notify callback."""
        if self.on_options_changed:
            options = self.get_credit_ledger_options()
            self.on_options_changed(options)
    
    def _set_date_to_today(self, date_var: tk.StringVar) -> None:
        """Set the specified date variable to today's date."""
        current_date = time.strftime(DEFAULT_DATE_FORMAT)
        date_var.set(current_date)
    
    def _set_current_month_range(self) -> None:
        """Set date range to current month (1st to last day)."""
        now = datetime.datetime.now()
        
        # First day of current month
        first_day = now.replace(day=1)
        
        # Last day of current month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        last_day = next_month - datetime.timedelta(days=1)
        
        self.from_date_var.set(first_day.strftime(DEFAULT_DATE_FORMAT))
        self.to_date_var.set(last_day.strftime(DEFAULT_DATE_FORMAT))
    
    def _set_last_month_range(self) -> None:
        """Set date range to last month (1st to last day)."""
        now = datetime.datetime.now()
        
        # First day of last month
        if now.month == 1:
            first_day = now.replace(year=now.year - 1, month=12, day=1)
        else:
            first_day = now.replace(month=now.month - 1, day=1)
        
        # Last day of last month
        last_day = now.replace(day=1) - datetime.timedelta(days=1)
        
        self.from_date_var.set(first_day.strftime(DEFAULT_DATE_FORMAT))
        self.to_date_var.set(last_day.strftime(DEFAULT_DATE_FORMAT))
    
    def _set_current_quarter_range(self) -> None:
        """Set date range to current quarter."""
        now = datetime.datetime.now()
        
        # Determine current quarter
        if now.month <= 3:
            # Q4 of previous financial year (Jan-Mar)
            quarter_start = datetime.datetime(now.year, 1, 1)
            quarter_end = datetime.datetime(now.year, 3, 31)
        elif now.month <= 6:
            # Q1 (Apr-Jun)
            quarter_start = datetime.datetime(now.year, 4, 1)
            quarter_end = datetime.datetime(now.year, 6, 30)
        elif now.month <= 9:
            # Q2 (Jul-Sep)
            quarter_start = datetime.datetime(now.year, 7, 1)
            quarter_end = datetime.datetime(now.year, 9, 30)
        else:
            # Q3 (Oct-Dec)
            quarter_start = datetime.datetime(now.year, 10, 1)
            quarter_end = datetime.datetime(now.year, 12, 31)
        
        self.from_date_var.set(quarter_start.strftime(DEFAULT_DATE_FORMAT))
        self.to_date_var.set(quarter_end.strftime(DEFAULT_DATE_FORMAT))
    
    def pack(self, **kwargs) -> None:
        """Pack the credit ledger options frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the credit ledger options frame."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the credit ledger options frame."""
        self.frame.place(**kwargs)
    
    def pack_forget(self) -> None:
        """Hide the credit ledger options frame."""
        self.frame.pack_forget()
    
    def grid_forget(self) -> None:
        """Hide the credit ledger options frame (grid)."""
        self.frame.grid_forget()
    
    def is_visible(self) -> bool:
        """
        Check if the component is currently visible.
        
        Returns:
            bool: True if visible, False if hidden
        """
        try:
            return self.frame.winfo_ismapped()
        except tk.TclError:
            return False
    
    def get_credit_ledger_options(self) -> CreditLedgerOptions:
        """
        Get the current credit ledger options.
        
        Returns:
            CreditLedgerOptions: Current date range options
        """
        return CreditLedgerOptions(
            from_date=self.from_date_var.get().strip(),
            to_date=self.to_date_var.get().strip()
        )
    
    def set_credit_ledger_options(self, options: CreditLedgerOptions) -> None:
        """
        Set the credit ledger options.
        
        Args:
            options (CreditLedgerOptions): Options to set
        """
        self.from_date_var.set(options.from_date)
        self.to_date_var.set(options.to_date)
        # Callback will be triggered automatically via trace
    
    def get_from_date(self) -> str:
        """
        Get the from date value.
        
        Returns:
            str: From date in DD-MM-YYYY format
        """
        return self.from_date_var.get().strip()
    
    def get_to_date(self) -> str:
        """
        Get the to date value.
        
        Returns:
            str: To date in DD-MM-YYYY format
        """
        return self.to_date_var.get().strip()
    
    def set_from_date(self, date: str) -> None:
        """
        Set the from date value.
        
        Args:
            date (str): Date in DD-MM-YYYY format
        """
        self.from_date_var.set(date)
    
    def set_to_date(self, date: str) -> None:
        """
        Set the to date value.
        
        Args:
            date (str): Date in DD-MM-YYYY format
        """
        self.to_date_var.set(date)
    
    def validate_date_format(self, date_str: str) -> bool:
        """
        Validate if date string is in correct format.
        
        Args:
            date_str (str): Date string to validate
            
        Returns:
            bool: True if format is correct, False otherwise
        """
        if not date_str:
            return False
        
        # Check format using regex (DD-MM-YYYY)
        pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
        if not re.match(pattern, date_str):
            return False
        
        # Try to parse the date
        try:
            datetime.datetime.strptime(date_str, DEFAULT_DATE_FORMAT)
            return True
        except ValueError:
            return False
    
    def validate_date_range(self) -> tuple[bool, str]:
        """
        Validate the current date range.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        from_date = self.get_from_date()
        to_date = self.get_to_date()
        
        if not from_date:
            return False, "From date cannot be empty"
        
        if not to_date:
            return False, "To date cannot be empty"
        
        if not self.validate_date_format(from_date):
            return False, f"From date format is invalid. Use {DEFAULT_DATE_FORMAT} format."
        
        if not self.validate_date_format(to_date):
            return False, f"To date format is invalid. Use {DEFAULT_DATE_FORMAT} format."
        
        # Check if from_date is not later than to_date
        try:
            from_dt = datetime.datetime.strptime(from_date, DEFAULT_DATE_FORMAT)
            to_dt = datetime.datetime.strptime(to_date, DEFAULT_DATE_FORMAT)
            
            if from_dt > to_dt:
                return False, "From date cannot be later than To date"
            
        except ValueError:
            return False, "Invalid date values"
        
        return True, ""
    
    def get_date_range_summary(self) -> str:
        """
        Get a summary of the current date range.
        
        Returns:
            str: Summary string of the date range
        """
        from_date = self.get_from_date()
        to_date = self.get_to_date()
        return f"From: {from_date} To: {to_date}"
    
    def clear_dates(self) -> None:
        """Clear both date fields."""
        self.from_date_var.set("")
        self.to_date_var.set("")
    
    def reset_to_today(self) -> None:
        """Reset both dates to today."""
        self._set_default_dates()
    
    def enable_all_options(self) -> None:
        """Enable all date input fields and buttons."""
        self.from_date_entry.config(state="normal")
        self.to_date_entry.config(state="normal")
        self.from_date_today_btn.config(state="normal")
        self.to_date_today_btn.config(state="normal")
    
    def disable_all_options(self) -> None:
        """Disable all date input fields and buttons."""
        self.from_date_entry.config(state="disabled")
        self.to_date_entry.config(state="disabled")
        self.from_date_today_btn.config(state="disabled")
        self.to_date_today_btn.config(state="disabled")