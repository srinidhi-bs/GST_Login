"""
Validation utilities for GST Automation Application.

This module provides comprehensive validation functions for user inputs,
file formats, data integrity, and configuration validation.

Author: Srinidhi B S
"""
import re
import os
import datetime
from typing import Union, Optional, List, Tuple, Any, Dict
import pandas as pd

from config.settings import (
    REQUIRED_EXCEL_COLUMNS, DEFAULT_DATE_FORMAT,
    FINANCIAL_YEARS, QUARTERS, MONTHS
)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ValidatedResult:
    """
    Container class for validation results.
    
    This class provides a standardized way to return validation results
    with success/failure status and detailed error messages.
    """
    
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None, warnings: Optional[List[str]] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid (bool): Whether validation passed
            errors (Optional[List[str]]): List of error messages
            warnings (Optional[List[str]]): List of warning messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def get_summary(self) -> str:
        """Get a summary of all errors and warnings."""
        summary_parts = []
        
        if self.errors:
            summary_parts.append(f"Errors: {'; '.join(self.errors)}")
        
        if self.warnings:
            summary_parts.append(f"Warnings: {'; '.join(self.warnings)}")
        
        if not summary_parts:
            return "Validation passed"
        
        return " | ".join(summary_parts)
    
    def __bool__(self) -> bool:
        """Return validation status for boolean checks."""
        return self.is_valid
    
    def __str__(self) -> str:
        """String representation of validation result."""
        return f"ValidationResult(valid={self.is_valid}, errors={len(self.errors)}, warnings={len(self.warnings)})"

# === String Validation Functions ===

def validate_non_empty_string(value: str, field_name: str = "Field") -> ValidatedResult:
    """
    Validate that a string is not empty or just whitespace.
    
    Args:
        value (str): String to validate
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(value, str):
        result.add_error(f"{field_name} must be a string")
        return result
    
    if not value.strip():
        result.add_error(f"{field_name} cannot be empty")
    
    return result

def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None, 
                          field_name: str = "Field") -> ValidatedResult:
    """
    Validate string length constraints.
    
    Args:
        value (str): String to validate
        min_length (int): Minimum required length
        max_length (Optional[int]): Maximum allowed length
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(value, str):
        result.add_error(f"{field_name} must be a string")
        return result
    
    length = len(value.strip())
    
    if length < min_length:
        result.add_error(f"{field_name} must be at least {min_length} characters long")
    
    if max_length is not None and length > max_length:
        result.add_error(f"{field_name} cannot exceed {max_length} characters")
    
    return result

def validate_email_format(email: str, field_name: str = "Email") -> ValidatedResult:
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(email, str):
        result.add_error(f"{field_name} must be a string")
        return result
    
    email = email.strip()
    
    if not email:
        result.add_error(f"{field_name} cannot be empty")
        return result
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        result.add_error(f"{field_name} format is invalid")
    
    return result

# === Date Validation Functions ===

def validate_date_format(date_str: str, date_format: str = DEFAULT_DATE_FORMAT, 
                        field_name: str = "Date") -> ValidatedResult:
    """
    Validate date string format.
    
    Args:
        date_str (str): Date string to validate
        date_format (str): Expected date format
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(date_str, str):
        result.add_error(f"{field_name} must be a string")
        return result
    
    date_str = date_str.strip()
    
    if not date_str:
        result.add_error(f"{field_name} cannot be empty")
        return result
    
    try:
        datetime.datetime.strptime(date_str, date_format)
    except ValueError as e:
        result.add_error(f"{field_name} format is invalid. Expected format: {date_format}")
    
    return result

def validate_date_range(from_date: str, to_date: str, 
                       date_format: str = DEFAULT_DATE_FORMAT,
                       allow_same_date: bool = True) -> ValidatedResult:
    """
    Validate a date range (from_date <= to_date).
    
    Args:
        from_date (str): Start date string
        to_date (str): End date string
        date_format (str): Expected date format
        allow_same_date (bool): Whether from_date can equal to_date
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    # Validate individual date formats first
    from_validation = validate_date_format(from_date, date_format, "From Date")
    to_validation = validate_date_format(to_date, date_format, "To Date")
    
    result.errors.extend(from_validation.errors)
    result.errors.extend(to_validation.errors)
    
    if result.errors:
        result.is_valid = False
        return result
    
    # Compare dates
    try:
        from_dt = datetime.datetime.strptime(from_date.strip(), date_format)
        to_dt = datetime.datetime.strptime(to_date.strip(), date_format)
        
        if allow_same_date:
            if from_dt > to_dt:
                result.add_error("From Date cannot be later than To Date")
        else:
            if from_dt >= to_dt:
                result.add_error("From Date must be earlier than To Date")
    
    except ValueError:
        result.add_error("Could not compare dates")
    
    return result

