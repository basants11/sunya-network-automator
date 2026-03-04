# SUNYA NET - High-Performance Network Diagnostic System

**Version:** 3.0.0 Ultra  
**Last Updated:** 2026-03-04  
**Author:** SUNYA Networking

---

## 🚀 Overview

SUNYA NET is a high-performance, low-latency, fully automated network diagnostic and monitoring system designed for real-time network analysis with minimal resource overhead.

### Key Features

- ✅ **Real-time monitoring** with 1-2 second dashboard updates
- ✅ **Parallel execution** using 8-10 threads for network tests
- ✅ **WebSocket streaming** for live dashboard updates
- ✅ **Background PDF generation** without blocking monitoring
- ✅ **Auto-cleanup** of stale processes
- ✅ **Adaptive monitoring intervals** based on network stability
- ✅ **CPU/RAM throttling** when system load exceeds 70%
- ✅ **Memory-efficient** circular buffers for data storage
- ✅ **Instant alerts** for threshold breaches

---

## 📋 System Requirements

### Minimum Requirements
- **OS:** Windows 10/11, Linux, macOS
- **Python:** 3.7 or higher
- **RAM:** 512 MB
- **CPU:** Dual-core processor
- **Network:** Internet connection for external tests

### Recommended Requirements
- **RAM:** 2 GB
- **CPU:** Quad-core processor
- **Storage:** 100 MB free space for reports

---

## 🛠️ Installation

### Step 1: Install Python Dependencies

```bash
cd sunya-pc
pip install -r requirements-performance.txt
```

Or install individually:
```bash
pip install psutil websockets fpdf2 matplotlib speedtest-cli
```

### Step 2: Run the Monitor

**Windows:**
```bash
run-sunyanet.bat
```

**Linux/macOS:**
```bash
python3 sunyanet-high-performance.py
```

---

## 📊 Dashboard Access

