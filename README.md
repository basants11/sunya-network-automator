# SUNYA NETWORKING

## Professional Network Automation & Diagnostics Suite

Sunya Networking is a premium, enterprise-grade network diagnostics platform designed for ISPs, NOC teams, network engineers, and field technicians. It provides automatic, silent, and forensic-grade network diagnostics on both PC (Windows/Linux) and Android platforms.

## Features

### 🚀 Automatic Diagnostics
- **Auto-run on network changes**: Wi-Fi SSID changes, Ethernet cable plug/unplug, IP/dns/gateway changes, mobile data switches
- **Background operation**: Runs silently without user intervention
- **Boot startup**: Starts automatically when device boots up
- **Prevent duplicates**: Uses network fingerprinting to avoid duplicate runs

### 🧪 Diagnostic Modules

#### 1️⃣ Advanced Ping Engine
- ICMP echo with 1400-byte payload
- Targets: Gateway, DNS servers, regional endpoints
- Metrics: Packet loss, latency, jitter
- Outputs: Raw text, JSON, PNG graphs

#### 2️⃣ Route & Path Analysis
- Traceroute (ICMP + UDP)
- MTR (My TraceRoute) for comprehensive path analysis
- Detect first loss hop, latency spikes, route instability
- Hop-by-hop visualizations

#### 3️⃣ Speed & Quality Tests
- Multi-server speed tests
- Measures download, upload, latency, consistency
- Average results with throughput graphs

#### 4️⃣ Intelligent Analysis Engine
- Automatically identifies:
  - Congestion
  - Packet loss zones
  - MTU issues
  - Poor routing
  - DNS delays
  - Wi-Fi vs LAN degradation
- Generates engineer-style diagnosis and recommendations

### 📊 Reports & Documentation

#### Standard Report Structure
```
SUNYA_Networking/
├── Auto_Report_2026-03-02_23-10-40/
│   ├── network_info.txt
│   ├── ping/
│   ├── traceroute/
│   ├── mtr/
│   ├── speedtest/
│   ├── analysis/
│   │   └── diagnosis.txt
│   └── SUNYA_Network_Report.pdf
```

#### Professional PDF Report
- Network fingerprint
- Test tables and graphs
- Findings and root-cause hints
- Recommendations
- Engineer conclusion
- SUNYA NETWORKING brand watermark
- NOC/SLA dispute ready

## Platform Support

### 🖥️ PC Application (Windows/Linux)
- Runs as background service
- Auto-start on boot
- Python core engine
- Uses native OS tools
- Parallel execution for efficiency
- Clean log management

### 📱 Android APK
- Written in Kotlin
- Android network callbacks for real-time detection
- Background services for continuous monitoring
- Auto-runs on Wi-Fi or mobile data changes
- Local report storage
- Optional PDF export/sharing

## Installation

### PC Setup (Windows/Linux)

#### Prerequisites
- Python 3.8 or higher
- pip package manager
- OS-specific dependencies

#### Installation Steps
1. Clone the repository
2. Navigate to the `sunya-pc` directory
3. Run the setup script:
   ```bash
   python setup.py
   ```
4. Install as a system service:
   - **Windows**:
     ```bash
     python sunya-service.py --install
     ```
   - **Linux**:
     ```bash
     sudo python sunya-service.py --install
     ```
5. Start the service:
   ```bash
   python sunya-service.py --run
   ```

### Android Setup

#### Prerequisites
- Android Studio
- Android device/emulator with API level 26 or higher

#### Installation Steps
1. Open the project in Android Studio
2. Sync Gradle files
3. Build and run on your device
4. Grant required permissions
5. The app will automatically start on boot and run in the background

## Configuration

### PC Configuration
Configuration file is located at `~/.sunya-networking/config/config.json`

Key settings:
```json
{
  "general": {
    "log_level": "INFO",
    "report_location": "reports",
    "max_reports": 50,
    "auto_cleanup": true
  },
  "diagnostics": {
    "ping": {
      "count": 20,
      "payload_size": 1400,
      "timeout": 2
    },
    "traceroute": {
      "max_hops": 30,
      "timeout": 2
    },
    "speedtest": {
      "server_count": 5,
      "max_time": 300
    },
    "mtr": {
      "count": 5,
      "interval": 1
    }
  },
  "monitoring": {
    "check_interval": 30,
    "skip_duplicate": true,
    "network_change_threshold": 30
  }
}
```

### Android Configuration
Settings are accessible through the app's settings menu.

## Usage

### PC Service Commands

```bash
# Install service
python sunya-service.py --install

# Uninstall service
python sunya-service.py --uninstall

# Run directly without service
python sunya-service.py --run
```

### Android App
1. Open the Sunya Networking app
2. View current network information on the main screen
3. Start manual diagnostics if needed
4. View historical reports
5. Configure settings and preferences

## Architecture

### Core Components
- **Core Engine**: Shared diagnostic logic
- **Network Monitor**: Detects network changes
- **Diagnostic Modules**: Ping, traceroute, MTR, speedtest
- **Parallel Execution Engine**: Runs tests in parallel
- **Analysis Engine**: Intelligent diagnostics
- **Report Generator**: PDF and visualization generation
- **Service Manager**: Background operation and startup

### Technology Stack
- **PC**: Python, psutil, speedtest-cli, ping3, matplotlib, fpdf
- **Android**: Kotlin, Android Jetpack, Room, WorkManager, Coroutines
- **Common**: JSON, PDF, PNG, SQLite

## Safety & Ethics

### Authorized Networks Only
- The tool operates only on authorized networks
- No hidden behavior or telemetry
- Full transparency in operations

### Rate Limiting
- Probes are rate-limited to prevent network flooding
- Diagnostics complete within 3-7 minutes
- Tests are optimized for minimal network impact

## Development

### Project Structure
```
networking automation/
├── sunya-core/              # Shared core engine
│   ├── core.py              # Main diagnostic engine
│   ├── requirements.txt     # Python dependencies
│   └── tests/               # Test suite
├── sunya-pc/                # PC application
│   ├── sunya-service.py     # Background service
│   ├── setup.py             # Installation script
│   └── service.sh           # Service management
└── sunya-android/           # Android application
    ├── app/
    │   ├── src/main/
    │   │   ├── java/com/sunya/networking/
    │   │   └── res/
    │   ├── build.gradle.kts
    │   └── proguard-rules.pro
    └── build.gradle.kts
```

### Building from Source

#### PC Version
```bash
cd sunya-pc
pip install -r ../sunya-core/requirements.txt
python setup.py
python sunya-service.py --run
```

#### Android Version
```bash
cd sunya-android
./gradlew assembleDebug
```

## License

Sunya Networking is proprietary software designed for professional use.

## Support

For enterprise support and licensing inquiries, please contact [support@sunya-networking.com](mailto:support@sunya-networking.com).

## Changelog

### v1.0.0 (2026-03-01)
- Initial release
- PC and Android platforms
- Full diagnostic cycle
- Automatic network detection
- PDF report generation
- Background service operation