# === File Validation Functions ===

def validate_file_exists(file_path: str, field_name: str = "File") -> ValidatedResult:
    """
    Validate that a file exists.
    
    Args:
        file_path (str): Path to the file
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(file_path, str):
        result.add_error(f"{field_name} path must be a string")
        return result
    
    file_path = file_path.strip()
    
    if not file_path:
        result.add_error(f"{field_name} path cannot be empty")
        return result
    
    if not os.path.exists(file_path):
        result.add_error(f"{field_name} does not exist: {file_path}")
    elif not os.path.isfile(file_path):
        result.add_error(f"{field_name} is not a file: {file_path}")
    
    return result

def validate_file_extension(file_path: str, allowed_extensions: List[str], 
                          field_name: str = "File") -> ValidatedResult:
    """
    Validate file extension.
    
    Args:
        file_path (str): Path to the file
        allowed_extensions (List[str]): List of allowed extensions (with or without dots)
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(file_path, str):
        result.add_error(f"{field_name} path must be a string")
        return result
    
    file_path = file_path.strip()
    
    if not file_path:
        result.add_error(f"{field_name} path cannot be empty")
        return result
    
    # Get file extension
    _, ext = os.path.splitext(file_path.lower())
    
    # Normalize allowed extensions (ensure they start with dot)
    normalized_extensions = []
    for allowed_ext in allowed_extensions:
        if not allowed_ext.startswith('.'):
            allowed_ext = '.' + allowed_ext
        normalized_extensions.append(allowed_ext.lower())
    
    if ext not in normalized_extensions:
        expected = ", ".join(normalized_extensions)
        result.add_error(f"{field_name} must have one of these extensions: {expected}")
    
    return result

def validate_excel_file_structure(file_path: str, required_columns: Optional[List[str]] = None) -> ValidatedResult:
    """
    Validate Excel file structure and columns.
    
    Args:
        file_path (str): Path to the Excel file
        required_columns (Optional[List[str]]): List of required column names
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    # Use default columns if none specified
    if required_columns is None:
        required_columns = REQUIRED_EXCEL_COLUMNS
    
    # First validate that file exists and is Excel
    file_validation = validate_file_exists(file_path, "Excel file")
    if not file_validation:
        result.errors.extend(file_validation.errors)
        return result
    
    ext_validation = validate_file_extension(file_path, ['.xlsx', '.xls'], "Excel file")
    if not ext_validation:
        result.errors.extend(ext_validation.errors)
        return result
    
    # Try to load and validate Excel structure
    try:
        df = pd.read_excel(file_path)
        
        # Check for required columns
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            result.add_error(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check if file has any data
        if df.empty:
            result.add_warning("Excel file is empty (no data rows)")
        else:
            # Check for completely empty required columns
            empty_columns = []
            for col in required_columns:
                if col in df.columns and df[col].isna().all():
                    empty_columns.append(col)
            
            if empty_columns:
                result.add_warning(f"Columns appear to be empty: {', '.join(empty_columns)}")
    
    except Exception as e:
        result.add_error(f"Could not read Excel file: {str(e)}")
    
    return result

# === Data Validation Functions ===

def validate_dropdown_selection(value: Any, allowed_values: List[Any], 
                               field_name: str = "Selection") -> ValidatedResult:
    """
    Validate that a value is in a list of allowed values.
    
    Args:
        value: Value to validate
        allowed_values (List[Any]): List of allowed values
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if value not in allowed_values:
        result.add_error(f"{field_name} is not a valid option. Allowed values: {allowed_values}")
    
    return result

