"""
Client selection GUI component for GST Automation Application.

This module provides a reusable component for Excel file browsing,
client loading, and client selection functionality.

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, Callable

from config.settings import DEFAULT_EXCEL_FILENAME
from models.client_data import ClientDataManager, ClientCredentials
from services.excel_service import ExcelService

class ClientSelectionComponent:
    """
    GUI component for Excel file browsing and client selection.
    
    This component handles:
    - Excel file path browsing and display
    - Loading clients from Excel files
    - Client selection dropdown
    - Client credentials display/editing
    """
    
    def __init__(self, parent: tk.Widget, 
                 on_client_selected: Optional[Callable[[Optional[ClientCredentials]], None]] = None,
                 status_callback: Optional[Callable[[str, str], None]] = None):
        """
        Initialize the client selection component.
        
        Args:
            parent (tk.Widget): Parent widget to contain this component
            on_client_selected (Optional[Callable]): Callback when client is selected
            status_callback (Optional[Callable]): Callback for status messages (message, level)
        """
        self.parent = parent
        self.on_client_selected = on_client_selected
        self.status_callback = status_callback or self._default_status_callback
        
        # Initialize services and data
        self.excel_service = ExcelService()
        self.client_manager = ClientDataManager()
        
        # Initialize UI variables
        self.excel_file_path = tk.StringVar(value=os.path.join(os.getcwd(), DEFAULT_EXCEL_FILENAME))
        
        # Create the UI components
        self._create_ui()
        
        # Attempt to load clients from default file (silent mode)
        self._load_clients_from_excel(silent=True)
    
    def _default_status_callback(self, message: str, level: str = "INFO") -> None:
        """Default status callback that does nothing."""
        pass
    
    def _create_ui(self) -> None:
        """Create the user interface components."""
        # Main frame for client data section
        self.frame = ttk.LabelFrame(self.parent, text="Client Data from Excel")
        
        # Excel file path row
        ttk.Label(self.frame, text="Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.excel_path_entry = ttk.Entry(self.frame, textvariable=self.excel_file_path, width=50)
        self.excel_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.browse_button = ttk.Button(self.frame, text="Browse", command=self._browse_excel_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Load clients button row
        self.load_clients_button = ttk.Button(
            self.frame, 
            text="Load Clients from Excel", 
            command=self._load_clients_from_excel
        )
        self.load_clients_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Client selection row
        ttk.Label(self.frame, text="Select Client:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.client_combo = ttk.Combobox(self.frame, state="readonly", width=47)
        self.client_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.client_combo.bind("<<ComboboxSelected>>", self._on_client_combo_selected)
        
        # Configure grid weights for responsive layout
        self.frame.grid_columnconfigure(1, weight=1)
    
    def pack(self, **kwargs) -> None:
        """Pack the client selection frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the client selection frame."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs) -> None:
        """Place the client selection frame."""
        self.frame.place(**kwargs)
    
    def _browse_excel_file(self) -> None:
        """Open file dialog to browse and select an Excel file."""
        filepath = filedialog.askopenfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Select Clients Excel File"
        )
        
        if filepath:
            self.excel_file_path.set(filepath)
            self._load_clients_from_excel()
    
    def _load_clients_from_excel(self, silent: bool = False) -> None:
        """
        Load client data from the specified Excel file.
        
        Args:
            silent (bool): If True, suppress error message boxes
        """
        excel_path = self.excel_file_path.get()
        
        try:
            self.status_callback(f"Loading clients from {excel_path}...", "INFO")
            
            # Load clients using Excel service
            client_manager, error_message = self.excel_service.load_clients_from_excel(excel_path, silent)
            
            if error_message:
                # Handle loading errors
                if not silent:
                    messagebox.showerror("Excel Load Error", error_message)
                self.status_callback(f"Error: {error_message}", "ERROR")
                
                # Clear client data on error
                self.client_manager.clear()
                self.client_combo['values'] = []
                return
            
            # Update client manager and UI
            self.client_manager = client_manager
            client_names = self.client_manager.get_all_client_names()
            self.client_combo['values'] = client_names
            
            if client_names:
                # Select first client by default and notify callback
                self.client_combo.current(0)
                self._trigger_client_selection()
                
                success_message = f"Successfully loaded {len(client_names)} clients."
                self.status_callback(success_message, "SUCCESS")
                
                # Show success message (unless in silent mode)
                if not silent:
                    messagebox.showinfo("Success", success_message)
            else:
                # No valid clients found
                self.client_combo.set("")  # Clear selection
                self.status_callback("No clients found in the Excel file or data is invalid.", "WARNING")
                
        except Exception as e:
            error_message = f"Unexpected error loading clients: {str(e)}"
            if not silent:
                messagebox.showerror("Excel Load Error", error_message)
            self.status_callback(error_message, "ERROR")
            
            # Clear client data on error
            self.client_manager.clear()
            self.client_combo['values'] = []
    
    def _on_client_combo_selected(self, event) -> None:
        """Handle client selection from dropdown."""
        self._trigger_client_selection()
    
    def _trigger_client_selection(self) -> None:
        """Trigger client selection callback with current selection."""
        selected_client_name = self.client_combo.get()
        
        if selected_client_name:
            client = self.client_manager.get_client(selected_client_name)
            if client:
                self.status_callback(f"Selected client: {selected_client_name}. Credentials loaded.", "INFO")
                if self.on_client_selected:
                    self.on_client_selected(client)
            else:
                self.status_callback(f"Client '{selected_client_name}' not found in loaded data.", "WARNING")
                if self.on_client_selected:
                    self.on_client_selected(None)
        else:
            # No client selected
            if self.on_client_selected:
                self.on_client_selected(None)
    
    def get_selected_client(self) -> Optional[ClientCredentials]:
        """
        Get the currently selected client credentials.
        
        Returns:
            Optional[ClientCredentials]: Selected client or None if no selection
        """
        selected_client_name = self.client_combo.get()
        if selected_client_name:
            return self.client_manager.get_client(selected_client_name)
        return None
    
    def get_client_count(self) -> int:
        """
        Get the number of loaded clients.
        
        Returns:
            int: Number of clients currently loaded
        """
        return self.client_manager.get_client_count()
    
    def refresh_clients(self) -> None:
        """Refresh client data from the current Excel file."""
        self._load_clients_from_excel(silent=False)
    
    def clear_selection(self) -> None:
        """Clear the current client selection."""
        self.client_combo.set("")
        if self.on_client_selected:
            self.on_client_selected(None)
    
    def set_excel_file_path(self, file_path: str) -> None:
        """
        Set the Excel file path and optionally reload clients.
        
        Args:
            file_path (str): Path to the Excel file
        """
        self.excel_file_path.set(file_path)
    
    def get_excel_file_path(self) -> str:
        """
        Get the current Excel file path.
        
        Returns:
            str: Current Excel file path
        """
        return self.excel_file_path.get()
    
    def validate_current_selection(self) -> tuple[bool, str]:
        """
        Validate the current client selection.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        client = self.get_selected_client()
        
        if not client:
            return False, "No client selected"
        
        if not client.is_valid():
            return False, "Selected client has invalid credentials"
        
        return True, ""
    
    def get_all_client_names(self) -> list[str]:
        """
        Get list of all available client names.
        
        Returns:
            list[str]: List of client names
        """
        return self.client_manager.get_all_client_names()
    
    def select_client_by_name(self, client_name: str) -> bool:
        """
        Select a client by name programmatically.
        
        Args:
            client_name (str): Name of the client to select
            
        Returns:
            bool: True if client was found and selected, False otherwise
        """
        client_names = self.get_all_client_names()
        
        if client_name in client_names:
            # Find the index and select it
            try:
                index = client_names.index(client_name)
                self.client_combo.current(index)
                self._trigger_client_selection()
                return True
            except (ValueError, tk.TclError):
                return False
        
        return False