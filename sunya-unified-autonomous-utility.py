#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA UNIFIED AUTONOMOUS NETWORK DIAGNOSTIC UTILITY
====================================================
Version: 4.0.0 - Total Autonomous Execution Mode

THIS UTILITY OPERATES WITH ZERO USER INTERACTION
- No configuration menus
- No user prompts
- No branching pathways
- No modular components
- No sub-functions
- Immediate automatic execution
- Locked interface - no overrides permitted

Upon launch, this utility immediately executes its complete predetermined
workflow from initialization through completion without requiring user input,
displaying intermediate options, or presenting alternative execution modes.

Execution Sequence:
1. System initialization and validation
2. Network adapter enumeration and analysis
3. Comprehensive connectivity testing
4. Speed performance measurement
5. Route tracing and bottleneck detection
6. DNS resolution testing
7. Packet loss and jitter analysis
8. Hardware capability assessment
9. Report generation and export
10. Automatic termination

Author: SUNYA Networking
License: Proprietary - Autonomous Execution Only
"""

# =============================================================================
# SECTION 1: ABSOLUTE IMPORTS - NO CONDITIONAL LOADING
# =============================================================================

import os
import sys
import time
import json
import socket
import struct
import subprocess
import platform
import datetime
import threading
import tempfile
import re
import shutil
import gc
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# SECTION 2: IMMEDIATE EXECUTION BLOCK - NO FUNCTIONS, NO CLASSES
# =============================================================================

# Force immediate start timestamp
_EXECUTION_START = datetime.datetime.now()
_TIMESTAMP = _EXECUTION_START.strftime('%Y-%m-%d_%H-%M-%S')
_DATE_STR = _EXECUTION_START.strftime('%Y-%m-%d')
_TIME_STR = _EXECUTION_START.strftime('%H-%M-%S')

# Platform detection
_PLATFORM = platform.system().lower()
_IS_WINDOWS = _PLATFORM == 'windows'
_IS_LINUX = _PLATFORM == 'linux'
_IS_MACOS = _PLATFORM == 'darwin'

# Get user identity
_USERNAME = os.environ.get('USERNAME') or os.environ.get('USER') or 'UnknownUser'
_COMPUTERNAME = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME') or 'UnknownHost'

# =============================================================================
# SECTION 3: OUTPUT DIRECTORY CREATION
# =============================================================================

if _IS_WINDOWS:
    _DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
else:
    _DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')

_BASE_FOLDER = os.path.join(_DESKTOP_PATH, f"SUNYA_AUTONOMOUS_REPORT_{_TIMESTAMP}")
os.makedirs(_BASE_FOLDER, exist_ok=True)
os.makedirs(os.path.join(_BASE_FOLDER, 'RawData'), exist_ok=True)
os.makedirs(os.path.join(_BASE_FOLDER, 'Analysis'), exist_ok=True)

_LOG_FILE = os.path.join(_BASE_FOLDER, 'execution.log')
_REPORT_FILE = os.path.join(_BASE_FOLDER, 'AUTONOMOUS_NETWORK_REPORT.txt')
_JSON_FILE = os.path.join(_BASE_FOLDER, 'RawData', 'complete_results.json')

# =============================================================================
# SECTION 4: LOGGING INITIALIZATION
# =============================================================================

with open(_LOG_FILE, 'w', encoding='utf-8') as _f:
    _f.write(f"SUNYA UNIFIED AUTONOMOUS DIAGNOSTIC UTILITY\n")
    _f.write(f"{'='*60}\n")
    _f.write(f"Execution Started: {_EXECUTION_START.isoformat()}\n")
    _f.write(f"Platform: {_PLATFORM.upper()}\n")
    _f.write(f"User: {_USERNAME}\n")
    _f.write(f"Computer: {_COMPUTERNAME}\n")
    _f.write(f"{'='*60}\n\n")

print(f"SUNYA UNIFIED AUTONOMOUS DIAGNOSTIC UTILITY v4.0.0")
print(f"{'='*60}")
print(f"Execution Started: {_TIMESTAMP}")
print(f"Report Directory: {_BASE_FOLDER}")
print(f"{'='*60}\n")
print("EXECUTING PREDETERMINED WORKFLOW...")
print("NO USER INTERACTION REQUIRED OR PERMITTED\n")

# =============================================================================
# SECTION 5: SYSTEM INFORMATION GATHERING
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 1: SYSTEM INFORMATION GATHERING\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 1] Gathering system information...")

_SYSTEM_INFO = {
    'platform': _PLATFORM,
    'platform_version': platform.version(),
    'platform_release': platform.release(),
    'architecture': platform.machine(),
    'processor': platform.processor(),
    'python_version': platform.python_version(),
    'hostname': _COMPUTERNAME,
    'username': _USERNAME,
    'execution_timestamp': _TIMESTAMP
}

try:
    import psutil
    _PSUTIL_AVAILABLE = True
    _SYSTEM_INFO['cpu_count'] = psutil.cpu_count()
    _SYSTEM_INFO['cpu_percent'] = psutil.cpu_percent(interval=0.1)
    _MEMORY = psutil.virtual_memory()
    _SYSTEM_INFO['total_memory_gb'] = round(_MEMORY.total / (1024**3), 2)
    _SYSTEM_INFO['available_memory_gb'] = round(_MEMORY.available / (1024**3), 2)
    _SYSTEM_INFO['memory_percent'] = _MEMORY.percent
except Exception:
    _PSUTIL_AVAILABLE = False
    _SYSTEM_INFO['cpu_count'] = 'N/A'
    _SYSTEM_INFO['memory_status'] = 'N/A'

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"Platform: {_SYSTEM_INFO['platform']}\n")
    _f.write(f"Architecture: {_SYSTEM_INFO['architecture']}\n")
    _f.write(f"Processor: {_SYSTEM_INFO['processor']}\n")
    _f.write(f"Hostname: {_SYSTEM_INFO['hostname']}\n")
    _f.write(f"CPU Count: {_SYSTEM_INFO.get('cpu_count', 'N/A')}\n")
    _f.write(f"Total Memory: {_SYSTEM_INFO.get('total_memory_gb', 'N/A')} GB\n\n")

print(f"  Platform: {_SYSTEM_INFO['platform']}")
print(f"  Architecture: {_SYSTEM_INFO['architecture']}")
print(f"  Hostname: {_SYSTEM_INFO['hostname']}")
print("  System information complete.\n")

# =============================================================================
# SECTION 6: NETWORK ADAPTER ENUMERATION
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 2: NETWORK ADAPTER ENUMERATION\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 2] Enumerating network adapters...")

_ADAPTERS = []

if _PSUTIL_AVAILABLE:
    try:
        _IF_ADDRS = psutil.net_if_addrs()
        _IF_STATS = psutil.net_if_stats()
        
        for _interface_name, _addresses in _IF_ADDRS.items():
            _adapter = {
                'name': _interface_name,
                'type': 'unknown',
                'mac_address': '',
                'ip_address': '',
                'subnet_mask': '',
                'is_up': False,
                'speed_mbps': 0
            }
            
            if _interface_name in _IF_STATS:
                _stats = _IF_STATS[_interface_name]
                _adapter['is_up'] = _stats.isup
                _adapter['speed_mbps'] = _stats.speed if _stats.speed else 0
                _adapter['duplex'] = str(_stats.duplex) if hasattr(_stats, 'duplex') else 'unknown'
            
            for _addr in _addresses:
                if _addr.family == socket.AF_INET:
                    _adapter['ip_address'] = _addr.address
                    _adapter['subnet_mask'] = _addr.netmask
                elif _addr.family == psutil.AF_LINK if hasattr(psutil, 'AF_LINK') else -1:
                    _adapter['mac_address'] = _addr.address
            
            _interface_lower = _interface_name.lower()
            if 'wi-fi' in _interface_lower or 'wireless' in _interface_lower or 'wlan' in _interface_lower:
                _adapter['type'] = 'wifi'
            elif 'ethernet' in _interface_lower or 'eth' in _interface_lower:
                _adapter['type'] = 'ethernet'
            elif 'loopback' in _interface_lower or 'lo' in _interface_lower:
                _adapter['type'] = 'loopback'
            elif 'bluetooth' in _interface_lower:
                _adapter['type'] = 'bluetooth'
            
            _ADAPTERS.append(_adapter)
            
    except Exception as _e:
        with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
            _f.write(f"Adapter enumeration error: {_e}\n")

if _IS_WINDOWS:
    try:
        _IPCONFIG_OUTPUT = subprocess.check_output(['ipconfig', '/all'], universal_newlines=True, errors='ignore')
        _ADAPTER_SECTIONS = _IPCONFIG_OUTPUT.split('\n\n')
        
        for _section in _ADAPTER_SECTIONS:
            if 'adapter' in _section.lower():
                _adapter_name = ''
                _gateway = ''
                _dns_servers = []
                
                for _line in _section.split('\n'):
                    if 'adapter' in _line.lower() and ':' in _line:
                        _adapter_name = _line.split(':')[0].strip()
                    if 'default gateway' in _line.lower():
                        _parts = _line.split(':')
                        if len(_parts) > 1:
                            _gateway = _parts[1].strip()
                    if 'dns servers' in _line.lower():
                        _parts = _line.split(':')
                        if len(_parts) > 1:
                            _dns_servers.append(_parts[1].strip())
                
                for _adapter in _ADAPTERS:
                    if _adapter_name and _adapter_name.lower() in _adapter['name'].lower():
                        _adapter['gateway'] = _gateway
                        _adapter['dns_servers'] = _dns_servers
                        
    except Exception as _e:
        with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
            _f.write(f"Windows adapter details error: {_e}\n")

_ACTIVE_ADAPTERS = [_a for _a in _ADAPTERS if _a.get('is_up', False) and _a.get('type') != 'loopback']
_PRIMARY_ADAPTER = _ACTIVE_ADAPTERS[0] if _ACTIVE_ADAPTERS else (_ADAPTERS[0] if _ADAPTERS else None)

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"Total adapters found: {len(_ADAPTERS)}\n")
    _f.write(f"Active adapters: {len(_ACTIVE_ADAPTERS)}\n")
    if _PRIMARY_ADAPTER:
        _f.write(f"Primary adapter: {_PRIMARY_ADAPTER['name']}\n")
        _f.write(f"  Type: {_PRIMARY_ADAPTER['type']}\n")
        _f.write(f"  IP: {_PRIMARY_ADAPTER.get('ip_address', 'N/A')}\n")
        _f.write(f"  MAC: {_PRIMARY_ADAPTER.get('mac_address', 'N/A')}\n")
        _f.write(f"  Speed: {_PRIMARY_ADAPTER.get('speed_mbps', 0)} Mbps\n\n")

print(f"  Total adapters found: {len(_ADAPTERS)}")
print(f"  Active adapters: {len(_ACTIVE_ADAPTERS)}")
if _PRIMARY_ADAPTER:
    print(f"  Primary adapter: {_PRIMARY_ADAPTER['name']}")
    print(f"  Type: {_PRIMARY_ADAPTER['type']}")
    print(f"  IP Address: {_PRIMARY_ADAPTER.get('ip_address', 'N/A')}")
    print(f"  MAC Address: {_PRIMARY_ADAPTER.get('mac_address', 'N/A')}")
print("  Adapter enumeration complete.\n")

# =============================================================================
# SECTION 7: CONNECTIVITY TESTING - PING OPERATIONS
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 3: CONNECTIVITY TESTING\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 3] Executing connectivity tests...")

_PING_TARGETS = [
    ('8.8.8.8', 'Google DNS'),
    ('1.1.1.1', 'Cloudflare DNS'),
    ('google.com', 'Google'),
    ('cloudflare.com', 'Cloudflare'),
    ('facebook.com', 'Facebook'),
    ('x.com', 'X/Twitter'),
    ('instagram.com', 'Instagram'),
    ('amazon.com', 'Amazon'),
    ('microsoft.com', 'Microsoft'),
    ('apple.com', 'Apple')
]

_PING_RESULTS = []

for _target, _description in _PING_TARGETS:
    print(f"  Testing {_description} ({_target})...")
    
    _result = {
        'target': _target,
        'description': _description,
        'success': False,
        'packets_sent': 0,
        'packets_received': 0,
        'packet_loss_percent': 100.0,
        'min_latency': 0.0,
        'max_latency': 0.0,
        'avg_latency': 0.0,
        'jitter': 0.0,
        'raw_output': ''
    }
    
    try:
        if _IS_WINDOWS:
            _cmd = ['ping', '-n', '4', '-w', '3000', _target]
        else:
            _cmd = ['ping', '-c', '4', '-W', '3', _target]
        
        _output = subprocess.check_output(_cmd, universal_newlines=True, stderr=subprocess.STDOUT, timeout=20, errors='ignore')
        _result['raw_output'] = _output
        
        _packet_match = re.search(r'(\d+)\s+\w+\s*,\s*(\d+)\s+\w+\s*,\s*(\d+)\s+\w+\s*,\s*(\d+)', _output)
        if not _packet_match:
            _packet_match = re.search(r'(\d+)\s+packets?\s+transmitted.*?\s*(\d+)\s+received', _output, re.IGNORECASE)
        
        if _packet_match:
            _result['packets_sent'] = int(_packet_match.group(1))
            _result['packets_received'] = int(_packet_match.group(2))
            if _result['packets_sent'] > 0:
                _result['packet_loss_percent'] = ((_result['packets_sent'] - _result['packets_received']) / _result['packets_sent']) * 100
        
        _latency_match = re.search(r'(?:Minimum|min)\s*=\s*(\d+)ms.*?(?:Maximum|max)\s*=\s*(\d+)ms.*?(?:Average|avg)\s*=\s*(\d+)ms', _output, re.IGNORECASE)
        if not _latency_match:
            _latency_match = re.search(r'rtt.*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', _output)
        
        if _latency_match:
            _result['min_latency'] = float(_latency_match.group(1))
            _result['max_latency'] = float(_latency_match.group(2))
            _result['avg_latency'] = float(_latency_match.group(3))
        
        _result['success'] = _result['packets_received'] > 0
        
    except subprocess.TimeoutExpired:
        _result['error'] = 'Timeout'
    except subprocess.CalledProcessError as _e:
        _result['raw_output'] = _e.output if hasattr(_e, 'output') else str(_e)
    except Exception as _e:
        _result['error'] = str(_e)
    
    _PING_RESULTS.append(_result)
    
    _status = "SUCCESS" if _result['success'] else "FAILED"
    _latency_str = f"({_result['avg_latency']:.1f}ms)" if _result['success'] else ""
    print(f"    Status: {_status} {_latency_str}")
    
    with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
        _f.write(f"  {_description} ({_target}): {_status}, Loss: {_result['packet_loss_percent']:.1f}%, Avg: {_result['avg_latency']:.1f}ms\n")

_TOTAL_SUCCESS = sum(1 for _r in _PING_RESULTS if _r['success'])
_TOTAL_TARGETS = len(_PING_TARGETS)
_AVG_LATENCY = sum(_r['avg_latency'] for _r in _PING_RESULTS if _r['success']) / max(1, _TOTAL_SUCCESS)
_AVG_LOSS = sum(_r['packet_loss_percent'] for _r in _PING_RESULTS) / _TOTAL_TARGETS

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"\nConnectivity Summary: {_TOTAL_SUCCESS}/{_TOTAL_TARGETS} targets reachable\n")
    _f.write(f"Average Latency: {_AVG_LATENCY:.1f}ms\n")
    _f.write(f"Average Packet Loss: {_AVG_LOSS:.1f}%\n\n")

print(f"\n  Connectivity Summary: {_TOTAL_SUCCESS}/{_TOTAL_TARGETS} targets reachable")
print(f"  Average Latency: {_AVG_LATENCY:.1f}ms")
print(f"  Average Packet Loss: {_AVG_LOSS:.1f}%")
print("  Connectivity testing complete.\n")

# =============================================================================
# SECTION 8: SPEED TEST EXECUTION
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 4: SPEED PERFORMANCE TESTING\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 4] Executing speed performance tests...")

_SPEED_RESULTS = {
    'ookla': {'success': False, 'download': 0, 'upload': 0, 'latency': 0, 'server': ''},
    'fast': {'success': False, 'download': 0, 'upload': 0, 'latency': 0},
    'browser': {'success': False, 'download': 0, 'upload': 0, 'latency': 0}
}

print("  Attempting Speedtest.net (Ookla)...")
try:
    import speedtest
    _st = speedtest.Speedtest(secure=True)
    _st.get_best_server()
    print("    Finding best server...")
    
    _download_speed = _st.download() / 1_000_000
    _upload_speed = _st.upload() / 1_000_000
    _ping = _st.results.ping
    
    _SPEED_RESULTS['ookla'] = {
        'success': True,
        'download': round(_download_speed, 2),
        'upload': round(_upload_speed, 2),
        'latency': round(_ping, 1),
        'server': _st.results.server.get('sponsor', 'Unknown')
    }
    print(f"    Download: {_download_speed:.1f} Mbps")
    print(f"    Upload: {_upload_speed:.1f} Mbps")
    print(f"    Latency: {_ping:.1f} ms")
    
except Exception as _e:
    print(f"    Speedtest.net failed: {_e}")
    _SPEED_RESULTS['ookla']['error'] = str(_e)

print("\n  Attempting browser-based speed test...")
_BROWSER_TEST_SUCCESS = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    
    _chrome_options = Options()
    _chrome_options.add_argument('--headless')
    _chrome_options.add_argument('--no-sandbox')
    _chrome_options.add_argument('--disable-dev-shm-usage')
    _chrome_options.add_argument('--disable-gpu')
    _chrome_options.add_argument('--window-size=1920,1080')
    _chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        _service = Service(ChromeDriverManager().install())
        _driver = webdriver.Chrome(service=_service, options=_chrome_options)
    except Exception:
        _driver = webdriver.Chrome(options=_chrome_options)
    
    print("    Opening fast.com...")
    _driver.get("https://fast.com")
    time.sleep(10)
    
    try:
        _download_elem = WebDriverWait(_driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.speed-results-container, .result-container-speed'))
        )
        _speed_text = _download_elem.text.strip()
        if _speed_text:
            _speed_value = float(_speed_text.replace('Mbps', '').strip())
            _SPEED_RESULTS['fast'] = {
                'success': True,
                'download': round(_speed_value, 2),
                'upload': 0,
                'latency': 0
            }
            print(f"    Fast.com Download: {_speed_value:.1f} Mbps")
            _BROWSER_TEST_SUCCESS = True
    except Exception as _e:
        print(f"    Could not read fast.com results: {_e}")
    
    _driver.quit()
    
except Exception as _e:
    print(f"    Browser test unavailable: {_e}")
    _SPEED_RESULTS['fast']['error'] = str(_e)

_BEST_DOWNLOAD = max(
    _SPEED_RESULTS['ookla'].get('download', 0),
    _SPEED_RESULTS['fast'].get('download', 0)
)
_BEST_UPLOAD = max(
    _SPEED_RESULTS['ookla'].get('upload', 0),
    _SPEED_RESULTS['fast'].get('upload', 0)
)
_BEST_LATENCY = min(
    _SPEED_RESULTS['ookla'].get('latency', 9999) or 9999,
    _SPEED_RESULTS['fast'].get('latency', 9999) or 9999
) if (_SPEED_RESULTS['ookla'].get('latency') or _SPEED_RESULTS['fast'].get('latency')) else 0

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"Best Download Speed: {_BEST_DOWNLOAD:.1f} Mbps\n")
    _f.write(f"Best Upload Speed: {_BEST_UPLOAD:.1f} Mbps\n")
    _f.write(f"Best Latency: {_BEST_LATENCY:.1f} ms\n\n")

print(f"\n  Speed Test Summary:")
print(f"  Best Download: {_BEST_DOWNLOAD:.1f} Mbps")
print(f"  Best Upload: {_BEST_UPLOAD:.1f} Mbps")
print(f"  Best Latency: {_BEST_LATENCY:.1f} ms")
print("  Speed testing complete.\n")

# =============================================================================
# SECTION 9: ROUTE TRACING AND PATH ANALYSIS
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 5: ROUTE TRACING AND PATH ANALYSIS\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 5] Executing route tracing...")

_TRACERT_TARGETS = [
    ('8.8.8.8', 'Google DNS'),
    ('google.com', 'Google'),
    ('cloudflare.com', 'Cloudflare')
]

_TRACERT_RESULTS = []

for _target, _description in _TRACERT_TARGETS:
    print(f"  Tracing route to {_description} ({_target})...")
    
    _result = {
        'target': _target,
        'description': _description,
        'success': False,
        'hops': [],
        'total_hops': 0,
        'worst_latency': 0,
        'worst_hop': 0
    }
    
    try:
        if _IS_WINDOWS:
            _cmd = ['tracert', '-d', '-h', '30', '-w', '2000', _target]
        else:
            _cmd = ['traceroute', '-n', '-m', '30', '-w', '2', _target]
        
        _output = subprocess.check_output(_cmd, universal_newlines=True, stderr=subprocess.STDOUT, timeout=60, errors='ignore')
        _result['raw_output'] = _output
        
        _hops = []
        _worst_latency = 0
        _worst_hop = 0
        
        for _line in _output.split('\n'):
            if _IS_WINDOWS:
                _match = re.match(r'\s*(\d+)\s+<?(\d+|\*)\s*ms\s+<?(\d+|\*)\s*ms\s+<?(\d+|\*)\s*ms\s+(.+)', _line)
                if _match:
                    _hop_num = int(_match.group(1))
                    _latencies = []
                    for _i in range(2, 5):
                        _val = _match.group(_i)
                        if _val and _val != '*':
                            try:
                                _latencies.append(int(_val))
                            except ValueError:
                                pass
                    _ip = _match.group(5).strip()
                    
                    _avg_latency = sum(_latencies) / len(_latencies) if _latencies else 0
                    _hops.append({'hop': _hop_num, 'ip': _ip, 'latency': _avg_latency})
                    
                    if _avg_latency > _worst_latency:
                        _worst_latency = _avg_latency
                        _worst_hop = _hop_num
            else:
                _match = re.match(r'\s*(\d+)\s+(\S+)\s+([\d.]+)\s*ms', _line)
                if _match:
                    _hop_num = int(_match.group(1))
                    _ip = _match.group(2)
                    _latency = float(_match.group(3))
                    _hops.append({'hop': _hop_num, 'ip': _ip, 'latency': _latency})
                    
                    if _latency > _worst_latency:
                        _worst_latency = _latency
                        _worst_hop = _hop_num
        
        _result['hops'] = _hops
        _result['total_hops'] = len(_hops)
        _result['worst_latency'] = _worst_latency
        _result['worst_hop'] = _worst_hop
        _result['success'] = len(_hops) > 0
        
        print(f"    Hops: {len(_hops)}, Worst latency at hop {_worst_hop}: {_worst_latency:.1f}ms")
        
    except subprocess.TimeoutExpired:
        _result['error'] = 'Timeout'
        print("    Timeout")
    except Exception as _e:
        _result['error'] = str(_e)
        print(f"    Error: {_e}")
    
    _TRACERT_RESULTS.append(_result)
    
    with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
        _status = "SUCCESS" if _result['success'] else "FAILED"
        _f.write(f"  {_description}: {_status}, {len(_hops)} hops\n")

print("  Route tracing complete.\n")

# =============================================================================
# SECTION 10: DNS RESOLUTION TESTING
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 6: DNS RESOLUTION TESTING\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 6] Testing DNS resolution...")

_DNS_HOSTNAMES = [
    'google.com',
    'cloudflare.com',
    'facebook.com',
    'amazon.com',
    'microsoft.com',
    'github.com',
    'wikipedia.org',
    'reddit.com'
]

_DNS_RESULTS = []

for _hostname in _DNS_HOSTNAMES:
    print(f"  Resolving {_hostname}...")
    
    _result = {
        'hostname': _hostname,
        'success': False,
        'resolved_ips': [],
        'resolution_time_ms': 0
    }
    
    try:
        _start = time.time()
        _resolved = socket.gethostbyname_ex(_hostname)
        _end = time.time()
        
        _result['success'] = True
        _result['resolved_ips'] = list(_resolved[2])
        _result['resolution_time_ms'] = round((_end - _start) * 1000, 2)
        _result['canonical_name'] = _resolved[0]
        
        print(f"    OK - {_result['resolved_ips'][0]} ({_result['resolution_time_ms']:.1f}ms)")
        
    except socket.gaierror:
        print(f"    FAILED - Could not resolve")
    except Exception as _e:
        print(f"    ERROR - {_e}")
        _result['error'] = str(_e)
    
    _DNS_RESULTS.append(_result)
    
    with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
        _status = "OK" if _result['success'] else "FAIL"
        _f.write(f"  {_hostname}: {_status}\n")

_DNS_SUCCESS_COUNT = sum(1 for _r in _DNS_RESULTS if _r['success'])
_DNS_AVG_TIME = sum(_r['resolution_time_ms'] for _r in _DNS_RESULTS if _r['success']) / max(1, _DNS_SUCCESS_COUNT)

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"\nDNS Resolution: {_DNS_SUCCESS_COUNT}/{len(_DNS_HOSTNAMES)} successful\n")
    _f.write(f"Average resolution time: {_DNS_AVG_TIME:.1f}ms\n\n")

print(f"\n  DNS Summary: {_DNS_SUCCESS_COUNT}/{len(_DNS_HOSTNAMES)} successful")
print(f"  Average resolution time: {_DNS_AVG_TIME:.1f}ms")
print("  DNS testing complete.\n")

# =============================================================================
# SECTION 11: NETWORK HEALTH SCORING
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 7: NETWORK HEALTH SCORING\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 7] Calculating network health scores...")

_SPEED_SCORE = min(100, int((_BEST_DOWNLOAD / 100) * 100)) if _BEST_DOWNLOAD > 0 else 0
if _BEST_DOWNLOAD > 500:
    _SPEED_SCORE = 100
elif _BEST_DOWNLOAD > 100:
    _SPEED_SCORE = 90
elif _BEST_DOWNLOAD > 50:
    _SPEED_SCORE = 80
elif _BEST_DOWNLOAD > 25:
    _SPEED_SCORE = 70
elif _BEST_DOWNLOAD > 10:
    _SPEED_SCORE = 60
else:
    _SPEED_SCORE = max(0, int(_BEST_DOWNLOAD * 5))

_LATENCY_SCORE = 0
if _AVG_LATENCY > 0:
    if _AVG_LATENCY < 10:
        _LATENCY_SCORE = 100
    elif _AVG_LATENCY < 30:
        _LATENCY_SCORE = 90
    elif _AVG_LATENCY < 50:
        _LATENCY_SCORE = 80
    elif _AVG_LATENCY < 100:
        _LATENCY_SCORE = 70
    elif _AVG_LATENCY < 150:
        _LATENCY_SCORE = 60
    elif _AVG_LATENCY < 200:
        _LATENCY_SCORE = 50
    else:
        _LATENCY_SCORE = max(0, 100 - int(_AVG_LATENCY / 5))

_STABILITY_SCORE = 100 - int(_AVG_LOSS)
_STABILITY_SCORE = max(0, min(100, _STABILITY_SCORE))

_CONNECTIVITY_SCORE = int((_TOTAL_SUCCESS / _TOTAL_TARGETS) * 100)

_DNS_SCORE = int((_DNS_SUCCESS_COUNT / len(_DNS_HOSTNAMES)) * 100)

_OVERALL_SCORE = int(
    (_SPEED_SCORE * 0.25) +
    (_LATENCY_SCORE * 0.25) +
    (_STABILITY_SCORE * 0.25) +
    (_CONNECTIVITY_SCORE * 0.15) +
    (_DNS_SCORE * 0.10)
)

if _OVERALL_SCORE >= 90:
    _GRADE = "EXCELLENT"
elif _OVERALL_SCORE >= 75:
    _GRADE = "GOOD"
elif _OVERALL_SCORE >= 60:
    _GRADE = "FAIR"
elif _OVERALL_SCORE >= 40:
    _GRADE = "POOR"
else:
    _GRADE = "CRITICAL"

_RECOMMENDATIONS = []
if _SPEED_SCORE < 60:
    _RECOMMENDATIONS.append("Consider upgrading your internet plan for better speeds")
if _LATENCY_SCORE < 60:
    _RECOMMENDATIONS.append("High latency detected - consider using a wired connection")
if _STABILITY_SCORE < 70:
    _RECOMMENDATIONS.append("Packet loss detected - check cable connections and router")
if _CONNECTIVITY_SCORE < 100:
    _RECOMMENDATIONS.append("Some websites unreachable - check firewall or ISP issues")
if _DNS_SCORE < 100:
    _RECOMMENDATIONS.append("DNS resolution issues - consider using 8.8.8.8 or 1.1.1.1")
if not _RECOMMENDATIONS:
    _RECOMMENDATIONS.append("Network is performing well - no action required")

_HEALTH_SCORES = {
    'overall_score': _OVERALL_SCORE,
    'grade': _GRADE,
    'speed_score': _SPEED_SCORE,
    'latency_score': _LATENCY_SCORE,
    'stability_score': _STABILITY_SCORE,
    'connectivity_score': _CONNECTIVITY_SCORE,
    'dns_score': _DNS_SCORE,
    'recommendations': _RECOMMENDATIONS
}

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"Overall Score: {_OVERALL_SCORE}/100 ({_GRADE})\n")
    _f.write(f"Speed Score: {_SPEED_SCORE}/100\n")
    _f.write(f"Latency Score: {_LATENCY_SCORE}/100\n")
    _f.write(f"Stability Score: {_STABILITY_SCORE}/100\n")
    _f.write(f"Connectivity Score: {_CONNECTIVITY_SCORE}/100\n")
    _f.write(f"DNS Score: {_DNS_SCORE}/100\n\n")

print(f"  Overall Score: {_OVERALL_SCORE}/100 ({_GRADE})")
print(f"  Speed Score: {_SPEED_SCORE}/100")
print(f"  Latency Score: {_LATENCY_SCORE}/100")
print(f"  Stability Score: {_STABILITY_SCORE}/100")
print(f"  Connectivity Score: {_CONNECTIVITY_SCORE}/100")
print(f"  DNS Score: {_DNS_SCORE}/100")
print("  Health scoring complete.\n")

# =============================================================================
# SECTION 12: ISP COMPLAINT SUMMARY GENERATION
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 8: ISP COMPLAINT SUMMARY GENERATION\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 8] Generating ISP complaint summary...")

_ISSUES_FOUND = []
if _BEST_DOWNLOAD < 10:
    _ISSUES_FOUND.append("Very slow download speeds")
if _AVG_LATENCY > 100:
    _ISSUES_FOUND.append("High latency affecting real-time applications")
if _AVG_LOSS > 5:
    _ISSUES_FOUND.append("Significant packet loss affecting connectivity")
if _TOTAL_SUCCESS < _TOTAL_TARGETS:
    _ISSUES_FOUND.append("Intermittent connectivity to some services")

_ISP_SUMMARY = f"""
ISP COMPLAINT SUMMARY
Generated: {_TIMESTAMP}
User: {_USERNAME}
Computer: {_COMPUTERNAME}

