"""
GST Portal-specific automation service.

This module provides specialized automation methods for GST portal interactions
including login, returns dashboard navigation, GSTR-2B downloads, and ledger access.

Author: Srinidhi B S
"""
import time
import logging
from typing import Callable, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from services.web_automation_service import (
    WebAutomationService, ElementNotFoundError, AutomationTimeoutError
)
from config.settings import (
    GST_PORTAL_BASE_URL, WELCOME_PAGE_URL_PART,
    LOGIN_FORM_USERNAME_ID, LOGIN_FORM_PASSWORD_ID, LOGIN_FORM_CAPTCHA_ID,
    WAIT_TIME_SHORT, WAIT_TIME_LONG, WAIT_TIME_VERY_LONG, WAIT_TIME_MANUAL_CAPTCHA,
    Locators, StatusMessages, ErrorMessages, LoginFormLocators
)
from models.client_data import (
    ClientCredentials, AutomationSettings, 
    ReturnsDashboardOptions, CreditLedgerOptions
)

# Set up logging for this module
logger = logging.getLogger(__name__)

class GSTPortalLoginError(Exception):
    """Custom exception for GST portal login failures."""
    pass

class GSTPortalNavigationError(Exception):
    """Custom exception for GST portal navigation failures."""
    pass

class GSTPortalService(WebAutomationService):
    """
    Service class for GST portal-specific automation operations.
    
    This class extends WebAutomationService with methods specifically
    designed for GST portal interactions.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None, headless: bool = False):
        """
        Initialize the GST portal automation service.
        
        Args:
            status_callback (Optional[Callable[[str], None]]): Callback function for status updates
            headless (bool): If True, run browser in headless mode
        """
        super().__init__(headless=headless)
        self.status_callback = status_callback or self._default_status_callback
        self.logger = logging.getLogger(__name__)
    
    def _default_status_callback(self, message: str) -> None:
        """Default status callback that just logs the message."""
        self.logger.info(message)
    
    def _log_status(self, message: str) -> None:
        """Log status message and call status callback."""
        self.logger.info(message)
        if self.status_callback:
            self.status_callback(message)
    
    def navigate_to_portal(self) -> None:
        """
        Navigate to the GST portal homepage.
        
        Raises:
            GSTPortalNavigationError: If navigation fails
        """
        try:
            self._log_status(StatusMessages.NAVIGATING_TO_PORTAL)
            self.navigate_to_url(GST_PORTAL_BASE_URL)
            self._log_status("Successfully navigated to GST portal")
        except Exception as e:
            error_msg = f"Failed to navigate to GST portal: {str(e)}"
            self.logger.error(error_msg)
            raise GSTPortalNavigationError(error_msg) from e
    
    def click_login_link(self) -> None:
        """
        Click the Login link on the GST portal homepage.
        
        Raises:
            ElementNotFoundError: If login link cannot be found or clicked
        """
        login_link_locators = [
            (By.XPATH, Locators.Login.LOGIN_LINK_XPATH),
            (By.XPATH, Locators.Login.LOGIN_LINK_FALLBACK_XPATH)
        ]
        
        try:
            self.click_element_with_fallbacks(
                login_link_locators, 
                WAIT_TIME_LONG,
                "Login link"
            )
            self._log_status(StatusMessages.LOGIN_LINK_CLICKED)
        except ElementNotFoundError as e:
            error_msg = "Could not find or click the Login link on GST portal"
            self.logger.error(error_msg)
            raise ElementNotFoundError(error_msg) from e
    
    def wait_for_page_overlay_to_disappear(self) -> None:
        """Wait for any page overlays or loaders to disappear."""
        try:
            self._log_status("Waiting for page overlay to disappear (if any)...")
            success = self.wait_for_element_invisible(
                By.CLASS_NAME, 
                Locators.Login.DIMMER_OVERLAY_CLASS, 
                WAIT_TIME_SHORT
            )
            if success:
                self._log_status("Overlay disappeared")
            else:
                self._log_status("No overlay found or it was persistent - proceeding...")
        except Exception as e:
            self.logger.debug(f"Error waiting for overlay: {e}")
            # This is not critical, so we continue
    
    def fill_login_credentials(self, credentials: ClientCredentials) -> None:
        """
        Fill the login form with provided credentials.
        
        Args:
            credentials (ClientCredentials): Client credentials to use for login
            
        Raises:
            ElementNotFoundError: If form fields cannot be found
        """
        try:
            # Wait for and fill username field (using original working approach)
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            WebDriverWait(self.driver, WAIT_TIME_LONG).until(
                EC.visibility_of_element_located((By.ID, LOGIN_FORM_USERNAME_ID))
            )
            
            username_element = self.driver.find_element(By.ID, LOGIN_FORM_USERNAME_ID)
            username_element.clear()
            username_element.send_keys(credentials.username)
            self._log_status("Entered username")
            
            # Fill password field (using original working approach)
            password_element = self.driver.find_element(By.ID, LOGIN_FORM_PASSWORD_ID)
            password_element.clear()
            password_element.send_keys(credentials.password)
            self._log_status("Entered password")
            
        except Exception as e:
            error_msg = f"Could not find login form fields: {str(e)}"
            self.logger.error(error_msg)
            raise ElementNotFoundError(error_msg) from e
    
    def handle_captcha_input(self) -> bool:
        """
        Handle CAPTCHA input by user (manual process).
        
        This method waits for the user to manually enter CAPTCHA
        and submit the login form.
        
        Returns:
            bool: True if login was successful, False if timeout
            
        Raises:
            GSTPortalLoginError: If CAPTCHA handling fails
        """
        try:
            # Wait for overlay to disappear and click CAPTCHA field to focus
            self.wait_for_page_overlay_to_disappear()
            
            # Multiple CAPTCHA field locator strategies for robustness
            captcha_locators = [
                (By.ID, LoginFormLocators.CAPTCHA_FIELD_ID),
                (By.NAME, LoginFormLocators.CAPTCHA_FIELD_NAME),
                (By.CSS_SELECTOR, LoginFormLocators.CAPTCHA_FIELD_CSS_INPUT),
                (By.CSS_SELECTOR, LoginFormLocators.CAPTCHA_FIELD_CSS_TYPE),
                (By.XPATH, LoginFormLocators.CAPTCHA_FIELD_XPATH_ID),
                (By.XPATH, LoginFormLocators.CAPTCHA_FIELD_XPATH_NAME),
                (By.XPATH, LoginFormLocators.CAPTCHA_FIELD_XPATH_PLACEHOLDER),
                (By.XPATH, LoginFormLocators.CAPTCHA_FIELD_XPATH_GENERIC)
            ]
            self.click_element_with_fallbacks(
                captcha_locators,
                WAIT_TIME_LONG,
                "CAPTCHA field"
            )
            
            # Notify user to enter CAPTCHA
            captcha_message = StatusMessages.CAPTCHA_PROMPT.format(timeout=WAIT_TIME_MANUAL_CAPTCHA)
            self._log_status(captcha_message)
            
            # Wait for successful login (URL change indicates success)
            success = self.wait_for_url_change(WELCOME_PAGE_URL_PART, WAIT_TIME_MANUAL_CAPTCHA)
            
            if success:
                self._log_status(StatusMessages.LOGIN_SUCCESS)
                return True
            else:
                error_msg = "Login timeout - user may not have completed CAPTCHA or login failed"
                self.logger.warning(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error during CAPTCHA handling: {str(e)}"
            self.logger.error(error_msg)
            raise GSTPortalLoginError(error_msg) from e
    
    def handle_post_login_popups(self) -> None:
        """Handle any popups that appear after successful login."""
        try:
            time.sleep(2)  # Brief pause for page stabilization
            
            popup_locators = [(By.XPATH, Locators.Login.POPUP_CLOSE_XPATH)]
            self.click_element_with_fallbacks(
                popup_locators,
                WAIT_TIME_SHORT,
                "post-login popup close button"
            )
            self._log_status("Closed post-login popup")
            time.sleep(1)
            
        except ElementNotFoundError:
            self._log_status("No post-login popup found (this is normal)")
        except Exception as e:
            self.logger.debug(f"Error handling post-login popup: {e}")
            # Not critical, continue
    
    def perform_login(self, credentials: ClientCredentials) -> bool:
        """
        Perform complete login process to GST portal.
        
        Args:
            credentials (ClientCredentials): Client credentials for login
            
        Returns:
            bool: True if login successful, False otherwise
            
        Raises:
            GSTPortalLoginError: If login process fails
        """
        try:
            self.navigate_to_portal()
            self.click_login_link()
            self.wait_for_page_overlay_to_disappear()
            self.fill_login_credentials(credentials)
            
            login_success = self.handle_captcha_input()
            
            if login_success:
                self.handle_post_login_popups()
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"Login process failed: {str(e)}"
            self.logger.error(error_msg)
            raise GSTPortalLoginError(error_msg) from e
    
    def navigate_to_returns_dashboard(self) -> None:
        """
        Navigate to the Returns Dashboard from the main portal.
        
        Raises:
            GSTPortalNavigationError: If navigation fails
        """
        try:
            self._log_status("Navigating to Returns Dashboard...")
            
            returns_dashboard_locators = [
                (By.CSS_SELECTOR, Locators.ReturnsDashboard.BUTTON_CSS),
                (By.XPATH, Locators.ReturnsDashboard.BUTTON_XPATH_ALT),
                (By.XPATH, Locators.ReturnsDashboard.BUTTON_XPATH_FALLBACK)
            ]
            
            self.click_element_with_fallbacks(
                returns_dashboard_locators,
                WAIT_TIME_LONG,
                "Returns Dashboard button"
            )
            
            self._log_status(StatusMessages.RETURNS_DASHBOARD_CLICKED)
            time.sleep(3)  # Wait for dashboard page to load
            
        except ElementNotFoundError as e:
            error_msg = "Could not find Returns Dashboard button"
            self.logger.error(error_msg)
            raise GSTPortalNavigationError(error_msg) from e
    
    def filter_returns_dashboard(self, options: ReturnsDashboardOptions) -> None:
        """
        Apply filters on the Returns Dashboard.
        
        Args:
            options (ReturnsDashboardOptions): Filter options to apply
            
        Raises:
            GSTPortalNavigationError: If filtering fails
        """
        try:
            self._log_status("Applying filters on Returns Dashboard...")
            
            # Wait for Angular to fully initialize the dropdowns
            # The dropdowns exist but Angular needs time to make them interactive
            self._log_status("Waiting for Angular dropdowns to initialize...")
            
            # DEBUG: Let's see what elements ARE available to Selenium
            try:
                all_selects = self.driver.find_elements(By.TAG_NAME, "select")
                self._log_status(f"DEBUG: Found {len(all_selects)} select elements total")
                
                for i, select in enumerate(all_selects):
                    try:
                        name = select.get_attribute("name") or "no-name"
                        classes = select.get_attribute("class") or "no-class"
                        visible = select.is_displayed()
                        enabled = select.is_enabled()
                        self._log_status(f"DEBUG: Select {i}: name='{name}', class='{classes}', visible={visible}, enabled={enabled}")
                    except Exception as e:
                        self._log_status(f"DEBUG: Select {i}: Error getting attributes: {e}")
                        
                # Check if we're in the right frame
                current_url = self.driver.current_url
                self._log_status(f"DEBUG: Current URL: {current_url}")
                
                # Check for iframes
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                self._log_status(f"DEBUG: Found {len(iframes)} iframes")
                
            except Exception as e:
                self._log_status(f"DEBUG: Error during debugging: {e}")
            
            # DIRECT approach - bypass the broken find_element_with_fallbacks method
            try:
                # Since we know the elements exist (debug showed them), use direct calls
                fin_dropdown = self.driver.find_element(By.NAME, "fin")
                self._log_status("SUCCESS: Found Financial Year dropdown directly!")
            except Exception as e:
                self._log_status(f"DIRECT method failed: {e}")
                raise
            
            # Extra wait for Angular to fully initialize all form states
            self._log_status("Waiting for Angular to complete initialization...")
            time.sleep(5)  # Increased wait time for Angular
            
            # Select Financial Year - DIRECT approach  
            try:
                fin_dropdown = self.driver.find_element(By.NAME, "fin")
                from selenium.webdriver.support.ui import Select
                select_fin = Select(fin_dropdown)
                select_fin.select_by_index(options.financial_year_index)
                self._log_status(f"SUCCESS: Selected Financial Year (index: {options.financial_year_index})")
            except Exception as e:
                self._log_status(f"FAILED: Could not select Financial Year: {e}")
                raise
            self._log_status(f"Selected Financial Year (index: {options.financial_year_index})")
            time.sleep(0.5)
            
            # Select Quarter - DIRECT approach
            try:
                quarter_dropdown = self.driver.find_element(By.NAME, "quarter")
                from selenium.webdriver.support.ui import Select
                select_quarter = Select(quarter_dropdown)
                select_quarter.select_by_index(options.quarter_index)
                self._log_status(f"SUCCESS: Selected Quarter (index: {options.quarter_index})")
            except Exception as e:
                self._log_status(f"FAILED: Could not select Quarter: {e}")
                raise
            self._log_status(f"Selected Quarter (index: {options.quarter_index})")
            time.sleep(0.5)
            
            # Select Period/Month - DIRECT approach
            try:
                month_dropdown = self.driver.find_element(By.NAME, "mon")
                from selenium.webdriver.support.ui import Select
                select_month = Select(month_dropdown)
                select_month.select_by_index(options.month_index)
                self._log_status(f"SUCCESS: Selected Month (index: {options.month_index})")
            except Exception as e:
                self._log_status(f"FAILED: Could not select Month: {e}")
                raise
            self._log_status(f"Selected Month (index: {options.month_index})")
            time.sleep(1)
            
            # Click Search button - DIRECT approach
            try:
                # Try multiple direct approaches for search button
                search_button = None
                try:
                    search_button = self.driver.find_element(By.XPATH, "//button[normalize-space()='SEARCH']")
                except:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                
                search_button.click()
                self._log_status("SUCCESS: Clicked Search button")
            except Exception as e:
                self._log_status(f"FAILED: Could not click Search button: {e}")
                raise
            self._log_status("Clicked Search button on Returns Dashboard")
            time.sleep(2)
            
        except (ElementNotFoundError, Exception) as e:
            error_msg = f"Failed to filter Returns Dashboard: {str(e)}"
            self.logger.error(error_msg)
            raise GSTPortalNavigationError(error_msg) from e
    
    def download_gstr2b(self) -> None:
        """
        Download GSTR-2B report from Returns Dashboard.
        
        Raises:
            GSTPortalNavigationError: If download process fails
        """
        try:
            self._log_status("Attempting to download GSTR-2B...")
            
            # Try to click initial download button
            try:
                initial_download_locators = [(By.CSS_SELECTOR, Locators.GSTR2B.INITIAL_DOWNLOAD_BUTTON_CSS)]
                self.click_element_with_fallbacks(
                    initial_download_locators,
                    WAIT_TIME_SHORT,
                    "GSTR-2B initial download button"
                )
                self._log_status("Clicked GSTR-2B 'Download' button")
                time.sleep(3)
            except ElementNotFoundError:
                self._log_status("Initial download button not found - may need to navigate differently")
            
            # Click generate Excel file button
            try:
                excel_generate_locators = [(By.XPATH, Locators.GSTR2B.GENERATE_EXCEL_BUTTON_XPATH)]
                self.click_element_with_fallbacks(
                    excel_generate_locators,
                    WAIT_TIME_SHORT,
                    "GSTR-2B generate Excel button"
                )
                self._log_status("Clicked 'GENERATE EXCEL FILE TO DOWNLOAD' button")
                self._log_status("GSTR-2B Excel download should start. Check your 'GST_Downloads' folder.")
                time.sleep(15)  # Wait for file generation and download
                
            except ElementNotFoundError as e:
                error_msg = "Could not find 'GENERATE EXCEL FILE TO DOWNLOAD' button"
                self.logger.error(error_msg)
                self._log_status("GSTR-2B download failed - button not found on the page")
                
        except Exception as e:
            error_msg = f"GSTR-2B download process failed: {str(e)}"
            self.logger.error(error_msg)
            raise GSTPortalNavigationError(error_msg) from e
    
    def navigate_to_credit_ledger(self, options: CreditLedgerOptions) -> None:
        """
        Navigate to Electronic Credit Ledger and set date range.
        
        Args:
            options (CreditLedgerOptions): Date range options for credit ledger
            
        Raises:
            GSTPortalNavigationError: If navigation fails
        """
        try:
            self._log_status("Navigating to Electronic Credit Ledger...")
            
            # Click Services menu
            services_locators = [(By.XPATH, Locators.CreditLedger.SERVICES_MENU_XPATH)]
            self.click_element_with_fallbacks(
                services_locators,
                WAIT_TIME_SHORT,
                "Services menu"
            )
            self._log_status("Clicked 'Services' menu")
            time.sleep(1)
            
            # Hover over Ledgers submenu
            ledgers_locators = [(By.LINK_TEXT, Locators.CreditLedger.LEDGERS_SUBMENU_LINK)]
            self.hover_over_element(
                ledgers_locators,
                WAIT_TIME_SHORT,
                "Ledgers submenu"
            )
            self._log_status("Hovered over 'Ledgers' submenu")
            
            # Click Electronic Credit Ledger from hover menu
            credit_ledger_locators = [(By.XPATH, Locators.CreditLedger.DIRECT_LINK_XPATH)]
            self.click_element_with_fallbacks(
                credit_ledger_locators,
                WAIT_TIME_LONG,
                "Electronic Credit Ledger link"
            )
            self._log_status("Clicked 'Electronic Credit Ledger' from hover menu")
            
            # Click detailed credit ledger link
            detailed_link_locators = [(By.CSS_SELECTOR, Locators.CreditLedger.DETAILED_LINK_CSS)]
            self.click_element_with_fallbacks(
                detailed_link_locators,
                WAIT_TIME_LONG,
                "detailed Electronic Credit Ledger link"
            )
            self._log_status("Clicked detailed 'Electronic Credit Ledger' link")
            time.sleep(2)
            
            # Set date range
            self._set_credit_ledger_dates(options)
            
        except Exception as e:
            error_msg = f"Failed to navigate to Electronic Credit Ledger: {str(e)}"
            self.logger.error(error_msg)
            if self.save_debug_screenshot:
                self.save_debug_screenshot("credit_ledger_navigation_error")
            raise GSTPortalNavigationError(error_msg) from e
    
    def _set_credit_ledger_dates(self, options: CreditLedgerOptions) -> None:
        """
        Set date range for credit ledger query.
        
        Args:
            options (CreditLedgerOptions): Date range options
        """
        try:
            self._log_status(f"Setting credit ledger dates: From {options.from_date} To {options.to_date}")
            
            # Set From Date
            from_date_locators = [(By.ID, Locators.CreditLedger.FROM_DATE_FIELD_ID)]
            from_date_element = self.find_element_with_fallbacks(
                from_date_locators,
                WAIT_TIME_SHORT,
                "From Date field"
            )
            from_date_element.clear()
            from_date_element.click()
            from_date_element.send_keys(options.from_date)
            self._log_status(f"Entered 'From Date': {options.from_date}")
            
            # Click elsewhere to close date picker
            self.execute_javascript("document.body.click();")
            time.sleep(0.5)
            
            # Set To Date
            to_date_locators = [(By.ID, Locators.CreditLedger.TO_DATE_FIELD_ID)]
            to_date_element = self.find_element_with_fallbacks(
                to_date_locators,
                WAIT_TIME_SHORT,
                "To Date field"
            )
            to_date_element.clear()
            to_date_element.click()
            to_date_element.send_keys(options.to_date)
            self._log_status(f"Entered 'To Date': {options.to_date}")
            
            # Click elsewhere to close date picker
            self.execute_javascript("document.body.click();")
            time.sleep(0.5)
            
            # Click GO button
            go_button_locators = [(By.CSS_SELECTOR, Locators.CreditLedger.GO_BUTTON_CSS)]
            self.click_element_with_fallbacks(
                go_button_locators,
                WAIT_TIME_SHORT,
                "GO button"
            )
            self._log_status("Clicked 'GO' button for credit ledger dates")
            time.sleep(2)
            
        except Exception as e:
            error_msg = f"Could not set credit ledger dates: {str(e)}"
            self.logger.warning(error_msg)
            self._log_status("Date setting failed - you may need to set dates manually")
            time.sleep(15)  # Pause for manual intervention if needed
    
    def navigate_to_cash_ledger(self) -> None:
        """
        Navigate to Electronic Cash Ledger.
        
        Raises:
            GSTPortalNavigationError: If navigation fails
        """
        try:
            self._log_status("Navigating to Electronic Cash Ledger...")
            
            # Click Services menu
            services_locators = [(By.XPATH, Locators.CashLedger.SERVICES_MENU_XPATH)]
            self.click_element_with_fallbacks(
                services_locators,
                WAIT_TIME_SHORT,
                "Services menu"
            )
            self._log_status("Clicked 'Services' menu")
            time.sleep(1)
            
            # Hover over Ledgers submenu
            ledgers_locators = [(By.LINK_TEXT, Locators.CashLedger.LEDGERS_SUBMENU_LINK)]
            self.hover_over_element(
                ledgers_locators,
                WAIT_TIME_SHORT,
                "Ledgers submenu"
            )
            self._log_status("Hovered over 'Ledgers' submenu")
            
            # Click Electronic Cash Ledger from hover menu
            cash_ledger_locators = [(By.XPATH, Locators.CashLedger.DIRECT_LINK_XPATH)]
            self.click_element_with_fallbacks(
                cash_ledger_locators,
                WAIT_TIME_LONG,
                "Electronic Cash Ledger link"
            )
            self._log_status("Clicked 'Electronic Cash Ledger' from hover menu")
            time.sleep(2)
            
            # Click balance details link
            balance_details_locators = [(By.CSS_SELECTOR, Locators.CashLedger.BALANCE_DETAILS_CSS)]
            self.click_element_with_fallbacks(
                balance_details_locators,
                WAIT_TIME_LONG,
                "cash ledger balance details link"
            )
            self._log_status("Clicked link to view cash ledger balance details")
            time.sleep(3)
            
        except Exception as e:
            error_msg = f"Failed to navigate to Electronic Cash Ledger: {str(e)}"
            self.logger.error(error_msg)
            if self.save_debug_screenshot:
                self.save_debug_screenshot("cash_ledger_navigation_error")
            raise GSTPortalNavigationError(error_msg) from e
    
    def execute_automation_workflow(self, credentials: ClientCredentials, 
                                  settings: AutomationSettings,
                                  returns_options: ReturnsDashboardOptions,
                                  credit_ledger_options: CreditLedgerOptions,
                                  keep_browser_open: bool = True) -> bool:
        """
        Execute the complete automation workflow based on user settings.
        
        Args:
            credentials (ClientCredentials): Client credentials for login
            settings (AutomationSettings): Selected automation actions
            returns_options (ReturnsDashboardOptions): Returns Dashboard settings
            credit_ledger_options (CreditLedgerOptions): Credit Ledger date range
            keep_browser_open (bool): If True, keep browser open after completion (default: True)
            
        Returns:
            bool: True if workflow completed successfully, False otherwise
        """
        try:
            # Initialize WebDriver
            self.initialize_webdriver()
            
            # Perform login
            login_success = self.perform_login(credentials)
            if not login_success:
                self._log_status("Login failed or timed out")
                return False
            
            # Execute selected actions
            if settings.just_login and not settings.requires_returns_dashboard() and not settings.access_credit_ledger and not settings.access_cash_ledger:
                self._log_status("Action: Just Login selected. Automation will stop here.")
                return True
            
            # Returns Dashboard workflow
            if settings.requires_returns_dashboard():
                self.navigate_to_returns_dashboard()
                self.filter_returns_dashboard(returns_options)
                
                if settings.download_gstr2b:
                    self.download_gstr2b()
            
            # Electronic Credit Ledger workflow
            if settings.access_credit_ledger:
                self.navigate_to_credit_ledger(credit_ledger_options)
            
            # Electronic Cash Ledger workflow
            if settings.access_cash_ledger:
                self.navigate_to_cash_ledger()
            
            self._log_status(StatusMessages.AUTOMATION_COMPLETE)
            return True
            
        except Exception as e:
            error_msg = f"Automation workflow failed: {str(e)}"
            self.logger.error(error_msg)
            self._log_status(f"Error: {error_msg}")
            return False
        finally:
            # Conditional cleanup based on keep_browser_open setting
            if keep_browser_open:
                self._log_status("Browser will remain open for continued use")
                self._log_status("Note: You can manually close the browser when finished")
            else:
                time.sleep(5)  # Brief pause before closing
                self.close_webdriver()
                self._log_status(StatusMessages.BROWSER_CLOSED)