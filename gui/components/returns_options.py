"""
Returns Dashboard options GUI component for GST Automation Application.

This module provides a reusable component for configuring Returns Dashboard
filtering options including financial year, quarter, and month selection.

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from config.settings import (
    FINANCIAL_YEARS, QUARTERS, MONTHS,
    DEFAULT_FINANCIAL_YEAR_INDEX, DEFAULT_QUARTER_INDEX, DEFAULT_MONTH_INDEX
)
from models.client_data import ReturnsDashboardOptions

class ReturnsOptionsComponent:
    """
    GUI component for Returns Dashboard filtering options.
    
    This component provides dropdowns for selecting financial year,
    quarter, and month/period for Returns Dashboard filtering.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_options_changed: Optional[Callable[[ReturnsDashboardOptions], None]] = None):
        """
        Initialize the returns options component.
        
        Args:
            parent (tk.Widget): Parent widget to contain this component
            on_options_changed (Optional[Callable]): Callback when options change
        """
        self.parent = parent
        self.on_options_changed = on_options_changed
        
        # Create the UI components
        self._create_ui()
        
        # Set default values
        self._set_default_values()
        
        # Update months based on initial quarter selection
        self._update_months_for_quarter()
        
        # Bind change events
        self._bind_change_events()
    
    def _create_ui(self) -> None:
        """Create the user interface components."""
        # Main frame for returns options
        self.frame = ttk.LabelFrame(self.parent, text="Returns Dashboard Options")
        
        # Financial Year selection
        ttk.Label(self.frame, text="Financial Year:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.year_combo = ttk.Combobox(
            self.frame, 
            values=FINANCIAL_YEARS, 
            state="readonly",
            width=15
        )
        self.year_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Quarter selection
        ttk.Label(self.frame, text="Quarter:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quarter_combo = ttk.Combobox(
            self.frame, 
            values=QUARTERS, 
            state="readonly",
            width=25
        )
        self.quarter_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Month/Period selection
        ttk.Label(self.frame, text="Period (Month):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.month_combo = ttk.Combobox(
            self.frame, 
            values=MONTHS, 
            state="readonly",
            width=15
        )
        self.month_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Add helpful information
        info_label = ttk.Label(
            self.frame,
            text="These filters will be applied when navigating to Returns Dashboard",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        info_label.grid(row=3, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="w")
        
        # Configure grid weights
        self.frame.grid_columnconfigure(1, weight=1)
    
    def _set_default_values(self) -> None:
        """Set default values for all dropdowns."""
        try:
            # Set default financial year
            if len(FINANCIAL_YEARS) > DEFAULT_FINANCIAL_YEAR_INDEX:
                self.year_combo.current(DEFAULT_FINANCIAL_YEAR_INDEX)
            elif FINANCIAL_YEARS:
                self.year_combo.current(0)
            
            # Set default quarter
            if len(QUARTERS) > DEFAULT_QUARTER_INDEX:
                self.quarter_combo.current(DEFAULT_QUARTER_INDEX)
            elif QUARTERS:
                self.quarter_combo.current(0)
            
            # Set default month
            if len(MONTHS) > DEFAULT_MONTH_INDEX:
                self.month_combo.current(DEFAULT_MONTH_INDEX)
            elif MONTHS:
                self.month_combo.current(0)
        
        except (tk.TclError, IndexError):
            # Handle any errors in setting defaults
            pass
    
    def _bind_change_events(self) -> None:
        """Bind change events to combo boxes."""
        self.year_combo.bind("<<ComboboxSelected>>", self._on_option_changed)
        self.quarter_combo.bind("<<ComboboxSelected>>", self._on_quarter_changed)
        self.month_combo.bind("<<ComboboxSelected>>", self._on_option_changed)
    
    def _on_quarter_changed(self, event=None) -> None:
        """Handle quarter selection change and update months accordingly."""
        # Update month dropdown based on selected quarter
        self._update_months_for_quarter()
        
        # Then call the regular option changed handler
        self._on_option_changed(event)
    
    def _update_months_for_quarter(self) -> None:
        """Update month dropdown options based on selected quarter."""
        selected_quarter_index = self.quarter_combo.current()
        
        # Define months for each quarter (0-based indexing)
        quarter_months = {
            0: ["April", "May", "June"],           # Quarter 1 (Apr-Jun)
            1: ["July", "August", "September"],    # Quarter 2 (Jul-Sep) 
            2: ["October", "November", "December"], # Quarter 3 (Oct-Dec)
            3: ["January", "February", "March"]    # Quarter 4 (Jan-Mar)
        }
        
        # Get months for selected quarter, default to all months if invalid
        if selected_quarter_index in quarter_months:
            relevant_months = quarter_months[selected_quarter_index]
        else:
            relevant_months = MONTHS  # Fallback to all months
        
        # Update the month dropdown values
        current_month_selection = self.month_combo.get()  # Save current selection
        self.month_combo['values'] = relevant_months
        
        # Try to preserve selection if it exists in new list, otherwise select first month
        try:
            if current_month_selection in relevant_months:
                new_index = relevant_months.index(current_month_selection)
                self.month_combo.current(new_index)
            else:
                # Default to middle month of the quarter (usually the current month)
                default_index = 1 if len(relevant_months) > 1 else 0
                self.month_combo.current(default_index)
        except (tk.TclError, ValueError):
            # Fallback: select first available month
            if relevant_months:
                self.month_combo.current(0)
    
    def _on_option_changed(self, event=None) -> None:
        """Handle changes to any option and notify callback."""
        if self.on_options_changed:
            options = self.get_returns_options()
            self.on_options_changed(options)
    
    def pack(self, **kwargs) -> None:
        """Pack the returns options frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the returns options frame."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the returns options frame."""
        self.frame.place(**kwargs)
    
    def pack_forget(self) -> None:
        """Hide the returns options frame."""
        self.frame.pack_forget()
    
    def grid_forget(self) -> None:
        """Hide the returns options frame (grid)."""
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
    
    def get_returns_options(self) -> ReturnsDashboardOptions:
        """
        Get the current returns dashboard options.
        
        Returns:
            ReturnsDashboardOptions: Current option selections
        """
        return ReturnsDashboardOptions(
            financial_year_index=self.year_combo.current(),
            quarter_index=self.quarter_combo.current(),
            month_index=self.month_combo.current()
        )
    
    def set_returns_options(self, options: ReturnsDashboardOptions) -> None:
        """
        Set the returns dashboard options.
        
        Args:
            options (ReturnsDashboardOptions): Options to set
        """
        try:
            # Validate indices before setting
            if 0 <= options.financial_year_index < len(FINANCIAL_YEARS):
                self.year_combo.current(options.financial_year_index)
            
            if 0 <= options.quarter_index < len(QUARTERS):
                self.quarter_combo.current(options.quarter_index)
            
            if 0 <= options.month_index < len(MONTHS):
                self.month_combo.current(options.month_index)
            
            # Notify callback
            self._on_option_changed()
            
        except (tk.TclError, IndexError) as e:
            # Log error but don't crash
            print(f"Error setting returns options: {e}")
    
    def get_selected_financial_year(self) -> str:
        """
        Get the currently selected financial year.
        
        Returns:
            str: Selected financial year
        """
        index = self.year_combo.current()
        if 0 <= index < len(FINANCIAL_YEARS):
            return FINANCIAL_YEARS[index]
        return ""
    
    def get_selected_quarter(self) -> str:
        """
        Get the currently selected quarter.
        
        Returns:
            str: Selected quarter
        """
        index = self.quarter_combo.current()
        if 0 <= index < len(QUARTERS):
            return QUARTERS[index]
        return ""
    
    def get_selected_month(self) -> str:
        """
        Get the currently selected month.
        
        Returns:
            str: Selected month
        """
        index = self.month_combo.current()
        if 0 <= index < len(MONTHS):
            return MONTHS[index]
        return ""
    
    def get_selection_summary(self) -> str:
        """
        Get a summary of current selections.
        
        Returns:
            str: Summary string of all selections
        """
        year = self.get_selected_financial_year()
        quarter = self.get_selected_quarter()
        month = self.get_selected_month()
        
        return f"FY: {year}, {quarter}, Month: {month}"
    
    def validate_selections(self) -> tuple[bool, str]:
        """
        Validate current selections.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        options = self.get_returns_options()
        
        if not options.is_valid():
            return False, "Invalid Returns Dashboard selections"
        
        if options.financial_year_index < 0:
            return False, "Financial year must be selected"
        
        if options.quarter_index < 0:
            return False, "Quarter must be selected"
        
        if options.month_index < 0:
            return False, "Month must be selected"
        
        return True, ""
    
    def reset_to_defaults(self) -> None:
        """Reset all selections to default values."""
        self._set_default_values()
        self._on_option_changed()
    
    def set_financial_year_by_name(self, year_name: str) -> bool:
        """
        Set financial year by name.
        
        Args:
            year_name (str): Name of the financial year (e.g., "2025-26")
            
        Returns:
            bool: True if year was found and set, False otherwise
        """
        try:
            index = FINANCIAL_YEARS.index(year_name)
            self.year_combo.current(index)
            self._on_option_changed()
            return True
        except ValueError:
            return False
    
    def set_quarter_by_name(self, quarter_name: str) -> bool:
        """
        Set quarter by name.
        
        Args:
            quarter_name (str): Name of the quarter
            
        Returns:
            bool: True if quarter was found and set, False otherwise
        """
        try:
            index = QUARTERS.index(quarter_name)
            self.quarter_combo.current(index)
            self._on_option_changed()
            return True
        except ValueError:
            return False
    
    def set_month_by_name(self, month_name: str) -> bool:
        """
        Set month by name.
        
        Args:
            month_name (str): Name of the month
            
        Returns:
            bool: True if month was found and set, False otherwise
        """
        try:
            index = MONTHS.index(month_name)
            self.month_combo.current(index)
            self._on_option_changed()
            return True
        except ValueError:
            return False
    
    def enable_all_options(self) -> None:
        """Enable all option dropdowns."""
        self.year_combo.config(state="readonly")
        self.quarter_combo.config(state="readonly")
        self.month_combo.config(state="readonly")
    
    def disable_all_options(self) -> None:
        """Disable all option dropdowns."""
        self.year_combo.config(state="disabled")
        self.quarter_combo.config(state="disabled")
        self.month_combo.config(state="disabled")