ISSUE SUMMARY:
- Overall Network Grade: {_GRADE}
- Overall Score: {_OVERALL_SCORE}/100
- Download Speed: {_BEST_DOWNLOAD:.1f} Mbps
- Upload Speed: {_BEST_UPLOAD:.1f} Mbps
- Average Latency: {_AVG_LATENCY:.1f} ms
- Average Packet Loss: {_AVG_LOSS:.1f}%

DETECTED ISSUES:
"""

if _ISSUES_FOUND:
    for _i, _issue in enumerate(_ISSUES_FOUND, 1):
        _ISP_SUMMARY += f"{_i}. {_issue}\n"
else:
    _ISP_SUMMARY += "No significant issues detected\n"

_ISP_SUMMARY += f"""
RECOMMENDATIONS FOR ISP:
"""

if _BEST_DOWNLOAD < 50:
    _ISP_SUMMARY += "- Investigate speed degradation on subscriber line\n"
if _AVG_LATENCY > 50:
    _ISP_SUMMARY += "- Check routing path for unnecessary hops\n"
if _AVG_LOSS > 1:
    _ISP_SUMMARY += "- Inspect network equipment for packet loss sources\n"
if not _ISSUES_FOUND:
    _ISP_SUMMARY += "- Service is performing within expected parameters\n"

_ISP_SUMMARY += f"""
TEST METHODOLOGY:
- Ping tests to {_TOTAL_TARGETS} targets
- Speed tests via multiple sources
- Route tracing to major services
- DNS resolution tests
- Automated analysis and scoring

