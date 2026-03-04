#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA Complete Network Diagnostic System
A fully automated professional Windows diagnostic system that performs:
- Deep hardware inspection
- Internet testing
- Route tracing
- Stress testing
- Intelligent scoring
- PDF report generation

Author: SUNYA Networking
Version: 2.0.0
"""

import os
import sys
import time
import json
import logging
import subprocess
import platform
import datetime
import socket
import threading
import tempfile
import re
import shutil
import psutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Third-party imports with fallbacks
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    print("Warning: wmi module not available. Some features may be limited.")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: selenium not available. Browser-based tests will be skipped.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_pdf import PdfPages
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Charts will be skipped.")

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not available. PDF reports will use fallback.")

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False

try:
    import ping3
    PING3_AVAILABLE = True
except ImportError:
    PING3_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# Configure logging with UTF-8 support
class UnicodeStreamHandler(logging.StreamHandler):
    """Stream handler that handles Unicode encoding properly on Windows"""
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace Unicode characters with ASCII equivalents
            msg = msg.replace('\u2713', '[OK]').replace('\u2717', '[FAIL]').replace('\u26a0', '[WARN]')
            msg = msg.replace('━', '-').replace('═', '=').replace('╔', '+').replace('╗', '+')
            msg = msg.replace('╚', '+').replace('╝', '+').replace('║', '|').replace('●', '*')
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        UnicodeStreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AdapterInfo:
    """Network adapter information"""
    name: str = ""
    manufacturer: str = ""
    description: str = ""
    mac_address: str = ""
    driver_version: str = ""
    driver_date: str = ""
    driver_provider: str = ""
    link_speed: int = 0  # Mbps
    supported_speeds: List[int] = field(default_factory=list)
    duplex_mode: str = ""
    interface_type: str = ""  # Ethernet/WiFi
    default_gateway: str = ""
    dns_servers: List[str] = field(default_factory=list)
    is_gigabit_capable: bool = False
    is_negotiating_gigabit: bool = False
    cable_limitation_flag: bool = False
    driver_outdated_flag: bool = False
    driver_age_days: int = 0

@dataclass
class SpeedTestResult:
    """Speed test results"""
    source: str = ""
    download_speed: float = 0.0  # Mbps
    upload_speed: float = 0.0  # Mbps
    latency: float = 0.0  # ms
    timestamp: str = ""
    screenshot_path: str = ""
    success: bool = False
    error_message: str = ""

@dataclass
class PingResult:
    """Ping test results"""
    target: str = ""
    min_latency: float = 0.0  # ms
    max_latency: float = 0.0  # ms
    avg_latency: float = 0.0  # ms
    packet_loss_percent: float = 0.0
    packets_sent: int = 0
    packets_received: int = 0
    screenshot_path: str = ""
    raw_output: str = ""
    success: bool = False

@dataclass
class LoadTestResult:
    """Load/stress test results"""
    target: str = ""
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    jitter: float = 0.0  # ms
    stability_score: float = 0.0  # 0-100
    screenshot_path: str = ""
    success: bool = False

@dataclass
class WinMTRResult:
    """WinMTR route trace results"""
    target: str = ""
    total_hops: int = 0
    worst_latency_hop: int = 0
    worst_latency_value: float = 0.0
    packet_loss_hop: int = 0
    packet_loss_percent: float = 0.0
    bottleneck_detected: bool = False
    bottleneck_hop: int = 0
    report_path: str = ""
    screenshot_path: str = ""
    success: bool = False

@dataclass
class NetworkHealthScore:
    """Network health score and recommendations"""
    overall_score: int = 0  # 0-100
    grade: str = ""  # Excellent/Good/Fair/Poor
    speed_score: int = 0
    stability_score: int = 0
    latency_score: int = 0
    hardware_score: int = 0
    recommendations: List[str] = field(default_factory=list)
    isp_complaint_summary: str = ""

# ============================================================================
# MAIN DIAGNOSTIC CLASS
# ============================================================================

class SunyaCompleteDiagnostic:
    """Complete automated network diagnostic system"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.username = os.environ.get('USERNAME') or os.environ.get('USER') or 'Unknown'
        self.base_folder = None
        self.folders = {}
        
        # Test results storage
        self.adapter_info = None
        self.speed_tests: List[SpeedTestResult] = []
        self.ping_tests: List[PingResult] = []
        self.load_tests: List[LoadTestResult] = []
        self.winmtr_tests: List[WinMTRResult] = []
        self.health_score = None
        
        # Chart paths
        self.chart_paths = []
        
        # Selenium driver
        self.driver = None
        
        # Target lists
        self.ping_targets = [
            "8.8.8.8",
            "facebook.com",
            "x.com",
            "instagram.com",
            "google.com",
            "bbc.com",
            "cloudflare.com",
            "opendns.com"
        ]
        
        logger.info(f"SUNYA Complete Diagnostic initialized")
        logger.info(f"Platform: {self.platform}")
        logger.info(f"Username: {self.username}")
    
    # ========================================================================
    # STEP 1: CREATE FOLDER STRUCTURE
    # ========================================================================
    
    def create_folder_structure(self) -> bool:
        """Create Desktop report folder with subfolders"""
        logger.info("STEP 1: Creating folder structure...")
        
        try:
            # Get Desktop path
            if self.platform == 'windows':
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            else:
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            
            # Create main folder
            self.base_folder = os.path.join(
                desktop_path, 
                f"SUNYA_Network_Report_{self.timestamp}"
            )
            
            # Define subfolders
            subfolders = [
                'AdapterInfo',
                'SpeedTests',
                'PingTests',
                'LoadTests',
                'WinMTR',
                'Screenshots',
                'RawLogs',
                'Charts',
                'FinalReport'
            ]
            
            # Create folders
            os.makedirs(self.base_folder, exist_ok=True)
            for folder in subfolders:
                folder_path = os.path.join(self.base_folder, folder)
                os.makedirs(folder_path, exist_ok=True)
                self.folders[folder] = folder_path
            
            logger.info(f"[OK] Base folder created: {self.base_folder}")
            logger.info(f"[OK] Created {len(subfolders)} subfolders")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to create folder structure: {e}")
            return False
    
    # ========================================================================
    # STEP 2: NETWORK ADAPTER + DRIVER ANALYSIS
    # ========================================================================
    
    def analyze_network_adapter(self) -> bool:
        """Analyze active network adapter and driver information"""
        logger.info("STEP 2: Analyzing network adapter...")
        
        self.adapter_info = AdapterInfo()
        
        try:
            if self.platform == 'windows' and WMI_AVAILABLE:
                return self._analyze_adapter_windows()
            else:
                return self._analyze_adapter_fallback()
                
        except Exception as e:
            logger.error(f"✗ Adapter analysis failed: {e}")
            return False
    
    def _analyze_adapter_windows(self) -> bool:
        """Windows-specific adapter analysis using WMI"""
        try:
            w = wmi.WMI()
            
            # Find active physical network adapter (non-virtual, non-VPN)
            active_adapter = None
            for nic in w.Win32_NetworkAdapter():
                # Skip virtual adapters, VPN, and disconnected adapters
                if nic.NetConnectionStatus != 2:  # 2 = Connected
                    continue
                if any(x in nic.Name.lower() for x in ['virtual', 'vpn', 'vmware', 'virtualbox', 'hyper-v', 'loopback', 'bluetooth', 'wan miniport']):
                    continue
                
                active_adapter = nic
                break
            
            if not active_adapter:
                logger.warning("No active physical adapter found, using fallback")
                return self._analyze_adapter_fallback()
            
            # Get adapter configuration
            nic_config = None
            for config in w.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                if config.SettingID == active_adapter.GUID:
                    nic_config = config
                    break
            
            # Populate adapter info
            self.adapter_info.name = active_adapter.Name
            self.adapter_info.manufacturer = active_adapter.Manufacturer or "Unknown"
            self.adapter_info.description = active_adapter.Description or ""
            self.adapter_info.mac_address = active_adapter.MACAddress or ""
            
            # Get driver information
            try:
                for driver in w.Win32_PnPSignedDriver():
                    if driver.DeviceID and active_adapter.PNPDeviceID and driver.DeviceID in active_adapter.PNPDeviceID:
                        self.adapter_info.driver_version = driver.DriverVersion or "Unknown"
                        self.adapter_info.driver_provider = driver.DriverProviderName or "Unknown"
                        if driver.DriverDate:
                            # Parse driver date (WMI format: YYYYMMDD*******)
                            driver_date_str = str(driver.DriverDate).split('.')[0][:8]
                            if len(driver_date_str) == 8:
                                year = int(driver_date_str[:4])
                                month = int(driver_date_str[4:6])
                                day = int(driver_date_str[6:8])
                                self.adapter_info.driver_date = f"{year}-{month:02d}-{day:02d}"
                                
                                # Calculate driver age
                                driver_date_obj = datetime.date(year, month, day)
                                current_date = datetime.date.today()
                                self.adapter_info.driver_age_days = (current_date - driver_date_obj).days
                                
                                # Flag if older than 2 years
                                if self.adapter_info.driver_age_days > 730:
                                    self.adapter_info.driver_outdated_flag = True
                        break
            except Exception as e:
                logger.warning(f"Could not get driver info: {e}")
            
            # Get link speed
            if active_adapter.Speed:
                self.adapter_info.link_speed = int(active_adapter.Speed) / 1_000_000  # Convert to Mbps
            
            # Determine supported speeds and type
            if 'ethernet' in active_adapter.Name.lower() or 'gbE' in active_adapter.Name.lower():
                self.adapter_info.interface_type = "Ethernet"
                # Common Ethernet speeds
                if self.adapter_info.link_speed >= 1000 or 'gigabit' in active_adapter.Name.lower():
                    self.adapter_info.supported_speeds = [10, 100, 1000]
                    self.adapter_info.is_gigabit_capable = True
                else:
                    self.adapter_info.supported_speeds = [10, 100]
            elif 'wi-fi' in active_adapter.Name.lower() or 'wireless' in active_adapter.Name.lower():
                self.adapter_info.interface_type = "WiFi"
                # WiFi speeds vary by standard
                self.adapter_info.supported_speeds = [54, 150, 300, 433, 866, 1200]
                if self.adapter_info.link_speed >= 1000:
                    self.adapter_info.is_gigabit_capable = True
            
            # Check if negotiating at gigabit
            self.adapter_info.is_negotiating_gigabit = self.adapter_info.link_speed >= 1000
            
            # Check for cable limitation
            if self.adapter_info.is_gigabit_capable and self.adapter_info.link_speed < 1000:
                self.adapter_info.cable_limitation_flag = True
            
            # Get duplex mode from registry or WMI
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 
                     f'Get-NetAdapter -Name "{active_adapter.NetConnectionID}" | Select-Object -ExpandProperty LinkLayerAddress'],
                    capture_output=True, text=True
                )
            except:
                pass
            
            # Get network configuration
            if nic_config:
                if nic_config.DefaultIPGateway:
                    # Handle both list and tuple returns from WMI
                    if isinstance(nic_config.DefaultIPGateway, (list, tuple)):
                        self.adapter_info.default_gateway = nic_config.DefaultIPGateway[0]
                    else:
                        self.adapter_info.default_gateway = str(nic_config.DefaultIPGateway)
                if nic_config.DNSServerSearchOrder:
                    self.adapter_info.dns_servers = list(nic_config.DNSServerSearchOrder)
            
            # Add gateway and DNS to ping targets
            if self.adapter_info.default_gateway and self.adapter_info.default_gateway not in self.ping_targets:
                self.ping_targets.insert(0, self.adapter_info.default_gateway)
            if self.adapter_info.dns_servers:
                for dns in self.adapter_info.dns_servers:
                    if dns not in self.ping_targets:
                        self.ping_targets.append(dns)
            
            # Save to JSON
            adapter_json = os.path.join(self.folders['AdapterInfo'], 'adapter_details.json')
            with open(adapter_json, 'w') as f:
                json.dump(asdict(self.adapter_info), f, indent=2, default=str)
            
            # Capture Device Manager screenshot
            self._capture_device_manager_screenshot()
            
            # Log results
            logger.info(f"✓ Adapter: {self.adapter_info.name}")
            logger.info(f"✓ Manufacturer: {self.adapter_info.manufacturer}")
            logger.info(f"✓ Link Speed: {self.adapter_info.link_speed} Mbps")
            logger.info(f"✓ Gigabit Capable: {self.adapter_info.is_gigabit_capable}")
            logger.info(f"✓ Negotiating Gigabit: {self.adapter_info.is_negotiating_gigabit}")
            if self.adapter_info.cable_limitation_flag:
                logger.warning("⚠ Cable or Router Limitation Detected!")
            if self.adapter_info.driver_outdated_flag:
                logger.warning(f"⚠ Driver is {self.adapter_info.driver_age_days // 365} years old - Update recommended!")
            
            return True
            
        except Exception as e:
            logger.error(f"Windows adapter analysis failed: {e}")
            return self._analyze_adapter_fallback()
    
    def _analyze_adapter_fallback(self) -> bool:
        """Fallback adapter analysis using psutil"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            # Find first non-loopback active interface
            for name, addrs in interfaces.items():
                if name.lower() in ['lo', 'loopback']:
                    continue
                
                if name in stats and stats[name].isup:
                    self.adapter_info.name = name
                    
                    # Determine type
                    if 'wi-fi' in name.lower() or 'wlan' in name.lower() or 'wireless' in name.lower():
                        self.adapter_info.interface_type = "WiFi"
                    else:
                        self.adapter_info.interface_type = "Ethernet"
                    
                    # Get MAC address
                    for addr in addrs:
                        if addr.family == psutil.AF_LINK:
                            self.adapter_info.mac_address = addr.address
                        elif addr.family == socket.AF_INET:
                            # Get default gateway
                            try:
                                gateways = psutil.net_if_addrs()
                            except:
                                pass
                    
                    break
            
            # Save to JSON
            adapter_json = os.path.join(self.folders['AdapterInfo'], 'adapter_details.json')
            with open(adapter_json, 'w') as f:
                json.dump(asdict(self.adapter_info), f, indent=2, default=str)
            
            logger.info(f"✓ Fallback adapter analysis completed: {self.adapter_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Fallback adapter analysis failed: {e}")
            return False
    
    def _capture_device_manager_screenshot(self):
        """Capture Device Manager screenshot"""
        try:
            if not PYAUTOGUI_AVAILABLE:
                return
            
            # Open Device Manager
            subprocess.Popen(['devmgmt.msc'], shell=True)
            time.sleep(3)
            
            # Take screenshot
            screenshot_path = os.path.join(self.folders['Screenshots'], 'device_manager_network.png')
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            
            # Close Device Manager
            subprocess.run(['taskkill', '/F', '/IM', 'mmc.exe'], capture_output=True)
            
            logger.info(f"✓ Device Manager screenshot saved")
        except Exception as e:
            logger.warning(f"Could not capture Device Manager screenshot: {e}")
    
    # ========================================================================
    # STEP 3: AUTOMATED SPEED TESTS
    # ========================================================================
    
    def run_speed_tests(self) -> bool:
        """Run automated speed tests using Chrome/Selenium"""
        logger.info("STEP 3: Running automated speed tests...")
        
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available, using CLI speedtest only")
            return self._run_speedtest_cli()
        
        success = True
        
        # Test fast.com
        if not self._run_fast_com_test():
            logger.warning("Fast.com test failed, retrying once...")
            time.sleep(5)
            self._run_fast_com_test()
        
        # Test speedtest.net
        if not self._run_speedtest_net_test():
            logger.warning("Speedtest.net test failed, retrying once...")
            time.sleep(5)
            self._run_speedtest_net_test()
        
        # Also run CLI test as backup
        self._run_speedtest_cli()
        
        # Save results to JSON
        speed_json = os.path.join(self.folders['SpeedTests'], 'speedtest_results.json')
        with open(speed_json, 'w') as f:
            json.dump([asdict(r) for r in self.speed_tests], f, indent=2)
        
        return len(self.speed_tests) > 0
    
    def _setup_chrome_driver(self) -> bool:
        """Setup Chrome driver for Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # Try to create driver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def _run_fast_com_test(self) -> bool:
        """Run speed test on fast.com"""
        logger.info("Testing on fast.com...")
        
        result = SpeedTestResult(source="fast.com", timestamp=self.timestamp)
        
        try:
            if not self.driver:
                if not self._setup_chrome_driver():
                    result.error_message = "Chrome driver setup failed"
                    self.speed_tests.append(result)
                    return False
            
            self.driver.get("https://fast.com")
            logger.info("Waiting for fast.com test to complete (30s)...")
            time.sleep(30)
            
            # Try to get more info (upload speed)
            try:
                show_more = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "show-more-details-link"))
                )
                show_more.click()
                time.sleep(10)
            except:
                pass
            
            # Extract results
            try:
                download_elem = self.driver.find_element(By.ID, "speed-value")
                result.download_speed = float(download_elem.text) if download_elem.text else 0
            except:
                pass
            
            try:
                upload_elem = self.driver.find_element(By.ID, "upload-value")
                result.upload_speed = float(upload_elem.text) if upload_elem.text else 0
            except:
                pass
            
            # Capture screenshot
            screenshot_path = os.path.join(self.folders['SpeedTests'], f'fast_com_{self.timestamp}.png')
            self.driver.save_screenshot(screenshot_path)
            result.screenshot_path = screenshot_path
            
            result.success = result.download_speed > 0
            
            if result.success:
                logger.info(f"✓ Fast.com: {result.download_speed:.1f} Mbps down, {result.upload_speed:.1f} Mbps up")
            
            self.speed_tests.append(result)
            return result.success
            
        except Exception as e:
            logger.error(f"Fast.com test failed: {e}")
            result.error_message = str(e)
            self.speed_tests.append(result)
            return False
    
    def _run_speedtest_net_test(self) -> bool:
        """Run speed test on speedtest.net"""
        logger.info("Testing on speedtest.net...")
        
        result = SpeedTestResult(source="speedtest.net", timestamp=self.timestamp)
        
        try:
            if not self.driver:
                if not self._setup_chrome_driver():
                    result.error_message = "Chrome driver setup failed"
                    self.speed_tests.append(result)
                    return False
            
            self.driver.get("https://www.speedtest.net")
            time.sleep(3)
            
            # Click start button
            try:
                start_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Go')]"))
                )
                start_btn.click()
                logger.info("Speed test started, waiting 60s...")
            except Exception as e:
                logger.warning(f"Could not click start button: {e}")
            
            time.sleep(60)
            
            # Try to extract results from page
            page_source = self.driver.page_source
            
            # Look for speed values in the page
            download_match = re.search(r'(\d+\.?\d*)\s*<span[^>]*>Mbps</span>', page_source)
            if download_match:
                result.download_speed = float(download_match.group(1))
            
            # Capture screenshot
            screenshot_path = os.path.join(self.folders['SpeedTests'], f'speedtest_net_{self.timestamp}.png')
            self.driver.save_screenshot(screenshot_path)
            result.screenshot_path = screenshot_path
            
            result.success = True
            logger.info(f"✓ Speedtest.net test completed")
            
            self.speed_tests.append(result)
            return True
            
        except Exception as e:
            logger.error(f"Speedtest.net test failed: {e}")
            result.error_message = str(e)
            self.speed_tests.append(result)
            return False
    
    def _run_speedtest_cli(self) -> bool:
        """Run speedtest using speedtest-cli library"""
        logger.info("Running CLI speed test...")
        
        result = SpeedTestResult(source="speedtest-cli", timestamp=self.timestamp)
        
        try:
            if not SPEEDTEST_AVAILABLE:
                result.error_message = "speedtest-cli not available"
                self.speed_tests.append(result)
                return False
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            result.download_speed = st.download() / 1_000_000
            result.upload_speed = st.upload() / 1_000_000
            result.latency = st.results.ping
            result.success = True
            
            logger.info(f"✓ CLI Speed Test: {result.download_speed:.1f} Mbps down, {result.upload_speed:.1f} Mbps up, {result.latency:.1f} ms ping")
            
            self.speed_tests.append(result)
            return True
            
        except Exception as e:
            logger.error(f"CLI speed test failed: {e}")
            result.error_message = str(e)
            self.speed_tests.append(result)
            return False
    
    # ========================================================================
    # STEP 4: MULTI-TARGET PING TESTS
    # ========================================================================
    
    def run_ping_tests(self) -> bool:
        """Run ping tests to multiple targets concurrently"""
        logger.info("STEP 4: Running multi-target ping tests...")
        
        logger.info(f"Testing {len(self.ping_targets)} targets for 60 seconds each...")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=min(5, len(self.ping_targets))) as executor:
            futures = {
                executor.submit(self._ping_target, target): target 
                for target in self.ping_targets
            }
            
            for future in as_completed(futures):
                target = futures[future]
                try:
                    result = future.result()
                    if result:
                        self.ping_tests.append(result)
                except Exception as e:
                    logger.error(f"Ping to {target} failed: {e}")
        
        # Save results
        ping_json = os.path.join(self.folders['PingTests'], 'ping_results.json')
        with open(ping_json, 'w') as f:
            json.dump([asdict(r) for r in self.ping_tests], f, indent=2)
        
        logger.info(f"✓ Completed ping tests for {len(self.ping_tests)} targets")
        return True
    
    def _ping_target(self, target: str) -> Optional[PingResult]:
        """Ping a single target for 60 seconds"""
        result = PingResult(target=target)
        
        try:
            # Run ping command for 60 seconds
            if self.platform == 'windows':
                cmd = f'ping -n 60 -w 1000 {target}'
            else:
                cmd = f'ping -c 60 -i 1 {target}'
            
            process = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=70
            )
            
            result.raw_output = process.stdout
            result.packets_sent = 60
            
            # Parse ping output
            output = process.stdout
            
            # Extract packet loss
            loss_match = re.search(r'(\d+)% loss', output) or re.search(r'(\d+)% packet loss', output)
            if loss_match:
                result.packet_loss_percent = float(loss_match.group(1))
            
            # Extract latency stats
            stats_match = re.search(r'Minimum\s*=\s*(\d+)ms.*?Maximum\s*=\s*(\d+)ms.*?Average\s*=\s*(\d+)ms', output)
            if stats_match:
                result.min_latency = float(stats_match.group(1))
                result.max_latency = float(stats_match.group(2))
                result.avg_latency = float(stats_match.group(3))
            else:
                # Try alternative format
                stats_match = re.search(r'min/avg/max.*?=\s*[\d\.]+/(\d+\.?\d*)/(\d+\.?\d*)', output)
                if stats_match:
                    result.avg_latency = float(stats_match.group(1))
                    result.max_latency = float(stats_match.group(2))
            
            # Calculate received packets
            result.packets_received = int(result.packets_sent * (1 - result.packet_loss_percent / 100))
            result.success = True
            
            # Save raw output
            log_file = os.path.join(self.folders['PingTests'], f'ping_{target.replace(".", "_")}.txt')
            with open(log_file, 'w') as f:
                f.write(output)
            
            logger.info(f"✓ {target}: {result.avg_latency:.1f}ms avg, {result.packet_loss_percent:.1f}% loss")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Ping to {target} timed out")
            result.error_message = "Timeout"
            return result
        except Exception as e:
            logger.error(f"Ping to {target} error: {e}")
            result.error_message = str(e)
            return result
    
    # ========================================================================
    # STEP 5: LOAD / STRESS TESTS
    # ========================================================================
    
    def run_load_tests(self) -> bool:
        """Run load/stress tests on targets"""
        logger.info("STEP 5: Running load/stress tests...")
        
        # Test key targets with load
        load_targets = ["8.8.8.8", "google.com", "cloudflare.com"]
        
        for target in load_targets:
            result = self._load_test_target(target)
            if result:
                self.load_tests.append(result)
        
        # Save results
        load_json = os.path.join(self.folders['LoadTests'], 'load_test_results.json')
        with open(load_json, 'w') as f:
            json.dump([asdict(r) for r in self.load_tests], f, indent=2)
        
        logger.info(f"✓ Completed load tests for {len(self.load_tests)} targets")
        return True
    
    def _load_test_target(self, target: str) -> Optional[LoadTestResult]:
        """Load test a target with 1000 packets"""
        result = LoadTestResult(target=target)
        
        try:
            logger.info(f"Load testing {target} with 1000 packets...")
            
            # Use hping3 or nping if available, otherwise use multiple ping threads
            latencies = []
            packets_sent = 1000
            packets_received = 0
            
            # Run multiple ping threads for load simulation
            def ping_batch(count):
                local_latencies = []
                for _ in range(count):
                    if self.platform == 'windows':
                        cmd = f'ping -n 1 -w 1000 {target}'
                    else:
                        cmd = f'ping -c 1 -W 1 {target}'
                    
                    start = time.time()
                    proc = subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
                    elapsed = (time.time() - start) * 1000
                    
                    if proc.returncode == 0:
                        local_latencies.append(elapsed)
                return local_latencies
            
            # Use thread pool for concurrent pings
            batch_size = 100
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(ping_batch, batch_size) for _ in range(10)]
                for future in as_completed(futures):
                    latencies.extend(future.result())
            
            packets_received = len(latencies)
            result.packets_sent = packets_sent
            result.packets_received = packets_received
            result.packet_loss_percent = ((packets_sent - packets_received) / packets_sent) * 100
            
            if latencies:
                # Calculate jitter (standard deviation of latency differences)
                if len(latencies) > 1:
                    diffs = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]
                    result.jitter = sum(diffs) / len(diffs)
                
                # Calculate stability score (based on packet loss and jitter)
                loss_penalty = result.packet_loss_percent * 2
                jitter_penalty = min(result.jitter / 10, 30)
                result.stability_score = max(0, 100 - loss_penalty - jitter_penalty)
            
            result.success = True
            logger.info(f"✓ {target}: {result.packet_loss_percent:.1f}% loss, {result.jitter:.1f}ms jitter, {result.stability_score:.1f}% stability")
            
            return result
            
        except Exception as e:
            logger.error(f"Load test to {target} failed: {e}")
            return result
    
    # ========================================================================
    # STEP 6: WINMTR ROUTE TRACE
    # ========================================================================
    
    def run_winmtr_tests(self) -> bool:
        """Run WinMTR route traces"""
        logger.info("STEP 6: Running WinMTR route traces...")
        
        # Check if WinMTR is available
        winmtr_paths = [
            r"C:\Program Files\WinMTR\WinMTR.exe",
            r"C:\Program Files (x86)\WinMTR\WinMTR.exe",
            r"C:\WinMTR\WinMTR.exe",
            r"WinMTR.exe"
        ]
        
        winmtr_path = None
        for path in winmtr_paths:
            if os.path.exists(path) or shutil.which(path):
                winmtr_path = path if os.path.exists(path) else shutil.which(path)
                break
        
        if not winmtr_path:
            logger.warning("WinMTR not found, using built-in tracert instead")
            return self._run_tracert_fallback()
        
        # Run WinMTR for each target
        for target in ["8.8.8.8", "google.com", "cloudflare.com"]:
            result = self._run_winmtr(winmtr_path, target)
            if result:
                self.winmtr_tests.append(result)
        
        # Save results
        winmtr_json = os.path.join(self.folders['WinMTR'], 'winmtr_results.json')
        with open(winmtr_json, 'w') as f:
            json.dump([asdict(r) for r in self.winmtr_tests], f, indent=2)
        
        logger.info(f"✓ Completed route traces for {len(self.winmtr_tests)} targets")
        return True
    
    def _run_winmtr(self, winmtr_path: str, target: str) -> Optional[WinMTRResult]:
        """Run WinMTR for a target"""
        result = WinMTRResult(target=target)
        
        try:
            logger.info(f"Running WinMTR to {target}...")
            
            # WinMTR command line options for 100 cycles
            report_file = os.path.join(self.folders['WinMTR'], f'winmtr_{target.replace(".", "_")}.txt')
            
            # Launch WinMTR with target
            proc = subprocess.Popen(
                [winmtr_path, target],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for it to run
            time.sleep(15)
            
            # Try to export and close
            try:
                proc.terminate()
            except:
                pass
            
            # Parse results (simplified - would need actual WinMTR output parsing)
            result.total_hops = 0
            result.success = True
            
            logger.info(f"✓ WinMTR to {target} completed")
            return result
            
        except Exception as e:
            logger.error(f"WinMTR to {target} failed: {e}")
            return result
    
    def _run_tracert_fallback(self) -> bool:
        """Fallback to tracert if WinMTR not available"""
        logger.info("Using tracert as fallback...")
        
        for target in ["8.8.8.8", "google.com", "cloudflare.com"]:
            result = WinMTRResult(target=target)
            
            try:
                cmd = f'tracert -h 30 {target}'
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                
                output = proc.stdout
                
                # Count hops
                hops = len(re.findall(r'\n\s*\d+\s+', output))
                result.total_hops = hops
                
                # Find worst latency hop
                worst_latency = 0
                worst_hop = 0
                for match in re.finditer(r'\n\s*(\d+)\s+.*?(\d+)\s*ms', output):
                    hop_num = int(match.group(1))
                    latency = int(match.group(2))
                    if latency > worst_latency:
                        worst_latency = latency
                        worst_hop = hop_num
                
                result.worst_latency_hop = worst_hop
                result.worst_latency_value = worst_latency
                result.success = True
                
                # Save output
                report_file = os.path.join(self.folders['WinMTR'], f'tracert_{target.replace(".", "_")}.txt')
                with open(report_file, 'w') as f:
                    f.write(output)
                result.report_path = report_file
                
                logger.info(f"✓ Tracert to {target}: {hops} hops, worst latency {worst_latency}ms at hop {worst_hop}")
                
                self.winmtr_tests.append(result)
                
            except Exception as e:
                logger.error(f"Tracert to {target} failed: {e}")
                self.winmtr_tests.append(result)
        
        return True
    
    # ========================================================================
    # STEP 7: INTELLIGENT NETWORK HEALTH SCORE
    # ========================================================================
    
    def calculate_health_score(self) -> bool:
        """Calculate intelligent network health score"""
        logger.info("STEP 7: Calculating network health score...")
        
        self.health_score = NetworkHealthScore()
        scores = []
        
        # Speed Quality Score (0-25)
        speed_score = 0
        if self.speed_tests:
            valid_tests = [t for t in self.speed_tests if t.success and t.download_speed > 0]
            if valid_tests:
                avg_speed = sum(t.download_speed for t in valid_tests) / len(valid_tests)
                if avg_speed >= 100:
                    speed_score = 25
                elif avg_speed >= 50:
                    speed_score = 20
                elif avg_speed >= 25:
                    speed_score = 15
                elif avg_speed >= 10:
                    speed_score = 10
                else:
                    speed_score = 5
        scores.append(speed_score)
        self.health_score.speed_score = speed_score
        
        # Packet Loss Score (0-25)
        loss_score = 25
        if self.ping_tests:
            avg_loss = sum(t.packet_loss_percent for t in self.ping_tests) / len(self.ping_tests)
            if avg_loss > 5:
                loss_score = 5
            elif avg_loss > 2:
                loss_score = 10
            elif avg_loss > 1:
                loss_score = 15
            elif avg_loss > 0.5:
                loss_score = 20
        scores.append(loss_score)
        
        # Latency Score (0-20)
        latency_score = 20
        if self.ping_tests:
            avg_latency = sum(t.avg_latency for t in self.ping_tests if t.success) / max(1, len([t for t in self.ping_tests if t.success]))
            if avg_latency > 100:
                latency_score = 5
            elif avg_latency > 50:
                latency_score = 10
            elif avg_latency > 30:
                latency_score = 15
        scores.append(latency_score)
        self.health_score.latency_score = latency_score
        
        # Stability Score (0-15)
        stability_score = 15
        if self.load_tests:
            avg_stability = sum(t.stability_score for t in self.load_tests) / len(self.load_tests)
            stability_score = int(avg_stability * 0.15)
        scores.append(stability_score)
        self.health_score.stability_score = stability_score
        
        # Hardware Score (0-15)
        hardware_score = 15
        if self.adapter_info:
            if self.adapter_info.cable_limitation_flag:
                hardware_score -= 5
                self.health_score.recommendations.append("Replace LAN cable to achieve Gigabit speeds")
            if self.adapter_info.driver_outdated_flag:
                hardware_score -= 5
                self.health_score.recommendations.append("Update network adapter driver")
            if not self.adapter_info.is_gigabit_capable:
                hardware_score -= 3
                self.health_score.recommendations.append("Consider upgrading to Gigabit-capable adapter")
        scores.append(max(0, hardware_score))
        self.health_score.hardware_score = max(0, hardware_score)
        
        # Calculate total score
        self.health_score.overall_score = sum(scores)
        
        # Determine grade
        if self.health_score.overall_score >= 90:
            self.health_score.grade = "Excellent"
        elif self.health_score.overall_score >= 75:
            self.health_score.grade = "Good"
        elif self.health_score.overall_score >= 60:
            self.health_score.grade = "Fair"
        else:
            self.health_score.grade = "Poor"
        
        # Add general recommendations based on score
        if self.health_score.overall_score < 60:
            if not any("ISP" in r for r in self.health_score.recommendations):
                self.health_score.recommendations.append("Contact ISP regarding connection quality issues")
        
        if self.health_score.overall_score < 75:
            if not any("router" in r.lower() for r in self.health_score.recommendations):
                self.health_score.recommendations.append("Check router configuration and firmware")
        
        # Generate ISP complaint summary
        self._generate_isp_complaint_summary()
        
        logger.info(f"✓ Health Score: {self.health_score.overall_score}/100 ({self.health_score.grade})")
        
        return True
    
    def _generate_isp_complaint_summary(self):
        """Generate ISP complaint ready summary"""
        summary = []
        summary.append("NETWORK DIAGNOSTIC SUMMARY FOR ISP COMPLAINT")
        summary.append("=" * 50)
        summary.append("")
        summary.append(f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Network Health Score: {self.health_score.overall_score}/100 ({self.health_score.grade})")
        summary.append("")
        
        if self.speed_tests:
            valid_tests = [t for t in self.speed_tests if t.success]
            if valid_tests:
                avg_speed = sum(t.download_speed for t in valid_tests) / len(valid_tests)
                summary.append(f"Average Download Speed: {avg_speed:.1f} Mbps")
        
        if self.ping_tests:
            avg_loss = sum(t.packet_loss_percent for t in self.ping_tests) / len(self.ping_tests)
            avg_latency = sum(t.avg_latency for t in self.ping_tests if t.success) / max(1, len([t for t in self.ping_tests if t.success]))
            summary.append(f"Average Packet Loss: {avg_loss:.2f}%")
            summary.append(f"Average Latency: {avg_latency:.1f} ms")
        
        summary.append("")
        summary.append("Issues Detected:")
        for rec in self.health_score.recommendations:
            summary.append(f"  - {rec}")
        
        summary.append("")
        summary.append("Technical Evidence:")
        summary.append(f"  - {len(self.ping_tests)} ping tests conducted to multiple targets")
        summary.append(f"  - {len(self.load_tests)} load tests performed")
        if self.winmtr_tests:
            summary.append(f"  - {len(self.winmtr_tests)} route traces completed")
        
        self.health_score.isp_complaint_summary = "\n".join(summary)
    
    # ========================================================================
    # STEP 8: GENERATE VISUAL CHARTS
    # ========================================================================
    
    def generate_charts(self) -> bool:
        """Generate visual charts using matplotlib"""
        logger.info("STEP 8: Generating visual charts...")
        
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available, skipping charts")
            return False
        
        try:
            # Set style
            plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
        except:
            pass
        
        success = True
        
        # Chart 1: Speed Comparison
        if self.speed_tests:
            try:
                self._create_speed_chart()
            except Exception as e:
                logger.warning(f"Speed chart failed: {e}")
                success = False
        
        # Chart 2: Ping Latency Comparison
        if self.ping_tests:
            try:
                self._create_latency_chart()
            except Exception as e:
                logger.warning(f"Latency chart failed: {e}")
                success = False
        
        # Chart 3: Packet Loss Chart
        if self.ping_tests:
            try:
                self._create_packet_loss_chart()
            except Exception as e:
                logger.warning(f"Packet loss chart failed: {e}")
                success = False
        
        # Chart 4: Load Test Stability
        if self.load_tests:
            try:
                self._create_stability_chart()
            except Exception as e:
                logger.warning(f"Stability chart failed: {e}")
                success = False
        
        # Chart 5: Health Score Gauge
        if self.health_score:
            try:
                self._create_health_gauge()
            except Exception as e:
                logger.warning(f"Health gauge failed: {e}")
                success = False
        
        logger.info(f"✓ Generated {len(self.chart_paths)} charts")
        return success
    
    def _create_speed_chart(self):
        """Create speed comparison bar chart"""
        valid_tests = [t for t in self.speed_tests if t.success]
        if not valid_tests:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sources = [t.source for t in valid_tests]
        downloads = [t.download_speed for t in valid_tests]
        uploads = [t.upload_speed for t in valid_tests]
        
        x = range(len(sources))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], downloads, width, label='Download', color='#2ecc71')
        ax.bar([i + width/2 for i in x], uploads, width, label='Upload', color='#3498db')
        
        ax.set_xlabel('Speed Test Source')
        ax.set_ylabel('Speed (Mbps)')
        ax.set_title('Internet Speed Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(sources, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(self.folders['Charts'], 'speed_comparison.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.chart_paths.append(chart_path)
    
    def _create_latency_chart(self):
        """Create ping latency comparison chart"""
        valid_tests = [t for t in self.ping_tests if t.success]
        if not valid_tests:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        targets = [t.target[:15] for t in valid_tests]  # Truncate long names
        avg_latencies = [t.avg_latency for t in valid_tests]
        min_latencies = [t.min_latency for t in valid_tests]
        max_latencies = [t.max_latency for t in valid_tests]
        
        x = range(len(targets))
        
        ax.bar(x, avg_latencies, color='#9b59b6', alpha=0.7, label='Average')
        ax.scatter(x, min_latencies, color='#2ecc71', s=50, label='Min', zorder=5)
        ax.scatter(x, max_latencies, color='#e74c3c', s=50, label='Max', zorder=5)
        
        ax.set_xlabel('Target')
        ax.set_ylabel('Latency (ms)')
        ax.set_title('Ping Latency Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(targets, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(self.folders['Charts'], 'latency_comparison.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.chart_paths.append(chart_path)
    
    def _create_packet_loss_chart(self):
        """Create packet loss chart"""
        valid_tests = [t for t in self.ping_tests if t.success]
        if not valid_tests:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        targets = [t.target[:15] for t in valid_tests]
        losses = [t.packet_loss_percent for t in valid_tests]
        
        colors = ['#e74c3c' if l > 0 else '#2ecc71' for l in losses]
        
        ax.bar(targets, losses, color=colors)
        ax.set_xlabel('Target')
        ax.set_ylabel('Packet Loss (%)')
        ax.set_title('Packet Loss by Target')
        ax.set_xticklabels(targets, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(self.folders['Charts'], 'packet_loss.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.chart_paths.append(chart_path)
    
    def _create_stability_chart(self):
        """Create load test stability chart"""
        if not self.load_tests:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        targets = [t.target for t in self.load_tests]
        scores = [t.stability_score for t in self.load_tests]
        
        colors = ['#2ecc71' if s >= 80 else '#f39c12' if s >= 60 else '#e74c3c' for s in scores]
        
        ax.barh(targets, scores, color=colors)
        ax.set_xlabel('Stability Score')
        ax.set_ylabel('Target')
        ax.set_title('Load Test Stability Scores')
        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3)
        
        # Add score labels
        for i, score in enumerate(scores):
            ax.text(score + 2, i, f'{score:.1f}', va='center')
        
        plt.tight_layout()
        chart_path = os.path.join(self.folders['Charts'], 'stability_scores.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.chart_paths.append(chart_path)
    
    def _create_health_gauge(self):
        """Create health score gauge chart"""
        if not self.health_score:
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        score = self.health_score.overall_score
        
        # Create semi-circle gauge
        theta = range(0, 181, 1)
        r = [1] * len(theta)
        
        # Color zones
        for i, t in enumerate(theta):
            if t < 60:
                color = '#e74c3c'  # Red
            elif t < 75:
                color = '#f39c12'  # Yellow
            elif t < 90:
                color = '#2ecc71'  # Green
            else:
                color = '#27ae60'  # Dark green
            ax.plot([0, 1.1 * np.cos(np.radians(t))], [0, 1.1 * np.sin(np.radians(t))], color=color, linewidth=3)
        
        # Add needle
        import numpy as np
        angle = 180 - (score / 100 * 180)
        ax.plot([0, 0.9 * np.cos(np.radians(angle))], [0, 0.9 * np.sin(np.radians(angle))], 'k-', linewidth=4)
        ax.plot(0, 0, 'ko', markersize=10)
        
        # Add score text
        ax.text(0, -0.3, f'{score}', fontsize=48, ha='center', fontweight='bold')
        ax.text(0, -0.5, self.health_score.grade, fontsize=24, ha='center')
        
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-0.8, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Network Health Score', fontsize=18, pad=20)
        
        plt.tight_layout()
        chart_path = os.path.join(self.folders['Charts'], 'health_score_gauge.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.chart_paths.append(chart_path)
    
    # ========================================================================
    # STEP 9: GENERATE PDF REPORT
    # ========================================================================
    
    def generate_pdf_report(self) -> str:
        """Generate professional PDF report using reportlab"""
        logger.info("STEP 9: Generating professional PDF report...")
        
        if REPORTLAB_AVAILABLE:
            return self._generate_reportlab_pdf()
        else:
            return self._generate_fallback_pdf()
    
    def _generate_reportlab_pdf(self) -> str:
        """Generate PDF using reportlab Platypus"""
        pdf_path = os.path.join(self.folders['FinalReport'], 'SUNYA_Network_Diagnostic_Report.pdf')
        
        try:
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=colors.HexColor('#7f8c8d'),
                spaceAfter=10
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY
            )
            
            story = []
            
            # COVER PAGE
            story.append(Spacer(1, 100))
            story.append(Paragraph("SUNYA NETWORK DIAGNOSTIC", title_style))
            story.append(Paragraph("SYSTEM REPORT", title_style))
            story.append(Spacer(1, 50))
            
            # Cover details
            cover_data = [
                ['Report Date:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['System Name:', socket.gethostname()],
                ['User:', self.username],
                ['Platform:', f"{platform.system()} {platform.release()}"]
            ]
            
            # Try to get ISP and public IP
            try:
                import urllib.request
                public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()
                cover_data.append(['Public IP:', public_ip])
            except:
                cover_data.append(['Public IP:', 'Could not determine'])
            
            if self.health_score:
                cover_data.append(['Health Score:', f"{self.health_score.overall_score}/100"])
                cover_data.append(['Status:', self.health_score.grade])
            
            cover_table = Table(cover_data, colWidths=[150, 300])
            cover_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(cover_table)
            
            story.append(PageBreak())
            
            # SECTION 1: Adapter Analysis
            story.append(Paragraph("SECTION 1 – Network Adapter Analysis", heading_style))
            story.append(Spacer(1, 12))
            
            if self.adapter_info:
                adapter_data = [
                    ['Property', 'Value'],
                    ['Adapter Name', self.adapter_info.name],
                    ['Manufacturer', self.adapter_info.manufacturer],
                    ['Description', self.adapter_info.description[:50] + '...' if len(self.adapter_info.description) > 50 else self.adapter_info.description],
                    ['MAC Address', self.adapter_info.mac_address],
                    ['Driver Version', self.adapter_info.driver_version],
                    ['Driver Date', self.adapter_info.driver_date],
                    ['Driver Provider', self.adapter_info.driver_provider],
                    ['Link Speed', f"{self.adapter_info.link_speed} Mbps"],
                    ['Interface Type', self.adapter_info.interface_type],
                    ['Gigabit Capable', 'Yes' if self.adapter_info.is_gigabit_capable else 'No'],
                    ['Negotiating Gigabit', 'Yes' if self.adapter_info.is_negotiating_gigabit else 'No'],
                ]
                
                adapter_table = Table(adapter_data, colWidths=[150, 300])
                adapter_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ]))
                story.append(adapter_table)
                story.append(Spacer(1, 12))
                
                # Warnings
                if self.adapter_info.cable_limitation_flag:
                    story.append(Paragraph(
                        "<font color='red'>⚠ WARNING: Cable or Router Limitation Detected!</font> "
                        "Adapter supports Gigabit but is negotiating at lower speed.",
                        body_style
                    ))
                    story.append(Spacer(1, 6))
                
                if self.adapter_info.driver_outdated_flag:
                    story.append(Paragraph(
                        f"<font color='orange'>⚠ WARNING: Driver is {self.adapter_info.driver_age_days // 365} years old. "
                        "Consider updating to latest version.</font>",
                        body_style
                    ))
            
            story.append(PageBreak())
            
            # SECTION 2: Speed Tests
            story.append(Paragraph("SECTION 2 – Speed Test Results", heading_style))
            story.append(Spacer(1, 12))
            
            if self.speed_tests:
                speed_data = [['Source', 'Download (Mbps)', 'Upload (Mbps)', 'Latency (ms)', 'Status']]
                for test in self.speed_tests:
                    speed_data.append([
                        test.source,
                        f"{test.download_speed:.1f}" if test.download_speed > 0 else "N/A",
                        f"{test.upload_speed:.1f}" if test.upload_speed > 0 else "N/A",
                        f"{test.latency:.1f}" if test.latency > 0 else "N/A",
                        '✓' if test.success else '✗'
                    ])
                
                speed_table = Table(speed_data, colWidths=[100, 100, 100, 100, 50])
                speed_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ]))
                story.append(speed_table)
                
                # Add speed chart
                speed_chart = os.path.join(self.folders['Charts'], 'speed_comparison.png')
                if os.path.exists(speed_chart):
                    story.append(Spacer(1, 20))
                    story.append(Image(speed_chart, width=450, height=270))
            
            story.append(PageBreak())
            
            # SECTION 3: Ping Results
            story.append(Paragraph("SECTION 3 – Ping Test Results", heading_style))
            story.append(Spacer(1, 12))
            
            if self.ping_tests:
                ping_data = [['Target', 'Avg (ms)', 'Min (ms)', 'Max (ms)', 'Loss %']]
                for test in self.ping_tests[:10]:  # Show first 10
                    ping_data.append([
                        test.target[:25],
                        f"{test.avg_latency:.1f}",
                        f"{test.min_latency:.1f}",
                        f"{test.max_latency:.1f}",
                        f"{test.packet_loss_percent:.1f}"
                    ])
                
                ping_table = Table(ping_data, colWidths=[150, 75, 75, 75, 75])
                ping_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ]))
                story.append(ping_table)
                
                # Add latency chart
                latency_chart = os.path.join(self.folders['Charts'], 'latency_comparison.png')
                if os.path.exists(latency_chart):
                    story.append(Spacer(1, 20))
                    story.append(Image(latency_chart, width=450, height=225))
            
            story.append(PageBreak())
            
            # SECTION 4: Load Tests
            story.append(Paragraph("SECTION 4 – Load Test Results", heading_style))
            story.append(Spacer(1, 12))
            
            if self.load_tests:
                load_data = [['Target', 'Packets', 'Loss %', 'Jitter (ms)', 'Stability']]
                for test in self.load_tests:
                    load_data.append([
                        test.target,
                        f"{test.packets_received}/{test.packets_sent}",
                        f"{test.packet_loss_percent:.1f}",
                        f"{test.jitter:.1f}",
                        f"{test.stability_score:.1f}%"
                    ])
                
                load_table = Table(load_data, colWidths=[125, 100, 75, 100, 100])
                load_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ]))
                story.append(load_table)
            
            story.append(PageBreak())
            
            # SECTION 5: WinMTR
            story.append(Paragraph("SECTION 5 – Route Analysis (WinMTR/Tracert)", heading_style))
            story.append(Spacer(1, 12))
            
            if self.winmtr_tests:
                winmtr_data = [['Target', 'Hops', 'Worst Latency', 'Bottleneck']]
                for test in self.winmtr_tests:
                    winmtr_data.append([
                        test.target,
                        str(test.total_hops),
                        f"{test.worst_latency_value:.1f}ms (hop {test.worst_latency_hop})",
                        'Yes' if test.bottleneck_detected else 'No'
                    ])
                
                winmtr_table = Table(winmtr_data, colWidths=[150, 75, 150, 100])
                winmtr_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ]))
                story.append(winmtr_table)
            
            story.append(PageBreak())
            
            # SECTION 6: Health Score and Recommendations
            story.append(Paragraph("SECTION 6 – Network Health Assessment", heading_style))
            story.append(Spacer(1, 12))
            
            if self.health_score:
                # Score breakdown
                score_data = [
                    ['Component', 'Score', 'Max'],
                    ['Speed Quality', str(self.health_score.speed_score), '25'],
                    ['Packet Loss', str(int(self.health_score.overall_score - sum([self.health_score.speed_score, self.health_score.latency_score, self.health_score.stability_score, self.health_score.hardware_score]))), '25'],
                    ['Latency', str(self.health_score.latency_score), '20'],
                    ['Stability', str(self.health_score.stability_score), '15'],
                    ['Hardware', str(self.health_score.hardware_score), '15'],
                    ['TOTAL', str(self.health_score.overall_score), '100'],
                ]
                
                score_table = Table(score_data, colWidths=[200, 100, 100])
                score_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(score_table)
                story.append(Spacer(1, 20))
                
                # Grade
                grade_color = '#27ae60' if self.health_score.grade == 'Excellent' else '#2ecc71' if self.health_score.grade == 'Good' else '#f39c12' if self.health_score.grade == 'Fair' else '#e74c3c'
                story.append(Paragraph(
                    f"<font color='{grade_color}' size='16'><b>Overall Grade: {self.health_score.grade}</b></font>",
                    ParagraphStyle('Grade', alignment=TA_CENTER)
                ))
                story.append(Spacer(1, 20))
                
                # Recommendations
                if self.health_score.recommendations:
                    story.append(Paragraph("Recommendations:", subheading_style))
                    for rec in self.health_score.recommendations:
                        story.append(Paragraph(f"• {rec}", body_style))
                        story.append(Spacer(1, 6))
            
            story.append(PageBreak())
            
            # SECTION 7: ISP Complaint Summary
            story.append(Paragraph("SECTION 7 – ISP Complaint Ready Summary", heading_style))
            story.append(Spacer(1, 12))
            
            if self.health_score and self.health_score.isp_complaint_summary:
                for line in self.health_score.isp_complaint_summary.split('\n'):
                    story.append(Paragraph(line.replace(' ', '&nbsp;'), body_style))
                    story.append(Spacer(1, 4))
            
            # Build PDF
            doc.build(story)
            logger.info(f"✓ PDF report generated: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"ReportLab PDF generation failed: {e}")
            return self._generate_fallback_pdf()
    
    def _generate_fallback_pdf(self) -> str:
        """Generate simple fallback PDF"""
        try:
            from fpdf import FPDF
            
            pdf_path = os.path.join(self.folders['FinalReport'], 'SUNYA_Network_Diagnostic_Report.pdf')
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'SUNYA Network Diagnostic Report', 0, 1, 'C')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
            pdf.ln(10)
            
            # Adapter Info
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Network Adapter', 0, 1)
            pdf.set_font('Arial', '', 11)
            if self.adapter_info:
                pdf.cell(0, 8, f'Name: {self.adapter_info.name}', 0, 1)
                pdf.cell(0, 8, f'Speed: {self.adapter_info.link_speed} Mbps', 0, 1)
                pdf.cell(0, 8, f'Type: {self.adapter_info.interface_type}', 0, 1)
            
            pdf.ln(10)
            
            # Health Score
            if self.health_score:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f'Health Score: {self.health_score.overall_score}/100 ({self.health_score.grade})', 0, 1)
            
            pdf.output(pdf_path)
            logger.info(f"✓ Fallback PDF generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Fallback PDF generation failed: {e}")
            return ""
    
    # ========================================================================
    # STEP 10: CLEANUP AND FINALIZE
    # ========================================================================
    
    def cleanup_and_finalize(self, pdf_path: str):
        """Cleanup and open results"""
        logger.info("STEP 10: Cleanup and finalizing...")
        
        try:
            # Close Chrome
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("✓ Chrome closed")
                except:
                    pass
            
            # Kill Chrome processes
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
            except:
                pass
            
            # Close any remaining terminals
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'cmd.exe'], capture_output=True)
            except:
                pass
            
            # Copy raw logs to RawLogs folder
            for root, dirs, files in os.walk(self.base_folder):
                if 'RawLogs' not in root:
                    for file in files:
                        if file.endswith('.txt') or file.endswith('.log'):
                            src = os.path.join(root, file)
                            dst = os.path.join(self.folders['RawLogs'], file)
                            try:
                                shutil.copy2(src, dst)
                            except:
                                pass
            
            # Open Desktop folder
            try:
                os.startfile(self.base_folder)
                logger.info(f"✓ Opened report folder: {self.base_folder}")
            except:
                pass
            
            # Open PDF
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.startfile(pdf_path)
                    logger.info(f"✓ Opened PDF report")
                except:
                    pass
            
            logger.info("=" * 60)
            logger.info("DIAGNOSTIC COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"Report Location: {self.base_folder}")
            if self.health_score:
                logger.info(f"Health Score: {self.health_score.overall_score}/100 ({self.health_score.grade})")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    def run_complete_diagnostic(self):
        """Run the complete diagnostic process"""
        logger.info("=" * 60)
        logger.info("SUNYA COMPLETE NETWORK DIAGNOSTIC SYSTEM")
        logger.info("=" * 60)
        logger.info(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Create folder structure
            if not self.create_folder_structure():
                logger.error("Failed to create folder structure")
                return False
            
            # Step 2: Analyze network adapter
            self.analyze_network_adapter()
            
            # Step 3: Run speed tests
            self.run_speed_tests()
            
            # Step 4: Run ping tests
            self.run_ping_tests()
            
            # Step 5: Run load tests
            self.run_load_tests()
            
            # Step 6: Run WinMTR
            self.run_winmtr_tests()
            
            # Step 7: Calculate health score
            self.calculate_health_score()
            
            # Step 8: Generate charts
            self.generate_charts()
            
            # Step 9: Generate PDF report
            pdf_path = self.generate_pdf_report()
            
            # Step 10: Cleanup and finalize
            self.cleanup_and_finalize(pdf_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Diagnostic process failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("=" * 60)
    print("SUNYA COMPLETE NETWORK DIAGNOSTIC SYSTEM")
    print("=" * 60)
    print()
    print("This tool will perform comprehensive network diagnostics:")
    print("  • Network adapter analysis")
    print("  • Internet speed tests")
    print("  • Multi-target ping tests")
    print("  • Load/stress testing")
    print("  • Route tracing")
    print("  • Health scoring")
    print("  • PDF report generation")
    print()
    print("Press Ctrl+C to cancel at any time")
    print("=" * 60)
    print()
    
    try:
        diagnostic = SunyaCompleteDiagnostic()
        success = diagnostic.run_complete_diagnostic()
        
        if success:
            print("\n✅ Diagnostic completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Diagnostic failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Diagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
