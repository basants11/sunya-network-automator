#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA High-Performance Network Diagnostic System v3.0
Maximum Speed & Efficiency Optimized Version

Optimizations:
- Parallel execution for all network tests
- Headless browser mode for speed tests
- Adaptive test intervals based on network stability
- Static data caching at startup
- In-memory logging with periodic flush
- Incremental WinMTR/PathPing (limited hops)
- Background PDF generation
- Process cleanup and session reuse
- Priority-based target checking
- Lightweight screenshot system

Author: SUNYA Networking
Version: 3.0.0
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
import queue
import tempfile
import re
import shutil
import psutil
import gc
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import deque
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Third-party imports with fallbacks
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

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

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for performance
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_pdf import PdfPages
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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

# ============================================================================
# HIGH-PERFORMANCE LOGGING SYSTEM
# ============================================================================

class InMemoryLogHandler(logging.Handler):
    """In-memory log handler that flushes to file periodically"""
    def __init__(self, flush_interval: int = 30):
        super().__init__()
        self.log_buffer = deque(maxlen=10000)  # Keep last 10k messages
        self.flush_interval = flush_interval
        self.last_flush = time.time()
        self.lock = threading.Lock()
        
    def emit(self, record):
        with self.lock:
            msg = self.format(record)
            self.log_buffer.append({
                'timestamp': datetime.datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'message': msg
            })
            
            # Flush if interval passed
            if time.time() - self.last_flush > self.flush_interval:
                self.flush()
    
    def flush(self, filepath: str = None):
        """Flush logs to file"""
        with self.lock:
            if filepath and len(self.log_buffer) > 0:
                try:
                    with open(filepath, 'a', encoding='utf-8') as f:
                        for entry in self.log_buffer:
                            f.write(f"{entry['timestamp']} - {entry['level']} - {entry['message']}\n")
                    self.log_buffer.clear()
                    self.last_flush = time.time()
                except Exception as e:
                    print(f"Log flush error: {e}")