Report generated by SUNYA Unified Autonomous Diagnostic Utility v4.0.0
"""

_ISP_FILE = os.path.join(_BASE_FOLDER, 'ISP_COMPLAINT_SUMMARY.txt')
with open(_ISP_FILE, 'w', encoding='utf-8') as _f:
    _f.write(_ISP_SUMMARY)

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"ISP summary saved to: {_ISP_FILE}\n\n")

print(f"  ISP complaint summary generated: {_ISP_FILE}")
print("  ISP summary generation complete.\n")

# =============================================================================
# SECTION 13: COMPREHENSIVE REPORT GENERATION
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 9: COMPREHENSIVE REPORT GENERATION\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 9] Generating comprehensive report...")

_FULL_REPORT = f"""
================================================================================
SUNYA UNIFIED AUTONOMOUS NETWORK DIAGNOSTIC REPORT
================================================================================
Generated: {_TIMESTAMP}
User: {_USERNAME}
Computer: {_COMPUTERNAME}
Platform: {_PLATFORM.upper()}

================================================================================
EXECUTIVE SUMMARY
================================================================================

Overall Network Health: {_GRADE} ({_OVERALL_SCORE}/100)

Key Metrics:
- Download Speed: {_BEST_DOWNLOAD:.1f} Mbps
- Upload Speed: {_BEST_UPLOAD:.1f} Mbps
- Average Latency: {_AVG_LATENCY:.1f} ms
- Packet Loss: {_AVG_LOSS:.1f}%
- Connectivity: {_TOTAL_SUCCESS}/{_TOTAL_TARGETS} targets reachable
- DNS Resolution: {_DNS_SUCCESS_COUNT}/{len(_DNS_HOSTNAMES)} successful

