"""
Configuration settings for GST Automation Application.

This module contains all configuration constants and settings used throughout
the application. Centralizing configuration makes it easy to modify behavior
without changing code in multiple places.

Author: Srinidhi B S
"""
import os
from typing import List, Dict, Any

# === Application Information ===
APP_TITLE = "GST Portal Automation - Srinidhi B S"
APP_VERSION = "2.0.0"
APP_GEOMETRY = "1000x700"
AUTHOR_EMAIL = "mailsrinidhibs@gmail.com"
GITHUB_URL = "https://github.com/srinidhi-bs/GST_Login"

# === File and Directory Paths ===
DEFAULT_EXCEL_FILENAME = "clients.xlsx"
DOWNLOAD_FOLDER_NAME = "GST_Downloads"
CHROMEDRIVER_RELATIVE_PATH = os.path.join("chromedriver-linux64", "chromedriver")

# === Excel Column Names ===
# Expected column names in the client data Excel file
EXCEL_COLUMN_CLIENT_NAME = "Client Name"
EXCEL_COLUMN_GST_USERNAME = "GST Username"
EXCEL_COLUMN_GST_PASSWORD = "GST Password"

# List of required columns for validation
REQUIRED_EXCEL_COLUMNS = [
    EXCEL_COLUMN_CLIENT_NAME,
    EXCEL_COLUMN_GST_USERNAME,
    EXCEL_COLUMN_GST_PASSWORD
]

# === WebDriver Wait Times (in seconds) ===
# Different timeout values for various scenarios
WAIT_TIME_SHORT = 15        # Quick elements (forms, buttons)
WAIT_TIME_LONG = 40         # Slower loading elements (dashboards, reports)
WAIT_TIME_VERY_LONG = 75    # Very slow operations (heavy reports, file generation)
WAIT_TIME_MANUAL_CAPTCHA = 90  # Time for user to manually enter CAPTCHA

# === GST Portal URLs and Identifiers ===
GST_PORTAL_BASE_URL = "https://www.gst.gov.in/"
WELCOME_PAGE_URL_PART = "services.gst.gov.in/services/auth/fowelcome"

# Login form field IDs
LOGIN_FORM_USERNAME_ID = "username"
LOGIN_FORM_PASSWORD_ID = "user_pass"
LOGIN_FORM_CAPTCHA_ID = "captcha"

# Login form locators with multiple fallback strategies
class LoginFormLocators:
    """Comprehensive locators for login form elements."""
    
    # CAPTCHA field locators (multiple strategies for robustness)
    CAPTCHA_FIELD_ID = "captcha"
    CAPTCHA_FIELD_NAME = "captcha"
    CAPTCHA_FIELD_CSS_INPUT = "input[placeholder*='captcha' i]"  # Case insensitive
    CAPTCHA_FIELD_CSS_TYPE = "input[type='text']:last-of-type"  # Usually last text input
    CAPTCHA_FIELD_XPATH_ID = "//input[@id='captcha']"
    CAPTCHA_FIELD_XPATH_NAME = "//input[@name='captcha']"
    CAPTCHA_FIELD_XPATH_PLACEHOLDER = "//input[contains(@placeholder, 'captcha') or contains(@placeholder, 'Captcha') or contains(@placeholder, 'CAPTCHA')]"
    CAPTCHA_FIELD_XPATH_GENERIC = "//input[@type='text' and position()=last()]"  # Last text input field

# === GUI Configuration ===
# Financial year options for Returns Dashboard
FINANCIAL_YEARS: List[str] = [
    "2025-26", "2024-25", "2023-24", "2022-23", 
    "2021-22", "2020-21", "2019-20", "2018-19"
]

# Quarter options for Returns Dashboard (Legacy - GST portal no longer has quarters)
QUARTERS: List[str] = [
    "Quarter 1 (Apr-Jun)", "Quarter 2 (Jul-Sep)", 
    "Quarter 3 (Oct-Dec)", "Quarter 4 (Jan-Mar)"
]

# Period options for Returns Dashboard (New GST portal structure)
# These are the month options that appear in the "Period" dropdown
PERIODS: List[str] = [
    "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "January", "February", "March"
]

# Month options for Returns Dashboard (Legacy compatibility)
MONTHS: List[str] = PERIODS  # Same as periods now

# Default selections (indices)
DEFAULT_FINANCIAL_YEAR_INDEX = 0  # Current year (2025-26)
DEFAULT_QUARTER_INDEX = 1         # Second quarter (Jul-Sep) - current
DEFAULT_MONTH_INDEX = 1           # Second month option (usually August for Q2)
DEFAULT_PERIOD_INDEX = 4          # August (current month)