def validate_index_in_range(index: int, max_index: int, field_name: str = "Index") -> ValidatedResult:
    """
    Validate that an index is within valid range.
    
    Args:
        index (int): Index to validate
        max_index (int): Maximum allowed index (exclusive)
        field_name (str): Name of the field for error messages
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(index, int):
        result.add_error(f"{field_name} must be an integer")
        return result
    
    if index < 0:
        result.add_error(f"{field_name} cannot be negative")
    elif index >= max_index:
        result.add_error(f"{field_name} ({index}) is out of range (0 to {max_index - 1})")
    
    return result

# === Credential Validation Functions ===

def validate_gst_username(username: str) -> ValidatedResult:
    """
    Validate GST username format.
    
    Args:
        username (str): GST username to validate
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    # Basic validation
    basic_validation = validate_non_empty_string(username, "GST Username")
    if not basic_validation:
        result.errors.extend(basic_validation.errors)
        return result
    
    # Length validation
    length_validation = validate_string_length(username, min_length=3, max_length=50, field_name="GST Username")
    if not length_validation:
        result.errors.extend(length_validation.errors)
    
    # Additional GST-specific validation can be added here
    # (e.g., format checks if GST has specific username patterns)
    
    return result

def validate_gst_password(password: str) -> ValidatedResult:
    """
    Validate GST password strength.
    
    Args:
        password (str): GST password to validate
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    # Basic validation
    basic_validation = validate_non_empty_string(password, "GST Password")
    if not basic_validation:
        result.errors.extend(basic_validation.errors)
        return result
    
    # Length validation
    length_validation = validate_string_length(password, min_length=6, max_length=100, field_name="GST Password")
    if not length_validation:
        result.errors.extend(length_validation.errors)
    
    # Password strength warnings (not errors)
    password = password.strip()
    
    if len(password) < 8:
        result.add_warning("Password is less than 8 characters - consider using a stronger password")
    
    if password.isdigit():
        result.add_warning("Password contains only numbers - consider adding letters and symbols")
    
    if password.isalpha():
        result.add_warning("Password contains only letters - consider adding numbers and symbols")
    
    return result

# === Configuration Validation Functions ===

def validate_financial_year_index(index: int) -> ValidatedResult:
    """
    Validate financial year index.
    
    Args:
        index (int): Financial year index to validate
        
    Returns:
        ValidatedResult: Validation result
    """
    return validate_index_in_range(index, len(FINANCIAL_YEARS), "Financial Year Index")

def validate_quarter_index(index: int) -> ValidatedResult:
    """
    Validate quarter index.
    
    Args:
        index (int): Quarter index to validate
        
    Returns:
        ValidatedResult: Validation result
    """
    return validate_index_in_range(index, len(QUARTERS), "Quarter Index")

def validate_month_index(index: int) -> ValidatedResult:
    """
    Validate month index.
    
    Args:
        index (int): Month index to validate
        
    Returns:
        ValidatedResult: Validation result
    """
    return validate_index_in_range(index, len(MONTHS), "Month Index")

# === Comprehensive Validation Functions ===

def validate_client_credentials_dict(credentials: Dict[str, str]) -> ValidatedResult:
    """
    Validate client credentials dictionary.
    
    Args:
        credentials (Dict[str, str]): Dictionary with username and password keys
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(credentials, dict):
        result.add_error("Credentials must be a dictionary")
        return result
    
    # Check required keys
    required_keys = ["username", "password"]
    for key in required_keys:
        if key not in credentials:
            result.add_error(f"Missing required key: {key}")
    
    if result.errors:
        return result
    
    # Validate username
    username_validation = validate_gst_username(credentials["username"])
    if not username_validation:
        result.errors.extend(username_validation.errors)
    result.warnings.extend(username_validation.warnings)
    
    # Validate password
    password_validation = validate_gst_password(credentials["password"])
    if not password_validation:
        result.errors.extend(password_validation.errors)
    result.warnings.extend(password_validation.warnings)
    
    return result

