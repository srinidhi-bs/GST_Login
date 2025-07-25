# GST Portal Automation

A Python GUI application that automates interactions with the GST portal using Selenium WebDriver.

## Features

- **Client Management**: Load client credentials from Excel files
- **GST Portal Login**: Automated login with CAPTCHA handling
- **Returns Dashboard**: Navigate and interact with returns dashboard
- **GSTR-2B Download**: Automated download of GSTR-2B Excel files
- **Electronic Credit Ledger**: Access and view credit ledger with date filtering
- **Electronic Cash Ledger**: Access and view cash ledger details
- **Download Management**: Organized downloads in dedicated folder

## Prerequisites

- Python 3.7+
- Chrome browser
- Excel file with client data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/srinidhi-bs/GST_Login.git
cd GST_Login
```

2. Create and activate virtual environment:
```bash
python -m venv gst_env
# On Windows:
gst_env\Scripts\activate
# On Linux/Mac:
source gst_env/bin/activate
```

3. Install required packages:
```bash
pip install tkinter selenium pandas webdriver-manager
```

## Usage

### Excel File Format

Create an Excel file (`clients.xlsx`) with the following columns:
- **Client Name**: Name of the client
- **GST Username**: GST portal username
- **GST Password**: GST portal password

### Running the Application

1. **Using Python:**
```bash
python gst_automation_app.py
```

2. **Using Batch File (Windows):**
```bash
GST.bat
```

### Application Flow

1. **Load Clients**: Browse and select your Excel file with client data
2. **Select Client**: Choose a client from the dropdown
3. **Choose Actions**: Select what operations to perform:
   - Just Login
   - Returns Dashboard
   - Download GSTR-2B
   - Electronic Credit Ledger
   - Electronic Cash Ledger
4. **Configure Options**: Set financial year, quarter, month, or date ranges as needed
5. **Start Automation**: Click "Start Automation" and handle CAPTCHA when prompted

## Application Structure

```
GST_Login/
├── gst_automation_app.py    # Main application file
├── GST.bat                  # Windows batch file to run the app
├── clients.xlsx             # Client data (not tracked in git)
├── GST_Downloads/           # Download directory (created automatically)
└── README.md               # This file
```

## Features in Detail

### Automated Login
- Navigates to GST portal
- Fills username and password
- Waits for manual CAPTCHA entry
- Handles post-login popups

### Returns Dashboard
- Selects financial year, quarter, and month
- Performs search operations
- Handles GSTR-2B downloads

### Ledger Access
- Navigates through Services menu
- Accesses Credit and Cash ledgers
- Supports date range filtering

## Error Handling

- Multiple fallback locators for web elements
- Timeout handling with configurable wait times
- Screenshot capture on critical failures
- Comprehensive status logging

## Downloads

All downloads are saved to the `GST_Downloads` folder in the application directory.

## Security Notes

- Credentials are stored in Excel files (ensure file security)
- No credentials are stored in the application code
- Browser remains visible for transparency

## Troubleshooting

1. **Chrome Driver Issues**: The app uses WebDriver Manager to automatically download the correct ChromeDriver
2. **Element Not Found**: The app includes multiple fallback locators for robustness
3. **Timeout Errors**: Adjust wait times in the code if your internet connection is slow
4. **CAPTCHA**: Manual intervention required - enter CAPTCHA when prompted

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Author

**Srinidhi B S**
- GitHub: [@srinidhi-bs](https://github.com/srinidhi-bs)
- Email: mailsrinidhibs@gmail.com

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and automation purposes. Users are responsible for compliance with GST portal terms of service and applicable regulations.