# === Chrome Browser Configuration ===
CHROME_DOWNLOAD_PREFERENCES: Dict[str, Any] = {
    "download.prompt_for_download": False,       # Auto-download without prompts
    "download.directory_upgrade": True,          # Allow directory changes
    "plugins.always_open_pdf_externally": True  # Open PDFs externally
}

# Chrome options for automation (commented out options for future use)
CHROME_OPTIONS = {
    "headless": False,        # Set to True for headless mode (no UI)
    "disable_gpu": False,     # Set to True when using headless mode
    "maximize_window": True,  # Maximize browser window for better element visibility
}

# === Web Element Locators ===
# This section contains all the locators used for finding web elements
# Organized by functionality for easier maintenance

class Locators:
    """Container class for all web element locators used in automation."""
    
    # === Login Page Locators ===
    class Login:
        # Multiple locator strategies for robustness
        LOGIN_LINK_XPATH = "//a[contains(@href,'login') and normalize-space()='Login']"
        LOGIN_LINK_FALLBACK_XPATH = "/html/body/div[1]/header/div[2]/div/div/ul/li[2]"
        
        DIMMER_OVERLAY_CLASS = "dimmer-holder"
        
        # Post-login popup - Updated for current GST portal structure
        POPUP_CLOSE_XPATH = "//*[normalize-space()='Remind me later']"
    
    # === Returns Dashboard Locators ===
    class ReturnsDashboard:
        # Returns Dashboard button (multiple fallback strategies)
        BUTTON_CSS = "button[onclick*='return.gst.gov.in/returns/auth/dashboard']"
        BUTTON_XPATH_ALT = "//button[.//span[normalize-space()='Return Dashboard']]"
        BUTTON_XPATH_FALLBACK = "/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/button/span"
        
        # EXACT locators based on actual GST portal HTML (Aug 2025)
        # Financial Year: <select name="fin" class="form-control...">
        YEAR_SELECT_CSS = "select[name='fin']"
        YEAR_SELECT_CSS_ALT = "select.form-control[name='fin']"
        
        # Quarter: <select name="quarter" class="form-control...">  
        QUARTER_SELECT_CSS = "select[name='quarter']"
        QUARTER_SELECT_CSS_ALT = "select.form-control[name='quarter']"
        
        # Period/Month: <select name="mon" class="form-control...">
        MONTH_SELECT_CSS = "select[name='mon']"
        MONTH_SELECT_CSS_ALT = "select.form-control[name='mon']"
        PERIOD_SELECT_CSS = "select[name='mon']"  # Same as month
        PERIOD_SELECT_CSS_ALT = "select.form-control[name='mon']"
        
        # Fallback name-based selectors (legacy)
        YEAR_SELECT_NAME = "fin"
        QUARTER_SELECT_NAME = "quarter" 
        MONTH_SELECT_NAME = "mon"
        PERIOD_SELECT_NAME = "period"  # New period selector name
        
        # Alternative CSS selectors with common form classes
        YEAR_SELECT_CSS_ALT = "select.form-control"  # Bootstrap form control
        QUARTER_SELECT_CSS_ALT = "select.form-control:nth-of-type(2)"
        MONTH_SELECT_CSS_ALT = "select.form-control:nth-of-type(2)"  # Same as period now
        PERIOD_SELECT_CSS_ALT = "select.form-control:nth-of-type(2)"
        
        # XPath locators based on exact HTML structure
        YEAR_SELECT_XPATH = "//select[@name='fin']"
        YEAR_SELECT_XPATH_ALT = "//select[@name='fin' and contains(@class, 'form-control')]"
        
        QUARTER_SELECT_XPATH = "//select[@name='quarter']"
        QUARTER_SELECT_XPATH_ALT = "//select[@name='quarter' and contains(@class, 'form-control')]"
        
        MONTH_SELECT_XPATH = "//select[@name='mon']"
        MONTH_SELECT_XPATH_ALT = "//select[@name='mon' and contains(@class, 'form-control')]"
        
        PERIOD_SELECT_XPATH = "//select[@name='mon']"  # Same as month
        PERIOD_SELECT_XPATH_ALT = "//select[@name='mon' and contains(@class, 'form-control')]"
        
        # Generic form-based selectors
        YEAR_SELECT_GENERIC = "form select:first-child"
        QUARTER_SELECT_GENERIC = "form select:nth-child(2)" 
        MONTH_SELECT_GENERIC = "form select:nth-child(2)"  # Same as period
        PERIOD_SELECT_GENERIC = "form select:nth-child(2)"
        
        # Search button - updated for current portal
        SEARCH_BUTTON_CSS = "button[type='submit']"  # Any submit button
        SEARCH_BUTTON_XPATH_ALT = "//button[normalize-space()='SEARCH']"  # Exact text match
        SEARCH_BUTTON_XPATH_FALLBACK = "//button[contains(text(), 'Search') or contains(text(), 'SEARCH')]"
    
    # === GSTR-2B Download Locators ===
    class GSTR2B:
        INITIAL_DOWNLOAD_BUTTON_CSS = "button[data-ng-click='offlinepath(x.return_ty)']"
        GENERATE_EXCEL_BUTTON_XPATH = "//button[normalize-space()='GENERATE EXCEL FILE TO DOWNLOAD']"
    
    # === Electronic Credit Ledger Locators ===
    class CreditLedger:
        # Navigation menu locators
        SERVICES_MENU_XPATH = "//a[contains(@class, 'dropdown-toggle') and starts-with(normalize-space(.), 'Services')]"
        LEDGERS_SUBMENU_LINK = "Ledgers"  # Used with By.LINK_TEXT
        
        # Direct credit ledger link from hover menu
        DIRECT_LINK_XPATH = "//a[@href='//return.gst.gov.in/returns/auth/ledger/itcledger' and normalize-space()='Electronic Credit Ledger']"
        
        # Detailed view link
        DETAILED_LINK_CSS = "a[data-ng-bind='trans.LBL_ELEC_CREDIT_LEDG']"
        
        # Date input fields
        FROM_DATE_FIELD_ID = "sumlg_frdt"
        TO_DATE_FIELD_ID = "sumlg_todt"
        
        # Go button
        GO_BUTTON_CSS = "button[data-ng-click='getdetLdgr()']"
    
    # === Electronic Cash Ledger Locators ===
    class CashLedger:
        # Navigation menu locators (same as Credit Ledger)
        SERVICES_MENU_XPATH = "//a[contains(@class, 'dropdown-toggle') and starts-with(normalize-space(.), 'Services')]"
        LEDGERS_SUBMENU_LINK = "Ledgers"  # Used with By.LINK_TEXT
        
        # Cash ledger specific link (assumed - may need user verification)
        DIRECT_LINK_XPATH = "//a[@href='//payment.gst.gov.in/payment/auth/ledger/cashledger' and normalize-space()='Electronic Cash Ledger']"
        
        # Balance details link
        BALANCE_DETAILS_CSS = "a.inverseLink[data-target='#balanceModal']"

