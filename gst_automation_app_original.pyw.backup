# GST Portal Automation Application
# Author: Srinidhi B S
# Description: Automates GST portal interactions including login, returns dashboard, 
#              GSTR-2B download, and ledger access using Selenium WebDriver

# GUI and file handling imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Selenium WebDriver imports for browser automation
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.common.exceptions import TimeoutException

# Additional utilities
# from webdriver_manager.chrome import ChromeDriverManager  # Auto-downloads ChromeDriver
import time
import threading  # For non-blocking automation execution
import pandas as pd  # Excel file handling
import os  # File system operations 

class GSTAutomationApp:
    """
    Main application class for GST Portal Automation.
    
    This class creates a GUI application that automates interactions with the GST portal.
    Features include:
    - Loading client credentials from Excel files
    - Automated GST portal login with CAPTCHA handling
    - Returns dashboard navigation and filtering
    - GSTR-2B download automation
    - Electronic Credit and Cash Ledger access
    - Comprehensive error handling and status logging
    """
    def __init__(self, root):
        """
        Initialize the GST Automation GUI application.
        
        Args:
            root: The main tkinter window instance
        """
        # Main window configuration
        self.root = root
        self.root.title("GST Portal Automation - Srinidhi B S")
        self.root.geometry("600x780") 

        # Data storage for client information loaded from Excel
        self.clients_data = {}  # Dictionary to store client credentials
        
        # Default Excel file path (current directory + clients.xlsx)
        self.excel_file_path = tk.StringVar(value=os.path.join(os.getcwd(), "clients.xlsx")) 

        # === Excel File Selection Section ===
        # Frame for Excel file selection and client management
        excel_frame = ttk.LabelFrame(root, text="Client Data from Excel")
        excel_frame.pack(padx=10, pady=10, fill="x")

        # Excel file path display and browse functionality
        ttk.Label(excel_frame, text="Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.excel_path_entry = ttk.Entry(excel_frame, textvariable=self.excel_file_path, width=50)
        self.excel_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ttk.Button(excel_frame, text="Browse", command=self.browse_excel_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Button to manually reload clients from Excel file
        self.load_clients_button = ttk.Button(excel_frame, text="Load Clients from Excel", command=self.load_clients_from_excel)
        self.load_clients_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Client selection dropdown
        ttk.Label(excel_frame, text="Select Client:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.client_combo = ttk.Combobox(excel_frame, state="readonly", width=47)
        self.client_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        # Bind event to auto-populate credentials when client is selected
        self.client_combo.bind("<<ComboboxSelected>>", self.on_client_selected)

        # === Credentials Section ===
        # Frame for GST username and password (auto-filled when client is selected)
        credential_frame = ttk.LabelFrame(root, text="Credentials (auto-filled on client selection)")
        credential_frame.pack(padx=10, pady=10, fill="x")

        # GST username input field
        ttk.Label(credential_frame, text="GST Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(credential_frame, width=40)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        # GST password input field (masked for security)
        ttk.Label(credential_frame, text="GST Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(credential_frame, width=40, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # === Actions Selection Section ===
        # Frame for selecting which automation actions to perform
        action_frame = ttk.LabelFrame(root, text="Actions to Perform")
        action_frame.pack(padx=10, pady=10, fill="x")

        # Option to only perform login (no additional actions)
        self.just_login_var = tk.BooleanVar()
        self.just_login_check = ttk.Checkbutton(action_frame, text="Just Login", variable=self.just_login_var)
        self.just_login_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Option to navigate to Returns Dashboard
        self.returns_dashboard_var = tk.BooleanVar()
        self.returns_dashboard_check = ttk.Checkbutton(action_frame, text="Returns Dashboard", 
                                                      variable=self.returns_dashboard_var, 
                                                      command=self.toggle_returns_options)
        self.returns_dashboard_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Option to download GSTR-2B (requires Returns Dashboard)
        self.gstr2b_var = tk.BooleanVar()
        self.gstr2b_check = ttk.Checkbutton(action_frame, text="Download GSTR-2B", 
                                           variable=self.gstr2b_var, 
                                           command=self.toggle_returns_options)
        self.gstr2b_check.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # Option to access Electronic Credit Ledger
        self.credit_ledger_var = tk.BooleanVar()
        self.credit_ledger_check = ttk.Checkbutton(action_frame, text="Electronic Credit Ledger", 
                                                  variable=self.credit_ledger_var, 
                                                  command=self.toggle_credit_ledger_options)
        self.credit_ledger_check.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Option to access Electronic Cash Ledger
        self.cash_ledger_var = tk.BooleanVar()
        self.cash_ledger_check = ttk.Checkbutton(action_frame, text="Electronic Cash Ledger", 
                                                variable=self.cash_ledger_var)
        self.cash_ledger_check.grid(row=4, column=0, padx=5, pady=5, sticky="w")


        # === Returns Dashboard Options Section ===
        # Frame for financial year, quarter, and month selection (shown when Returns Dashboard is selected)
        self.returns_options_frame = ttk.LabelFrame(root, text="Returns Dashboard Options")

        # Financial Year selection dropdown
        ttk.Label(self.returns_options_frame, text="Financial Year:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.year_options = ["2025-26", "2024-25", "2023-24", "2022-23", "2021-22", "2020-21", "2019-20", "2018-19"] 
        self.year_combo = ttk.Combobox(self.returns_options_frame, values=self.year_options, state="readonly")
        self.year_combo.grid(row=0, column=1, padx=5, pady=5)
        # Set default selection to current financial year (2025-26)
        try:
            default_year_index = self.year_options.index("2025-26")
            self.year_combo.current(default_year_index)
        except ValueError:
            # Fallback to first option if default year not found
            if self.year_options: self.year_combo.current(0)


        # Quarter selection dropdown
        ttk.Label(self.returns_options_frame, text="Quarter:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quarter_options = ["Quarter 1 (Apr-Jun)", "Quarter 2 (Jul-Sep)", "Quarter 3 (Oct-Dec)", "Quarter 4 (Jan-Mar)"]
        self.quarter_combo = ttk.Combobox(self.returns_options_frame, values=self.quarter_options, state="readonly")
        self.quarter_combo.grid(row=1, column=1, padx=5, pady=5)
        # Default to first quarter
        if self.quarter_options : self.quarter_combo.current(0)


        # Month/Period selection dropdown
        ttk.Label(self.returns_options_frame, text="Period (Month):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.month_options = ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"]
        self.month_combo = ttk.Combobox(self.returns_options_frame, values=self.month_options, state="readonly")
        self.month_combo.grid(row=2, column=1, padx=5, pady=5)
        # Default to first month (April)
        if self.month_options: self.month_combo.current(0) 

        # === Credit Ledger Options Section ===
        # Frame for date range selection when accessing Credit Ledger
        self.credit_ledger_options_frame = ttk.LabelFrame(root, text="Credit Ledger Options")

        # From Date input field (defaults to current date)
        ttk.Label(self.credit_ledger_options_frame, text="From Date (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_date_entry = ttk.Entry(self.credit_ledger_options_frame)
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.from_date_entry.insert(0, time.strftime("%d-%m-%Y"))  # Insert today's date as default

        # To Date input field (defaults to current date)
        ttk.Label(self.credit_ledger_options_frame, text="To Date (DD-MM-YYYY):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.to_date_entry = ttk.Entry(self.credit_ledger_options_frame)
        self.to_date_entry.grid(row=1, column=1, padx=5, pady=5)
        self.to_date_entry.insert(0, time.strftime("%d-%m-%Y"))  # Insert today's date as default 
        
        # === Control Buttons Section ===
        # Frame for main control buttons (Start/Quit)
        control_frame = ttk.Frame(root)
        control_frame.pack(padx=10, pady=15, fill="x")

        # Start automation button (runs automation in separate thread)
        self.start_button = ttk.Button(control_frame, text="Start Automation", command=self.start_automation_thread)
        self.start_button.pack(side="left", padx=5)

        # Quit application button
        self.quit_button = ttk.Button(control_frame, text="Quit", command=root.quit)
        self.quit_button.pack(side="right", padx=5)

        # === Status Log Section ===
        # Frame for displaying automation progress and status messages
        status_frame = ttk.LabelFrame(root, text="Status")
        status_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Text widget for status messages (disabled to prevent user editing)
        self.status_text = tk.Text(status_frame, height=8, wrap="word", state="disabled") 
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize UI state - hide optional frames initially
        self.toggle_returns_options()
        self.toggle_credit_ledger_options()
        
        # Attempt to load clients from default Excel file (silent mode - no error popups)
        self.load_clients_from_excel(silent=True) 

        # Initialize WebDriver variable (will be set when automation starts)
        self.driver = None

    def log_status(self, message):
        """
        Add a status message to the status log display.
        
        Args:
            message (str): The status message to display
        """
        # Temporarily enable text widget to add new message
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)  # Auto-scroll to latest message
        self.status_text.config(state="disabled")  # Disable to prevent user editing
        self.root.update_idletasks()  # Force GUI update 

    def browse_excel_file(self):
        """
        Open file dialog to browse and select an Excel file containing client data.
        Expected Excel format: columns 'Client Name', 'GST Username', 'GST Password'
        """
        # Open file selection dialog with Excel file filter
        filepath = filedialog.askopenfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Select Clients Excel File"
        )
        if filepath:
            # Update the file path and automatically load clients
            self.excel_file_path.set(filepath)
            self.load_clients_from_excel() 

    def load_clients_from_excel(self, silent=False):
        """
        Load client data from the specified Excel file.
        
        Expected Excel columns:
        - 'Client Name': Name of the client
        - 'GST Username': GST portal username
        - 'GST Password': GST portal password
        
        Args:
            silent (bool): If True, suppress error message boxes (default: False)
        """
        excel_path = self.excel_file_path.get()
        
        # Check if file exists
        if not excel_path or not os.path.exists(excel_path):
            if not silent:
                messagebox.showerror("Error", f"Excel file not found at: {excel_path}")
            self.log_status(f"Error: Excel file not found at {excel_path}. Please select a valid file.")
            return

        try:
            self.log_status(f"Loading clients from {excel_path}...")
            
            # Define expected column names
            col_client_name = "Client Name"
            col_username = "GST Username" 
            col_password = "GST Password" 

            # Load Excel file as DataFrame with all columns as strings
            df = pd.read_excel(excel_path, dtype=str) 
            
            # Validate that all required columns exist
            required_cols = [col_client_name, col_username, col_password]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                messagebox.showerror("Excel Error", f"Missing required columns in Excel: {', '.join(missing_cols)}\nExpected: Client Name, GST Username, GST Password")
                self.log_status(f"Error: Missing columns in Excel: {', '.join(missing_cols)}")
                return

            # Process each row and build clients dictionary
            self.clients_data = {}
            for index, row in df.iterrows():
                client_name = str(row[col_client_name]).strip()
                username = str(row[col_username]).strip()
                password = str(row[col_password]).strip() 
                
                # Only add clients with valid name and username
                if client_name and username: 
                    self.clients_data[client_name] = {"username": username, "password": password}
            
            # Update UI with loaded client data
            client_names = list(self.clients_data.keys())
            self.client_combo['values'] = client_names
            
            if client_names:
                # Select first client by default and populate credentials
                self.client_combo.current(0)
                self.on_client_selected(None)  # Trigger credential population
                self.log_status(f"Successfully loaded {len(client_names)} clients.")
            else:
                # Clear combo box and credential fields if no valid clients found
                self.client_combo['values'] = []
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.log_status("No clients found in the Excel file or data is invalid.")
                
            # Show success message (unless in silent mode)
            if not silent and client_names:
                 messagebox.showinfo("Success", f"Successfully loaded {len(client_names)} clients.")

        except Exception as e:
            # Handle any errors during Excel file processing
            if not silent:
                messagebox.showerror("Excel Load Error", f"Failed to load clients from Excel: {e}")
            self.log_status(f"Error loading clients: {e}")
            self.client_combo['values'] = []  # Clear combo box on error 

    def on_client_selected(self, event):
        """
        Handle client selection from dropdown - auto-populate username and password fields.
        
        Args:
            event: Tkinter event object (not used but required by binding)
        """
        selected_client_name = self.client_combo.get()
        
        if selected_client_name in self.clients_data:
            # Get client credentials and populate entry fields
            client_info = self.clients_data[selected_client_name]
            
            # Clear and populate username field
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, client_info["username"])
            
            # Clear and populate password field
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, client_info["password"])
            
            self.log_status(f"Selected client: {selected_client_name}. Credentials populated.")
        else:
            # Clear fields if client not found in data
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)


    def toggle_returns_options(self):
        """
        Show/hide the Returns Dashboard options frame based on checkbox selections.
        The frame is shown when either Returns Dashboard or GSTR-2B is selected.
        """
        # Show options frame if Returns Dashboard or GSTR-2B is selected
        if self.returns_dashboard_var.get() or self.gstr2b_var.get():
            # Position before credit ledger options if visible, otherwise before control buttons
            before_widget = (self.credit_ledger_options_frame if self.credit_ledger_options_frame.winfo_ismapped() 
                           else self.start_button.master)
            self.returns_options_frame.pack(padx=10, pady=5, fill="x", before=before_widget)
        else:
            # Hide the options frame
            self.returns_options_frame.pack_forget()
        
        # Inform user that GSTR-2B requires Returns Dashboard
        if self.gstr2b_var.get() and not self.returns_dashboard_var.get():
             self.log_status("Note: GSTR-2B requires Returns Dashboard flow.")


    def toggle_credit_ledger_options(self):
        """
        Show/hide the Credit Ledger options frame based on checkbox selection.
        The frame contains date range fields for credit ledger queries.
        """
        if self.credit_ledger_var.get():
            # Show credit ledger options frame before control buttons
            self.credit_ledger_options_frame.pack(padx=10, pady=5, fill="x", before=self.start_button.master)
        else:
            # Hide the options frame
            self.credit_ledger_options_frame.pack_forget()

    def start_automation_thread(self):
        """
        Start the automation process in a separate thread to keep the GUI responsive.
        Validates input data and collects all selected options before starting.
        """
        # Disable start button to prevent multiple simultaneous runs
        self.start_button.config(state="disabled")
        self.log_status("Starting automation...")
        
        # Get credentials from entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Get selected action options
        do_just_login = self.just_login_var.get()
        do_returns_dashboard = self.returns_dashboard_var.get()
        do_gstr2b = self.gstr2b_var.get()
        do_credit_ledger = self.credit_ledger_var.get()
        do_cash_ledger = self.cash_ledger_var.get() 

        # Validate that credentials are provided
        if not username or not password:
            messagebox.showerror("Error", "Username and Password cannot be empty. Please select a client or enter credentials manually.")
            self.log_status("Error: Username and Password cannot be empty.")
            self.start_button.config(state="normal")  # Re-enable start button
            return

        # GSTR-2B download requires Returns Dashboard, so enable it automatically
        if do_gstr2b:
            do_returns_dashboard = True

        # Get Returns Dashboard options (dropdown indices)
        returns_year_index = self.year_combo.current() 
        returns_quarter_index = self.quarter_combo.current()
        returns_month_index = self.month_combo.current()

        # Get Credit Ledger date range
        credit_from_date = self.from_date_entry.get()
        credit_to_date = self.to_date_entry.get()

        # Create and start automation thread with all parameters
        automation_thread = threading.Thread(
            target=self.run_automation, 
            args=(username, password, do_just_login, 
                  do_returns_dashboard, do_gstr2b, 
                  do_credit_ledger, do_cash_ledger, 
                  returns_year_index, returns_quarter_index, returns_month_index,
                  credit_from_date, credit_to_date)
        )
        automation_thread.daemon = True  # Thread will close when main program exits
        automation_thread.start()


    def run_automation(self, username, password, do_just_login, 
                       do_returns_dashboard, do_gstr2b, 
                       do_credit_ledger, do_cash_ledger, 
                       returns_year_index, returns_quarter_index, returns_month_index,
                       credit_from_date, credit_to_date):
        """
        Main automation execution method that runs in a separate thread.
        
        This method handles the complete automation flow:
        1. Initialize Chrome WebDriver with download preferences
        2. Navigate to GST portal and perform login
        3. Execute selected actions (Returns Dashboard, GSTR-2B, Ledgers)
        4. Handle errors and cleanup
        
        Args:
            username (str): GST portal username
            password (str): GST portal password
            do_just_login (bool): If True, only perform login
            do_returns_dashboard (bool): If True, navigate to Returns Dashboard
            do_gstr2b (bool): If True, download GSTR-2B
            do_credit_ledger (bool): If True, access Credit Ledger
            do_cash_ledger (bool): If True, access Cash Ledger
            returns_year_index (int): Selected financial year index
            returns_quarter_index (int): Selected quarter index
            returns_month_index (int): Selected month index
            credit_from_date (str): Credit ledger from date (DD-MM-YYYY)
            credit_to_date (str): Credit ledger to date (DD-MM-YYYY)
        """
        # Define wait times for different scenarios (in seconds)
        short_wait_time = 15     # Quick elements
        long_wait_time = 40      # Slower loading elements
        very_long_wait_time = 75 # Very slow operations
        manual_captcha_wait_time = 90  # Time for user to enter CAPTCHA 

        try:
            # === WebDriver Initialization ===
            self.log_status("Initializing Chrome WebDriver...")
            # Use local ChromeDriver executable
            script_dir = os.path.dirname(os.path.abspath(__file__))
            chromedriver_path = os.path.join(script_dir, "chromedriver-linux64", "chromedriver")
            service = ChromeService(chromedriver_path)
            
            # Set up download directory
            download_dir = os.path.join(script_dir, "GST_Downloads")
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)  # Create directory if it doesn't exist
            self.log_status(f"Downloads will be saved to: {download_dir}")

            # Configure Chrome options for automated downloads
            chrome_options = webdriver.ChromeOptions()
            prefs = {
                "download.default_directory": download_dir,  # Set download location
                "download.prompt_for_download": False,       # Auto-download without prompts
                "download.directory_upgrade": True,          # Allow directory changes
                "plugins.always_open_pdf_externally": True   # Open PDFs externally
            }
            chrome_options.add_experimental_option("prefs", prefs)
            # Uncomment below lines to run Chrome in headless mode (no GUI)
            # chrome_options.add_argument("--headless")
            # chrome_options.add_argument("--disable-gpu") 

            # Initialize Chrome WebDriver with configured options
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            actions = ActionChains(self.driver)  # For hover and complex mouse actions
            self.driver.maximize_window()  # Maximize browser window for better element visibility

            # === GST Portal Navigation ===
            self.log_status("Navigating to GST portal...")
            self.driver.get("https://www.gst.gov.in/")

            # Find and click the Login link (with fallback locators)
            login_link_locator = (By.XPATH, "//a[contains(@href,'login') and normalize-space()='Login']")
            try:
                WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable(login_link_locator)).click()
            except:
                self.log_status("Preferred login link locator failed, trying original XPath...")
                # Fallback to absolute XPath if primary locator fails
                original_login_link_xpath = "/html/body/div[1]/header/div[2]/div/div/ul/li[2]"
                WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable((By.XPATH, original_login_link_xpath))).click()
            self.log_status("Clicked on Login link.")

            # Wait for any page overlays/loaders to disappear
            dimmer_locator = (By.CLASS_NAME, "dimmer-holder") 
            try:
                self.log_status("Waiting for page overlay to disappear (if any)...")
                WebDriverWait(self.driver, short_wait_time).until(EC.invisibility_of_element_located(dimmer_locator))
                self.log_status("Overlay gone or not present.")
            except:
                self.log_status("Overlay did not disappear in time, or was not found. Proceeding...")

            # === Login Form Filling ===
            # Wait for and fill username field
            username_field_id = "username" 
            WebDriverWait(self.driver, long_wait_time).until(EC.visibility_of_element_located((By.ID, username_field_id)))
            
            self.driver.find_element(By.ID, username_field_id).send_keys(username)
            self.log_status("Entered username.")
            
            # Fill password field
            password_field_id = "user_pass" 
            self.driver.find_element(By.ID, password_field_id).send_keys(password)
            self.log_status("Entered password.")

            # Handle CAPTCHA (manual user input required)
            captcha_field_id = "captcha"
            try:
                # Wait for any remaining overlays to disappear
                WebDriverWait(self.driver, short_wait_time).until(EC.invisibility_of_element_located(dimmer_locator))
            except:
                pass  # Ignore if overlay is not present

            # Click on CAPTCHA field to focus it
            WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable((By.ID, captcha_field_id))).click()
            
            # Notify user to manually enter CAPTCHA
            self.log_status(f"IMPORTANT: Please enter the CAPTCHA in the browser and click Login. You have {manual_captcha_wait_time} seconds.")
            
            # Wait for successful login (URL change indicates success)
            welcome_page_url_part = "services.gst.gov.in/services/auth/fowelcome"
            WebDriverWait(self.driver, manual_captcha_wait_time).until(EC.url_contains(welcome_page_url_part))
            self.log_status("Login successful. Navigated to welcome page.")
            
            time.sleep(2)  # Brief pause for page stabilization 

            # Handle post-login popups (if any)
            try:
                popup_close_button_locator = (By.XPATH, "//a[@data-dismiss='modal' and normalize-space()='Remind me later']")
                popup_button = WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(popup_close_button_locator))
                popup_button.click()
                self.log_status("Closed a pop-up ('Remind me later').")
                time.sleep(1)
            except Exception as e:
                self.log_status(f"No pop-up found or could not close it (this is often OK).")

            # === Action Execution Based on User Selection ===
            # Check if only login was requested
            if do_just_login and not do_returns_dashboard and not do_credit_ledger and not do_cash_ledger: 
                self.log_status("Action: Just Login selected. Automation will stop here.")
            
            # === Returns Dashboard Navigation ===
            if do_returns_dashboard: 
                self.log_status("Navigating to Returns Dashboard...")
                
                # Multiple locators for Returns Dashboard button (fallback strategy)
                returns_dashboard_button_locator_preferred = (By.CSS_SELECTOR, "button[onclick*='return.gst.gov.in/returns/auth/dashboard']")
                returns_dashboard_button_locator_alternative_xpath = (By.XPATH, "//button[.//span[normalize-space()='Return Dashboard']]")
                returns_dashboard_button_locator_original_vba_xpath = (By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/button/span")
                
                # Try to click Returns Dashboard button with multiple fallback strategies
                try:
                    WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(returns_dashboard_button_locator_preferred)).click()
                except:
                    self.log_status("Could not click Returns Dashboard with preferred CSS Selector, trying alternative XPath...")
                    try:
                        WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(returns_dashboard_button_locator_alternative_xpath)).click()
                    except:
                        self.log_status("Alternative XPath for Returns Dashboard failed, trying original VBA XPath (this might be slow)...")
                        WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable(returns_dashboard_button_locator_original_vba_xpath)).click()

                self.log_status("Clicked Returns Dashboard button.")
                time.sleep(3)  # Wait for dashboard page to load 

                # Define locators for Returns Dashboard filter elements
                year_select_name = "fin"     # Financial year dropdown
                quarter_select_name = "quarter"  # Quarter dropdown
                month_select_name = "mon"    # Month dropdown
                search_button_locator_preferred = (By.CSS_SELECTOR, "button.srchbtn[type='submit']") 
                search_button_locator_alternative_xpath = (By.XPATH, "//button[contains(@class, 'srchbtn') and normalize-space()='Search']")

                # Fallback XPath locators (absolute paths as last resort)
                year_select_xpath_fallback = "/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div[1]/div[1]/select" 
                quarter_select_xpath_fallback = "/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div[1]/div[2]/select"
                month_select_xpath_fallback = "/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div[1]/div[3]/select"
                search_button_xpath_fallback = "/html/body/div[2]/div[2]/div/div[2]/div[2]/form/div[1]/div[4]/button"

                try:
                    Select(WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located((By.NAME, year_select_name)))).select_by_index(returns_year_index)
                except:
                    self.log_status(f"Year dropdown with name '{year_select_name}' not found, using fallback XPath.")
                    Select(WebDriverWait(self.driver, long_wait_time).until(EC.visibility_of_element_located((By.XPATH, year_select_xpath_fallback)))).select_by_index(returns_year_index)
                self.log_status(f"Selected Year (index: {returns_year_index}).")
                time.sleep(0.5)

                try:
                    Select(WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located((By.NAME, quarter_select_name)))).select_by_index(returns_quarter_index)
                except:
                    self.log_status(f"Quarter dropdown with name '{quarter_select_name}' not found, using fallback XPath.")
                    Select(WebDriverWait(self.driver, long_wait_time).until(EC.visibility_of_element_located((By.XPATH, quarter_select_xpath_fallback)))).select_by_index(returns_quarter_index)
                self.log_status(f"Selected Quarter (index: {returns_quarter_index}).")
                time.sleep(0.5)

                try:
                    Select(WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located((By.NAME, month_select_name)))).select_by_index(returns_month_index)
                except:
                    self.log_status(f"Month dropdown with name '{month_select_name}' not found, using fallback XPath.")
                    Select(WebDriverWait(self.driver, long_wait_time).until(EC.visibility_of_element_located((By.XPATH, month_select_xpath_fallback)))).select_by_index(returns_month_index)
                self.log_status(f"Selected Month (index: {returns_month_index}).")
                time.sleep(1)

                try:
                    WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(search_button_locator_preferred)).click()
                except:
                    self.log_status(f"Search button with preferred CSS Selector failed, trying alternative XPath.")
                    try:
                        WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(search_button_locator_alternative_xpath)).click()
                    except:
                        self.log_status(f"Alternative XPath for Search button failed, using fallback XPath.")
                        WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable((By.XPATH, search_button_xpath_fallback))).click()
                self.log_status("Clicked Search/View on Returns page.")
                time.sleep(2) 

                if do_gstr2b:
                    self.log_status("Attempting to download GSTR-2B...")
                    
                    gstr2b_initial_download_button_locator = (By.CSS_SELECTOR, "button[data-ng-click='offlinepath(x.return_ty)']")
                    
                    try:
                        WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(gstr2b_initial_download_button_locator)).click()
                        self.log_status("Clicked GSTR-2B 'Download' button (user's step 4).")
                        time.sleep(3) 
                    except Exception as e1:
                        self.log_status(f"Error clicking initial GSTR-2B download button: {e1}. This button might not be directly available or visible under GSTR-2B section after search.")
                        
                    gstr2b_generate_excel_button_locator = (By.XPATH, "//button[normalize-space()='GENERATE EXCEL FILE TO DOWNLOAD']")
                    try:
                        WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(gstr2b_generate_excel_button_locator)).click()
                        self.log_status("Clicked 'GENERATE EXCEL FILE TO DOWNLOAD' button (user's step 5).")
                        self.log_status("GSTR-2B Excel download should start. Check your 'GST_Downloads' folder.")
                        time.sleep(15) 
                    except Exception as gstr2b_err_final:
                        self.log_status(f"Error clicking 'GENERATE EXCEL FILE TO DOWNLOAD': {gstr2b_err_final}")
                        self.log_status("This means the generate button was not found on the subsequent page/modal, or the previous step failed.")

            # --- Electronic Credit Ledger Flow (Click Services -> Hover Ledgers -> Click ECL) ---
            if do_credit_ledger:
                self.log_status("Navigating to Electronic Credit Ledger (using click Services -> hover Ledgers -> click ECL)...")
                services_menu_locator = (By.XPATH, "//a[contains(@class, 'dropdown-toggle') and starts-with(normalize-space(.), 'Services')]")
                ledgers_submenu_to_hover_locator = (By.LINK_TEXT, "Ledgers") 
                direct_credit_ledger_link_locator = (By.XPATH, "//a[@href='//return.gst.gov.in/returns/auth/ledger/itcledger' and normalize-space()='Electronic Credit Ledger']")
                electronic_credit_ledger_detailed_link_locator = (By.CSS_SELECTOR, "a[data-ng-bind='trans.LBL_ELEC_CREDIT_LEDG']")
                
                try:
                    self.log_status("Attempting to click 'Services' menu...")
                    services_element = WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(services_menu_locator))
                    services_element.click()
                    self.log_status("Clicked 'Services' menu.")
                    time.sleep(1) 

                    self.log_status("Attempting to hover over 'Ledgers' submenu...")
                    ledgers_to_hover_element = WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located(ledgers_submenu_to_hover_locator))
                    actions = ActionChains(self.driver) 
                    actions.move_to_element(ledgers_to_hover_element).perform()
                    self.log_status("Hovered over 'Ledgers' submenu.")
                    
                    self.log_status(f"Waiting for direct 'Electronic Credit Ledger' link from hover menu to be clickable...")
                    direct_credit_ledger_link = WebDriverWait(self.driver, long_wait_time).until(
                        EC.element_to_be_clickable(direct_credit_ledger_link_locator)
                    )
                    self.log_status("Direct 'Electronic Credit Ledger' link is clickable.")
                    direct_credit_ledger_link.click()
                    self.log_status("Clicked 'Electronic Credit Ledger' from hover menu.")
                    
                    self.log_status("Waiting for detailed credit ledger page to load...")
                    WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable(electronic_credit_ledger_detailed_link_locator)).click()
                    self.log_status("Clicked second 'Electronic Credit Ledger' link (for detailed view/date selection).")
                    time.sleep(2) 

                    self.log_status(f"Attempting to set dates for Credit Ledger: From {credit_from_date} To {credit_to_date}.")
                    from_date_field_id = "sumlg_frdt" 
                    to_date_field_id = "sumlg_todt"   
                    go_button_locator = (By.CSS_SELECTOR, "button[data-ng-click='getdetLdgr()']")

                    try:
                        from_date_field = WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located((By.ID, from_date_field_id))) 
                        from_date_field.clear()
                        from_date_field.click() 
                        from_date_field.send_keys(credit_from_date) 
                        self.log_status(f"Entered 'From Date': {credit_from_date}")
                        self.driver.find_element(By.TAG_NAME, "body").click() 
                        time.sleep(0.5)

                        to_date_field = WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located((By.ID, to_date_field_id))) 
                        to_date_field.clear()
                        to_date_field.click()
                        to_date_field.send_keys(credit_to_date)
                        self.log_status(f"Entered 'To Date': {credit_to_date}")
                        self.driver.find_element(By.TAG_NAME, "body").click() 
                        time.sleep(0.5)

                        go_button_element = WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(go_button_locator)) 
                        go_button_element.click()
                        self.log_status("Clicked 'GO' button for credit ledger dates.")
                        time.sleep(2)
                    except Exception as date_err:
                        self.log_status(f"Could not set dates automatically for Credit Ledger: {date_err}")
                        self.log_status("You may need to select dates manually if the automation fails here.")
                        self.log_status("The script will pause for 15 seconds for manual intervention if needed.")
                        time.sleep(15) 
                except TimeoutException:
                    self.log_status(f"TimeoutException: Timed out during Electronic Credit Ledger navigation (click Services -> hover Ledgers method).")
                    self.driver.save_screenshot(f"debug_credit_ledger_click_hover_fail_{time.time()}.png")
                    self.log_status(f"Screenshot saved: debug_credit_ledger_click_hover_fail_{time.time()}.png")
                except Exception as e_credit_nav:
                    self.log_status(f"An unexpected error occurred during Electronic Credit Ledger navigation (click Services -> hover Ledgers method): {e_credit_nav}")

            
            # --- Electronic Cash Ledger Flow (New Hover Logic) ---
            if do_cash_ledger:
                self.log_status("Navigating to Electronic Cash Ledger (using click Services -> hover Ledgers -> click ECL)...")
                services_menu_locator = (By.XPATH, "//a[contains(@class, 'dropdown-toggle') and starts-with(normalize-space(.), 'Services')]")
                ledgers_submenu_to_hover_locator = (By.LINK_TEXT, "Ledgers")
                # ASSUMED SELECTOR - USER NEEDS TO PROVIDE THE ACTUAL SELECTOR FOR THIS LINK FROM HOVER MENU
                direct_cash_ledger_link_locator = (By.XPATH, "//a[@href='//payment.gst.gov.in/payment/auth/ledger/cashledger' and normalize-space()='Electronic Cash Ledger']")
                cash_ledger_balance_details_link_locator = (By.CSS_SELECTOR, "a.inverseLink[data-target='#balanceModal']")
                
                try:
                    self.log_status("Attempting to click 'Services' menu...")
                    services_element = WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(services_menu_locator))
                    services_element.click()
                    self.log_status("Clicked 'Services' menu.")
                    time.sleep(1) 

                    self.log_status("Attempting to hover over 'Ledgers' submenu...")
                    ledgers_to_hover_element = WebDriverWait(self.driver, short_wait_time).until(EC.visibility_of_element_located(ledgers_submenu_to_hover_locator))
                    actions = ActionChains(self.driver) 
                    actions.move_to_element(ledgers_to_hover_element).perform()
                    self.log_status("Hovered over 'Ledgers' submenu.")
                    
                    self.log_status(f"Waiting for direct 'Electronic Cash Ledger' link from hover menu to be clickable...")
                    direct_cash_ledger_link = WebDriverWait(self.driver, long_wait_time).until(
                        EC.element_to_be_clickable(direct_cash_ledger_link_locator)
                    )
                    self.log_status("Direct 'Electronic Cash Ledger' link is clickable.")
                    direct_cash_ledger_link.click()
                    self.log_status("Clicked 'Electronic Cash Ledger' from hover menu.")
                    
                    # Now we should be on the cash ledger page
                    time.sleep(2) # Allow page to load

                    WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable(cash_ledger_balance_details_link_locator)).click()
                    self.log_status("Clicked link to view cash ledger balance details (modal should open).")
                    time.sleep(3) 
                except TimeoutException:
                    self.log_status(f"TimeoutException: Timed out during Electronic Cash Ledger navigation (click Services -> hover Ledgers method).")
                    self.driver.save_screenshot(f"debug_cash_ledger_click_hover_fail_{time.time()}.png")
                    self.log_status(f"Screenshot saved: debug_cash_ledger_click_hover_fail_{time.time()}.png")
                except Exception as e_cash_nav:
                    self.log_status(f"An unexpected error occurred during Electronic Cash Ledger navigation (click Services -> hover Ledgers method): {e_cash_nav}")
                
            self.log_status("Automation actions completed (or reached selected point).")
            messagebox.showinfo("GST Automation", "Automation actions completed (or reached selected point). Check status log for details. Browser will remain open for a few seconds.")
            time.sleep(5) 

        except TimeoutException as te: 
            self.log_status(f"A major timeout occurred: {te}")
            # self.driver.save_screenshot(f"debug_major_timeout_{time.time()}.png") 
            # self.log_status(f"Screenshot saved on major timeout: debug_major_timeout_{time.time()}.png")
            messagebox.showerror("Timeout Error", f"The operation timed out. Please check the logs and network. {te}")
        except Exception as e:
            self.log_status(f"An error occurred: {e}")
            messagebox.showerror("Error", f"An error occurred during automation: {e}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    self.log_status("Browser closed.")
                except Exception as e:
                    self.log_status(f"Error closing browser: {e}")
            self.start_button.config(state="normal") 

if __name__ == "__main__":
    root = tk.Tk()
    app = GSTAutomationApp(root)
    root.mainloop()
