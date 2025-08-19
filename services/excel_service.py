"""
Excel file handling service for GST Automation Application.

This module provides comprehensive Excel file operations including loading
client data, validating file format, and handling Excel-related errors.

Author: Srinidhi B S
"""
import os
import pandas as pd
from typing import Optional, Tuple, List, Dict
import logging

from config.settings import (
    REQUIRED_EXCEL_COLUMNS,
    EXCEL_COLUMN_CLIENT_NAME,
    EXCEL_COLUMN_GST_USERNAME,
    EXCEL_COLUMN_GST_PASSWORD,
    ErrorMessages
)
from models.client_data import ClientCredentials, ClientDataManager

# Set up logging for this module
logger = logging.getLogger(__name__)

class ExcelValidationError(Exception):
    """Custom exception for Excel file validation errors."""
    pass

class ExcelFileNotFoundError(Exception):
    """Custom exception for missing Excel files."""
    pass

class ExcelService:
    """
    Service class for handling all Excel file operations.
    
    This class provides methods for loading client data from Excel files,
    validating file format, and managing Excel-related operations.
    """
    
    def __init__(self):
        """Initialize the Excel service."""
        self.logger = logging.getLogger(__name__)
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Check if the specified Excel file exists.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return bool(file_path) and os.path.exists(file_path)
    
    def validate_excel_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Validate that the DataFrame contains all required columns.
        
        Args:
            df (pd.DataFrame): The loaded Excel data
            
        Returns:
            List[str]: List of missing column names (empty if all present)
        """
        missing_columns = []
        for required_col in REQUIRED_EXCEL_COLUMNS:
            if required_col not in df.columns:
                missing_columns.append(required_col)
        return missing_columns
    
    def clean_cell_value(self, value) -> str:
        """
        Clean and standardize a cell value from Excel.
        
        Args:
            value: Raw value from Excel cell
            
        Returns:
            str: Cleaned string value
        """
        if pd.isna(value) or value is None:
            return ""
        return str(value).strip()
    
    def load_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Load Excel file and return DataFrame.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            pd.DataFrame: Loaded Excel data
            
        Raises:
            ExcelFileNotFoundError: If file doesn't exist
            ExcelValidationError: If file can't be loaded or has wrong format
        """
        # Check if file exists
        if not self.validate_file_exists(file_path):
            raise ExcelFileNotFoundError(
                ErrorMessages.EXCEL_FILE_NOT_FOUND.format(path=file_path)
            )
        
        try:
            # Load Excel file with all columns as strings to prevent data type issues
            self.logger.info(f"Loading Excel file: {file_path}")
            df = pd.read_excel(file_path, dtype=str)
            self.logger.info(f"Successfully loaded Excel with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            error_msg = f"Failed to load Excel file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ExcelValidationError(error_msg) from e
    
    def validate_excel_structure(self, df: pd.DataFrame) -> None:
        """
        Validate that the DataFrame has the correct structure.
        
        Args:
            df (pd.DataFrame): The loaded Excel data
            
        Raises:
            ExcelValidationError: If required columns are missing
        """
        missing_columns = self.validate_excel_columns(df)
        
        if missing_columns:
            error_msg = ErrorMessages.EXCEL_MISSING_COLUMNS.format(
                columns=", ".join(missing_columns)
            )
            self.logger.error(f"Excel validation failed: {error_msg}")
            raise ExcelValidationError(error_msg)
        
        self.logger.info("Excel structure validation passed")
    
    def extract_client_credentials(self, df: pd.DataFrame) -> List[ClientCredentials]:
        """
        Extract client credentials from validated DataFrame.
        
        Args:
            df (pd.DataFrame): The validated Excel data
            
        Returns:
            List[ClientCredentials]: List of valid client credentials
        """
        clients = []
        
        for index, row in df.iterrows():
            try:
                # Clean and extract cell values
                client_name = self.clean_cell_value(row[EXCEL_COLUMN_CLIENT_NAME])
                username = self.clean_cell_value(row[EXCEL_COLUMN_GST_USERNAME])
                password = self.clean_cell_value(row[EXCEL_COLUMN_GST_PASSWORD])
                
                # Create client credentials object
                client = ClientCredentials(
                    client_name=client_name,
                    username=username,
                    password=password
                )
                
                # Only add clients with valid data
                if client.is_valid():
                    clients.append(client)
                    self.logger.debug(f"Added valid client: {client_name}")
                else:
                    self.logger.warning(f"Skipping invalid client at row {index + 1}: {client_name}")
                    
            except Exception as e:
                self.logger.warning(f"Error processing row {index + 1}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(clients)} valid clients from Excel")
        return clients
    
    def load_clients_from_excel(self, file_path: str, silent: bool = False) -> Tuple[ClientDataManager, Optional[str]]:
        """
        Load client data from Excel file into ClientDataManager.
        
        This is the main method for loading client data. It performs complete
        validation and error handling.
        
        Args:
            file_path (str): Path to the Excel file
            silent (bool): If True, suppress detailed logging (default: False)
            
        Returns:
            Tuple[ClientDataManager, Optional[str]]: 
                - ClientDataManager with loaded clients
                - Error message string if any errors occurred, None if successful
        """
        client_manager = ClientDataManager()
        
        try:
            if not silent:
                self.logger.info(f"Starting to load clients from: {file_path}")
            
            # Load and validate Excel file
            df = self.load_excel_file(file_path)
            self.validate_excel_structure(df)
            
            # Extract client credentials
            clients = self.extract_client_credentials(df)
            
            # Add clients to manager
            for client in clients:
                client_manager.add_client(client)
            
            success_msg = f"Successfully loaded {client_manager.get_client_count()} clients from Excel"
            if not silent:
                self.logger.info(success_msg)
            
            return client_manager, None
            
        except (ExcelFileNotFoundError, ExcelValidationError) as e:
            error_msg = str(e)
            if not silent:
                self.logger.error(f"Excel loading failed: {error_msg}")
            return client_manager, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error loading Excel file: {str(e)}"
            if not silent:
                self.logger.error(error_msg)
            return client_manager, error_msg
    
    def validate_client_data_format(self, clients_dict: Dict[str, Dict[str, str]]) -> Tuple[bool, List[str]]:
        """
        Validate client data in dictionary format (for backward compatibility).
        
        Args:
            clients_dict (Dict[str, Dict[str, str]]): Client data in dictionary format
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(clients_dict, dict):
            errors.append("Client data must be a dictionary")
            return False, errors
        
        if not clients_dict:
            errors.append("Client data dictionary is empty")
            return False, errors
        
        for client_name, credentials in clients_dict.items():
            if not isinstance(credentials, dict):
                errors.append(f"Credentials for '{client_name}' must be a dictionary")
                continue
            
            required_keys = ["username", "password"]
            missing_keys = [key for key in required_keys if key not in credentials]
            
            if missing_keys:
                errors.append(f"Client '{client_name}' missing keys: {missing_keys}")
                continue
            
            # Check for empty values
            empty_fields = [key for key in required_keys if not credentials[key].strip()]
            if empty_fields:
                errors.append(f"Client '{client_name}' has empty fields: {empty_fields}")
        
        return len(errors) == 0, errors
    
    def get_sample_excel_data(self) -> Dict[str, List[str]]:
        """
        Generate sample data for creating a template Excel file.
        
        Returns:
            Dict[str, List[str]]: Sample data in format suitable for DataFrame creation
        """
        return {
            EXCEL_COLUMN_CLIENT_NAME: [
                "Sample Client 1",
                "Sample Client 2", 
                "Sample Client 3"
            ],
            EXCEL_COLUMN_GST_USERNAME: [
                "sample_username_1",
                "sample_username_2",
                "sample_username_3"
            ],
            EXCEL_COLUMN_GST_PASSWORD: [
                "sample_password_1",
                "sample_password_2", 
                "sample_password_3"
            ]
        }
    
    def create_sample_excel_file(self, output_path: str) -> bool:
        """
        Create a sample Excel file with the correct format.
        
        Args:
            output_path (str): Path where to save the sample file
            
        Returns:
            bool: True if file was created successfully, False otherwise
        """
        try:
            sample_data = self.get_sample_excel_data()
            df = pd.DataFrame(sample_data)
            df.to_excel(output_path, index=False)
            self.logger.info(f"Sample Excel file created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sample Excel file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, any]:
        """
        Get information about an Excel file without fully loading it.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            Dict[str, any]: File information including size, modification time, etc.
        """
        info = {
            "exists": False,
            "size": 0,
            "modified": None,
            "readable": False
        }
        
        try:
            if os.path.exists(file_path):
                info["exists"] = True
                stat = os.stat(file_path)
                info["size"] = stat.st_size
                info["modified"] = stat.st_mtime
                info["readable"] = os.access(file_path, os.R_OK)
        
        except Exception as e:
            self.logger.warning(f"Could not get file info for {file_path}: {e}")
        
        return info

# Convenience function for backward compatibility
def load_clients_from_excel_legacy(file_path: str, silent: bool = False) -> Tuple[Dict[str, Dict[str, str]], Optional[str]]:
    """
    Legacy function that returns client data in the old dictionary format.
    
    This function maintains backward compatibility with the original code structure.
    
    Args:
        file_path (str): Path to the Excel file
        silent (bool): If True, suppress detailed logging
        
    Returns:
        Tuple[Dict[str, Dict[str, str]], Optional[str]]: 
            - Dictionary with client data in legacy format
            - Error message if any errors occurred
    """
    service = ExcelService()
    client_manager, error = service.load_clients_from_excel(file_path, silent)
    
    if error:
        return {}, error
    
    return client_manager.to_dict(), None