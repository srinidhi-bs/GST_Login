"""
Client data models for GST Automation Application.

This module defines data classes and models for representing client information
and automation settings throughout the application.

Author: Srinidhi B S
"""
from dataclasses import dataclass
from typing import Dict, Optional, Any
import time

@dataclass
class ClientCredentials:
    """
    Represents GST portal credentials for a single client.
    
    This class encapsulates the basic authentication information needed
    to log into the GST portal for a specific client.
    
    Attributes:
        client_name (str): The display name of the client
        username (str): GST portal username
        password (str): GST portal password
    """
    client_name: str
    username: str
    password: str
    
    def is_valid(self) -> bool:
        """
        Check if the client credentials are valid (non-empty).
        
        Returns:
            bool: True if all credential fields are non-empty, False otherwise
        """
        return (
            bool(self.client_name and self.client_name.strip()) and
            bool(self.username and self.username.strip()) and
            bool(self.password and self.password.strip())
        )
    
    def __str__(self) -> str:
        """
        String representation of client (hides password for security).
        
        Returns:
            str: Client information without exposing password
        """
        return f"Client: {self.client_name}, Username: {self.username}"

@dataclass
class AutomationSettings:
    """
    Contains all user-selected automation settings and options.
    
    This class encapsulates all the choices made by the user regarding
    which actions to perform and their specific parameters.
    
    Attributes:
        just_login (bool): If True, only perform login without other actions
        returns_dashboard (bool): If True, navigate to Returns Dashboard
        download_gstr2b (bool): If True, download GSTR-2B report
        access_credit_ledger (bool): If True, access Electronic Credit Ledger
        access_cash_ledger (bool): If True, access Electronic Cash Ledger
    """
    just_login: bool = False
    returns_dashboard: bool = False
    download_gstr2b: bool = False
    access_credit_ledger: bool = False
    access_cash_ledger: bool = False
    
    def has_actions_selected(self) -> bool:
        """
        Check if any automation actions are selected.
        
        Returns:
            bool: True if at least one action is selected, False otherwise
        """
        return any([
            self.just_login,
            self.returns_dashboard,
            self.download_gstr2b,
            self.access_credit_ledger,
            self.access_cash_ledger
        ])
    
    def requires_returns_dashboard(self) -> bool:
        """
        Check if the selected actions require Returns Dashboard access.
        
        GSTR-2B download requires Returns Dashboard navigation.
        
        Returns:
            bool: True if Returns Dashboard access is needed
        """
        return self.returns_dashboard or self.download_gstr2b

@dataclass
class ReturnsDashboardOptions:
    """
    Settings for Returns Dashboard filtering and navigation.
    
    This class contains the specific options for filtering data
    in the GST Returns Dashboard.
    
    Attributes:
        financial_year_index (int): Index of selected financial year
        quarter_index (int): Index of selected quarter
        month_index (int): Index of selected month/period
    """
    financial_year_index: int = 0  # Default to first option
    quarter_index: int = 0         # Default to first quarter
    month_index: int = 0           # Default to first month
    
    def is_valid(self) -> bool:
        """
        Validate that all indices are non-negative.
        
        Returns:
            bool: True if all indices are valid (>= 0)
        """
        return (
            self.financial_year_index >= 0 and
            self.quarter_index >= 0 and
            self.month_index >= 0
        )

@dataclass
class CreditLedgerOptions:
    """
    Date range settings for Electronic Credit Ledger queries.
    
    This class contains the date range parameters for querying
    the Electronic Credit Ledger.
    
    Attributes:
        from_date (str): Start date in DD-MM-YYYY format
        to_date (str): End date in DD-MM-YYYY format
    """
    from_date: str = ""  # Will be set to current date by default
    to_date: str = ""    # Will be set to current date by default
    
    def __post_init__(self):
        """Set default dates to current date if not provided."""
        if not self.from_date:
            self.from_date = time.strftime("%d-%m-%Y")
        if not self.to_date:
            self.to_date = time.strftime("%d-%m-%Y")
    
    def is_valid(self) -> bool:
        """
        Check if date range is valid (both dates provided).
        
        Returns:
            bool: True if both dates are non-empty, False otherwise
        """
        return bool(self.from_date.strip()) and bool(self.to_date.strip())

