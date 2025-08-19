"""
Credentials form GUI component for GST Automation Application.

This module provides a reusable component for displaying and editing
GST portal credentials (username and password).

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from models.client_data import ClientCredentials

class CredentialsForm:
    """
    GUI component for displaying and editing GST portal credentials.
    
    This component provides input fields for username and password,
    with auto-population support from client selection.
    """
    
    def __init__(self, parent: tk.Widget,
                 on_credentials_changed: Optional[Callable[[str, str], None]] = None):
        """
        Initialize the credentials form component.
        
        Args:
            parent (tk.Widget): Parent widget to contain this component
            on_credentials_changed (Optional[Callable]): Callback when credentials change
        """
        self.parent = parent
        self.on_credentials_changed = on_credentials_changed
        
        # Create the UI components
        self._create_ui()
        
        # Track changes to credentials
        self.username_var.trace('w', self._on_credentials_change)
        self.password_var.trace('w', self._on_credentials_change)
    
    def _create_ui(self) -> None:
        """Create the user interface components."""
        # Main frame for credentials section
        self.frame = ttk.LabelFrame(self.parent, text="Credentials (auto-filled on client selection)")
        
        # Create StringVar instances for the entry fields
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Username field
        ttk.Label(self.frame, text="GST Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Password field (masked for security)
        ttk.Label(self.frame, text="GST Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.frame, textvariable=self.password_var, width=40, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Show/Hide password button
        self.show_password_var = tk.BooleanVar()
        self.show_password_button = ttk.Checkbutton(
            self.frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility
        )
        self.show_password_button.grid(row=2, column=1, padx=5, pady=(0, 5), sticky="w")
        
        # Configure grid weights for responsive layout
        self.frame.grid_columnconfigure(1, weight=1)
    
    def pack(self, **kwargs) -> None:
        """Pack the credentials form frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the credentials form frame."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the credentials form frame."""
        self.frame.place(**kwargs)
    
    def _toggle_password_visibility(self) -> None:
        """Toggle password field visibility between masked and plain text."""
        if self.show_password_var.get():
            self.password_entry.config(show="")  # Show password
        else:
            self.password_entry.config(show="*")  # Hide password
    
    def _on_credentials_change(self, *args) -> None:
        """Handle changes to credentials and notify callback."""
        if self.on_credentials_changed:
            username = self.get_username()
            password = self.get_password()
            self.on_credentials_changed(username, password)
    
    def populate_from_client(self, client: Optional[ClientCredentials]) -> None:
        """
        Populate the form fields with client credentials.
        
        Args:
            client (Optional[ClientCredentials]): Client credentials to populate, 
                                                 None to clear fields
        """
        if client:
            self.username_var.set(client.username)
            self.password_var.set(client.password)
        else:
            self.clear_credentials()
    
    def clear_credentials(self) -> None:
        """Clear both username and password fields."""
        self.username_var.set("")
        self.password_var.set("")
    
    def get_username(self) -> str:
        """
        Get the current username value.
        
        Returns:
            str: Current username
        """
        return self.username_var.get().strip()
    
    def get_password(self) -> str:
        """
        Get the current password value.
        
        Returns:
            str: Current password
        """
        return self.password_var.get().strip()
    
    def set_username(self, username: str) -> None:
        """
        Set the username field value.
        
        Args:
            username (str): Username to set
        """
        self.username_var.set(username)
    
    def set_password(self, password: str) -> None:
        """
        Set the password field value.
        
        Args:
            password (str): Password to set
        """
        self.password_var.set(password)
    
    def get_credentials(self) -> ClientCredentials:
        """
        Get current credentials as a ClientCredentials object.
        
        Returns:
            ClientCredentials: Current credentials (with Manual Entry as client name)
        """
        return ClientCredentials(
            client_name="Manual Entry",  # Default name for manual credential entry
            username=self.get_username(),
            password=self.get_password()
        )
    
    def validate_credentials(self) -> tuple[bool, str]:
        """
        Validate the current credentials.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        username = self.get_username()
        password = self.get_password()
        
        if not username:
            return False, "Username cannot be empty"
        
        if not password:
            return False, "Password cannot be empty"
        
        return True, ""
    
    def are_credentials_empty(self) -> bool:
        """
        Check if both username and password are empty.
        
        Returns:
            bool: True if both fields are empty, False otherwise
        """
        return not self.get_username() and not self.get_password()
    
    def focus_username(self) -> None:
        """Set focus to the username field."""
        self.username_entry.focus()
    
    def focus_password(self) -> None:
        """Set focus to the password field."""
        self.password_entry.focus()
    
    def set_readonly(self, readonly: bool = True) -> None:
        """
        Make the credentials fields read-only or editable.
        
        Args:
            readonly (bool): If True, make fields read-only
        """
        state = "readonly" if readonly else "normal"
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
    
    def enable_fields(self) -> None:
        """Enable both credential fields for editing."""
        self.set_readonly(False)
    
    def disable_fields(self) -> None:
        """Disable both credential fields (read-only)."""
        self.set_readonly(True)
    
    def get_form_data(self) -> dict:
        """
        Get form data as a dictionary.
        
        Returns:
            dict: Dictionary containing username and password
        """
        return {
            "username": self.get_username(),
            "password": self.get_password()
        }
    
    def set_form_data(self, data: dict) -> None:
        """
        Set form data from a dictionary.
        
        Args:
            data (dict): Dictionary containing username and password keys
        """
        self.set_username(data.get("username", ""))
        self.set_password(data.get("password", ""))