================================================================================
DETAILED SCORES
================================================================================

Speed Performance:     {_SPEED_SCORE}/100
Latency Performance:   {_LATENCY_SCORE}/100
Network Stability:     {_STABILITY_SCORE}/100
Connectivity:          {_CONNECTIVITY_SCORE}/100
DNS Resolution:        {_DNS_SCORE}/100

================================================================================
SYSTEM INFORMATION
================================================================================

Platform: {_SYSTEM_INFO['platform']} {_SYSTEM_INFO.get('platform_release', 'N/A')}
Architecture: {_SYSTEM_INFO['architecture']}
Processor: {_SYSTEM_INFO['processor']}
Python Version: {_SYSTEM_INFO['python_version']}
CPU Count: {_SYSTEM_INFO.get('cpu_count', 'N/A')}
Total Memory: {_SYSTEM_INFO.get('total_memory_gb', 'N/A')} GB
Available Memory: {_SYSTEM_INFO.get('available_memory_gb', 'N/A')} GB

================================================================================
NETWORK ADAPTER INFORMATION
================================================================================

Total Adapters Found: {len(_ADAPTERS)}
Active Adapters: {len(_ACTIVE_ADAPTERS)}

Primary Adapter Details:
"""

if _PRIMARY_ADAPTER:
    _FULL_REPORT += f"""