class UnicodeStreamHandler(logging.StreamHandler):
    """Stream handler that handles Unicode encoding properly on Windows"""
    def emit(self, record):
        try:
            msg = self.format(record)
            msg = msg.replace('\u2713', '[OK]').replace('\u2717', '[FAIL]').replace('\u26a0', '[WARN]')
            msg = msg.replace('━', '-').replace('═', '=').replace('╔', '+').replace('╗', '+')
            msg = msg.replace('╚', '+').replace('╝', '+').replace('║', '|').replace('●', '*')
            self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[UnicodeStreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA CLASSES
# ============================================================================

class NetworkStatus(Enum):
    STABLE = "stable"
    DEGRADED = "degraded"
    UNSTABLE = "unstable"
    UNKNOWN = "unknown"

@dataclass
class AdapterInfo:
    """Network adapter information - cached at startup"""
    name: str = ""
    manufacturer: str = ""
    description: str = ""
    mac_address: str = ""
    driver_version: str = ""
    driver_date: str = ""
    driver_provider: str = ""
    link_speed: int = 0
    supported_speeds: List[int] = field(default_factory=list)
    duplex_mode: str = ""
    interface_type: str = ""
    default_gateway: str = ""
    dns_servers: List[str] = field(default_factory=list)
    ip_address: str = ""
    subnet_mask: str = ""
    is_gigabit_capable: bool = False
    is_negotiating_gigabit: bool = False
    cable_limitation_flag: bool = False
    driver_outdated_flag: bool = False
    driver_age_days: int = 0
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

@dataclass
class SpeedTestResult:
    """Speed test results"""
    source: str = ""
    timestamp: str = ""
    download_speed: float = 0.0  # Mbps
    upload_speed: float = 0.0  # Mbps
    latency: float = 0.0  # ms
    jitter: float = 0.0
    server_name: str = ""
    server_location: str = ""
    success: bool = False
    error_message: str = ""
    screenshot_path: str = ""

@dataclass
class PingResult:
    """Ping test results"""
    target: str = ""
    target_type: str = ""  # 'isp', 'dns', 'public'
    timestamp: str = ""
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    avg_latency: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0
    jitter: float = 0.0
    success: bool = False
    error_message: str = ""

@dataclass
class PathPingResult:
    """PathPing/WinMTR results"""
    target: str = ""
    timestamp: str = ""
    total_hops: int = 0
    hops_analyzed: int = 0
    worst_latency_hop: int = 0
    worst_latency_value: float = 0.0
    avg_hop_latency: float = 0.0
    packet_loss_at_hop: Dict[int, float] = field(default_factory=dict)
    success: bool = False
    error_message: str = ""
    report_path: str = ""

@dataclass
class DNSResult:
    """DNS resolution results"""
    hostname: str = ""
    resolved_ips: List[str] = field(default_factory=list)
    resolution_time_ms: float = 0.0
    dns_server_used: str = ""
    success: bool = False
    timestamp: str = ""

@dataclass
class NetworkHealthScore:
    """Network health scoring"""
    overall_score: int = 0
    grade: str = "Unknown"
    speed_score: int = 0
    latency_score: int = 0
    loss_score: int = 0
    stability_score: int = 0
    hardware_score: int = 0
    recommendations: List[str] = field(default_factory=list)
    isp_complaint_summary: str = ""

@dataclass
class TestCycleResult:
    """Results from one complete test cycle"""
    cycle_id: int = 0
    timestamp: str = ""
    ping_results: List[PingResult] = field(default_factory=list)
    pathping_results: List[PathPingResult] = field(default_factory=list)
    dns_results: List[DNSResult] = field(default_factory=list)
    speed_results: List[SpeedTestResult] = field(default_factory=list)
    network_status: NetworkStatus = NetworkStatus.UNKNOWN
    alerts_triggered: List[str] = field(default_factory=list)

# ============================================================================
# HIGH-PERFORMANCE NETWORK DIAGNOSTIC ENGINE
# ============================================================================

class SunyaHighPerformanceDiagnostic:
    """
    High-performance network diagnostic engine with parallel execution,
    adaptive intervals, and optimized resource usage.
    """
    
    # Target priorities - ISP/DNS first, then public sites
    PRIORITY_TARGETS = {
        'isp_gateway': ['192.168.100.1', '192.168.1.1', '192.168.0.1', '10.0.0.1'],
        'dns_servers': ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1'],
        'public_sites': ['google.com', 'cloudflare.com', 'facebook.com', 'x.com', 'instagram.com']
    }
    
    DNS_HOSTNAMES = ['google.com', 'cloudflare.com', 'facebook.com', 'amazon.com']
    
    def __init__(self, 
                 max_workers: int = 8,
                 adaptive_interval: bool = True,
                 stable_interval: float = 10.0,
                 unstable_interval: float = 2.0,
                 log_flush_interval: int = 30,
                 screenshot_on_alert_only: bool = True,
                 max_pathping_hops: int = 20,
                 skip_speed_test_if_stable: bool = True):
        """
        Initialize high-performance diagnostic engine.
        
        Args:
            max_workers: Maximum parallel threads
            adaptive_interval: Enable adaptive test intervals
            stable_interval: Seconds between tests when stable
            unstable_interval: Seconds between tests when unstable
            log_flush_interval: Seconds between log flushes
            screenshot_on_alert_only: Only capture screenshots on alerts
            max_pathping_hops: Maximum hops for pathping (not 60)
            skip_speed_test_if_stable: Skip speed test if network is stable
        """
        self.max_workers = max_workers
        self.adaptive_interval = adaptive_interval
        self.stable_interval = stable_interval
        self.unstable_interval = unstable_interval
        self.log_flush_interval = log_flush_interval
        self.screenshot_on_alert_only = screenshot_on_alert_only
        self.max_pathping_hops = max_pathping_hops
        self.skip_speed_test_if_stable = skip_speed_test_if_stable
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.lock = threading.RLock()
        
        # Results storage
        self.cycle_results: deque = deque(maxlen=100)  # Keep last 100 cycles
        self.current_cycle = 0
        
        # Cached static data
        self.cached_adapter_info: Optional[AdapterInfo] = None
        self.cached_system_info: Dict = {}
        self.public_ip: str = ""
        
        # Network state tracking
        self.network_status = NetworkStatus.UNKNOWN
        self.status_history: deque = deque(maxlen=10)  # Last 10 status readings
        self.consecutive_stable_cycles = 0
        
        # Logging
        self.in_memory_handler = InMemoryLogHandler(log_flush_interval)
        self.in_memory_handler.setLevel(logging.INFO)
        logger.addHandler(self.in_memory_handler)
        
        # Folders
        self.base_folder = ""
        self.folders = {}
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Browser drivers (reused)
        self.chrome_driver = None
        
        # Command session reuse
        self.cmd_sessions = {}
        
        # Performance metrics
        self.start_time = None
        self.total_cycles_completed = 0
        
    # ========================================================================
    # INITIALIZATION & CLEANUP
    # ========================================================================
    
    def cleanup_stale_processes(self):
        """Kill stale Chrome, CMD, PowerShell processes at startup"""
        logger.info("Cleaning up stale processes...")
        killed = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                # Kill stale Chrome drivers
                if 'chromedriver' in name or 'chrome' in name:
                    if proc.info['pid'] != os.getpid():
                        psutil.Process(proc.info['pid']).terminate()
                        killed.append(f"chrome ({proc.info['pid']})")
                        time.sleep(0.1)
                # Kill excess CMD/PowerShell (keep current)
                elif name in ['cmd.exe', 'powershell.exe']:
                    if proc.info['pid'] != os.getpid():
                        # Only kill if it looks like a diagnostic process
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'ping' in cmdline.lower() or 'tracert' in cmdline.lower():
                            psutil.Process(proc.info['pid']).terminate()
                            killed.append(f"{name} ({proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed:
            logger.info(f"Terminated {len(killed)} stale processes")
        gc.collect()  # Force garbage collection
    
    def create_folder_structure(self) -> bool:
        """Create optimized folder structure"""
        try:
            desktop = Path.home() / "Desktop"
            self.base_folder = desktop / f"SUNYA_HP_Diagnostic_{self.timestamp}"
            self.base_folder.mkdir(parents=True, exist_ok=True)
            
            # Minimal folder structure
            self.folders = {
                'Logs': self.base_folder / 'Logs',
                'Screenshots': self.base_folder / 'Screenshots',
                'Reports': self.base_folder / 'Reports',
                'Data': self.base_folder / 'Data',
            }
            
            for folder in self.folders.values():
                folder.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Output folder: {self.base_folder}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create folders: {e}")
            return False
    
    def cache_static_data(self):
        """Fetch adapter info, IP, gateway, DNS once at startup"""
        logger.info("Caching static network information...")
        
        # Cache adapter info
        self.cached_adapter_info = self._fetch_adapter_info()
        
        # Cache system info
        self.cached_system_info = {
            'hostname': socket.gethostname(),
            'platform': f"{platform.system()} {platform.release()}",
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / (1024**3)
        }
        
        # Cache public IP
        try:
            import urllib.request
            self.public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()
        except:
            self.public_ip = "Unknown"
        
        logger.info(f"Cached adapter: {self.cached_adapter_info.name}")
        logger.info(f"Cached gateway: {self.cached_adapter_info.default_gateway}")
        logger.info(f"Cached DNS: {', '.join(self.cached_adapter_info.dns_servers[:2])}")
    
    def _fetch_adapter_info(self) -> AdapterInfo:
        """Fetch network adapter information (cached)"""
        adapter = AdapterInfo()
        
        try:
            if WMI_AVAILABLE:
                c = wmi.WMI()
                
                # Get active network adapter
                for nic in c.Win32_NetworkAdapter(PhysicalAdapter=True, NetEnabled=True):
                    adapter.name = nic.Name
                    adapter.manufacturer = nic.Manufacturer
                    adapter.description = nic.Description
                    adapter.mac_address = nic.MACAddress or ""
                    
                    # Get driver info
                    try:
                        drivers = c.Win32_PnPSignedDriver(DeviceID=nic.PNPDeviceID)
                        if drivers:
                            driver = drivers[0]
                            adapter.driver_version = driver.DriverVersion or ""
                            adapter.driver_date = driver.DriverDate or ""
                            adapter.driver_provider = driver.DriverProviderName or ""
                    except:
                        pass
                    
                    # Get link speed
                    if nic.Speed:
                        adapter.link_speed = int(nic.Speed) // 1000000  # Convert to Mbps
                        adapter.is_gigabit_capable = adapter.link_speed >= 1000
                    
                    # Check configuration
                    configs = c.Win32_NetworkAdapterConfiguration(Index=nic.Index, IPEnabled=True)
                    if configs:
                        config = configs[0]
                        adapter.ip_address = config.IPAddress[0] if config.IPAddress else ""
                        adapter.subnet_mask = config.IPSubnet[0] if config.IPSubnet else ""
                        adapter.default_gateway = config.DefaultIPGateway[0] if config.DefaultIPGateway else ""
                        adapter.dns_servers = list(config.DNSServerSearchOrder or [])
                    
                    break  # Only get first active adapter
                    
        except Exception as e:
            logger.warning(f"WMI adapter fetch failed: {e}")
            # Fallback to psutil
            try:
                stats = psutil.net_if_stats()
                io_counters = psutil.net_io_counters(pernic=True)
                
                for iface_name, iface_stats in stats.items():
                    if iface_stats.isup and 'loop' not in iface_name.lower():
                        adapter.name = iface_name
                        adapter.link_speed = iface_stats.speed // 1000000 if iface_stats.speed else 0
                        adapter.is_gigabit_capable = adapter.link_speed >= 1000
                        break
                        
            except Exception as e2:
                logger.error(f"Fallback adapter fetch failed: {e2}")
        
        return adapter
    
    # ========================================================================
    # PARALLEL TEST EXECUTION
    # ========================================================================
    
    def run_parallel_tests(self, cycle_id: int) -> TestCycleResult:
        """
        Run all network tests in parallel threads.
        Returns aggregated results for the cycle.
        """
        result = TestCycleResult(cycle_id=cycle_id, timestamp=datetime.datetime.now().isoformat())
        futures = []
        
        with self.executor as executor:
            # Submit ping tests (parallel)
            ping_targets = self._get_prioritized_targets()
            for target, target_type in ping_targets:
                future = executor.submit(self._ping_target, target, target_type)
                futures.append(('ping', future))
            
            # Submit DNS tests (parallel)
            for hostname in self.DNS_HOSTNAMES:
                future = executor.submit(self._dns_lookup, hostname)
                futures.append(('dns', future))
            
            # Submit PathPing/Tracert (parallel, limited hops)
            for target in ['8.8.8.8', 'google.com', 'cloudflare.com']:
                future = executor.submit(self._pathping_target, target)
                futures.append(('pathping', future))
            
            # Collect results
            for test_type, future in futures:
                try:
                    test_result = future.result(timeout=60)
                    if test_type == 'ping':
                        result.ping_results.append(test_result)
                    elif test_type == 'dns':
                        result.dns_results.append(test_result)
                    elif test_type == 'pathping':
                        result.pathping_results.append(test_result)
                except Exception as e:
                    logger.error(f"Test failed: {e}")
        
        return result
    
    def _get_prioritized_targets(self) -> List[Tuple[str, str]]:
        """Get targets in priority order: ISP > DNS > Public"""
        targets = []
        
        # ISP Gateway (highest priority)
        if self.cached_adapter_info and self.cached_adapter_info.default_gateway:
            targets.append((self.cached_adapter_info.default_gateway, 'isp'))
        targets.extend([(ip, 'isp') for ip in self.PRIORITY_TARGETS['isp_gateway']])
        
        # DNS Servers
        if self.cached_adapter_info and self.cached_adapter_info.dns_servers:
            for dns in self.cached_adapter_info.dns_servers[:2]:
                targets.append((dns, 'dns'))
        targets.extend([(ip, 'dns') for ip in self.PRIORITY_TARGETS['dns_servers']])
        
        # Public sites
        targets.extend([(site, 'public') for site in self.PRIORITY_TARGETS['public_sites']])
        
        return targets
    
    def _ping_target(self, target: str, target_type: str) -> PingResult:
        """Ping a single target (thread-safe)"""
        result = PingResult(target=target, target_type=target_type, timestamp=datetime.datetime.now().isoformat())
        
        try:
            if PING3_AVAILABLE:
                # Use ping3 library (faster)
                latencies = []
                for _ in range(10):
                    latency = ping3.ping(target, timeout=2)
                    if latency is not None:
                        latencies.append(latency * 1000)  # Convert to ms
                    time.sleep(0.1)
                
                if latencies:
                    result.packets_sent = 10
                    result.packets_received = len(latencies)
                    result.packet_loss_percent = (1 - len(latencies)/10) * 100
                    result.avg_latency = sum(latencies) / len(latencies)
                    result.min_latency = min(latencies)
                    result.max_latency = max(latencies)
                    result.jitter = max(latencies) - min(latencies) if len(latencies) > 1 else 0
                    result.success = True
                else:
                    result.packet_loss_percent = 100
                    
            else:
                # Use system ping
                cmd = f'ping -n 10 -w 2000 {target}'
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                output = proc.stdout
                
                # Parse results
                loss_match = re.search(r'(\d+)% loss', output)
                if loss_match:
                    result.packet_loss_percent = float(loss_match.group(1))
                
                avg_match = re.search(r'Average\s*=\s*(\d+)ms', output)
                if avg_match:
                    result.avg_latency = float(avg_match.group(1))
                
                min_match = re.search(r'Minimum\s*=\s*(\d+)ms', output)
                if min_match:
                    result.min_latency = float(min_match.group(1))
                
                max_match = re.search(r'Maximum\s*=\s*(\d+)ms', output)
                if max_match:
                    result.max_latency = float(max_match.group(1))
                
                result.packets_sent = 10
                result.packets_received = int(10 * (1 - result.packet_loss_percent/100))
                result.success = result.packets_received > 0
                
        except Exception as e:
            result.error_message = str(e)
            result.packet_loss_percent = 100
        
        return result
    
    def _dns_lookup(self, hostname: str) -> DNSResult:
        """Perform DNS lookup (thread-safe)"""
        result = DNSResult(hostname=hostname, timestamp=datetime.datetime.now().isoformat())
        
        try:
            import dns.resolver
            start_time = time.time()
            
            resolver = dns.resolver.Resolver()
            if self.cached_adapter_info and self.cached_adapter_info.dns_servers:
                resolver.nameservers = self.cached_adapter_info.dns_servers[:2]
            
            answers = resolver.resolve(hostname, 'A')
            result.resolved_ips = [str(rdata) for rdata in answers]
            result.resolution_time_ms = (time.time() - start_time) * 1000
            result.dns_server_used = resolver.nameservers[0] if resolver.nameservers else ""
            result.success = True
            
        except ImportError:
            # Fallback to socket
            try:
                start_time = time.time()
                ip = socket.gethostbyname(hostname)
                result.resolved_ips = [ip]
                result.resolution_time_ms = (time.time() - start_time) * 1000
                result.success = True
            except Exception as e:
                result.error_message = str(e)
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    def _pathping_target(self, target: str) -> PathPingResult:
        """Run incremental PathPing/Tracert with limited hops"""
        result = PathPingResult(target=target, timestamp=datetime.datetime.now().isoformat())
        
        try:
            # Use tracert with limited hops (not full 30-60)
            cmd = f'tracert -h {self.max_pathping_hops} -w 2000 {target}'
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = proc.stdout
            
            # Parse hops
            hops = []
            worst_latency = 0
            worst_hop = 0
            
            for line in output.split('\n'):
                # Match hop lines: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
                match = re.match(r'\s*(\d+)\s+(\d+)\s*ms\s+(\d+)\s*ms\s+(\d+)\s*ms\s+(.+)', line)
                if match:
                    hop_num = int(match.group(1))
                    latencies = [int(match.group(2)), int(match.group(3)), int(match.group(4))]
                    avg_latency = sum(latencies) / 3
                    
                    hops.append({
                        'hop': hop_num,
                        'latency': avg_latency,
                        'host': match.group(5).strip()
                    })
                    
                    if avg_latency > worst_latency:
                        worst_latency = avg_latency
                        worst_hop = hop_num
            
            result.total_hops = len(hops)
            result.hops_analyzed = len(hops)
            result.worst_latency_hop = worst_hop
            result.worst_latency_value = worst_latency
            result.avg_hop_latency = sum(h['latency'] for h in hops) / len(hops) if hops else 0
            result.success = len(hops) > 0
            
            # Save output
            report_file = self.folders['Data'] / f'pathping_{target.replace(".", "_")}.txt'
            with open(report_file, 'w') as f:
                f.write(output)
            result.report_path = str(report_file)
            
        except Exception as e:
            result.error_message = str(e)
        
        return result
    
    # ========================================================================
    # ADAPTIVE TEST INTERVALS
    # ========================================================================
    
    def analyze_network_status(self, cycle_result: TestCycleResult) -> NetworkStatus:
        """
        Analyze network status based on test results.
        Returns: STABLE, DEGRADED, or UNSTABLE
        """
        if not cycle_result.ping_results:
            return NetworkStatus.UNKNOWN
        
        # Calculate metrics
        successful_pings = [p for p in cycle_result.ping_results if p.success]
        if not successful_pings:
            return NetworkStatus.UNSTABLE
        
        avg_loss = sum(p.packet_loss_percent for p in successful_pings) / len(successful_pings)
        avg_latency = sum(p.avg_latency for p in successful_pings) / len(successful_pings)
        
        # Determine status
        if avg_loss > 2 or avg_latency > 100:
            status = NetworkStatus.UNSTABLE
        elif avg_loss > 0.5 or avg_latency > 50:
            status = NetworkStatus.DEGRADED
        else:
            status = NetworkStatus.STABLE
        
        # Track history
        self.status_history.append(status)
        
        # Track consecutive stable cycles
        if status == NetworkStatus.STABLE:
            self.consecutive_stable_cycles += 1
        else:
            self.consecutive_stable_cycles = 0
        
        return status
    
    def get_adaptive_interval(self) -> float:
        """Get test interval based on network stability"""
        if not self.adaptive_interval:
            return self.stable_interval
        
        # If network is unstable, use shorter interval
        if self.network_status == NetworkStatus.UNSTABLE:
            return self.unstable_interval
        elif self.network_status == NetworkStatus.DEGRADED:
            return (self.stable_interval + self.unstable_interval) / 2
        
        # Stable network - gradually increase interval
        if self.consecutive_stable_cycles > 5:
            return min(self.stable_interval * 1.5, 30)  # Max 30s
        
        return self.stable_interval
    
    # ========================================================================
    # SPEED TESTS (HEADLESS BROWSER)
    # ========================================================================
    
    def run_speed_tests(self) -> List[SpeedTestResult]:
        """Run speed tests using headless browser mode"""
        results = []
        
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available, using CLI speedtest")
            return self._run_speedtest_cli()
        
        # Check if we should skip (network stable for multiple cycles)
        if self.skip_speed_test_if_stable and self.consecutive_stable_cycles > 3:
            logger.info("Network stable - skipping speed test this cycle")
            return results
        
        logger.info("Running headless speed tests...")
        
        # Setup headless Chrome (single driver, two tabs)
        try:
            driver = self._get_headless_driver()
            if not driver:
                return self._run_speedtest_cli()
            
            # Run fast.com test
            fast_result = self._run_fast_com_headless(driver)
            if fast_result:
                results.append(fast_result)
            
            # Run speedtest.net test  
            speedtest_result = self._run_speedtest_net_headless(driver)
            if speedtest_result:
                results.append(speedtest_result)
            
            # Cleanup driver
            try:
                driver.quit()
            except:
                pass
            
        except Exception as e:
            logger.error(f"Headless speed test failed: {e}")
            # Fallback to CLI
            results.extend(self._run_speedtest_cli())
        
        return results
    
    def _get_headless_driver(self) -> Optional[Any]:
        """Get headless Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                driver = webdriver.Chrome(options=chrome_options)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create headless driver: {e}")
            return None
    
    def _run_fast_com_headless(self, driver: Any) -> Optional[SpeedTestResult]:
        """Run fast.com speed test in headless mode"""
        result = SpeedTestResult(source="fast.com", timestamp=datetime.datetime.now().isoformat())
        
        try:
            logger.info("Testing fast.com (headless)...")
            driver.get("https://fast.com")
            
            # Wait for test to complete (faster in headless)
            time.sleep(25)
            
            # Try to show more details
            try:
                show_more = driver.find_element(By.ID, "show-more-details-link")
                show_more.click()
                time.sleep(5)
            except:
                pass
            
            # Extract results
            try:
                download_elem = driver.find_element(By.ID, "speed-value")
                result.download_speed = float(download_elem.text) if download_elem.text else 0
            except:
                pass
            
            try:
                upload_elem = driver.find_element(By.ID, "upload-value")
                result.upload_speed = float(upload_elem.text) if upload_elem.text else 0
            except:
                pass
            
            result.success = result.download_speed > 0
            
            if result.success:
                logger.info(f"Fast.com: {result.download_speed:.1f} Mbps down, {result.upload_speed:.1f} Mbps up")
            
            return result
            
        except Exception as e:
            logger.error(f"Fast.com test failed: {e}")
            result.error_message = str(e)
            return result
    
    def _run_speedtest_net_headless(self, driver: Any) -> Optional[SpeedTestResult]:
        """Run speedtest.net speed test in headless mode"""
        result = SpeedTestResult(source="speedtest.net", timestamp=datetime.datetime.now().isoformat())
        
        try:
            logger.info("Testing speedtest.net (headless)...")
            driver.get("https://www.speedtest.net")
            
            # Click go button
            go_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "js-start-test"))
            )
            go_button.click()
            
            # Wait for test (shorter in headless)
            time.sleep(45)
            
            # Extract results
            try:
                download_elem = driver.find_element(By.CLASS_NAME, "download-speed")
                result.download_speed = float(download_elem.text) if download_elem.text else 0
            except:
                pass
            
            try:
                upload_elem = driver.find_element(By.CLASS_NAME, "upload-speed")
                result.upload_speed = float(upload_elem.text) if upload_elem.text else 0
            except:
                pass
            
            result.success = result.download_speed > 0
            
            if result.success:
                logger.info(f"Speedtest.net: {result.download_speed:.1f} Mbps down, {result.upload_speed:.1f} Mbps up")
            
            return result
            
        except Exception as e:
            logger.error(f"Speedtest.net test failed: {e}")
            result.error_message = str(e)
            return result
    
    def _run_speedtest_cli(self) -> List[SpeedTestResult]:
        """Run CLI speedtest as fallback"""
        results = []
        
        if SPEEDTEST_AVAILABLE:
            try:
                logger.info("Running CLI speedtest...")
                st = speedtest.Speedtest()
                st.get_best_server()
                
                download_speed = st.download() / 1_000_000  # Convert to Mbps
                upload_speed = st.upload() / 1_000_000
                
                result = SpeedTestResult(
                    source="speedtest-cli",
                    timestamp=datetime.datetime.now().isoformat(),
                    download_speed=download_speed,
                    upload_speed=upload_speed,
                    server_name=st.best['host'],
                    server_location=st.best['name'],
                    success=True
                )
                results.append(result)
                logger.info(f"CLI Speedtest: {download_speed:.1f} Mbps down, {upload_speed:.1f} Mbps up")
                
            except Exception as e:
                logger.error(f"CLI speedtest failed: {e}")
        
        return results
    
    # ========================================================================
    # SCREENSHOT SYSTEM (ALERT-ONLY)
    # ========================================================================
    
    def capture_screenshot_if_alert(self, alerts: List[str], cycle_id: int):
        """Capture screenshot only if alerts triggered"""
        if not self.screenshot_on_alert_only:
            return
        
        if not alerts:
            return
        
        if not PYAUTOGUI_AVAILABLE:
            return
        
        try:
            screenshot_path = self.folders['Screenshots'] / f'alert_cycle_{cycle_id}_{int(time.time())}.png'
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            logger.info(f"Alert screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
    
    # ========================================================================
    # BACKGROUND PDF GENERATION
    # ========================================================================
    
    def generate_pdf_background(self, final: bool = False) -> threading.Thread:
        """Start PDF generation in background thread"""
        thread = threading.Thread(target=self._generate_pdf_worker, args=(final,))
        thread.daemon = True
        thread.start()
        return thread
    
    def _generate_pdf_worker(self, final: bool = False):
        """Worker function for background PDF generation"""
        try:
            if REPORTLAB_AVAILABLE:
                self._generate_reportlab_pdf(final)
            else:
                self._generate_simple_pdf(final)
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
    
    def _generate_reportlab_pdf(self, final: bool = False) -> str:
        """Generate comprehensive PDF report"""
        pdf_path = self.folders['Reports'] / f'SUNYA_HP_Report_{self.timestamp}.pdf'
        
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30
        )
        story.append(Paragraph("SUNYA High-Performance Network Diagnostic Report", title_style))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_data = [
            ['Report Generated:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Cycles Completed:', str(self.total_cycles_completed)],
            ['Duration:', f"{(time.time() - self.start_time)/60:.1f} minutes" if self.start_time else "N/A"],
            ['Network Status:', self.network_status.value],
            ['Public IP:', self.public_ip],
        ]
        
        summary_table = Table(summary_data, colWidths=[150, 300])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Adapter Info (cached)
        story.append(Paragraph("Network Adapter Information", styles['Heading2']))
        if self.cached_adapter_info:
            adapter_data = [
                ['Property', 'Value'],
                ['Name', self.cached_adapter_info.name],
                ['IP Address', self.cached_adapter_info.ip_address],
                ['Gateway', self.cached_adapter_info.default_gateway],
                ['DNS Servers', ', '.join(self.cached_adapter_info.dns_servers[:3])],
                ['Link Speed', f"{self.cached_adapter_info.link_speed} Mbps"],
                ['MAC Address', self.cached_adapter_info.mac_address],
            ]
            
            adapter_table = Table(adapter_data, colWidths=[150, 300])
            adapter_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            story.append(adapter_table)
        
        story.append(PageBreak())
        
        # Recent Results
        story.append(Paragraph("Recent Test Results", styles['Heading2']))
        
        if self.cycle_results:
            recent = list(self.cycle_results)[-5:]  # Last 5 cycles
            
            for cycle in recent:
                story.append(Paragraph(f"Cycle {cycle.cycle_id} - {cycle.timestamp[:19]}", styles['Heading3']))
                
                # Ping summary
                if cycle.ping_results:
                    ping_data = [['Target', 'Type', 'Avg Latency', 'Loss %']]
                    for ping in cycle.ping_results[:5]:  # Top 5
                        ping_data.append([
                            ping.target[:20],
                            ping.target_type,
                            f"{ping.avg_latency:.1f}ms",
                            f"{ping.packet_loss_percent:.1f}%"
                        ])
                    
                    ping_table = Table(ping_data, colWidths=[120, 60, 80, 60])
                    ping_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ]))
                    story.append(ping_table)
                    story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF report generated: {pdf_path}")
        
        return str(pdf_path)
    
    def _generate_simple_pdf(self, final: bool = False) -> str:
        """Generate simple text-based report fallback"""
        report_path = self.folders['Reports'] / f'SUNYA_HP_Report_{self.timestamp}.txt'
        
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("SUNYA High-Performance Network Diagnostic Report\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Cycles: {self.total_cycles_completed}\n")
            f.write(f"Status: {self.network_status.value}\n\n")
            
            f.write("Network Adapter:\n")
            if self.cached_adapter_info:
                f.write(f"  Name: {self.cached_adapter_info.name}\n")
                f.write(f"  IP: {self.cached_adapter_info.ip_address}\n")
                f.write(f"  Gateway: {self.cached_adapter_info.default_gateway}\n")
            
            f.write("\nRecent Results:\n")
            for cycle in list(self.cycle_results)[-3:]:
                f.write(f"\nCycle {cycle.cycle_id}:\n")
                for ping in cycle.ping_results[:3]:
                    f.write(f"  {ping.target}: {ping.avg_latency:.1f}ms, {ping.packet_loss_percent:.1f}% loss\n")
        
        logger.info(f"Text report generated: {report_path}")
        return str(report_path)
    
    # ========================================================================
    # DATA EXPORT (JSON/CSV)
    # ========================================================================
    
    def export_cycle_data(self, cycle_result: TestCycleResult):
        """Export cycle data to JSON and CSV"""
        try:
            # Export to JSON (append mode for efficiency)
            json_path = self.folders['Data'] / 'all_cycles.json'
            
            data = {
                'cycle_id': cycle_result.cycle_id,
                'timestamp': cycle_result.timestamp,
                'network_status': cycle_result.network_status.value,
                'ping_results': [asdict(p) for p in cycle_result.ping_results],
                'dns_results': [asdict(d) for d in cycle_result.dns_results],
                'pathping_results': [asdict(pp) for pp in cycle_result.pathping_results],
            }
            
            # Append to JSON file
            mode = 'a' if json_path.exists() else 'w'
            with open(json_path, mode) as f:
                if mode == 'w':
                    f.write('[\n')
                else:
                    # Remove last bracket and add comma
                    f.seek(0, 2)  # End of file
                    pos = f.tell()
                    f.seek(pos - 2)
                    f.write(',\n')
                
                f.write(json.dumps(data, indent=2))
                f.write('\n]')
            
            # Export ping results to CSV
            csv_path = self.folders['Data'] / 'ping_results.csv'
            csv_exists = csv_path.exists()
            
            with open(csv_path, 'a', newline='') as f:
                import csv
                writer = csv.writer(f)
                
                if not csv_exists:
                    writer.writerow(['cycle_id', 'timestamp', 'target', 'type', 'avg_latency', 'packet_loss'])
                
                for ping in cycle_result.ping_results:
                    writer.writerow([
                        cycle_result.cycle_id,
                        cycle_result.timestamp,
                        ping.target,
                        ping.target_type,
                        f"{ping.avg_latency:.2f}",
                        f"{ping.packet_loss_percent:.2f}"
                    ])
                    
        except Exception as e:
            logger.error(f"Data export failed: {e}")
    
    # ========================================================================
    # MAIN MONITORING LOOP
    # ========================================================================
    
    def run_monitoring_cycle(self) -> TestCycleResult:
        """Run one complete monitoring cycle"""
        self.current_cycle += 1
        cycle_id = self.current_cycle
        
        logger.info(f"=== Starting Cycle {cycle_id} ===")
        
        # Run parallel network tests
        cycle_result = self.run_parallel_tests(cycle_id)
        
        # Analyze network status
        self.network_status = self.analyze_network_status(cycle_result)
        cycle_result.network_status = self.network_status
        
        logger.info(f"Network status: {self.network_status.value}")
        
        # Run speed tests (if needed)
        speed_results = self.run_speed_tests()
        cycle_result.speed_results = speed_results
        
        # Check for alerts
        alerts = self._check_alerts(cycle_result)
        cycle_result.alerts_triggered = alerts
        
        if alerts:
            logger.warning(f"Alerts triggered: {alerts}")
            self.capture_screenshot_if_alert(alerts, cycle_id)
        
        # Store results
        self.cycle_results.append(cycle_result)
        
        # Export data
        self.export_cycle_data(cycle_result)
        
        # Flush logs
        log_path = self.folders['Logs'] / 'diagnostic.log'
        self.in_memory_handler.flush(str(log_path))
        
        self.total_cycles_completed += 1
        
        logger.info(f"=== Cycle {cycle_id} Complete ===")
        
        return cycle_result
    
    def _check_alerts(self, cycle_result: TestCycleResult) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        # High latency alert
        high_latency_pings = [p for p in cycle_result.ping_results if p.avg_latency > 100]
        if high_latency_pings:
            alerts.append(f"High latency detected: {len(high_latency_pings)} targets")
        
        # Packet loss alert
        loss_pings = [p for p in cycle_result.ping_results if p.packet_loss_percent > 5]
        if loss_pings:
            alerts.append(f"Packet loss detected: {len(loss_pings)} targets")
        
        # DNS failure alert
        failed_dns = [d for d in cycle_result.dns_results if not d.success]
        if failed_dns:
            alerts.append(f"DNS resolution failures: {len(failed_dns)} hosts")
        
        # Path issues
        failed_paths = [pp for pp in cycle_result.pathping_results if not pp.success]
        if failed_paths:
            alerts.append(f"Path tracing failures: {len(failed_paths)} targets")
        
        return alerts
    
    def run_continuous_monitoring(self, max_cycles: int = None, duration_minutes: float = None):
        """
        Run continuous monitoring with adaptive intervals.
        
        Args:
            max_cycles: Maximum number of cycles (None = infinite)
            duration_minutes: Maximum duration in minutes (None = infinite)
        """
        logger.info("=" * 60)
        logger.info("SUNYA HIGH-PERFORMANCE NETWORK DIAGNOSTIC")
        logger.info("=" * 60)
        logger.info(f"Max Workers: {self.max_workers}")
        logger.info(f"Adaptive Intervals: {self.adaptive_interval}")
        logger.info(f"Max PathPing Hops: {self.max_pathping_hops}")
        logger.info(f"Screenshot on Alert Only: {self.screenshot_on_alert_only}")
        logger.info("=" * 60)
        
        try:
            # Initialize
            self.cleanup_stale_processes()
            
            if not self.create_folder_structure():
                logger.error("Failed to create folder structure")
                return
            
            self.cache_static_data()
            
            self.start_time = time.time()
            self.running = True
            
            # Start background PDF generation thread (updates periodically)
            pdf_thread = None
            last_pdf_update = 0
            
            cycle_count = 0
            
            while self.running:
                # Check duration limit
                if duration_minutes:
                    elapsed = (time.time() - self.start_time) / 60
                    if elapsed >= duration_minutes:
                        logger.info(f"Duration limit reached ({duration_minutes} min)")
                        break
                
                # Check cycle limit
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"Cycle limit reached ({max_cycles})")
                    break
                
                # Run monitoring cycle
                cycle_start = time.time()
                self.run_monitoring_cycle()
                cycle_count += 1
                
                # Update PDF periodically (every 5 cycles)
                if cycle_count % 5 == 0:
                    if pdf_thread is None or not pdf_thread.is_alive():
                        pdf_thread = self.generate_pdf_background(final=False)
                
                # Calculate adaptive interval
                interval = self.get_adaptive_interval()
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, interval - cycle_duration)
                
                if sleep_time > 0:
                    logger.info(f"Sleeping for {sleep_time:.1f}s (adaptive interval)")
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        logger.info("Stopping monitoring...")
        self.running = False
        
        # Shutdown executor
        try:
            self.executor.shutdown(wait=False)
        except:
            pass
        
        # Generate final PDF
        logger.info("Generating final report...")
        self.generate_pdf_background(final=True)
        time.sleep(2)  # Give PDF thread time to start
        
        # Final log flush
        log_path = self.folders['Logs'] / 'diagnostic.log'
        self.in_memory_handler.flush(str(log_path))
        
        # Cleanup processes
        self.cleanup_stale_processes()
        
        # Summary
        logger.info("=" * 60)
        logger.info("MONITORING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total Cycles: {self.total_cycles_completed}")
        logger.info(f"Duration: {(time.time() - self.start_time)/60:.1f} minutes")
        logger.info(f"Output: {self.base_folder}")
        logger.info("=" * 60)
        
        # Open folder
        try:
            os.startfile(self.base_folder)
        except:
            pass

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point with argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SUNYA High-Performance Network Diagnostic')
    parser.add_argument('--cycles', type=int, default=None, help='Maximum number of cycles')
    parser.add_argument('--duration', type=float, default=None, help='Maximum duration in minutes')
    parser.add_argument('--workers', type=int, default=8, help='Number of parallel workers')
    parser.add_argument('--stable-interval', type=float, default=10.0, help='Interval when stable (seconds)')
    parser.add_argument('--unstable-interval', type=float, default=2.0, help='Interval when unstable (seconds)')
    parser.add_argument('--max-hops', type=int, default=20, help='Maximum PathPing hops')
    parser.add_argument('--no-adaptive', action='store_true', help='Disable adaptive intervals')
    parser.add_argument('--skip-speed-stable', action='store_true', help='Skip speed test when stable')
    parser.add_argument('--screenshot-all', action='store_true', help='Screenshot every cycle (not just alerts)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SUNYA HIGH-PERFORMANCE NETWORK DIAGNOSTIC v3.0")
    print("=" * 60)
    print()
    print("Optimizations:")
    print("  ✓ Parallel execution (ping/pathping/DNS)")
    print("  ✓ Headless browser mode")
    print("  ✓ Adaptive test intervals")
    print("  ✓ Static data caching")
    print("  ✓ In-memory logging")
    print("  ✓ Incremental PathPing (limited hops)")
    print("  ✓ Background PDF generation")
    print("  ✓ Process cleanup & reuse")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        diagnostic = SunyaHighPerformanceDiagnostic(
            max_workers=args.workers,
            adaptive_interval=not args.no_adaptive,
            stable_interval=args.stable_interval,
            unstable_interval=args.unstable_interval,
            max_pathping_hops=args.max_hops,
            screenshot_on_alert_only=not args.screenshot_all,
            skip_speed_test_if_stable=args.skip_speed_stable
        )
        
        diagnostic.run_continuous_monitoring(
            max_cycles=args.cycles,
            duration_minutes=args.duration
        )
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
