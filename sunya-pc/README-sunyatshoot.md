# SunyatShoot - Automatic Network Diagnostic Tool

A standalone desktop tool that automatically starts network diagnostics when launched.

## Features

- **Automatic Startup**: Runs network diagnostics automatically when opened
- **Comprehensive Testing**: Performs multiple network tests including:
  - DNS resolution tests
  - Gateway connectivity check
  - Ping tests to multiple targets
  - Traceroute tests
  - Speed test
  - MTR (My TraceRoute) analysis
- **Smart Analysis**: Uses intelligent analysis to determine network quality and issues
- **Report Generation**: Generates diagnostic reports with evidence integrity verification
- **Easy to Use**: Simply double-click to run - no configuration needed
- **Cross-Platform**: Works on Windows, Linux, and macOS

## How to Run

### Windows

1. Double-click on `run-sunyatshoot.bat`
2. The tool will automatically start running
3. A command prompt window will show the progress
4. Reports will be saved to your desktop

### Linux/macOS

1. Make sure the script is executable:
   ```bash
   chmod +x run-sunyatshoot.sh
   ```
2. Double-click on `run-sunyatshoot.sh` or run from terminal:
   ```bash
   ./run-sunyatshoot.sh
   ```

### Direct Execution

You can also run the Python script directly:

```bash
python sunyatshoot.py
```

## Output

- **Diagnostic Reports**: Saved in `SUNYA_Networking/Auto_Report_YYYY-MM-DD_HH-MM-SS` folder
- **Log File**: `sunyatshoot.log` (logs all activity)
- **Desktop Report Folder**: Creates a timestamped folder on your desktop

## Requirements

- Python 3.x
- Required Python packages (automatically installed by setup.py):
  - requests
  - psutil
  - speedtest-cli
  - ping3
  - pandas
  - matplotlib
  - seaborn
  - fpdf
  - pytest
  - scipy
  - numpy
  - pyautogui
  - selenium
  - webdriver-manager
  - wmi (Windows only)

## First Time Setup

If you haven't run the setup script before, run:

```bash
python setup.py
```

## Note

- The tool may take a few minutes to complete all tests
- Do not close the command prompt window while the diagnostics are running
- If you encounter any issues, check the `sunyatshoot.log` file for details

## Troubleshooting

**PDF Generation Errors**: If you see encoding errors when generating PDF reports, this is an issue with the FPDF library's handling of UTF-8 characters. The tool will still save all diagnostic data without PDF reports.

**Permission Issues (Linux/macOS)**: Make sure the script has executable permissions:

```bash
chmod +x run-sunyatshoot.sh
```

**Python Not Found**: Ensure Python 3.x is installed and available in your system PATH.

## License

This tool is part of the Sunya Networking project.