1. Start the monitoring system
2. Open `dashboard.html` in your web browser
3. The dashboard will automatically connect via WebSocket (ws://localhost:8765)
4. View real-time metrics, charts, and alerts

### Dashboard Features
- **Live latency chart** with 60-second history
- **Packet loss visualization** with threshold indicators
- **Speed test results** (download/upload)
- **Active alerts panel** with color-coded severity
- **System resource monitoring** (CPU/Memory)
- **Route information** (hop count, worst latency)

---

## ⚙️ Configuration

### Alert Thresholds

Edit the `alert_thresholds` dictionary in the code:

```python
self.alert_thresholds = {
    'latency_critical': 200,    # ms
    'latency_warning': 100,     # ms
    'packet_loss_critical': 10, # %
    'packet_loss_warning': 5,   # %
    'speed_critical': 5,        # Mbps
    'speed_warning': 20         # Mbps
}
```

### Monitoring Intervals

- **Ping tests:** 1-2 seconds (adaptive)
- **Speed tests:** Every 30 seconds (lightweight), every 5 minutes (full)
- **Route traces:** Every 2 minutes
- **System metrics:** Every 2 seconds

---

## 🔄 Execution Flow

```
Start monitoring engine
    ↓
Initialize adapter info (cached)
    ↓
Launch WebSocket dashboard server
    ↓
Start multi-threaded ping/load/WinMTR
    ↓
Update charts & metrics every 1-2 seconds
    ↓
Trigger alerts & incident log instantly
    ↓
Background PDF/report generation at interval
    ↓
Automatic cleanup & process optimization
    ↓
End only on user stop command (Ctrl+C)
```

---

## 📁 Output Structure

```
Desktop/
└── SUNYA_Live_Monitoring/
    ├── Session_YYYY-MM-DD_HH-MM-SS/
    │   └── (session data)
    └── FinalReport/
        ├── report_YYYYMMDD_HHMMSS.pdf
        └── final_report.pdf
```

---

## 🔧 Performance Optimization

### Speed Optimizations
- **Multi-threaded execution:** 8-10 parallel ping threads
- **Async I/O:** Non-blocking network queries
- **Lightweight speed tests:** Small TCP downloads instead of full speedtest.net
- **Cached adapter info:** Refreshed only every 30 minutes
- **Memory-efficient queues:** Circular buffers with automatic size limiting
- **Reduced screenshot frequency:** Key events only

### Resource Management
- **CPU throttling:** Reduces activity when CPU > 70%
- **Memory throttling:** Reduces activity when RAM > 80%
- **Process cleanup:** Auto-kills stale Chrome/WinMTR processes
- **Garbage collection:** Periodic cleanup of unused objects

---

## 🚨 Alert System

### Alert Types
- **Critical (🔴):** Immediate attention required
  - Latency > 200ms
  - Packet loss > 10%
  - Download speed < 5 Mbps

- **Warning (🟡):** Attention recommended
  - Latency > 100ms
  - Packet loss > 5%
  - Download speed < 20 Mbps

- **Info (🔵):** Informational messages

---

## 🧪 Testing

### Test Targets
- 8.8.8.8 (Google DNS)
- 1.1.1.1 (Cloudflare DNS)
- 208.67.222.222 (OpenDNS)
- 9.9.9.9 (Quad9)
- facebook.com
- google.com
- cloudflare.com

### Test Types
1. **Ping Tests:** ICMP echo requests with 4 packets per target
2. **Speed Tests:** Lightweight TCP downloads + full speedtest.net
3. **Route Traces:** WinMTR with traceroute fallback
4. **System Monitoring:** CPU and memory usage

---

## 🐛 Troubleshooting

### Dashboard Not Connecting
1. Ensure the monitor is running
2. Check that port 8765 is not blocked by firewall
3. Try refreshing the browser page

### High CPU Usage
- The system automatically throttles when CPU > 70%
- Reduce `max_workers` in the code if needed
- Check for other resource-intensive applications

### No Speed Test Results
- Verify internet connection
- Check if speedtest-cli is installed: `pip install speedtest-cli`
- The system will fallback to lightweight tests if full tests fail

### PDF Generation Fails
- Ensure fpdf2 is installed: `pip install fpdf2`
- Check write permissions to Desktop/SUNYA_Live_Monitoring/

---

## 📈 Performance Metrics

### Typical Resource Usage
- **CPU:** 2-5% on modern processors
- **Memory:** 50-100 MB
- **Network:** ~100 KB/s (monitoring traffic only)
- **Disk:** Minimal (logs only, rotated automatically)

### Update Frequencies
- **Dashboard updates:** 1-2 seconds
- **Chart redraws:** Incremental (only new data points)
- **WebSocket broadcasts:** 2 per second (batched)
- **PDF generation:** Every 5 minutes (background thread)

---

## 🔒 Security Considerations

- WebSocket server only accepts local connections by default
- No sensitive data is transmitted over the network
- PDF reports are stored locally only
- Process cleanup prevents zombie processes

---

## 📚 API Reference

### WebSocket Protocol

**Connection:** `ws://localhost:8765`

**Message Format:**
```json
{
  "type": "metrics_batch",
  "data": [...],
  "timestamp": "2026-03-04T07:30:00"
}
```

**Metric Types:**
- `ping`: Latency, packet loss, jitter
- `speed`: Download/upload speeds
- `route`: Hop count, worst latency
- `system`: CPU, memory usage
- `alerts`: Active alerts array

---

## 🤝 Contributing

To contribute to SUNYA NET:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

Copyright (c) 2026 SUNYA Networking. All rights reserved.

---

## 📞 Support

For support and inquiries:
- **Email:** support@sunyanetworking.com
- **Documentation:** See README files in project directories
- **Issues:** Submit via project issue tracker

---

## 🎉 Version History

### v3.0.0 Ultra (Current)
- High-performance monitoring engine
- WebSocket real-time dashboard
- Background PDF generation
- Adaptive monitoring intervals
- CPU/RAM throttling
- Auto-cleanup processes

### v2.0.0 (Previous)
- Basic diagnostic capabilities
- Sequential test execution
- Static reporting

---

**SUNYA NET - Professional Network Automation & Diagnostics**

*Monitoring made simple, performance made powerful.*