# === Status Messages ===
# Predefined status messages for consistent logging
class StatusMessages:
    """Container class for standardized status messages."""
    
    # Application startup
    APP_STARTING = "GST Automation Application starting..."
    LOADING_CLIENTS = "Loading clients from Excel file..."
    CLIENTS_LOADED = "Successfully loaded {count} clients."
    
    # WebDriver initialization
    WEBDRIVER_INIT = "Initializing Chrome WebDriver..."
    DOWNLOAD_DIR_CREATED = "Downloads will be saved to: {path}"
    
    # Navigation
    NAVIGATING_TO_PORTAL = "Navigating to GST portal..."
    LOGIN_LINK_CLICKED = "Clicked on Login link."
    CREDENTIALS_ENTERED = "Username and password entered."
    
    # CAPTCHA handling
    CAPTCHA_PROMPT = "IMPORTANT: Please enter the CAPTCHA in the browser and click Login. You have {timeout} seconds."
    LOGIN_SUCCESS = "Login successful. Navigated to welcome page."
    
    # Actions
    RETURNS_DASHBOARD_CLICKED = "Clicked Returns Dashboard button."
    GSTR2B_DOWNLOAD_STARTED = "Attempting to download GSTR-2B..."
    CREDIT_LEDGER_ACCESS = "Navigating to Electronic Credit Ledger..."
    
    # Completion
    AUTOMATION_COMPLETE = "Automation actions completed (or reached selected point)."
    BROWSER_CLOSED = "Browser closed."

# === Error Messages ===
class ErrorMessages:
    """Container class for standardized error messages."""
    
    EXCEL_FILE_NOT_FOUND = "Excel file not found at: {path}. Please select a valid file."
    EXCEL_MISSING_COLUMNS = "Missing required columns in Excel: {columns}\nExpected: Client Name, GST Username, GST Password"
    EMPTY_CREDENTIALS = "Username and Password cannot be empty. Please select a client or enter credentials manually."
    TIMEOUT_ERROR = "A major timeout occurred: {error}"
    GENERAL_ERROR = "An error occurred during automation: {error}"

# === Logging Configuration ===
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_DATE_FORMAT = "%d-%m-%Y"  # Format for date entry fields

# === Development and Debug Settings ===
DEBUG_MODE = False  # Set to True to enable debug features
SAVE_SCREENSHOTS_ON_ERROR = True  # Save screenshots when errors occur
SCREENSHOT_PREFIX = "debug_"