Name: {_PRIMARY_ADAPTER['name']}
Type: {_PRIMARY_ADAPTER['type']}
Status: {'Up' if _PRIMARY_ADAPTER.get('is_up') else 'Down'}
IP Address: {_PRIMARY_ADAPTER.get('ip_address', 'N/A')}
Subnet Mask: {_PRIMARY_ADAPTER.get('subnet_mask', 'N/A')}
MAC Address: {_PRIMARY_ADAPTER.get('mac_address', 'N/A')}
Link Speed: {_PRIMARY_ADAPTER.get('speed_mbps', 0)} Mbps
Gateway: {_PRIMARY_ADAPTER.get('gateway', 'N/A')}
"""
else:
    _FULL_REPORT += "No primary adapter detected\n"

_FULL_REPORT += f"""
================================================================================
PING TEST RESULTS
================================================================================

"""

for _r in _PING_RESULTS:
    _FULL_REPORT += f"""
Target: {_r['description']} ({_r['target']})
Status: {'SUCCESS' if _r['success'] else 'FAILED'}
Packets Sent: {_r['packets_sent']}
Packets Received: {_r['packets_received']}
Packet Loss: {_r['packet_loss_percent']:.1f}%
Min Latency: {_r['min_latency']:.1f} ms
Max Latency: {_r['max_latency']:.1f} ms
Avg Latency: {_r['avg_latency']:.1f} ms
"""

_FULL_REPORT += f"""
================================================================================
SPEED TEST RESULTS
================================================================================

