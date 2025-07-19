import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.common.exceptions import TimeoutException # Import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading 
import pandas as pd 
import os 

class GSTAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GST Portal Automation - Srinidhi B S")
        self.root.geometry("600x780") 

        self.clients_data = {} 
        self.excel_file_path = tk.StringVar(value=os.path.join(os.getcwd(), "clients.xlsx")) 

        excel_frame = ttk.LabelFrame(root, text="Client Data from Excel")
        excel_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(excel_frame, text="Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.excel_path_entry = ttk.Entry(excel_frame, textvariable=self.excel_file_path, width=50)
        self.excel_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ttk.Button(excel_frame, text="Browse", command=self.browse_excel_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        self.load_clients_button = ttk.Button(excel_frame, text="Load Clients from Excel", command=self.load_clients_from_excel)
        self.load_clients_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ttk.Label(excel_frame, text="Select Client:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.client_combo = ttk.Combobox(excel_frame, state="readonly", width=47)
        self.client_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.client_combo.bind("<<ComboboxSelected>>", self.on_client_selected)

        credential_frame = ttk.LabelFrame(root, text="Credentials (auto-filled on client selection)")
        credential_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(credential_frame, text="GST Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(credential_frame, width=40)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(credential_frame, text="GST Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(credential_frame, width=40, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        action_frame = ttk.LabelFrame(root, text="Actions to Perform")
        action_frame.pack(padx=10, pady=10, fill="x")

        self.just_login_var = tk.BooleanVar()
        self.just_login_check = ttk.Checkbutton(action_frame, text="Just Login", variable=self.just_login_var)
        self.just_login_check.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.returns_dashboard_var = tk.BooleanVar()
        self.returns_dashboard_check = ttk.Checkbutton(action_frame, text="Returns Dashboard", variable=self.returns_dashboard_var, command=self.toggle_returns_options)
        self.returns_dashboard_check.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.gstr2b_var = tk.BooleanVar()
        self.gstr2b_check = ttk.Checkbutton(action_frame, text="Download GSTR-2B", variable=self.gstr2b_var, command=self.toggle_returns_options)
        self.gstr2b_check.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.credit_ledger_var = tk.BooleanVar()
        self.credit_ledger_check = ttk.Checkbutton(action_frame, text="Electronic Credit Ledger", variable=self.credit_ledger_var, command=self.toggle_credit_ledger_options)
        self.credit_ledger_check.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.cash_ledger_var = tk.BooleanVar()
        self.cash_ledger_check = ttk.Checkbutton(action_frame, text="Electronic Cash Ledger", variable=self.cash_ledger_var)
        self.cash_ledger_check.grid(row=4, column=0, padx=5, pady=5, sticky="w")


        self.returns_options_frame = ttk.LabelFrame(root, text="Returns Dashboard Options")

        ttk.Label(self.returns_options_frame, text="Financial Year:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.year_options = ["2025-26", "2024-25", "2023-24", "2022-23", "2021-22", "2020-21", "2019-20", "2018-19"] 
        self.year_combo = ttk.Combobox(self.returns_options_frame, values=self.year_options, state="readonly")
        self.year_combo.grid(row=0, column=1, padx=5, pady=5)
        try:
            default_year_index = self.year_options.index("2025-26")
            self.year_combo.current(default_year_index)
        except ValueError:
            if self.year_options: self.year_combo.current(0)


        ttk.Label(self.returns_options_frame, text="Quarter:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quarter_options = ["Quarter 1 (Apr-Jun)", "Quarter 2 (Jul-Sep)", "Quarter 3 (Oct-Dec)", "Quarter 4 (Jan-Mar)"]
        self.quarter_combo = ttk.Combobox(self.returns_options_frame, values=self.quarter_options, state="readonly")
        self.quarter_combo.grid(row=1, column=1, padx=5, pady=5)
        if self.quarter_options : self.quarter_combo.current(0)


        ttk.Label(self.returns_options_frame, text="Period (Month):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.month_options = ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"]
        self.month_combo = ttk.Combobox(self.returns_options_frame, values=self.month_options, state="readonly")
        self.month_combo.grid(row=2, column=1, padx=5, pady=5)
        if self.month_options: self.month_combo.current(0) 

        self.credit_ledger_options_frame = ttk.LabelFrame(root, text="Credit Ledger Options")

        ttk.Label(self.credit_ledger_options_frame, text="From Date (DD-MM-YYYY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_date_entry = ttk.Entry(self.credit_ledger_options_frame)
        self.from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.from_date_entry.insert(0, time.strftime("%d-%m-%Y")) 

        ttk.Label(self.credit_ledger_options_frame, text="To Date (DD-MM-YYYY):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.to_date_entry = ttk.Entry(self.credit_ledger_options_frame)
        self.to_date_entry.grid(row=1, column=1, padx=5, pady=5)
        self.to_date_entry.insert(0, time.strftime("%d-%m-%Y")) 
        
        control_frame = ttk.Frame(root)
        control_frame.pack(padx=10, pady=15, fill="x")

        self.start_button = ttk.Button(control_frame, text="Start Automation", command=self.start_automation_thread)
        self.start_button.pack(side="left", padx=5)

        self.quit_button = ttk.Button(control_frame, text="Quit", command=root.quit)
        self.quit_button.pack(side="right", padx=5)

        status_frame = ttk.LabelFrame(root, text="Status")
        status_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, wrap="word", state="disabled") 
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.toggle_returns_options()
        self.toggle_credit_ledger_options()
        self.load_clients_from_excel(silent=True) 

        self.driver = None

    def log_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END) 
        self.status_text.config(state="disabled")
        self.root.update_idletasks() 

    def browse_excel_file(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Select Clients Excel File"
        )
        if filepath:
            self.excel_file_path.set(filepath)
            self.load_clients_from_excel() 

    def load_clients_from_excel(self, silent=False):
        excel_path = self.excel_file_path.get()
        if not excel_path or not os.path.exists(excel_path):
            if not silent:
                messagebox.showerror("Error", f"Excel file not found at: {excel_path}")
            self.log_status(f"Error: Excel file not found at {excel_path}. Please select a valid file.")
            return

        try:
            self.log_status(f"Loading clients from {excel_path}...")
            col_client_name = "Client Name"
            col_username = "GST Username" 
            col_password = "GST Password" 

            df = pd.read_excel(excel_path, dtype=str) 
            
            required_cols = [col_client_name, col_username, col_password]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                messagebox.showerror("Excel Error", f"Missing required columns in Excel: {', '.join(missing_cols)}\nExpected: Client Name, GST Username, GST Password")
                self.log_status(f"Error: Missing columns in Excel: {', '.join(missing_cols)}")
                return

            self.clients_data = {}
            for index, row in df.iterrows():
                client_name = str(row[col_client_name]).strip()
                username = str(row[col_username]).strip()
                password = str(row[col_password]).strip() 
                if client_name and username: 
                    self.clients_data[client_name] = {"username": username, "password": password}
            
            client_names = list(self.clients_data.keys())
            self.client_combo['values'] = client_names
            if client_names:
                self.client_combo.current(0)
                self.on_client_selected(None) 
                self.log_status(f"Successfully loaded {len(client_names)} clients.")
            else:
                self.client_combo['values'] = []
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.log_status("No clients found in the Excel file or data is invalid.")
            if not silent and client_names:
                 messagebox.showinfo("Success", f"Successfully loaded {len(client_names)} clients.")

        except Exception as e:
            if not silent:
                messagebox.showerror("Excel Load Error", f"Failed to load clients from Excel: {e}")
            self.log_status(f"Error loading clients: {e}")
            self.client_combo['values'] = [] 

    def on_client_selected(self, event):
        selected_client_name = self.client_combo.get()
        if selected_client_name in self.clients_data:
            client_info = self.clients_data[selected_client_name]
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, client_info["username"])
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, client_info["password"])
            self.log_status(f"Selected client: {selected_client_name}. Credentials populated.")
        else:
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)


    def toggle_returns_options(self):
        if self.returns_dashboard_var.get() or self.gstr2b_var.get():
            self.returns_options_frame.pack(padx=10, pady=5, fill="x", before=self.credit_ledger_options_frame if self.credit_ledger_options_frame.winfo_ismapped() else self.start_button.master)
        else:
            self.returns_options_frame.pack_forget()
        
        if self.gstr2b_var.get() and not self.returns_dashboard_var.get():
             self.log_status("Note: GSTR-2B requires Returns Dashboard flow.")


    def toggle_credit_ledger_options(self):
        if self.credit_ledger_var.get():
            self.credit_ledger_options_frame.pack(padx=10, pady=5, fill="x", before=self.start_button.master)
        else:
            self.credit_ledger_options_frame.pack_forget()

    def start_automation_thread(self):
        self.start_button.config(state="disabled")
        self.log_status("Starting automation...")
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        do_just_login = self.just_login_var.get()
        do_returns_dashboard = self.returns_dashboard_var.get()
        do_gstr2b = self.gstr2b_var.get()
        do_credit_ledger = self.credit_ledger_var.get()
        do_cash_ledger = self.cash_ledger_var.get() 

        if not username or not password:
            messagebox.showerror("Error", "Username and Password cannot be empty. Please select a client or enter credentials manually.")
            self.log_status("Error: Username and Password cannot be empty.")
            self.start_button.config(state="normal")
            return

        if do_gstr2b:
            do_returns_dashboard = True

        returns_year_index = self.year_combo.current() 
        returns_quarter_index = self.quarter_combo.current()
        returns_month_index = self.month_combo.current()

        credit_from_date = self.from_date_entry.get()
        credit_to_date = self.to_date_entry.get()

        automation_thread = threading.Thread(target=self.run_automation, 
                                             args=(username, password, do_just_login, 
                                                   do_returns_dashboard, do_gstr2b, 
                                                   do_credit_ledger, do_cash_ledger, 
                                                   returns_year_index, returns_quarter_index, returns_month_index,
                                                   credit_from_date, credit_to_date))
        automation_thread.daemon = True 
        automation_thread.start()


    def run_automation(self, username, password, do_just_login, 
                       do_returns_dashboard, do_gstr2b, 
                       do_credit_ledger, do_cash_ledger, 
                       returns_year_index, returns_quarter_index, returns_month_index,
                       credit_from_date, credit_to_date):
        short_wait_time = 15 
        long_wait_time = 40  
        very_long_wait_time = 75 
        manual_captcha_wait_time = 90 

        try:
            self.log_status("Initializing Chrome WebDriver...")
            service = ChromeService(ChromeDriverManager().install())
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            download_dir = os.path.join(script_dir, "GST_Downloads")
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            self.log_status(f"Downloads will be saved to: {download_dir}")

            chrome_options = webdriver.ChromeOptions()
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False, 
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True 
            }
            chrome_options.add_experimental_option("prefs", prefs)
            # chrome_options.add_argument("--headless")
            # chrome_options.add_argument("--disable-gpu") 

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            actions = ActionChains(self.driver) 
            self.driver.maximize_window()

            self.log_status("Navigating to GST portal...")
            self.driver.get("https://www.gst.gov.in/")

            login_link_locator = (By.XPATH, "//a[contains(@href,'login') and normalize-space()='Login']")
            try:
                WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable(login_link_locator)).click()
            except:
                self.log_status("Preferred login link locator failed, trying original XPath...")
                original_login_link_xpath = "/html/body/div[1]/header/div[2]/div/div/ul/li[2]"
                WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable((By.XPATH, original_login_link_xpath))).click()
            self.log_status("Clicked on Login link.")

            dimmer_locator = (By.CLASS_NAME, "dimmer-holder") 
            try:
                self.log_status("Waiting for page overlay to disappear (if any)...")
                WebDriverWait(self.driver, short_wait_time).until(EC.invisibility_of_element_located(dimmer_locator))
                self.log_status("Overlay gone or not present.")
            except:
                self.log_status("Overlay did not disappear in time, or was not found. Proceeding...")

            username_field_id = "username" 
            WebDriverWait(self.driver, long_wait_time).until(EC.visibility_of_element_located((By.ID, username_field_id)))
            
            self.driver.find_element(By.ID, username_field_id).send_keys(username)
            self.log_status("Entered username.")
            
            password_field_id = "user_pass" 
            self.driver.find_element(By.ID, password_field_id).send_keys(password)
            self.log_status("Entered password.")

            captcha_field_id = "captcha"
            try:
                WebDriverWait(self.driver, short_wait_time).until(EC.invisibility_of_element_located(dimmer_locator))
            except:
                pass 

            WebDriverWait(self.driver, long_wait_time).until(EC.element_to_be_clickable((By.ID, captcha_field_id))).click()
            
            self.log_status(f"IMPORTANT: Please enter the CAPTCHA in the browser and click Login. You have {manual_captcha_wait_time} seconds.")
            
            welcome_page_url_part = "services.gst.gov.in/services/auth/fowelcome"
            WebDriverWait(self.driver, manual_captcha_wait_time).until(EC.url_contains(welcome_page_url_part))
            self.log_status("Login successful. Navigated to welcome page.")
            
            time.sleep(2) 

            try:
                popup_close_button_locator = (By.XPATH, "//a[@data-dismiss='modal' and normalize-space()='Remind me later']")
                popup_button = WebDriverWait(self.driver, short_wait_time).until(EC.element_to_be_clickable(popup_close_button_locator))
                popup_button.click()
                self.log_status("Closed a pop-up ('Remind me later').")
                time.sleep(1)
            except Exception as e:
                self.log_status(f"No pop-up found or could not close it (this is often OK).")

            if do_just_login and not do_returns_dashboard and not do_credit_ledger and not do_cash_ledger: 
                self.log_status("Action: Just Login selected. Automation will stop here.")
            
            if do_returns_dashboard: 
                self.log_status("Navigating to Returns Dashboard...")
                returns_dashboard_button_locator_preferred = (By.CSS_SELECTOR, "button[onclick*='return.gst.gov.in/returns/auth/dashboard']")
                returns_dashboard_button_locator_alternative_xpath = (By.XPATH, "//button[.//span[normalize-space()='Return Dashboard']]")
                returns_dashboard_button_locator_original_vba_xpath = (By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/button/span")
                
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
                time.sleep(3) 

                year_select_name = "fin" 
                quarter_select_name = "quarter" 
                month_select_name = "mon"       
                search_button_locator_preferred = (By.CSS_SELECTOR, "button.srchbtn[type='submit']") 
                search_button_locator_alternative_xpath = (By.XPATH, "//button[contains(@class, 'srchbtn') and normalize-space()='Search']")

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
