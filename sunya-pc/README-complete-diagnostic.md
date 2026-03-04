# SUNYA Complete Network Diagnostic System

A fully automated professional Windows diagnostic system that performs deep hardware inspection, internet testing, route tracing, stress testing, intelligent scoring, and generates a detailed PDF report.

## Features

### ✅ Step 1 – Desktop Report Folder Structure
- Automatically detects Windows username
- Creates timestamped folder on Desktop: `SUNYA_Network_Report_YYYY-MM-DD_HH-MM-SS/`
- Organized subfolders:
  - `/AdapterInfo` - Network adapter details
  - `/SpeedTests` - Speed test results and screenshots
  - `/PingTests` - Ping test results
  - `/LoadTests` - Load/stress test results
  - `/WinMTR` - Route trace reports
  - `/Screenshots` - All captured screenshots
  - `/RawLogs` - Raw output logs
  - `/Charts` - Generated visual charts
  - `/FinalReport` - PDF report

### ✅ Step 2 – Network Adapter + Driver Analysis
- Detects active physical network adapter (ignores VPN & virtual adapters)
- Collects:
  - Adapter Name, Manufacturer, Description
  - MAC Address
  - Driver Version, Driver Date, Driver Provider
  - Link Speed, Supported Speeds, Duplex Mode
  - Interface Type (Ethernet/WiFi)
  - Default Gateway, DNS Servers
- Smart analysis:
  - Gigabit capability detection
  - Cable/router limitation flags
  - Outdated driver warnings (2+ years)
- Saves results to JSON
- Captures Device Manager screenshots

### ✅ Step 3 – Automated Speed Tests
- Launches Chrome (maximized) via Selenium
- Tests on:
  - fast.com
  - speedtest.net
- Auto-extracts:
  - Download speed
  - Upload speed
  - Latency/Ping
- High-resolution screenshots
- JSON data export
- Automatic retry on failure
- CLI fallback using speedtest-cli

### ✅ Step 4 – Multi-Target Ping Tests
- Targets tested (60 seconds each):
  - 8.8.8.8 (Google DNS)
  - facebook.com
  - x.com
  - instagram.com
  - google.com
  - bbc.com
  - cloudflare.com
  - opendns.com
  - Default Gateway
  - Connected DNS
- Parallel execution using threading
- Calculates:
  - Min/Max/Average latency
  - Packet loss percentage
- Individual log files per target
- Screenshot capture

### ✅ Step 5 – Load/Stress Testing
- Sends 1000 packets per target
- Targets: 8.8.8.8, google.com, cloudflare.com
- Measures:
  - Jitter (latency variation)
  - Packet loss under load
  - Stability score (0-100)
- Results saved to JSON

### ✅ Step 6 – WinMTR Route Trace
- Runs 100 cycle route traces
- Detects:
  - Total hops
  - Worst latency hop
  - Packet loss by hop
  - Bottleneck locations
- Falls back to Windows tracert if WinMTR not available
- Saves .txt reports

### ✅ Step 7 – Intelligent Network Health Score (0-100)
Score breakdown:
- Speed Quality: 0-25 points
- Packet Loss: 0-25 points
- Latency: 0-20 points
- Stability: 0-15 points
- Hardware: 0-15 points

Grade scale:
- 90-100: Excellent
- 75-89: Good
- 60-74: Fair
- Below 60: Poor

Automatic recommendations for:
- Driver updates
- Cable replacement
- Router upgrade
- ISP contact
- Internal wiring check

### ✅ Step 8 – Visual Charts (matplotlib)
Generated charts:
- Speed comparison bar chart
- Ping latency comparison chart
- Packet loss chart
- Load test stability chart
- Network health score gauge

### ✅ Step 9 – Professional PDF Report
Using ReportLab Platypus:

**Cover Page:**
- Tool Name
- Date & Time
- System Name
- ISP Name/Public IP
- Network Health Score
- Final Status

**Sections:**
1. Adapter Analysis - Full hardware + driver report
2. Speed Tests - Comparison with charts
3. Ping Results - Detailed table per target
4. Load Test - Stability analysis
5. WinMTR Route Analysis - Hop details
6. ISP Complaint Ready Summary - Professional paragraph

All screenshots and charts embedded with professional formatting.

### ✅ Step 10 – Final Cleanup
- Closes Chrome
- Closes all terminals
- Kills background processes
- Removes temp files
- Opens Desktop folder automatically
- Opens generated PDF automatically
- Displays completion message

## Installation

### Method 1: Using Batch File (Recommended)
1. Double-click `run-complete-diagnostic.bat`
2. The batch file will automatically install dependencies
3. Wait for the diagnostic to complete

### Method 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements-complete.txt

# Run the diagnostic
python sunya-complete-diagnostic.py
```

### Dependencies
- Python 3.7+
- Windows 10/11
- Chrome browser
- WMI, psutil, matplotlib, reportlab, selenium, speedtest-cli, ping3, pyautogui

## Usage

### Quick Start
Simply double-click `run-complete-diagnostic.bat`

### Command Line
```bash
cd sunya-pc
python sunya-complete-diagnostic.py
```

### Options
The tool runs fully automated with no manual interaction required.

## Output

All results are saved to:
```
Desktop/SUNYA_Network_Report_YYYY-MM-DD_HH-MM-SS/
├── AdapterInfo/
│   └── adapter_details.json
├── SpeedTests/
│   ├── speedtest_results.json
│   ├── fast_com_*.png
│   └── speedtest_net_*.png
├── PingTests/
│   ├── ping_results.json
│   └── ping_*.txt
├── LoadTests/
│   └── load_test_results.json
├── WinMTR/
│   ├── winmtr_results.json
│   └── tracert_*.txt
├── Screenshots/
│   └── device_manager_network.png
├── RawLogs/
│   └── [copied log files]
├── Charts/
│   ├── speed_comparison.png
│   ├── latency_comparison.png
│   ├── packet_loss.png
│   ├── stability_scores.png
│   └── health_score_gauge.png
└── FinalReport/
    └── SUNYA_Network_Diagnostic_Report.pdf
```

## Health Score Interpretation

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | Excellent | Network performing optimally |
| 75-89 | Good | Minor issues, acceptable performance |
| 60-74 | Fair | Noticeable issues, may need attention |
| < 60 | Poor | Significant problems, action required |

## Troubleshooting

### Chrome Driver Issues
The tool uses webdriver-manager to automatically download the correct ChromeDriver version.

### WMI Not Available
If WMI is not available, the tool will fallback to psutil for basic adapter information.

### WinMTR Not Found
If WinMTR is not installed, the tool will use Windows built-in tracert command.

### Permission Issues
Run as Administrator for complete adapter information.

## License

This tool is part of the SUNYA Networking project.

## Support

For issues or questions, please refer to the project documentation.
