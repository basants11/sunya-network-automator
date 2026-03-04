# SUNYA Networking - Automated Diagnostic Tool

## Overview

The Automated Diagnostic Tool is a comprehensive solution that automatically runs a series of network diagnostic tests, captures screenshots, and compiles all results into a professional PDF report. It's designed to streamline network troubleshooting by providing a complete diagnostic report with just a single command.

## Features

### 🚀 Automatic Application Launch
- **Terminal/Command Prompt**: Opens system terminal for network diagnostics
- **Google Chrome**: Launches web browser for speed test visualization
- **NMTr/MTR**: Opens Network MTR tool for comprehensive route analysis
- **PowerShell**: Launches PowerShell for advanced network commands

### 🧪 Diagnostic Tests
1. **Advanced Ping Test**: 20 pings with 1400-byte payload to 8.8.8.8
2. **Traceroute Test**: Route analysis to 8.8.8.8 with detailed hop information
3. **Speed Test**: Measures download/upload speeds and latency using speedtest-cli
4. **Screenshot Capture**: Takes screenshots of each test for visual documentation

### 📊 Report Generation
- Creates a new report folder on the desktop
- Saves all test results in text files
- Captures and saves screenshots of each test
- Compiles all information into a professional PDF report
- PDF includes:
  - Test results with timestamps
  - Screenshot documentation
  - Network configuration details
  - Professional formatting with SUNYA branding

## Installation

### Prerequisites
- Python 3.6 or higher
- pip package manager
- System must have:
  - Terminal/Command Prompt
  - Google Chrome (or default browser)
  - PowerShell (Windows) or pwsh (Linux/macOS)
  - MTR (Linux/macOS) or NMTr (Windows)

### Installation Steps
1. Navigate to the `sunya-pc` directory:
   ```bash
   cd sunya-pc
   ```

2. Run the setup script:
   ```bash
   python setup.py
   ```

3. Verify all dependencies are installed:
   ```bash
   pip install -r ../sunya-core/requirements.txt
   ```

## Usage

### Quick Start
Run the automated diagnostic tool directly:

```bash
python automated-diagnostic-tool.py
```

### Demo Mode
For a guided demo with user prompts:

```bash
python demo-automated-diagnostic.py
```

### Test Mode
Test specific functionality:

```bash
python test-pdf.py    # Test PDF generation
```

## Report Location

Reports are automatically saved in a new folder on your desktop with the format:
`Network_Diagnostic_Report_YYYY-MM-DD_HH-MM-SS`

Each report folder contains:
- `ping_results_*.txt`: Detailed ping test output
- `traceroute_results_*.txt`: Traceroute test output
- `speedtest_results_*.txt`: Speed test results
- `*.png`: Screenshots of each test
- `Network_Diagnostic_Report_*.pdf`: Complete PDF report

## Configuration

### Custom Targets
To modify the test targets, edit the `run_ping_test()` and `run_traceroute_test()` methods in `automated-diagnostic-tool.py`.

### Test Parameters
- Ping count: Default 20, can be modified in `run_ping_test()`
- Packet size: Default 1400 bytes, configured in `run_ping_test()`
- Target address: Default 8.8.8.8 (Google DNS)

### Application Paths
If applications are installed in non-standard locations, update the paths in the `open_applications()` method.

## Troubleshooting

### Common Issues

1. **Applications not found**: Ensure Chrome and PowerShell/MTR are properly installed
2. **Screenshot capture fails**: Make sure the application windows are visible on screen
3. **PDF generation errors**: Check that all required dependencies are installed
4. **Permission issues**: Run as administrator if encountering network access problems

### Error Logs
Detailed logs are recorded in `automated-diagnostic-tool.log` for troubleshooting.

## System Requirements

### Windows
- Windows 10 or higher
- Python 3.6+
- Chrome browser
- PowerShell
- NMTr (Network MTR tool)

### Linux
- Ubuntu 18.04 or equivalent
- Python 3.6+
- Chrome browser
- PowerShell Core (pwsh)
- mtr package

### macOS
- macOS 10.15 or higher
- Python 3.6+
- Chrome browser
- PowerShell Core (pwsh)
- mtr package

## Performance

### Test Duration
- **Ping test**: ~10 seconds
- **Traceroute test**: ~15 seconds
- **Speed test**: ~30 seconds
- **Total time**: ~60-90 seconds depending on internet connection

### Resource Usage
- CPU: Light to moderate
- Memory: < 100MB
- Network: Depends on speed test results

## Integration

The tool can be integrated with:
- Task schedulers for automatic testing
- Network monitoring systems
- IT support workflows
- CI/CD pipelines

## Contributing

If you'd like to contribute to the development of this tool, please refer to the main SUNYA Networking project guidelines.

## License

This tool is part of the SUNYA Networking suite and follows the same license terms.

## Support

For enterprise support and customization options, please contact [support@sunya-networking.com](mailto:support@sunya-networking.com).

---
*Last updated: March 2026*
