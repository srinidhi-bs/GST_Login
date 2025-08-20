"""
Main GUI window for GST Automation Application.

This module provides the main application window that coordinates all
GUI components and handles the overall application flow.

Author: Srinidhi B S
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from typing import Optional

# Import configuration
from config.settings import (
    APP_TITLE, APP_GEOMETRY, AUTHOR_EMAIL, GITHUB_URL,
    PLATFORM_DISPLAY_NAME, StatusMessages
)

# Import models
from models.client_data import (
    ClientCredentials, AutomationSettings, 
    ReturnsDashboardOptions, CreditLedgerOptions, AutomationConfig
)

# Import services
from services.gst_portal_service import GSTPortalService
from services.chromedriver_service import ChromeDriverService

# Import GUI components
from gui.components.status_logger import StatusLogger
from gui.components.client_selection import ClientSelectionComponent
from gui.components.credentials_form import CredentialsForm
from gui.components.action_selection import ActionSelectionComponent
from gui.components.returns_options import ReturnsOptionsComponent
from gui.components.credit_ledger_options import CreditLedgerOptionsComponent

class MainWindow:
    """
    Main application window that coordinates all GUI components.
    
    This class manages the overall application flow, component interactions,
    and automation execution.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main application window.
        
        Args:
            root (tk.Tk): The root tkinter window
        """
        self.root = root
        self.logger = logging.getLogger(__name__)
        
        # Configure main window
        self._configure_window()
        
        # Initialize component state
        self.current_client: Optional[ClientCredentials] = None
        self.current_automation_settings = AutomationSettings()
        self.current_returns_options = ReturnsDashboardOptions()
        self.current_credit_ledger_options = CreditLedgerOptions()
        
        # Keep reference to GST service to prevent garbage collection
        self.current_gst_service = None
        
        # Create GUI components
        self._create_components()
        
        # Set up component interactions
        self._setup_component_interactions()
        
        # Initialize UI state
        self._initialize_ui_state()
    
    def _configure_window(self) -> None:
        """Configure the main window properties."""
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        
        # Prevent window from being too small (wider for two-column layout)
        self.root.minsize(800, 600)
        
        # Configure window closing behavior
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_components(self) -> None:
        """Create all GUI components."""
        # Create main container with two columns first
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights for responsive layout
        self.main_container.grid_columnconfigure(0, weight=1, minsize=400)  # Left column for controls
        self.main_container.grid_columnconfigure(1, weight=1, minsize=400)  # Right column for log
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Create left frame for controls
        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Create right frame for log
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Status logger (create first as other components may need to log)
        self.status_logger = StatusLogger(self.right_frame, height=15)
        
        # Client selection component
        self.client_selection = ClientSelectionComponent(
            self.left_frame,
            on_client_selected=self._on_client_selected,
            status_callback=self.status_logger.log_message
        )
        
        # Credentials form component
        self.credentials_form = CredentialsForm(
            self.left_frame,
            on_credentials_changed=self._on_credentials_changed
        )
        
        # Populate credentials form if a client was already selected during initialization
        if self.current_client:
            self.credentials_form.populate_from_client(self.current_client)
        
        # Action selection component
        self.action_selection = ActionSelectionComponent(
            self.left_frame,
            on_actions_changed=self._on_actions_changed,
            status_callback=self.status_logger.log_message
        )
        
        # Returns options component (initially hidden)
        self.returns_options = ReturnsOptionsComponent(
            self.left_frame,
            on_options_changed=self._on_returns_options_changed
        )
        
        # Credit ledger options component (initially hidden)
        self.credit_ledger_options = CreditLedgerOptionsComponent(
            self.left_frame,
            on_options_changed=self._on_credit_ledger_options_changed
        )
        
        # Control buttons
        self._create_control_buttons()
    
    def _create_control_buttons(self) -> None:
        """Create the main control buttons."""
        # Control buttons frame
        self.control_frame = ttk.Frame(self.left_frame)
        
        # Start automation button
        self.start_button = ttk.Button(
            self.control_frame,
            text="Start Automation",
            command=self._start_automation_thread,
            style="Accent.TButton"
        )
        self.start_button.pack(side="left", padx=5)
        
        # Clear log button
        self.clear_log_button = ttk.Button(
            self.control_frame,
            text="Clear Log",
            command=self.status_logger.clear_log
        )
        self.clear_log_button.pack(side="left", padx=5)
        
        # Update ChromeDriver button
        self.update_chromedriver_button = ttk.Button(
            self.control_frame,
            text="Update ChromeDriver",
            command=self._update_chromedriver_thread
        )
        self.update_chromedriver_button.pack(side="left", padx=5)
        
        # Close browser button
        self.close_browser_button = ttk.Button(
            self.control_frame,
            text="Close Browser",
            command=self._close_browser
        )
        self.close_browser_button.pack(side="left", padx=5)
        
        # Quit button
        self.quit_button = ttk.Button(
            self.control_frame,
            text="Quit",
            command=self._on_quit_requested
        )
        self.quit_button.pack(side="right", padx=5)
        
        # About button
        self.about_button = ttk.Button(
            self.control_frame,
            text="About",
            command=self._show_about_dialog
        )
        self.about_button.pack(side="right", padx=5)
    
    def _setup_component_interactions(self) -> None:
        """Set up interactions between components."""
        # Pack components in left frame (components are already created with proper parents)
        self.client_selection.pack(padx=0, pady=10, fill="x")
        self.credentials_form.pack(padx=0, pady=10, fill="x")
        self.action_selection.pack(padx=0, pady=10, fill="x")
        
        # Returns and Credit Ledger options will be packed/unpacked dynamically in left frame
        
        self.control_frame.pack(padx=0, pady=15, fill="x")
        
        # Pack status logger in right frame with full expansion
        self.status_logger.pack(fill="both", expand=True)
    
    def _initialize_ui_state(self) -> None:
        """Initialize the UI state and component visibility."""
        # Hide optional components initially
        self._update_component_visibility()
        
        # Log application startup
        self.status_logger.log_info("GST Automation Application started")
        self.status_logger.log_info(StatusMessages.PLATFORM_DETECTED)
        self.status_logger.log_info(f"Author: Srinidhi B S ({AUTHOR_EMAIL})")
        self.status_logger.log_info(f"GitHub: {GITHUB_URL}")
    
    def _on_client_selected(self, client: Optional[ClientCredentials]) -> None:
        """
        Handle client selection from the client selection component.
        
        Args:
            client (Optional[ClientCredentials]): Selected client or None
        """
        self.current_client = client
        # Only populate credentials form if it has been created
        if hasattr(self, 'credentials_form'):
            self.credentials_form.populate_from_client(client)
    
    def _on_credentials_changed(self, username: str, password: str) -> None:
        """
        Handle changes to credentials form.
        
        Args:
            username (str): Current username
            password (str): Current password
        """
        # Update current client if we have manual credentials
        if username and password and not self.current_client:
            self.current_client = ClientCredentials(
                client_name="Manual Entry",
                username=username,
                password=password
            )
    
    def _on_actions_changed(self, settings: AutomationSettings) -> None:
        """
        Handle changes to action selections.
        
        Args:
            settings (AutomationSettings): Current automation settings
        """
        self.current_automation_settings = settings
        self._update_component_visibility()
    
    def _on_returns_options_changed(self, options: ReturnsDashboardOptions) -> None:
        """
        Handle changes to returns dashboard options.
        
        Args:
            options (ReturnsDashboardOptions): Current returns options
        """
        self.current_returns_options = options
    
    def _on_credit_ledger_options_changed(self, options: CreditLedgerOptions) -> None:
        """
        Handle changes to credit ledger options.
        
        Args:
            options (CreditLedgerOptions): Current credit ledger options
        """
        self.current_credit_ledger_options = options
    
    def _update_component_visibility(self) -> None:
        """Update visibility of optional components based on selected actions."""
        # Show/hide returns options based on action selection
        if self.action_selection.requires_returns_dashboard_options():
            if not self.returns_options.is_visible():
                # Pack before control frame (components already have proper parent)
                self.returns_options.pack(padx=0, pady=5, fill="x", before=self.control_frame)
        else:
            if self.returns_options.is_visible():
                self.returns_options.pack_forget()
        
        # Show/hide credit ledger options based on action selection
        if self.action_selection.requires_credit_ledger_options():
            if not self.credit_ledger_options.is_visible():
                # Pack before control frame (components already have proper parent)
                self.credit_ledger_options.pack(padx=0, pady=5, fill="x", before=self.control_frame)
        else:
            if self.credit_ledger_options.is_visible():
                self.credit_ledger_options.pack_forget()
    
    def _validate_automation_config(self) -> tuple[bool, str]:
        """
        Validate the current automation configuration.
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Validate credentials
        credentials = self._get_current_credentials()
        if not credentials or not credentials.is_valid():
            return False, "Valid credentials are required. Please select a client or enter username and password manually."
        
        # Validate action selections
        if not self.current_automation_settings.has_actions_selected():
            return False, "At least one automation action must be selected."
        
        # Validate returns options if needed
        if self.action_selection.requires_returns_dashboard_options():
            is_valid, error = self.returns_options.validate_selections()
            if not is_valid:
                return False, f"Returns Dashboard options invalid: {error}"
        
        # Validate credit ledger options if needed
        if self.action_selection.requires_credit_ledger_options():
            is_valid, error = self.credit_ledger_options.validate_date_range()
            if not is_valid:
                return False, f"Credit Ledger options invalid: {error}"
        
        return True, ""
    
    def _get_current_credentials(self) -> Optional[ClientCredentials]:
        """
        Get the current credentials from either selected client or manual entry.
        
        Returns:
            Optional[ClientCredentials]: Current credentials or None
        """
        # Try to get credentials from form first (handles manual entry)
        form_credentials = self.credentials_form.get_credentials()
        
        if form_credentials.is_valid():
            # Use form credentials with client name if available
            client_name = self.current_client.client_name if self.current_client else "Manual Entry"
            return ClientCredentials(
                client_name=client_name,
                username=form_credentials.username,
                password=form_credentials.password
            )
        
        return None
    
    def _create_automation_config(self) -> Optional[AutomationConfig]:
        """
        Create automation configuration from current UI state.
        
        Returns:
            Optional[AutomationConfig]: Complete automation configuration or None if invalid
        """
        credentials = self._get_current_credentials()
        if not credentials:
            return None
        
        return AutomationConfig(
            credentials=credentials,
            automation_settings=self.current_automation_settings,
            returns_options=self.current_returns_options,
            credit_ledger_options=self.current_credit_ledger_options
        )
    
    def _start_automation_thread(self) -> None:
        """Start the automation process in a separate thread."""
        # Validate configuration first
        is_valid, error_message = self._validate_automation_config()
        if not is_valid:
            messagebox.showerror("Configuration Error", error_message)
            self.status_logger.log_error(f"Configuration Error: {error_message}")
            return
        
        # Create automation configuration
        config = self._create_automation_config()
        if not config:
            messagebox.showerror("Error", "Failed to create automation configuration")
            return
        
        # Disable start button to prevent multiple runs
        self.start_button.config(state="disabled")
        self.start_button.config(text="Running...")
        
        # Log automation start
        selected_actions = self.action_selection.get_selected_action_names()
        self.status_logger.log_info(f"Starting automation with actions: {', '.join(selected_actions)}")
        
        # Start automation in separate thread
        automation_thread = threading.Thread(
            target=self._run_automation,
            args=(config,),
            daemon=True
        )
        automation_thread.start()
    
    def _run_automation(self, config: AutomationConfig) -> None:
        """
        Run the automation process in a separate thread.
        
        Args:
            config (AutomationConfig): Complete automation configuration
        """
        try:
            # Create GST portal service and store reference to prevent garbage collection
            self.current_gst_service = GSTPortalService(
                status_callback=self.status_logger.log_info,
                headless=False
            )
            
            # Execute automation workflow
            success = self.current_gst_service.execute_automation_workflow(
                credentials=config.credentials,
                settings=config.automation_settings,
                returns_options=config.returns_options,
                credit_ledger_options=config.credit_ledger_options,
                keep_browser_open=True  # Keep browser open after automation
            )
            
            # Show completion message
            if success:
                messagebox.showinfo(
                    "Automation Complete", 
                    "Automation completed successfully! Check the status log for details."
                )
                self.status_logger.log_success("Automation completed successfully!")
            else:
                messagebox.showwarning(
                    "Automation Issues", 
                    "Automation completed with issues. Check the status log for details."
                )
                self.status_logger.log_warning("Automation completed with issues.")
        
        except Exception as e:
            error_message = f"Automation failed with error: {str(e)}"
            self.status_logger.log_error(error_message)
            messagebox.showerror("Automation Error", error_message)
            
        finally:
            # Re-enable start button
            self.root.after(0, self._reset_start_button)
    
    def _close_browser(self) -> None:
        """
        Manually close the browser if it's open.
        This allows users to close the browser without closing the application.
        """
        try:
            if self.current_gst_service:
                self.current_gst_service.close_webdriver()
                self.current_gst_service = None
                self.status_logger.log_info("Browser closed successfully.")
            else:
                self.status_logger.log_warning("No active browser session to close.")
        except Exception as e:
            self.status_logger.log_error(f"Error closing browser: {str(e)}")
    
    def _reset_start_button(self) -> None:
        """Reset the start button state (called from main thread)."""
        self.start_button.config(state="normal")
        self.start_button.config(text="Start Automation")
    
    def _update_chromedriver_thread(self) -> None:
        """Start the ChromeDriver update process in a separate thread."""
        # Disable the update button to prevent multiple updates
        self.update_chromedriver_button.config(state="disabled")
        self.update_chromedriver_button.config(text="Updating...")
        
        # Log update start
        self.status_logger.log_info("🚀 Starting ChromeDriver update...")
        
        # Start update in separate thread
        update_thread = threading.Thread(
            target=self._run_chromedriver_update,
            daemon=True
        )
        update_thread.start()
    
    def _run_chromedriver_update(self) -> None:
        """
        Run the ChromeDriver update process in a separate thread.
        """
        try:
            # Create ChromeDriver service
            chromedriver_service = ChromeDriverService(
                status_callback=self.status_logger.log_info
            )
            
            # Check current status
            is_available, status_message = chromedriver_service.check_chromedriver_status()
            if is_available:
                self.status_logger.log_info(f"ℹ️ Current status: {status_message}")
            else:
                self.status_logger.log_warning(f"⚠️ Current status: {status_message}")
            
            # Perform the update
            success = chromedriver_service.update_chromedriver()
            
            if success:
                self.status_logger.log_success("✅ ChromeDriver update completed successfully!")
                
                # Check new status
                is_available, status_message = chromedriver_service.check_chromedriver_status()
                if is_available:
                    self.status_logger.log_success(f"✅ New status: {status_message}")
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "ChromeDriver Update", 
                    "ChromeDriver has been updated successfully!\n\n"
                    "You can now use the automation features."
                ))
            else:
                self.status_logger.log_error("❌ ChromeDriver update failed")
                
                # Show error message
                self.root.after(0, lambda: messagebox.showerror(
                    "ChromeDriver Update Failed", 
                    "Failed to update ChromeDriver.\n\n"
                    "Please check the status log for details and try again."
                ))
        
        except Exception as e:
            error_message = f"ChromeDriver update failed with error: {str(e)}"
            self.status_logger.log_error(error_message)
            
            # Show error message
            self.root.after(0, lambda: messagebox.showerror(
                "ChromeDriver Update Error", 
                f"An error occurred during ChromeDriver update:\n\n{str(e)}"
            ))
            
        finally:
            # Re-enable update button
            self.root.after(0, self._reset_chromedriver_button)
    
    def _reset_chromedriver_button(self) -> None:
        """Reset the ChromeDriver update button state (called from main thread)."""
        self.update_chromedriver_button.config(state="normal")
        self.update_chromedriver_button.config(text="Update ChromeDriver")
    
    def _show_about_dialog(self) -> None:
        """Show the about dialog."""
        about_text = f"""GST Portal Automation Application

Version: 2.1.0 (Cross-Platform Support)
Author: Srinidhi B S
Email: {AUTHOR_EMAIL}
GitHub: {GITHUB_URL}

Platform Support:
• Windows: Uses chromedriver-win64/chromedriver.exe
• Linux/WSL: Uses chromedriver-linux64/chromedriver
• Currently running on: {PLATFORM_DISPLAY_NAME}

This application automates GST portal interactions including:
• Client credential management from Excel files
• Automated login with CAPTCHA support
• Returns Dashboard navigation and filtering
• GSTR-2B report downloads
• Electronic Credit and Cash Ledger access
• Automatic ChromeDriver updates with one click

Built with Python, Tkinter, and Selenium WebDriver.

Note: This tool requires manual CAPTCHA entry during login.
💡 TIP: Click "Update ChromeDriver" for automatic setup - no manual downloads needed!
        
        messagebox.showinfo("About GST Automation", about_text)
    
    def _on_quit_requested(self) -> None:
        """Handle quit request."""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self._on_window_close()
    
    def _on_window_close(self) -> None:
        """Handle window close event."""
        try:
            self.status_logger.log_info("Application shutting down...")
            
            # Close browser if it's still open
            if self.current_gst_service:
                try:
                    self.current_gst_service.close_webdriver()
                    self.status_logger.log_info("Browser closed.")
                except:
                    pass  # Ignore errors if browser is already closed
                    
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            # Force exit if there are issues
            import sys
            sys.exit(0)
    
    def run(self) -> None:
        """Start the main GUI event loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_window_close()
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")

def create_main_window() -> MainWindow:
    """
    Create and configure the main application window.
    
    Returns:
        MainWindow: Configured main window instance
    """
    root = tk.Tk()
    
    # Configure ttk styles for better appearance
    style = ttk.Style()
    
    # Try to use a modern theme if available
    available_themes = style.theme_names()
    if "vista" in available_themes:
        style.theme_use("vista")
    elif "clam" in available_themes:
        style.theme_use("clam")
    
    # Create accent button style
    style.configure("Accent.TButton", 
                   font=("TkDefaultFont", 9, "bold"))
    
    return MainWindow(root)