def validate_automation_config_dict(config: Dict[str, Any]) -> ValidatedResult:
    """
    Validate complete automation configuration dictionary.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        ValidatedResult: Validation result
    """
    result = ValidatedResult(True)
    
    if not isinstance(config, dict):
        result.add_error("Configuration must be a dictionary")
        return result
    
    # Validate credentials section
    if "credentials" in config:
        cred_validation = validate_client_credentials_dict(config["credentials"])
        if not cred_validation:
            result.errors.extend([f"Credentials: {error}" for error in cred_validation.errors])
        result.warnings.extend([f"Credentials: {warning}" for warning in cred_validation.warnings])
    else:
        result.add_error("Missing credentials section")
    
    # Validate returns options if present
    if "returns_options" in config:
        returns_options = config["returns_options"]
        if isinstance(returns_options, dict):
            for index_field, max_value in [
                ("financial_year_index", len(FINANCIAL_YEARS)),
                ("quarter_index", len(QUARTERS)),
                ("month_index", len(MONTHS))
            ]:
                if index_field in returns_options:
                    index_validation = validate_index_in_range(
                        returns_options[index_field], 
                        max_value, 
                        index_field
                    )
                    if not index_validation:
                        result.errors.extend(index_validation.errors)
    
    # Validate credit ledger options if present
    if "credit_ledger_options" in config:
        ledger_options = config["credit_ledger_options"]
        if isinstance(ledger_options, dict):
            if "from_date" in ledger_options and "to_date" in ledger_options:
                date_validation = validate_date_range(
                    ledger_options["from_date"],
                    ledger_options["to_date"]
                )
                if not date_validation:
                    result.errors.extend([f"Credit Ledger: {error}" for error in date_validation.errors])
    
    return result

# === Utility Functions ===

def combine_validation_results(*results: ValidatedResult) -> ValidatedResult:
    """
    Combine multiple validation results into one.
    
    Args:
        *results: Variable number of ValidatedResult instances
        
    Returns:
        ValidatedResult: Combined result
    """
    combined = ValidatedResult(True)
    
    for result in results:
        if not result.is_valid:
            combined.is_valid = False
        combined.errors.extend(result.errors)
        combined.warnings.extend(result.warnings)
    
    return combined

def validate_all(**field_validations) -> ValidatedResult:
    """
    Validate multiple fields and combine results.
    
    Args:
        **field_validations: Keyword arguments where keys are field names
                           and values are validation results
        
    Returns:
        ValidatedResult: Combined validation result
    """
    combined = ValidatedResult(True)
    
    for field_name, validation_result in field_validations.items():
        if not isinstance(validation_result, ValidatedResult):
            continue
        
        if not validation_result.is_valid:
            combined.is_valid = False
        
        # Prefix errors with field name for clarity
        combined.errors.extend([f"{field_name}: {error}" for error in validation_result.errors])
        combined.warnings.extend([f"{field_name}: {warning}" for warning in validation_result.warnings])
    
    return combined

def create_validation_summary(results: Dict[str, ValidatedResult]) -> str:
    """
    Create a human-readable validation summary.
    
    Args:
        results (Dict[str, ValidatedResult]): Dictionary of field names to validation results
        
    Returns:
        str: Formatted validation summary
    """
    summary_lines = []
    
    total_errors = 0
    total_warnings = 0
    
    for field_name, result in results.items():
        if result.errors:
            total_errors += len(result.errors)
            summary_lines.append(f"❌ {field_name}: {'; '.join(result.errors)}")
        
        if result.warnings:
            total_warnings += len(result.warnings)
            summary_lines.append(f"⚠️  {field_name}: {'; '.join(result.warnings)}")
        
        if not result.errors and not result.warnings:
            summary_lines.append(f"✅ {field_name}: Valid")
    
    header = f"Validation Summary - {total_errors} errors, {total_warnings} warnings"
    
    if summary_lines:
        return header + "\n" + "\n".join(summary_lines)
    else:
        return header + "\nNo validation performed"