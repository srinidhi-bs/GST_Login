"""
ChromeDriver Auto-Update Service for GST Automation Application.

This service handles automatic detection of Chrome browser version,
downloading the matching ChromeDriver, and installing it in the correct
platform-specific directory.

Author: Srinidhi B S
"""
import os
import re
import json
import shutil
import zipfile
import tempfile
import subprocess
import urllib.request
import urllib.error
from typing import Optional, Tuple, Callable
import logging

from config.settings import (
    CHROMEDRIVER_DIRECTORY, CHROMEDRIVER_RELATIVE_PATH,
    IS_EFFECTIVE_WINDOWS, PLATFORM_DISPLAY_NAME
)

# Set up logging for this module
logger = logging.getLogger(__name__)

class ChromeDriverUpdateError(Exception):
    """Custom exception for ChromeDriver update failures."""
    pass

class ChromeDriverService:
    """
    Service class for ChromeDriver management and auto-update functionality.
    
    This class provides methods to detect Chrome version, download matching
    ChromeDriver, and install it in the correct platform-specific directory.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the ChromeDriver service.
        
        Args:
            status_callback (Optional[Callable[[str], None]]): Callback for status updates
        """
        self.status_callback = status_callback or self._default_status_callback
        self.logger = logging.getLogger(__name__)
        
        # ChromeDriver download URLs
        self.base_url = "https://chromedriver.storage.googleapis.com"
        self.version_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        
        # New ChromeDriver URLs (for versions 115+)
        self.new_base_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
        self.new_api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    
    def _default_status_callback(self, message: str) -> None:
        """Default status callback that logs the message."""
        self.logger.info(message)
    
    def _log_status(self, message: str) -> None:
        """Log status message and call status callback."""
        self.logger.info(message)
        if self.status_callback:
            self.status_callback(message)
    
    def detect_chrome_version(self) -> Optional[str]:
        """
        Detect the installed Chrome browser version.
        
        Returns:
            Optional[str]: Chrome version string (e.g., "119.0.6045.105") or None if not found
        """
        self._log_status("🔍 Detecting Chrome browser version...")
        
        try:
            if IS_EFFECTIVE_WINDOWS:
                return self._detect_chrome_version_windows()
            else:
                return self._detect_chrome_version_linux()
        except Exception as e:
            self._log_status(f"❌ Error detecting Chrome version: {str(e)}")
            return None
    
    def _detect_chrome_version_windows(self) -> Optional[str]:
        """Detect Chrome version on Windows."""
        # Common Chrome installation paths on Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe"
        ]
        
        # Try to get version from registry first
        try:
            import winreg
            key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                self._log_status(f"✅ Found Chrome version from registry: {version}")
                return version
            except FileNotFoundError:
                # Try HKEY_LOCAL_MACHINE
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                self._log_status(f"✅ Found Chrome version from registry: {version}")
                return version
        except ImportError:
            pass  # winreg not available
        except Exception:
            pass  # Registry method failed
        
        # Fallback: Try to execute chrome with version flag
        for chrome_path in chrome_paths:
            try:
                if os.path.exists(chrome_path):
                    result = subprocess.run(
                        [chrome_path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        # Extract version from output like "Google Chrome 119.0.6045.105"
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if match:
                            version = match.group(1)
                            self._log_status(f"✅ Found Chrome version: {version}")
                            return version
            except Exception:
                continue
        
        return None
    
    def _detect_chrome_version_linux(self) -> Optional[str]:
        """Detect Chrome version on Linux/WSL."""
        # Try different Chrome commands
        chrome_commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
        
        for cmd in chrome_commands:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # Extract version from output
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if match:
                        version = match.group(1)
                        self._log_status(f"✅ Found Chrome version: {version}")
                        return version
            except FileNotFoundError:
                continue
            except Exception:
                continue
        
        return None
    
    def get_chromedriver_download_url(self, chrome_version: str) -> Optional[Tuple[str, str]]:
        """
        Get the download URL for ChromeDriver matching the Chrome version.
        
        Args:
            chrome_version (str): Chrome version string
            
        Returns:
            Optional[Tuple[str, str]]: (download_url, filename) or None if not found
        """
        self._log_status(f"🔍 Finding ChromeDriver for Chrome {chrome_version}...")
        
        # Determine platform suffix
        if IS_EFFECTIVE_WINDOWS:
            platform_suffix = "win64"
            filename = f"chromedriver-{platform_suffix}.zip"
        else:
            platform_suffix = "linux64"
            filename = f"chromedriver-{platform_suffix}.zip"
        
        try:
            # For Chrome 115+, use the new API
            major_version = int(chrome_version.split('.')[0])
            
            if major_version >= 115:
                return self._get_new_chromedriver_url(chrome_version, platform_suffix, filename)
            else:
                return self._get_legacy_chromedriver_url(chrome_version, platform_suffix, filename)
                
        except Exception as e:
            self._log_status(f"❌ Error getting ChromeDriver URL: {str(e)}")
            return None
    
    def _get_new_chromedriver_url(self, chrome_version: str, platform_suffix: str, filename: str) -> Optional[Tuple[str, str]]:
        """Get ChromeDriver URL for Chrome 115+ using new API."""
        try:
            # Try to get exact version match first
            api_url = self.new_api_url
            with urllib.request.urlopen(api_url, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            # Find exact version match
            for version_info in data.get('versions', []):
                if version_info.get('version') == chrome_version:
                    downloads = version_info.get('downloads', {})
                    chromedriver_downloads = downloads.get('chromedriver', [])
                    
                    for download in chromedriver_downloads:
                        if download.get('platform') == platform_suffix:
                            url = download.get('url')
                            if url:
                                self._log_status(f"✅ Found exact ChromeDriver match: {chrome_version}")
                                return url, filename
            
            # If exact match not found, try major version match
            major_version = chrome_version.split('.')[0]
            for version_info in data.get('versions', []):
                version = version_info.get('version', '')
                if version.startswith(f"{major_version}."):
                    downloads = version_info.get('downloads', {})
                    chromedriver_downloads = downloads.get('chromedriver', [])
                    
                    for download in chromedriver_downloads:
                        if download.get('platform') == platform_suffix:
                            url = download.get('url')
                            if url:
                                self._log_status(f"✅ Found compatible ChromeDriver: {version} (for Chrome {chrome_version})")
                                return url, filename
            
            return None
            
        except Exception as e:
            self._log_status(f"⚠️ New API failed, trying fallback: {str(e)}")
            return None
    
    def _get_legacy_chromedriver_url(self, chrome_version: str, platform_suffix: str, filename: str) -> Optional[Tuple[str, str]]:
        """Get ChromeDriver URL for Chrome versions before 115."""
        try:
            # Try to get the exact version
            version_url = f"{self.version_url}_{chrome_version}"
            try:
                with urllib.request.urlopen(version_url, timeout=10) as response:
                    chromedriver_version = response.read().decode().strip()
            except urllib.error.HTTPError:
                # Try major version
                major_version = chrome_version.split('.')[0]
                version_url = f"{self.version_url}_{major_version}"
                with urllib.request.urlopen(version_url, timeout=10) as response:
                    chromedriver_version = response.read().decode().strip()
            
            download_url = f"{self.base_url}/{chromedriver_version}/{filename}"
            self._log_status(f"✅ Found ChromeDriver version: {chromedriver_version}")
            return download_url, filename
            
        except Exception as e:
            self._log_status(f"⚠️ Legacy API failed: {str(e)}")
            return None
    
    def download_and_install_chromedriver(self, download_url: str, filename: str) -> bool:
        """
        Download and install ChromeDriver.
        
        Args:
            download_url (str): URL to download ChromeDriver from
            filename (str): Filename of the downloaded file
            
        Returns:
            bool: True if successful, False otherwise
        """
        temp_dir = None
        try:
            self._log_status("📥 Downloading ChromeDriver...")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, filename)
            
            # Download the file
            with urllib.request.urlopen(download_url, timeout=60) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(zip_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self._log_status(f"📥 Downloading... {progress:.1f}%")
            
            self._log_status("✅ Download completed, extracting...")
            
            # Extract the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the ChromeDriver executable
            chromedriver_exe = "chromedriver.exe" if IS_EFFECTIVE_WINDOWS else "chromedriver"
            extracted_chromedriver = None
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == chromedriver_exe:
                        extracted_chromedriver = os.path.join(root, file)
                        break
                if extracted_chromedriver:
                    break
            
            if not extracted_chromedriver:
                raise ChromeDriverUpdateError(f"ChromeDriver executable not found in downloaded package")
            
            # Get the destination directory
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            chromedriver_dir = os.path.join(script_dir, CHROMEDRIVER_DIRECTORY)
            
            # Create destination directory if it doesn't exist
            os.makedirs(chromedriver_dir, exist_ok=True)
            
            # Copy ChromeDriver to destination
            destination_path = os.path.join(script_dir, CHROMEDRIVER_RELATIVE_PATH)
            shutil.copy2(extracted_chromedriver, destination_path)
            
            # Set executable permissions on Linux/WSL
            if not IS_EFFECTIVE_WINDOWS:
                os.chmod(destination_path, 0o755)
                self._log_status("✅ Set executable permissions")
            
            self._log_status(f"✅ ChromeDriver installed successfully!")
            self._log_status(f"📍 Location: {destination_path}")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Failed to download/install ChromeDriver: {str(e)}"
            self._log_status(error_msg)
            return False
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass  # Ignore cleanup errors
    
    def update_chromedriver(self) -> bool:
        """
        Complete ChromeDriver update workflow.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._log_status(f"🚀 Starting ChromeDriver update for {PLATFORM_DISPLAY_NAME}...")
            
            # Step 1: Detect Chrome version
            chrome_version = self.detect_chrome_version()
            if not chrome_version:
                self._log_status("❌ Could not detect Chrome browser version")
                self._log_status("💡 Please ensure Chrome is installed and accessible")
                return False
            
            # Step 2: Get download URL
            download_info = self.get_chromedriver_download_url(chrome_version)
            if not download_info:
                self._log_status("❌ Could not find matching ChromeDriver")
                return False
            
            download_url, filename = download_info
            
            # Step 3: Download and install
            success = self.download_and_install_chromedriver(download_url, filename)
            
            if success:
                self._log_status("🎉 ChromeDriver update completed successfully!")
                self._log_status("✅ You can now use the automation features")
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"❌ ChromeDriver update failed: {str(e)}"
            self._log_status(error_msg)
            return False
    
    def check_chromedriver_status(self) -> Tuple[bool, Optional[str]]:
        """
        Check if ChromeDriver is available and get its version.
        
        Returns:
            Tuple[bool, Optional[str]]: (is_available, version_or_error_message)
        """
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            chromedriver_path = os.path.join(script_dir, CHROMEDRIVER_RELATIVE_PATH)
            
            if not os.path.exists(chromedriver_path):
                return False, f"ChromeDriver not found at {chromedriver_path}"
            
            # Try to get ChromeDriver version
            try:
                result = subprocess.run(
                    [chromedriver_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # Extract version from output
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        version = version_match.group(1)
                        return True, f"ChromeDriver {version}"
                    else:
                        return True, "ChromeDriver (version unknown)"
                else:
                    return False, f"ChromeDriver exists but failed to run: {result.stderr}"
            except Exception as e:
                return False, f"ChromeDriver exists but error running: {str(e)}"
                
        except Exception as e:
            return False, f"Error checking ChromeDriver: {str(e)}"