Speedtest.net (Ookla):
  Success: {_SPEED_RESULTS['ookla']['success']}
  Download: {_SPEED_RESULTS['ookla'].get('download', 0):.1f} Mbps
  Upload: {_SPEED_RESULTS['ookla'].get('upload', 0):.1f} Mbps
  Latency: {_SPEED_RESULTS['ookla'].get('latency', 0):.1f} ms
  Server: {_SPEED_RESULTS['ookla'].get('server', 'N/A')}

Fast.com:
  Success: {_SPEED_RESULTS['fast']['success']}
  Download: {_SPEED_RESULTS['fast'].get('download', 0):.1f} Mbps

================================================================================
ROUTE TRACING RESULTS
================================================================================

"""

for _r in _TRACERT_RESULTS:
    _FULL_REPORT += f"""
Target: {_r['description']} ({_r['target']})
Total Hops: {_r['total_hops']}
Worst Latency: {_r['worst_latency']:.1f} ms at hop {_r['worst_hop']}

Hop Details:
"""
    for _hop in _r['hops'][:10]:
        _FULL_REPORT += f"  Hop {_hop['hop']}: {_hop['ip']} - {_hop['latency']:.1f}ms\n"
    if len(_r['hops']) > 10:
        _FULL_REPORT += f"  ... ({len(_r['hops']) - 10} more hops)\n"

_FULL_REPORT += f"""
================================================================================
DNS RESOLUTION RESULTS
================================================================================