@dataclass
class AutomationConfig:
    """
    Complete configuration for a single automation run.
    
    This class combines all the necessary information to perform
    a complete automation session, including client credentials
    and all selected options.
    
    Attributes:
        credentials (ClientCredentials): Client authentication information
        automation_settings (AutomationSettings): Selected automation actions
        returns_options (ReturnsDashboardOptions): Returns Dashboard settings
        credit_ledger_options (CreditLedgerOptions): Credit Ledger date range
    """
    credentials: ClientCredentials
    automation_settings: AutomationSettings
    returns_options: ReturnsDashboardOptions
    credit_ledger_options: CreditLedgerOptions
    
    def is_valid(self) -> bool:
        """
        Validate that the complete automation configuration is valid.
        
        Returns:
            bool: True if all components are valid, False otherwise
        """
        return (
            self.credentials.is_valid() and
            self.automation_settings.has_actions_selected() and
            (not self.automation_settings.requires_returns_dashboard() or 
             self.returns_options.is_valid()) and
            (not self.automation_settings.access_credit_ledger or 
             self.credit_ledger_options.is_valid())
        )
    
    def get_validation_errors(self) -> list:
        """
        Get a list of validation errors for debugging/user feedback.
        
        Returns:
            list: List of error messages describing validation issues
        """
        errors = []
        
        if not self.credentials.is_valid():
            errors.append("Invalid client credentials: username and password are required")
        
        if not self.automation_settings.has_actions_selected():
            errors.append("No automation actions selected")
        
        if (self.automation_settings.requires_returns_dashboard() and 
            not self.returns_options.is_valid()):
            errors.append("Invalid Returns Dashboard options")
        
        if (self.automation_settings.access_credit_ledger and 
            not self.credit_ledger_options.is_valid()):
            errors.append("Invalid Credit Ledger date range")
        
        return errors

class ClientDataManager:
    """
    Manager class for handling multiple client credentials.
    
    This class provides methods for managing a collection of client
    credentials loaded from Excel files or other sources.
    """
    
    def __init__(self):
        """Initialize empty client data manager."""
        self._clients: Dict[str, ClientCredentials] = {}
    
    def add_client(self, client: ClientCredentials) -> None:
        """
        Add a client to the manager.
        
        Args:
            client (ClientCredentials): The client credentials to add
        """
        if client.is_valid():
            self._clients[client.client_name] = client
    
    def get_client(self, client_name: str) -> Optional[ClientCredentials]:
        """
        Get client credentials by name.
        
        Args:
            client_name (str): The name of the client to retrieve
            
        Returns:
            Optional[ClientCredentials]: The client credentials or None if not found
        """
        return self._clients.get(client_name)
    
    def get_all_client_names(self) -> list:
        """
        Get list of all client names.
        
        Returns:
            list: Sorted list of client names
        """
        return sorted(self._clients.keys())
    
    def get_client_count(self) -> int:
        """
        Get the number of clients managed.
        
        Returns:
            int: Number of clients in the manager
        """
        return len(self._clients)
    
    def clear(self) -> None:
        """Clear all client data."""
        self._clients.clear()
    
    def update_from_dict(self, clients_dict: Dict[str, Dict[str, str]]) -> int:
        """
        Update clients from dictionary format (legacy support).
        
        Args:
            clients_dict (Dict[str, Dict[str, str]]): Dictionary with client data
                Format: {client_name: {"username": str, "password": str}}
        
        Returns:
            int: Number of valid clients added
        """
        self.clear()
        added_count = 0
        
        for client_name, credentials in clients_dict.items():
            try:
                client = ClientCredentials(
                    client_name=client_name,
                    username=credentials.get("username", ""),
                    password=credentials.get("password", "")
                )
                if client.is_valid():
                    self.add_client(client)
                    added_count += 1
            except (KeyError, TypeError):
                # Skip invalid entries
                continue
        
        return added_count
    
    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """
        Convert clients to dictionary format (legacy compatibility).
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary format of all clients
        """
        return {
            name: {
                "username": client.username,
                "password": client.password
            }
            for name, client in self._clients.items()
        }