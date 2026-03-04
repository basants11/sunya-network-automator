# SUNYA Master Diagnostic Tool v5.0.0

## 🎯 The One Tool To Rule Them All

**SUNYA Master** is a unified, powerful network diagnostic and automation platform that combines all previous SUNYA diagnostic tools into a single, comprehensive solution.

## ✨ Features

### 🔬 Diagnostic Capabilities
- **Multi-threaded Ping Tests** - Parallel execution to multiple targets
- **Speed Tests** - Using speedtest-cli with fallback options
- **Traceroute Analysis** - Route tracking with bottleneck detection
- **Load/Stress Testing** - Network stability under load
- **Health Scoring** - Intelligent A-F grading system

### ⚡ Performance
- **Parallel Execution** - Configurable thread pool for maximum speed
- **Multiple Test Modes** - Quick (30s), Standard (2min), Full (5min)
- **Efficient Resource Usage** - Minimal CPU/memory footprint

### 📊 Reporting
- **Comprehensive Text Reports** - Detailed analysis in .txt format
- **Organized Output** - Separate folders for reports, screenshots, and raw data
- **Health Score Summary** - Overall network health at a glance

## 📦 What's Included

This unified tool replaces and combines:
- ✅ `sunya-complete-diagnostic.py` - Deep hardware inspection
- ✅ `sunya-ultra.py` - Ultra-fast async operations
- ✅ `sunyanet-high-performance.py` - Multi-threaded execution
- ✅ `one-click-automation.py` - Browser automation
- ✅ `sunyatshoot.py` - Quick diagnostics
- ✅ `comprehensive-network-diagnostic.py` - Comprehensive testing
- ✅ All individual batch files

## 🚀 Quick Start

### Option 1: Double-Click (Easiest)
1. Double-click `run-sunya-master.bat`
2. Select your test mode from the menu
3. View results on your Desktop

### Option 2: Command Line
```bash
# Quick 30-second test
python sunya-master.py --quick

# Standard 2-minute diagnostic (default)
python sunya-master.py

# Full 5-minute deep analysis
python sunya-master.py --full

# Custom output directory
python sunya-master.py --output "C:\Reports"
```

## 📋 Requirements

### Required
- Python 3.8 or higher
- `psutil` package

### Optional (Enhanced Features)
```bash
# For speed tests
pip install speedtest-cli

# For browser automation
pip install selenium webdriver-manager

# For screenshots
pip install pyautogui pillow

# For Windows hardware info
pip install WMI

# For PDF reports
pip install fpdf2
```

## 🎮 Test Modes

| Mode | Duration | Description | Use Case |
|------|----------|-------------|----------|
| **QUICK** | ~30 sec | Basic connectivity check | Quick health check |
| **STANDARD** | ~2 min | Comprehensive diagnostic | Regular maintenance |
| **FULL** | ~5 min | Deep analysis | Troubleshooting |

## 📁 Output Structure

```
Desktop/
└── SUNYA_Master_2026-03-04_12-30-00/
    ├── reports/
    │   └── SUNYA_Master_Report_2026-03-04_12-30-00.txt
    ├── screenshots/
    ├── raw_data/
    ├── ping_tests/
    ├── speed_tests/
    ├── traceroute/
    └── load_tests/
```

## 📊 Report Contents

Each report includes:
- **Overall Health Score** (0-100) with Grade (A-F)
- **Speed Analysis** - Download/Upload speeds
- **Latency Metrics** - Average, min, max, jitter
- **Packet Loss** - Percentage by target
- **Route Analysis** - Hop-by-hop traceroute
- **Stability Score** - Under load conditions
- **Issues & Recommendations** - Actionable insights

## 🔧 Troubleshooting

### "Python not found"
- Install Python 3.8+ from python.org
- Check "Add Python to PATH" during installation

### "speedtest-cli not available"
- Install: `pip install speedtest-cli`
- Tool will work without it (skips speed tests)

### Permission Denied
- Run as Administrator for full hardware info
- Right-click → "Run as administrator"

## 🏆 Health Score Guide

| Grade | Score | Status | Action |
|-------|-------|--------|--------|
| A | 90-100 | Excellent | No action needed |
| B | 75-89 | Good | Monitor periodically |
| C | 60-74 | Fair | Consider optimization |
| D | 40-59 | Poor | Investigate issues |
| F | 0-39 | Critical | Immediate attention |

## 🔄 Migration from Old Tools

If you were using individual tools:

| Old Tool | New Command | Notes |
|----------|-------------|-------|
| `sunyatshoot.py` | `python sunya-master.py --quick` | Same functionality |
| `comprehensive-network-diagnostic.py` | `python sunya-master.py` | Enhanced version |
| `sunya-complete-diagnostic.py` | `python sunya-master.py --full` | Full deep analysis |
| `sunya-ultra.py` | `python sunya-master.py --quick` | Optimized execution |

## 📝 Changelog

### v5.0.0 (2026-03-04)
- 🎉 Initial unified release
- 🔧 Combined all diagnostic tools
- ⚡ Multi-threaded execution
- 📊 Improved health scoring
- 🎯 Three test modes
- 📁 Organized output structure

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review generated logs in the output folder
3. Run dependency check: `run-sunya-master.bat` → Option 5

## 📄 License

Proprietary - SUNYA Networking

---

**SUNYA Master** - One tool to diagnose them all! 🚀
