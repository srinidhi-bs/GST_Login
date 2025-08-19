"""
Action selection GUI component for GST Automation Application.

This module provides a reusable component for selecting which automation
actions to perform during the GST portal session.

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from models.client_data import AutomationSettings

class ActionSelectionComponent:
    """
    GUI component for selecting automation actions to perform.
    
    This component provides checkboxes for various automation actions
    and handles dependencies between actions (e.g., GSTR-2B requires Returns Dashboard).
    """
    
    def __init__(self, parent: tk.Widget,
                 on_actions_changed: Optional[Callable[[AutomationSettings], None]] = None,
                 status_callback: Optional[Callable[[str, str], None]] = None):
        """
        Initialize the action selection component.
        
        Args:
            parent (tk.Widget): Parent widget to contain this component
            on_actions_changed (Optional[Callable]): Callback when actions change
            status_callback (Optional[Callable]): Callback for status messages
        """
        self.parent = parent
        self.on_actions_changed = on_actions_changed
        self.status_callback = status_callback or self._default_status_callback
        
        # Initialize action variables
        self.just_login_var = tk.BooleanVar()
        self.returns_dashboard_var = tk.BooleanVar()
        self.download_gstr2b_var = tk.BooleanVar()
        self.access_credit_ledger_var = tk.BooleanVar()
        self.access_cash_ledger_var = tk.BooleanVar()
        
        # Create the UI components
        self._create_ui()
        
        # Bind change events to handle action dependencies
        self._bind_change_events()
    
    def _default_status_callback(self, message: str, level: str = "INFO") -> None:
        """Default status callback that does nothing."""
        pass
    
    def _create_ui(self) -> None:
        """Create the user interface components."""
        # Main frame for action selection
        self.frame = ttk.LabelFrame(self.parent, text="Actions to Perform")
        
        # Just Login option
        self.just_login_check = ttk.Checkbutton(
            self.frame,
            text="Just Login",
            variable=self.just_login_var,
            command=self._on_action_changed
        )
        self.just_login_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Add tooltip/description for Just Login
        just_login_desc = ttk.Label(
            self.frame,
            text="(Login only, no other actions will be performed)",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        just_login_desc.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # Returns Dashboard option
        self.returns_dashboard_check = ttk.Checkbutton(
            self.frame,
            text="Returns Dashboard",
            variable=self.returns_dashboard_var,
            command=self._on_action_changed
        )
        self.returns_dashboard_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Add description for Returns Dashboard
        returns_desc = ttk.Label(
            self.frame,
            text="(Navigate to Returns Dashboard and apply filters)",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        returns_desc.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # Download GSTR-2B option
        self.download_gstr2b_check = ttk.Checkbutton(
            self.frame,
            text="Download GSTR-2B",
            variable=self.download_gstr2b_var,
            command=self._on_action_changed
        )
        self.download_gstr2b_check.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        # Add description for GSTR-2B
        gstr2b_desc = ttk.Label(
            self.frame,
            text="(Requires Returns Dashboard - will auto-enable)",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        gstr2b_desc.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # Electronic Credit Ledger option
        self.credit_ledger_check = ttk.Checkbutton(
            self.frame,
            text="Electronic Credit Ledger",
            variable=self.access_credit_ledger_var,
            command=self._on_action_changed
        )
        self.credit_ledger_check.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        # Add description for Credit Ledger
        credit_desc = ttk.Label(
            self.frame,
            text="(Access credit ledger with date range)",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        credit_desc.grid(row=3, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # Electronic Cash Ledger option
        self.cash_ledger_check = ttk.Checkbutton(
            self.frame,
            text="Electronic Cash Ledger",
            variable=self.access_cash_ledger_var,
            command=self._on_action_changed
        )
        self.cash_ledger_check.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        # Add description for Cash Ledger
        cash_desc = ttk.Label(
            self.frame,
            text="(Access cash ledger balance details)",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        cash_desc.grid(row=4, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # Configure grid weights for responsive layout
        self.frame.grid_columnconfigure(1, weight=1)
    
    def _bind_change_events(self) -> None:
        """Bind change events to action variables."""
        # These are already bound via command= in the checkbuttons
        pass
    
    def pack(self, **kwargs) -> None:
        """Pack the action selection frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the action selection frame."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the action selection frame."""
        self.frame.place(**kwargs)
    
    def _on_action_changed(self) -> None:
        """Handle changes to action selections and enforce dependencies."""
        self._handle_action_dependencies()
        self._notify_actions_changed()
    
    def _handle_action_dependencies(self) -> None:
        """Handle dependencies between actions."""
        # If GSTR-2B is selected, Returns Dashboard must also be selected
        if self.download_gstr2b_var.get() and not self.returns_dashboard_var.get():
            self.returns_dashboard_var.set(True)
            self.status_callback("Note: GSTR-2B requires Returns Dashboard - auto-enabled.", "INFO")
        
        # If Just Login is selected, consider disabling other conflicting options
        # (This is optional - user might want to select multiple actions)
        if self.just_login_var.get():
            # Optionally inform user about the interaction
            if (self.returns_dashboard_var.get() or self.download_gstr2b_var.get() or 
                self.access_credit_ledger_var.get() or self.access_cash_ledger_var.get()):
                self.status_callback("Note: 'Just Login' selected along with other actions. Other actions will be performed after login.", "INFO")
    
    def _notify_actions_changed(self) -> None:
        """Notify callback about action changes."""
        if self.on_actions_changed:
            settings = self.get_automation_settings()
            self.on_actions_changed(settings)
    
    def get_automation_settings(self) -> AutomationSettings:
        """
        Get the current automation settings based on selected actions.
        
        Returns:
            AutomationSettings: Current automation settings
        """
        return AutomationSettings(
            just_login=self.just_login_var.get(),
            returns_dashboard=self.returns_dashboard_var.get(),
            download_gstr2b=self.download_gstr2b_var.get(),
            access_credit_ledger=self.access_credit_ledger_var.get(),
            access_cash_ledger=self.access_cash_ledger_var.get()
        )
    
    def set_automation_settings(self, settings: AutomationSettings) -> None:
        """
        Set the action selections from automation settings.
        
        Args:
            settings (AutomationSettings): Settings to apply
        """
        self.just_login_var.set(settings.just_login)
        self.returns_dashboard_var.set(settings.returns_dashboard)
        self.download_gstr2b_var.set(settings.download_gstr2b)
        self.access_credit_ledger_var.set(settings.access_credit_ledger)
        self.access_cash_ledger_var.set(settings.access_cash_ledger)
        
        # Handle dependencies and notify
        self._handle_action_dependencies()
        self._notify_actions_changed()
    
    def clear_all_selections(self) -> None:
        """Clear all action selections."""
        self.just_login_var.set(False)
        self.returns_dashboard_var.set(False)
        self.download_gstr2b_var.set(False)
        self.access_credit_ledger_var.set(False)
        self.access_cash_ledger_var.set(False)
        self._notify_actions_changed()
    
    def select_just_login(self) -> None:
        """Select only the 'Just Login' option, clearing others."""
        self.clear_all_selections()
        self.just_login_var.set(True)
        self._notify_actions_changed()
    
    def select_returns_dashboard_workflow(self) -> None:
        """Select Returns Dashboard and GSTR-2B download workflow."""
        self.clear_all_selections()
        self.returns_dashboard_var.set(True)
        self.download_gstr2b_var.set(True)
        self._handle_action_dependencies()
        self._notify_actions_changed()
    
    def validate_selections(self) -> tuple[bool, str]:
        """
        Validate the current action selections.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        settings = self.get_automation_settings()
        
        if not settings.has_actions_selected():
            return False, "At least one action must be selected"
        
        return True, ""
    
    def get_selected_action_names(self) -> list[str]:
        """
        Get names of currently selected actions.
        
        Returns:
            list[str]: List of selected action names
        """
        selected_actions = []
        
        if self.just_login_var.get():
            selected_actions.append("Just Login")
        
        if self.returns_dashboard_var.get():
            selected_actions.append("Returns Dashboard")
        
        if self.download_gstr2b_var.get():
            selected_actions.append("Download GSTR-2B")
        
        if self.access_credit_ledger_var.get():
            selected_actions.append("Electronic Credit Ledger")
        
        if self.access_cash_ledger_var.get():
            selected_actions.append("Electronic Cash Ledger")
        
        return selected_actions
    
    def requires_returns_dashboard_options(self) -> bool:
        """
        Check if selected actions require Returns Dashboard options.
        
        Returns:
            bool: True if Returns Dashboard options are needed
        """
        settings = self.get_automation_settings()
        return settings.requires_returns_dashboard()
    
    def requires_credit_ledger_options(self) -> bool:
        """
        Check if selected actions require Credit Ledger options.
        
        Returns:
            bool: True if Credit Ledger options are needed
        """
        return self.access_credit_ledger_var.get()
    
    def enable_all_actions(self) -> None:
        """Enable all action checkboxes."""
        self.just_login_check.config(state="normal")
        self.returns_dashboard_check.config(state="normal")
        self.download_gstr2b_check.config(state="normal")
        self.credit_ledger_check.config(state="normal")
        self.cash_ledger_check.config(state="normal")
    
    def disable_all_actions(self) -> None:
        """Disable all action checkboxes."""
        self.just_login_check.config(state="disabled")
        self.returns_dashboard_check.config(state="disabled")
        self.download_gstr2b_check.config(state="disabled")
        self.credit_ledger_check.config(state="disabled")
        self.cash_ledger_check.config(state="disabled")