"""
Base web automation service for GST Automation Application.

This module provides the foundational WebDriver management, element location
strategies, and common web automation utilities used throughout the application.

Author: Srinidhi B S
"""
import os
import time
import logging
from typing import Optional, Callable, Any, List, Tuple
from contextlib import contextmanager

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, StaleElementReferenceException
)

from config.settings import (
    WAIT_TIME_SHORT, WAIT_TIME_LONG, WAIT_TIME_VERY_LONG,
    CHROMEDRIVER_RELATIVE_PATH, DOWNLOAD_FOLDER_NAME,
    CHROME_DOWNLOAD_PREFERENCES, CHROME_OPTIONS,
    SAVE_SCREENSHOTS_ON_ERROR, SCREENSHOT_PREFIX,
    PLATFORM_DISPLAY_NAME, CHROMEDRIVER_DIRECTORY, IS_EFFECTIVE_WINDOWS
)

# Set up logging for this module
logger = logging.getLogger(__name__)

class WebDriverInitializationError(Exception):
    """Custom exception for WebDriver initialization failures."""
    pass

class ElementNotFoundError(Exception):
    """Custom exception for element location failures."""
    pass

class AutomationTimeoutError(Exception):
    """Custom exception for automation timeout errors."""
    pass

class WebAutomationService:
    """
    Base service class for web automation operations.
    
    This class provides WebDriver management, element finding strategies,
    and common automation utilities that can be used by specific
    automation services.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the web automation service.
        
        Args:
            headless (bool): If True, run browser in headless mode
        """
        self.logger = logging.getLogger(__name__)
        self.driver: Optional[webdriver.Chrome] = None
        self.actions: Optional[ActionChains] = None
        self.headless = headless
        self._download_dir: Optional[str] = None
    
    def _get_chromedriver_path(self) -> str:
        """
        Get the path to the ChromeDriver executable (platform-aware).
        
        Automatically selects the correct ChromeDriver based on the current platform:
        - Windows: chromedriver-win64/chromedriver.exe
        - Linux/WSL: chromedriver-linux64/chromedriver
        
        Returns:
            str: Path to ChromeDriver executable
            
        Raises:
            WebDriverInitializationError: If ChromeDriver is not found
        """
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chromedriver_path = os.path.join(script_dir, CHROMEDRIVER_RELATIVE_PATH)
        
        if not os.path.exists(chromedriver_path):
            # Create platform-specific error message with setup guidance
            platform_name = PLATFORM_DISPLAY_NAME
            chromedriver_exe = "chromedriver.exe" if IS_EFFECTIVE_WINDOWS else "chromedriver"
            download_url = "https://chromedriver.chromium.org/downloads"
            
            error_msg = (
                f"ChromeDriver not found for {platform_name} at: {chromedriver_path}\n\n"
                f"🚀 EASY FIX: Use the 'Update ChromeDriver' button in the app!\n"
                f"   The app will automatically download and install the correct ChromeDriver.\n\n"
                f"Manual alternative (if auto-update fails):\n"
                f"1. Download ChromeDriver for {platform_name} from: {download_url}\n"
                f"2. Extract {chromedriver_exe} to: {os.path.join(script_dir, CHROMEDRIVER_DIRECTORY)}/\n"
                f"3. Ensure the file is executable (Linux/WSL: chmod +x {chromedriver_exe})"
            )
            
            self.logger.error(error_msg)
            raise WebDriverInitializationError(error_msg)
        
        return chromedriver_path
    
    def _setup_download_directory(self) -> str:
        """
        Set up and return the download directory path.
        
        Returns:
            str: Path to the download directory
        """
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(script_dir, DOWNLOAD_FOLDER_NAME)
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            self.logger.info(f"Created download directory: {download_dir}")
        
        self._download_dir = download_dir
        return download_dir
    
    def _configure_chrome_options(self) -> webdriver.ChromeOptions:
        """
        Configure Chrome options for automation.
        
        Returns:
            webdriver.ChromeOptions: Configured Chrome options
        """
        chrome_options = webdriver.ChromeOptions()
        
        # Set up download preferences
        download_dir = self._setup_download_directory()
        prefs = CHROME_DOWNLOAD_PREFERENCES.copy()
        prefs["download.default_directory"] = download_dir
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Apply headless mode if requested
        if self.headless or CHROME_OPTIONS.get("headless", False):
            chrome_options.add_argument("--headless")
            self.logger.info("Running Chrome in headless mode")
        
        # Additional Chrome arguments for better automation
        if CHROME_OPTIONS.get("disable_gpu", False):
            chrome_options.add_argument("--disable-gpu")
        
        # Add other useful arguments for automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        
        return chrome_options
    
    def initialize_webdriver(self) -> None:
        """
        Initialize the Chrome WebDriver with configured options.
        
        Raises:
            WebDriverInitializationError: If WebDriver initialization fails
        """
        try:
            self.logger.info("Initializing Chrome WebDriver...")
            
            # Get ChromeDriver path and configure options
            chromedriver_path = self._get_chromedriver_path()
            service = ChromeService(chromedriver_path)
            chrome_options = self._configure_chrome_options()
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.actions = ActionChains(self.driver)
            
            # Maximize window if not in headless mode
            if CHROME_OPTIONS.get("maximize_window", True) and not self.headless:
                self.driver.maximize_window()
            
            self.logger.info("WebDriver initialized successfully")
            self.logger.info(f"Downloads will be saved to: {self._download_dir}")
            
        except Exception as e:
            error_msg = f"Failed to initialize WebDriver: {str(e)}"
            self.logger.error(error_msg)
            raise WebDriverInitializationError(error_msg) from e
    
    def close_webdriver(self) -> None:
        """Close the WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
                self.actions = None
    
    @contextmanager
    def webdriver_context(self):
        """
        Context manager for WebDriver lifecycle management.
        
        Yields:
            webdriver.Chrome: The initialized WebDriver instance
        """
        try:
            self.initialize_webdriver()
            yield self.driver
        finally:
            self.close_webdriver()
    
    def navigate_to_url(self, url: str) -> None:
        """
        Navigate to the specified URL.
        
        Args:
            url (str): The URL to navigate to
            
        Raises:
            WebDriverException: If navigation fails
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            self.logger.info("Navigation completed")
        except Exception as e:
            error_msg = f"Failed to navigate to {url}: {str(e)}"
            self.logger.error(error_msg)
            raise WebDriverException(error_msg) from e
    
    def find_element_with_fallbacks(self, locator_strategies: List[Tuple[By, str]], 
                                  wait_time: int = WAIT_TIME_SHORT,
                                  description: str = "element") -> Any:
        """
        Find element using multiple locator strategies with fallbacks.
        
        Args:
            locator_strategies (List[Tuple[By, str]]): List of (By, locator) tuples to try
            wait_time (int): Time to wait for each strategy
            description (str): Description of the element for logging
            
        Returns:
            WebElement: The found element
            
        Raises:
            ElementNotFoundError: If element cannot be found with any strategy
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        last_exception = None
        
        # Debug: Log current page info
        current_url = self.driver.current_url if self.driver else "Unknown"
        page_title = self.driver.title if self.driver else "Unknown"
        self.logger.debug(f"Searching for {description} on page: {current_url} (Title: {page_title})")
        
        for i, (by, locator) in enumerate(locator_strategies):
            try:
                self.logger.info(f"Trying locator {i+1}/{len(locator_strategies)} for {description}: {by.name}='{locator}'")
                
                # Debug: Try to find elements without wait first
                try:
                    immediate_elements = self.driver.find_elements(by, locator)
                    self.logger.debug(f"Found {len(immediate_elements)} elements immediately with locator {i+1}")
                    if immediate_elements:
                        element = immediate_elements[0]
                        self.logger.info(f"Successfully found {description} with locator {i+1} (immediate)")
                        return element
                except Exception as e:
                    self.logger.debug(f"Immediate search failed for locator {i+1}: {str(e)}")
                
                # Try element_to_be_clickable first (better for interactive elements)
                try:
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((by, locator))
                    )
                    self.logger.info(f"Successfully found {description} with locator {i+1} (clickable)")
                    return element
                except TimeoutException:
                    # Fallback to presence_of_element_located
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((by, locator))
                    )
                    self.logger.info(f"Successfully found {description} with locator {i+1} (present)")
                    return element
                
            except TimeoutException as e:
                last_exception = e
                self.logger.debug(f"Locator {i+1} failed for {description}: {str(e)}")
                continue
            except Exception as e:
                last_exception = e
                self.logger.debug(f"Unexpected error with locator {i+1} for {description}: {str(e)}")
                continue
        
        # If we get here, all strategies failed
        error_msg = f"Could not find {description} with any of the {len(locator_strategies)} locator strategies"
        self.logger.error(error_msg)
        
        if SAVE_SCREENSHOTS_ON_ERROR:
            self.save_debug_screenshot(f"element_not_found_{description}")
        
        raise ElementNotFoundError(error_msg) from last_exception
    
    def click_element_with_fallbacks(self, locator_strategies: List[Tuple[By, str]], 
                                   wait_time: int = WAIT_TIME_SHORT,
                                   description: str = "element") -> None:
        """
        Click element using multiple locator strategies with fallbacks.
        
        Args:
            locator_strategies (List[Tuple[By, str]]): List of (By, locator) tuples to try
            wait_time (int): Time to wait for each strategy
            description (str): Description of the element for logging
            
        Raises:
            ElementNotFoundError: If element cannot be found or clicked
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        last_exception = None
        
        for i, (by, locator) in enumerate(locator_strategies):
            try:
                self.logger.debug(f"Trying to click {description} with locator {i+1}/{len(locator_strategies)}")
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((by, locator))
                )
                element.click()
                self.logger.info(f"Successfully clicked {description}")
                return
                
            except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                last_exception = e
                self.logger.debug(f"Click attempt {i+1} failed for {description}: {str(e)}")
                continue
            except Exception as e:
                last_exception = e
                self.logger.debug(f"Unexpected error clicking {description} with locator {i+1}: {str(e)}")
                continue
        
        # If we get here, all strategies failed
        error_msg = f"Could not click {description} with any of the {len(locator_strategies)} locator strategies"
        self.logger.error(error_msg)
        
        if SAVE_SCREENSHOTS_ON_ERROR:
            self.save_debug_screenshot(f"click_failed_{description}")
        
        raise ElementNotFoundError(error_msg) from last_exception
    
    def select_dropdown_option(self, locator_strategies: List[Tuple[By, str]], 
                             selection_index: int,
                             wait_time: int = WAIT_TIME_SHORT,
                             description: str = "dropdown") -> None:
        """
        Select option from dropdown using multiple locator strategies.
        
        Args:
            locator_strategies (List[Tuple[By, str]]): List of (By, locator) tuples to try
            selection_index (int): Index of option to select
            wait_time (int): Time to wait for element
            description (str): Description of the dropdown for logging
            
        Raises:
            ElementNotFoundError: If dropdown cannot be found or option selected
        """
        element = self.find_element_with_fallbacks(locator_strategies, wait_time, description)
        
        try:
            select = Select(element)
            select.select_by_index(selection_index)
            self.logger.info(f"Selected option {selection_index} from {description}")
        except Exception as e:
            error_msg = f"Failed to select option {selection_index} from {description}: {str(e)}"
            self.logger.error(error_msg)
            raise ElementNotFoundError(error_msg) from e
    
    def wait_for_url_change(self, expected_url_part: str, timeout: int = WAIT_TIME_LONG) -> bool:
        """
        Wait for URL to contain expected part (useful for login flows).
        
        Args:
            expected_url_part (str): Part of URL to wait for
            timeout (int): Maximum time to wait
            
        Returns:
            bool: True if URL changed as expected, False if timeout
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        try:
            self.logger.info(f"Waiting for URL to contain: {expected_url_part}")
            WebDriverWait(self.driver, timeout).until(EC.url_contains(expected_url_part))
            self.logger.info(f"URL changed successfully to contain: {expected_url_part}")
            return True
        except TimeoutException:
            current_url = self.driver.current_url
            self.logger.warning(f"URL did not change to contain '{expected_url_part}' within {timeout}s. Current URL: {current_url}")
            return False
    
    def wait_for_element_invisible(self, by: By, locator: str, timeout: int = WAIT_TIME_SHORT) -> bool:
        """
        Wait for an element to become invisible (useful for overlays/loaders).
        
        Args:
            by (By): The method to locate the element
            locator (str): The locator string
            timeout (int): Maximum time to wait
            
        Returns:
            bool: True if element became invisible, False if timeout or not found
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        try:
            self.logger.debug(f"Waiting for element to become invisible: {by.name}='{locator}'")
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((by, locator))
            )
            self.logger.debug("Element became invisible")
            return True
        except TimeoutException:
            self.logger.debug(f"Element did not become invisible within {timeout}s")
            return False
    
    def hover_over_element(self, locator_strategies: List[Tuple[By, str]], 
                          wait_time: int = WAIT_TIME_SHORT,
                          description: str = "element") -> None:
        """
        Hover over element using multiple locator strategies.
        
        Args:
            locator_strategies (List[Tuple[By, str]]): List of (By, locator) tuples to try
            wait_time (int): Time to wait for element
            description (str): Description of the element for logging
            
        Raises:
            ElementNotFoundError: If element cannot be found or hovered
        """
        element = self.find_element_with_fallbacks(locator_strategies, wait_time, description)
        
        try:
            if not self.actions:
                self.actions = ActionChains(self.driver)
            
            self.actions.move_to_element(element).perform()
            self.logger.info(f"Successfully hovered over {description}")
        except Exception as e:
            error_msg = f"Failed to hover over {description}: {str(e)}"
            self.logger.error(error_msg)
            raise ElementNotFoundError(error_msg) from e
    
    def send_keys_to_element(self, locator_strategies: List[Tuple[By, str]], 
                           text: str,
                           clear_first: bool = True,
                           wait_time: int = WAIT_TIME_SHORT,
                           description: str = "input field") -> None:
        """
        Send keys to input element using multiple locator strategies.
        
        Args:
            locator_strategies (List[Tuple[By, str]]): List of (By, locator) tuples to try
            text (str): Text to send to the element
            clear_first (bool): If True, clear field before entering text
            wait_time (int): Time to wait for element
            description (str): Description of the element for logging
            
        Raises:
            ElementNotFoundError: If element cannot be found or text entered
        """
        element = self.find_element_with_fallbacks(locator_strategies, wait_time, description)
        
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            self.logger.info(f"Successfully sent text to {description}")
        except Exception as e:
            error_msg = f"Failed to send text to {description}: {str(e)}"
            self.logger.error(error_msg)
            raise ElementNotFoundError(error_msg) from e
    
    def save_debug_screenshot(self, filename_suffix: str = "") -> Optional[str]:
        """
        Save a screenshot for debugging purposes.
        
        Args:
            filename_suffix (str): Suffix to add to the filename
            
        Returns:
            Optional[str]: Path to saved screenshot, None if failed
        """
        if not self.driver:
            return None
        
        try:
            timestamp = int(time.time())
            filename = f"{SCREENSHOT_PREFIX}{filename_suffix}_{timestamp}.png"
            filepath = os.path.join(self._download_dir or ".", filename)
            
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Debug screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.warning(f"Failed to save screenshot: {e}")
            return None
    
    def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script (str): JavaScript code to execute
            
        Returns:
            Any: Result of the JavaScript execution
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        try:
            result = self.driver.execute_script(script)
            self.logger.debug(f"Executed JavaScript: {script[:100]}...")
            return result
        except Exception as e:
            self.logger.error(f"JavaScript execution failed: {e}")
            raise
    
    def get_current_url(self) -> str:
        """
        Get the current URL of the browser.
        
        Returns:
            str: Current URL
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            str: Page title
        """
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        return self.driver.title
    
    def refresh_page(self) -> None:
        """Refresh the current page."""
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        self.driver.refresh()
        self.logger.info("Page refreshed")
    
    def go_back(self) -> None:
        """Navigate back to the previous page."""
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        self.driver.back()
        self.logger.info("Navigated back")
    
    def go_forward(self) -> None:
        """Navigate forward to the next page."""
        if not self.driver:
            raise WebDriverException("WebDriver not initialized")
        
        self.driver.forward()
        self.logger.info("Navigated forward")