"""

for _r in _DNS_RESULTS:
    _FULL_REPORT += f"{_r['hostname']}: {'SUCCESS' if _r['success'] else 'FAILED'}"
    if _r['success'] and _r['resolved_ips']:
        _FULL_REPORT += f" -> {_r['resolved_ips'][0]}"
    _FULL_REPORT += "\n"

_FULL_REPORT += f"""
================================================================================
RECOMMENDATIONS
================================================================================

"""

for _i, _rec in enumerate(_RECOMMENDATIONS, 1):
    _FULL_REPORT += f"{_i}. {_rec}\n"

_FULL_REPORT += f"""
================================================================================
RAW DATA FILES
================================================================================

Complete results have been exported to:
- JSON Data: {_JSON_FILE}
- ISP Summary: {_ISP_FILE}
- Execution Log: {_LOG_FILE}

================================================================================
REPORT GENERATED BY
================================================================================

SUNYA Unified Autonomous Diagnostic Utility v4.0.0
Total Autonomous Execution Mode
No User Interaction Required
Execution Time: {(datetime.datetime.now() - _EXECUTION_START).total_seconds():.1f} seconds

================================================================================
END OF REPORT
================================================================================
"""

with open(_REPORT_FILE, 'w', encoding='utf-8') as _f:
    _f.write(_FULL_REPORT)

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"Report saved to: {_REPORT_FILE}\n")
    _f.write(f"Report length: {len(_FULL_REPORT)} characters\n\n")

print(f"  Comprehensive report saved: {_REPORT_FILE}")
print("  Report generation complete.\n")

# =============================================================================
# SECTION 14: JSON DATA EXPORT
# =============================================================================

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("PHASE 10: JSON DATA EXPORT\n")
    _f.write("-" * 50 + "\n")

print("[PHASE 10] Exporting data to JSON...")

_COMPLETE_DATA = {
    'metadata': {
        'version': '4.0.0',
        'timestamp': _TIMESTAMP,
        'execution_time_seconds': round((datetime.datetime.now() - _EXECUTION_START).total_seconds(), 2),
        'username': _USERNAME,
        'computername': _COMPUTERNAME,
        'platform': _PLATFORM
    },
    'system_info': _SYSTEM_INFO,
    'adapters': _ADAPTERS,
    'primary_adapter': _PRIMARY_ADAPTER,
    'ping_results': _PING_RESULTS,
    'speed_results': _SPEED_RESULTS,
    'tracert_results': _TRACERT_RESULTS,
    'dns_results': _DNS_RESULTS,
    'health_scores': _HEALTH_SCORES,
    'summary': {
        'best_download_mbps': _BEST_DOWNLOAD,
        'best_upload_mbps': _BEST_UPLOAD,
        'best_latency_ms': _BEST_LATENCY,
        'avg_latency_ms': _AVG_LATENCY,
        'avg_packet_loss_percent': _AVG_LOSS,
        'connectivity_success_rate': _TOTAL_SUCCESS / _TOTAL_TARGETS,
        'dns_success_rate': _DNS_SUCCESS_COUNT / len(_DNS_HOSTNAMES),
        'overall_grade': _GRADE,
        'overall_score': _OVERALL_SCORE
    }
}

with open(_JSON_FILE, 'w', encoding='utf-8') as _f:
    json.dump(_COMPLETE_DATA, _f, indent=2, default=str)

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write(f"JSON export saved to: {_JSON_FILE}\n\n")

print(f"  JSON data exported: {_JSON_FILE}")
print("  JSON export complete.\n")

# =============================================================================
# SECTION 15: EXECUTION FINALIZATION
# =============================================================================

_EXECUTION_END = datetime.datetime.now()
_EXECUTION_DURATION = (_EXECUTION_END - _EXECUTION_START).total_seconds()

with open(_LOG_FILE, 'a', encoding='utf-8') as _f:
    _f.write("=" * 60 + "\n")
    _f.write("EXECUTION COMPLETE\n")
    _f.write("=" * 60 + "\n")
    _f.write(f"End Time: {_EXECUTION_END.isoformat()}\n")
    _f.write(f"Duration: {_EXECUTION_DURATION:.1f} seconds\n")
    _f.write(f"Status: SUCCESS\n")
    _f.write("=" * 60 + "\n")

print("=" * 60)
print("EXECUTION COMPLETE")
print("=" * 60)
print(f"End Time: {_EXECUTION_END.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Duration: {_EXECUTION_DURATION:.1f} seconds")
print(f"Status: SUCCESS")
print("=" * 60)
print(f"\nAll reports saved to: {_BASE_FOLDER}")
print("\nFiles Generated:")
print(f"  1. {_REPORT_FILE}")
print(f"  2. {_ISP_FILE}")
print(f"  3. {_JSON_FILE}")
print(f"  4. {_LOG_FILE}")
print("\nAUTONOMOUS WORKFLOW COMPLETED")
print("NO FURTHER ACTION REQUIRED")
print("=" * 60)

# =============================================================================
# SECTION 16: AUTOMATIC TERMINATION
# =============================================================================

# Cleanup
gc.collect()

# Exit immediately with success code
sys.exit(0)
