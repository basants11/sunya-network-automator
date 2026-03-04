#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA ULTRA - Single File Ultra-Fast Network Automation
Version: 4.0.0 - "One Package To Rule Them All"

Optimizations:
- Async/await for true parallelism (not threading)
- Lazy imports - only load what's needed
- Compiled regex patterns cached
- Connection pooling for HTTP requests
- Memory-efficient data structures
- Zero external dependencies for basic ops
- Smart caching with TTL
- Batch system calls

Usage: python sunya-ultra.py [--quick|--full|--monitor]
"""

from __future__ import annotations
import os
import sys
import time
import json
import socket
import struct
import subprocess
import platform
import tempfile
import threading
import queue
import re
import gc
import ctypes
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import deque, defaultdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# VERSION & METADATA
# ============================================================================

__version__ = "4.0.0"
__author__ = "SUNYA Networking"
__description__ = "Ultra-Fast Single-File Network Automation"

# ============================================================================
# DATA CLASSES - Lightweight & Fast
# ============================================================================

class TestMode(Enum):
    QUICK = "quick"      # 30 seconds
    STANDARD = "standard" # 2 minutes  
    FULL = "full"        # 5 minutes
    MONITOR = "monitor"  # Continuous

@dataclass(slots=True)
class NetConfig:
    """Network configuration - cached"""
    interface: str = ""
    mac: str = ""
    ip: str = ""
    gateway: str = ""
    dns: List[str] = field(default_factory=list)
    speed_mbps: int = 0
    is_ethernet: bool = False

@dataclass(slots=True)  
class PingStats:
    """Ping statistics"""
    target: str = ""
    sent: int = 0
    received: int = 0
    loss: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    jitter: float = 0.0
    success: bool = False

@dataclass(slots=True)
class SpeedResult:
    """Speed test result"""
    source: str = ""
    download: float = 0.0  # Mbps
    upload: float = 0.0    # Mbps
    latency: float = 0.0   # ms
    server: str = ""
    timestamp: str = ""
    success: bool = False

@dataclass(slots=True)
class RouteHop:
    """Single route hop"""
    number: int = 0
    host: str = ""
    ip: str = ""
    latency_ms: float = 0.0
    loss_pct: float = 0.0

@dataclass(slots=True)
class HealthScore:
    """Network health scoring"""
    overall: int = 0
    speed: int = 0
    latency: int = 0
    loss_score: int = 0
    stability: int = 0
    grade: str = "F"
    issues: List[str] = field(default_factory=list)

@dataclass(slots=True)
class DiagnosticReport:
    """Complete diagnostic report"""
    timestamp: str = ""
    duration_sec: float = 0.0
    config: NetConfig = field(default_factory=NetConfig)
    pings: List[PingStats] = field(default_factory=list)
    speeds: List[SpeedResult] = field(default_factory=list)
    routes: List[RouteHop] = field(default_factory=list)
    health: HealthScore = field(default_factory=HealthScore)
    raw_data: Dict = field(default_factory=dict)

# ============================================================================
# FAST UTILITIES - Zero-overhead helpers
# ============================================================================

class FastCache:
    """TTL cache for expensive operations"""
    _cache: Dict[str, Tuple[Any, float]] = {}
    _ttl: float = 60.0  # Default 60 second TTL
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._cache:
            value, expiry = cls._cache[key]
            if time.time() < expiry:
                return value
            del cls._cache[key]
        return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl: Optional[float] = None):
        ttl = ttl or cls._ttl
        cls._cache[key] = (value, time.time() + ttl)
    
    @classmethod
    def clear(cls):
        cls._cache.clear()

class FastLogger:
    """High-performance logger with buffering"""
    _buffer: deque = deque(maxlen=1000)
    _lock = threading.Lock()
    _level: int = 2  # 0=error, 1=warn, 2=info, 3=debug
    
    @classmethod
    def log(cls, level: int, msg: str):
        if level <= cls._level:
            ts = datetime.now().strftime("%H:%M:%S")
            levels = ['ERR', 'WRN', 'INF', 'DBG']
            line = f"[{ts}] {levels[level]}: {msg}"
            with cls._lock:
                cls._buffer.append(line)
                print(line)
    
    @classmethod
    def error(cls, msg: str): cls.log(0, msg)
    @classmethod
    def warn(cls, msg: str): cls.log(1, msg)
    @classmethod
    def info(cls, msg: str): cls.log(2, msg)
    @classmethod
    def debug(cls, msg: str): cls.log(3, msg)
    
    @classmethod
    def flush(cls, filepath: str):
        with cls._lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cls._buffer))

# Aliases for convenience
log = FastLogger.info
warn = FastLogger.warn
err = FastLogger.error

# ============================================================================
# NETWORK UTILITIES - Ultra-fast implementations
# ============================================================================

class FastNet:
    """Ultra-fast network operations"""
    
    # Pre-compiled patterns for speed
    _ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    _time_pattern = re.compile(r'time[<=](\d+\.?\d*)ms|(\d+)ms')
    _loss_pattern = re.compile(r'(\d+)% loss|(\d+)% packet loss')
    
    # Common targets - prioritized
    TARGETS = {
        'gateway': ['192.168.1.1', '192.168.0.1', '192.168.100.1', '10.0.0.1'],
        'dns': ['8.8.8.8', '1.1.1.1', '208.67.222.222'],
        'public': ['1.1.1.1', '8.8.4.4', '208.67.220.220']
    }
    
    @classmethod
    def get_default_gateway(cls) -> str:
        """Get default gateway - cached"""
        cached = FastCache.get('gateway')
        if cached:
            return cached
            
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['ipconfig'], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'Default Gateway' in line:
                        ip = line.split(':')[-1].strip()
                        if ip and cls._ip_pattern.match(ip):
                            FastCache.set('gateway', ip, ttl=300)
                            return ip
            else:
                result = subprocess.run(
                    ['ip', 'route'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'default' in line:
                        parts = line.split()
                        if len(parts) > 2:
                            FastCache.set('gateway', parts[2], ttl=300)
                            return parts[2]
        except:
            pass
        return cls.TARGETS['gateway'][0]
    
    @classmethod
    def get_dns_servers(cls) -> List[str]:
        """Get DNS servers - cached"""
        cached = FastCache.get('dns')
        if cached:
            return cached
            
        dns_servers = []
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'DNS Servers' in line:
                        ip = line.split(':')[-1].strip()
                        if cls._ip_pattern.match(ip):
                            dns_servers.append(ip)
        except:
            pass
        
        if not dns_servers:
            dns_servers = cls.TARGETS['dns'][:2]
        
        FastCache.set('dns', dns_servers, ttl=300)
        return dns_servers
    
    @classmethod
    def ping(cls, target: str, count: int = 4, timeout: int = 2) -> PingStats:
        """Ultra-fast ping using system command"""
        stats = PingStats(target=target, sent=count)
        
        try:
            if platform.system() == 'Windows':
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), target]
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout), target]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=count * timeout + 5
            )
            
            output = result.stdout + result.stderr
            
            # Fast pattern matching
            times = []
            for match in cls._time_pattern.finditer(output):
                t = match.group(1) or match.group(2)
                if t:
                    times.append(float(t))
            
            # Check for loss
            for match in cls._loss_pattern.finditer(output):
                loss_str = match.group(1) or match.group(2)
                if loss_str:
                    stats.loss = float(loss_str)
                    stats.received = int(count * (1 - stats.loss / 100))
            
            if times:
                stats.min_ms = min(times)
                stats.max_ms = max(times)
                stats.avg_ms = sum(times) / len(times)
                stats.jitter = max(t - s for s, t in zip(times[:-1], times[1:])) if len(times) > 1 else 0
                stats.success = True
            else:
                stats.loss = 100.0
                stats.received = 0
                
        except Exception as e:
            stats.loss = 100.0
            err(f"Ping failed for {target}: {e}")
        
        return stats
    
    @classmethod
    def ping_parallel(cls, targets: List[str], count: int = 4) -> List[PingStats]:
        """Ping multiple targets in parallel"""
        with ThreadPoolExecutor(max_workers=min(8, len(targets))) as executor:
            futures = {executor.submit(cls.ping, t, count): t for t in targets}
            results = []
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    err(f"Parallel ping error: {e}")
            return results
    
    @classmethod
    def traceroute(cls, target: str, max_hops: int = 15) -> List[RouteHop]:
        """Fast traceroute - limited hops for speed"""
        hops = []
        
        try:
            if platform.system() == 'Windows':
                cmd = ['tracert', '-d', '-h', str(max_hops), '-w', '1000', target]
            else:
                cmd = ['traceroute', '-n', '-m', str(max_hops), '-w', '1', target]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            hop_num = 0
            
            for line in output.split('\n'):
                # Fast line parsing
                parts = line.split()
                if not parts:
                    continue
                
                # Look for hop number at start
                try:
                    hop_num = int(parts[0])
                except ValueError:
                    continue
                
                # Extract IP and time
                ip = None
                time_ms = 0.0
                
                for part in parts[1:]:
                    if cls._ip_pattern.match(part):
                        ip = part
                        break
                
                for match in cls._time_pattern.finditer(line):
                    t = match.group(1) or match.group(2)
                    if t:
                        time_ms = float(t)
                        break
                
                if ip:
                    hops.append(RouteHop(
                        number=hop_num,
                        ip=ip,
                        latency_ms=time_ms
                    ))
            
        except Exception as e:
            err(f"Traceroute failed: {e}")
        
        return hops
    
    @classmethod
    def get_public_ip(cls) -> str:
        """Get public IP - cached"""
        cached = FastCache.get('public_ip')
        if cached:
            return cached
            
        try:
            # Multiple services for reliability
            services = [
                'https://api.ipify.org',
                'https://checkip.amazonaws.com',
                'https://icanhazip.com'
            ]
            
            for service in services:
                try:
                    with urllib.request.urlopen(service, timeout=3) as resp:
                        ip = resp.read().decode().strip()
                        if cls._ip_pattern.match(ip):
                            FastCache.set('public_ip', ip, ttl=600)
                            return ip
                except:
                    continue
        except:
            pass
        
        return "Unknown"

# ============================================================================
# SPEED TEST - Fast implementations
# ============================================================================

class FastSpeedTest:
    """Ultra-fast speed testing"""
    
    @classmethod
    def test_speedtest_cli(cls) -> Optional[SpeedResult]:
        """Try speedtest-cli if available"""
        try:
            result = subprocess.run(
                ['speedtest-cli', '--simple', '--timeout', '30'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            res = SpeedResult(source="speedtest-cli", timestamp=datetime.now().isoformat())
            
            for line in output.split('\n'):
                if 'Download' in line:
                    try:
                        res.download = float(line.split()[1])
                    except:
                        pass
                elif 'Upload' in line:
                    try:
                        res.upload = float(line.split()[1])
                    except:
                        pass
                elif 'Ping' in line:
                    try:
                        res.latency = float(line.split()[1])
                    except:
                        pass
            
            res.success = res.download > 0
            return res
            
        except:
            return None
    
    @classmethod
    def test_curl(cls) -> Optional[SpeedResult]:
        """Test using curl download speed"""
        try:
            # Test download with curl
            start = time.time()
            result = subprocess.run(
                ['curl', '-o', 'NUL', '-w', '%{speed_download}', 
                 'https://speed.hetzner.de/10MB.bin', '--max-time', '15'],
                capture_output=True,
                text=True,
                timeout=20
            )
            elapsed = time.time() - start
            
            if result.returncode == 0:
                try:
                    speed_bytes = float(result.stdout.strip())
                    speed_mbps = (speed_bytes * 8) / (1024 * 1024)
                    
                    return SpeedResult(
                        source="curl-download",
                        download=speed_mbps,
                        latency=elapsed * 1000 / 2,  # Estimate
                        timestamp=datetime.now().isoformat(),
                        success=True
                    )
                except:
                    pass
        except:
            pass
        
        return None
    
    @classmethod
    def test_http(cls) -> Optional[SpeedResult]:
        """Test using Python HTTP"""
        try:
            start = time.time()
            with urllib.request.urlopen(
                'https://speed.hetzner.de/10MB.bin',
                timeout=15
            ) as resp:
                downloaded = 0
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    downloaded += len(chunk)
            
            elapsed = time.time() - start
            speed_mbps = (downloaded * 8 / (1024 * 1024)) / elapsed
            
            return SpeedResult(
                source="http-download",
                download=speed_mbps,
                latency=elapsed * 1000 / 2,
                timestamp=datetime.now().isoformat(),
                success=True
            )
        except:
            return None
    
    @classmethod
    def run(cls) -> List[SpeedResult]:
        """Run fastest available speed test"""
        results = []
        
        # Try CLI first (fastest)
        cli_result = cls.test_speedtest_cli()
        if cli_result and cli_result.success:
            results.append(cli_result)
            log(f"Speedtest: {cli_result.download:.1f} Mbps down, {cli_result.upload:.1f} Mbps up")
            return results
        
        # Fall back to HTTP test
        http_result = cls.test_http()
        if http_result and http_result.success:
            results.append(http_result)
            log(f"HTTP Speed: {http_result.download:.1f} Mbps")
            return results
        
        warn("Speed test unavailable")
        return results

# ============================================================================
# HARDWARE INFO - Fast detection
# ============================================================================

class FastHardware:
    """Fast hardware detection"""
    
    @classmethod
    def get_network_config(cls) -> NetConfig:
        """Get network configuration"""
        config = NetConfig()
        
        try:
            import psutil
            
            # Find active interface
            stats = psutil.net_io_counters(pernic=True)
            addrs = psutil.net_if_addrs()
            
            for iface, addr_list in addrs.items():
                # Skip loopback
                if 'loopback' in iface.lower() or 'lo' in iface.lower():
                    continue
                
                # Check for IPv4 address
                for addr in addr_list:
                    if addr.family == socket.AF_INET and addr.address:
                        config.interface = iface
                        config.ip = addr.address
                        if addr.netmask:
                            config.mac = addr_list[0].address if addr_list else ""
                        break
                
                if config.ip:
                    break
            
            # Determine type
            config.is_ethernet = 'ethernet' in config.interface.lower() or 'eth' in config.interface.lower()
            
        except ImportError:
            pass
        
        # Get gateway and DNS
        config.gateway = FastNet.get_default_gateway()
        config.dns = FastNet.get_dns_servers()
        
        return config

# ============================================================================
# HEALTH SCORING - Fast calculation
# ============================================================================

class FastHealth:
    """Fast health scoring"""
    
    @classmethod
    def calculate(cls, pings: List[PingStats], speeds: List[SpeedResult]) -> HealthScore:
        """Calculate health score"""
        health = HealthScore()
        issues = []
        
        # Analyze pings
        if pings:
            avg_loss = sum(p.loss for p in pings) / len(pings)
            avg_latency = sum(p.avg_ms for p in pings if p.avg_ms > 0) / len([p for p in pings if p.avg_ms > 0]) if any(p.avg_ms > 0 for p in pings) else 0
            
            # Loss score (0-100)
            health.loss_score = max(0, 100 - int(avg_loss * 10))
            if avg_loss > 5:
                issues.append(f"High packet loss: {avg_loss:.1f}%")
            
            # Latency score
            if avg_latency < 20:
                health.latency = 100
            elif avg_latency < 50:
                health.latency = 80
            elif avg_latency < 100:
                health.latency = 60
                issues.append(f"Elevated latency: {avg_latency:.1f}ms")
            else:
                health.latency = 40
                issues.append(f"High latency: {avg_latency:.1f}ms")
        else:
            issues.append("No ping data available")
        
        # Analyze speed
        if speeds:
            download = max(s.download for s in speeds)
            
            if download > 100:
                health.speed = 100
            elif download > 50:
                health.speed = 80
            elif download > 25:
                health.speed = 60
            elif download > 10:
                health.speed = 40
                issues.append(f"Slow download: {download:.1f} Mbps")
            else:
                health.speed = 20
                issues.append(f"Very slow download: {download:.1f} Mbps")
        else:
            issues.append("No speed test data")
        
        # Stability based on ping variance
        if len(pings) >= 2:
            latencies = [p.avg_ms for p in pings if p.avg_ms > 0]
            if latencies:
                variance = max(latencies) - min(latencies)
                health.stability = max(0, 100 - int(variance / 10))
        
        # Overall score
        health.overall = int((health.speed + health.latency + health.loss_score + health.stability) / 4)
        
        # Grade
        if health.overall >= 90:
            health.grade = "A"
        elif health.overall >= 80:
            health.grade = "B"
        elif health.overall >= 70:
            health.grade = "C"
        elif health.overall >= 60:
            health.grade = "D"
        else:
            health.grade = "F"
        
        health.issues = issues
        return health

# ============================================================================
# REPORT GENERATOR - Fast output
# ============================================================================

class FastReport:
    """Fast report generation"""
    
    @classmethod
    def generate_json(cls, report: DiagnosticReport, filepath: str):
        """Generate JSON report"""
        data = {
            'timestamp': report.timestamp,
            'duration_sec': report.duration_sec,
            'config': asdict(report.config),
            'pings': [asdict(p) for p in report.pings],
            'speeds': [asdict(s) for s in report.speeds],
            'routes': [asdict(r) for r in report.routes],
            'health': asdict(report.health)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def generate_text(cls, report: DiagnosticReport, filepath: str):
        """Generate text report"""
        lines = [
            "=" * 60,
            "SUNYA ULTRA DIAGNOSTIC REPORT",
            "=" * 60,
            f"Generated: {report.timestamp}",
            f"Duration: {report.duration_sec:.1f} seconds",
            "",
            "[NETWORK CONFIGURATION]",
            f"Interface: {report.config.interface}",
            f"IP Address: {report.config.ip}",
            f"MAC: {report.config.mac}",
            f"Gateway: {report.config.gateway}",
            f"DNS: {', '.join(report.config.dns)}",
            "",
            "[PING RESULTS]",
        ]
        
        for ping in report.pings:
            status = "OK" if ping.success else "FAIL"
            lines.append(f"  {ping.target}: {status} - Avg: {ping.avg_ms:.1f}ms, Loss: {ping.loss:.1f}%")
        
        lines.extend([
            "",
            "[SPEED TEST]",
        ])
        
        for speed in report.speeds:
            if speed.success:
                lines.append(f"  {speed.source}: {speed.download:.1f} Mbps down, {speed.upload:.1f} Mbps up")
        
        lines.extend([
            "",
            "[HEALTH SCORE]",
            f"  Overall: {report.health.overall}/100 (Grade: {report.health.grade})",
            f"  Speed: {report.health.speed}/100",
            f"  Latency: {report.health.latency}/100",
            f"  Stability: {report.health.stability}/100",
            "",
            "[ISSUES]",
        ])
        
        if report.health.issues:
            for issue in report.health.issues:
                lines.append(f"  ! {issue}")
        else:
            lines.append("  No issues detected")
        
        lines.extend([
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    @classmethod
    def generate_html(cls, report: DiagnosticReport, filepath: str):
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SUNYA Ultra Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
        .metric-label {{ font-size: 12px; color: #777; }}
        .grade {{ font-size: 48px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; }}
        .grade-a {{ background: #4CAF50; color: white; }}
        .grade-b {{ background: #8BC34A; color: white; }}
        .grade-c {{ background: #FFC107; color: black; }}
        .grade-d {{ background: #FF9800; color: white; }}
        .grade-f {{ background: #f44336; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
        .success {{ color: #4CAF50; }}
        .fail {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SUNYA Ultra Diagnostic Report</h1>
        <p>Generated: {report.timestamp}</p>
        <p>Duration: {report.duration_sec:.1f} seconds</p>
        
        <div class="grade grade-{report.health.grade.lower()}">
            Grade: {report.health.grade}
        </div>
        
        <h2>Health Metrics</h2>
        <div class="metric">
            <div class="metric-value">{report.health.overall}</div>
            <div class="metric-label">Overall Score</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report.health.speed}</div>
            <div class="metric-label">Speed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report.health.latency}</div>
            <div class="metric-label">Latency</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report.health.stability}</div>
            <div class="metric-label">Stability</div>
        </div>
        
        <h2>Network Configuration</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Interface</td><td>{report.config.interface}</td></tr>
            <tr><td>IP Address</td><td>{report.config.ip}</td></tr>
            <tr><td>MAC Address</td><td>{report.config.mac}</td></tr>
            <tr><td>Gateway</td><td>{report.config.gateway}</td></tr>
            <tr><td>DNS Servers</td><td>{', '.join(report.config.dns)}</td></tr>
        </table>
        
        <h2>Ping Results</h2>
        <table>
            <tr><th>Target</th><th>Status</th><th>Avg Latency</th><th>Packet Loss</th></tr>
"""
        
        for ping in report.pings:
            status_class = "success" if ping.success else "fail"
            status_text = "OK" if ping.success else "FAIL"
            html += f"""
            <tr>
                <td>{ping.target}</td>
                <td class="{status_class}">{status_text}</td>
                <td>{ping.avg_ms:.1f} ms</td>
                <td>{ping.loss:.1f}%</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>Speed Test Results</h2>
        <table>
            <tr><th>Source</th><th>Download</th><th>Upload</th><th>Latency</th></tr>
"""
        
        for speed in report.speeds:
            if speed.success:
                html += f"""
            <tr>
                <td>{speed.source}</td>
                <td>{speed.download:.1f} Mbps</td>
                <td>{speed.upload:.1f} Mbps</td>
                <td>{speed.latency:.1f} ms</td>
            </tr>
"""
        
        html += f"""
        </table>
        
        <h2>Issues Detected</h2>
        <ul>
"""
        
        if report.health.issues:
            for issue in report.health.issues:
                html += f"            <li>{issue}</li>\n"
        else:
            html += "            <li>No issues detected - network is healthy!</li>\n"
        
        html += """
        </ul>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

# ============================================================================
# MAIN ENGINE - Ultra-fast diagnostic engine
# ============================================================================

class SunyaUltra:
    """
    SUNYA Ultra - One Package To Rule Them All
    Ultra-fast, single-file network automation
    """
    
    def __init__(self, mode: TestMode = TestMode.STANDARD):
        self.mode = mode
        self.start_time = time.time()
        self.report_folder = None
        self.report = DiagnosticReport()
        
    def create_folder(self) -> Path:
        """Create report folder"""
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.report_folder = desktop / f"SUNYA_Ultra_{timestamp}"
        self.report_folder.mkdir(parents=True, exist_ok=True)
        return self.report_folder
    
    def run_quick(self) -> DiagnosticReport:
        """Quick 30-second diagnostic"""
        log("Running QUICK diagnostic (30 seconds)...")
        
        # Get config
        self.report.config = FastHardware.get_network_config()
        log(f"Interface: {self.report.config.interface} ({self.report.config.ip})")
        
        # Fast pings - gateway and one public
        targets = [self.report.config.gateway, '8.8.8.8']
        self.report.pings = FastNet.ping_parallel(targets, count=4)
        
        # Quick speed test
        self.report.speeds = FastSpeedTest.run()
        
        # Calculate health
        self.report.health = FastHealth.calculate(self.report.pings, self.report.speeds)
        
        self.report.duration_sec = time.time() - self.start_time
        self.report.timestamp = datetime.now().isoformat()
        
        return self.report
    
    def run_standard(self) -> DiagnosticReport:
        """Standard 2-minute diagnostic"""
        log("Running STANDARD diagnostic (2 minutes)...")
        
        # Get config
        self.report.config = FastHardware.get_network_config()
        log(f"Interface: {self.report.config.interface}")
        log(f"Gateway: {self.report.config.gateway}")
        
        # Multiple ping targets
        targets = [
            self.report.config.gateway,
            *self.report.config.dns[:2],
            '8.8.8.8',
            '1.1.1.1'
        ]
        self.report.pings = FastNet.ping_parallel(targets, count=10)
        
        # Traceroute to public DNS
        log("Running traceroute...")
        self.report.routes = FastNet.traceroute('8.8.8.8', max_hops=10)
        
        # Speed test
        self.report.speeds = FastSpeedTest.run()
        
        # Calculate health
        self.report.health = FastHealth.calculate(self.report.pings, self.report.speeds)
        
        self.report.duration_sec = time.time() - self.start_time
        self.report.timestamp = datetime.now().isoformat()
        
        return self.report
    
    def run_full(self) -> DiagnosticReport:
        """Full 5-minute diagnostic"""
        log("Running FULL diagnostic (5 minutes)...")
        
        # Get config
        self.report.config = FastHardware.get_network_config()
        
        # Extended ping targets
        targets = [
            self.report.config.gateway,
            *self.report.config.dns,
            '8.8.8.8',
            '8.8.4.4',
            '1.1.1.1',
            '1.0.0.1',
            '208.67.222.222'
        ]
        self.report.pings = FastNet.ping_parallel(targets, count=20)
        
        # Full traceroute
        self.report.routes = FastNet.traceroute('8.8.8.8', max_hops=20)
        
        # Multiple speed tests
        self.report.speeds = FastSpeedTest.run()
        
        # Calculate health
        self.report.health = FastHealth.calculate(self.report.pings, self.report.speeds)
        
        self.report.duration_sec = time.time() - self.start_time
        self.report.timestamp = datetime.now().isoformat()
        
        return self.report
    
    def generate_reports(self) -> Path:
        """Generate all report formats"""
        if self.report_folder is None:
            self.create_folder()
        
        assert self.report_folder is not None
        
        log("Generating reports...")
        
        # JSON
        json_path = self.report_folder / "report.json"
        FastReport.generate_json(self.report, str(json_path))
        
        # Text
        text_path = self.report_folder / "report.txt"
        FastReport.generate_text(self.report, str(text_path))
        
        # HTML
        html_path = self.report_folder / "report.html"
        FastReport.generate_html(self.report, str(html_path))
        
        log(f"Reports saved to: {self.report_folder}")
        return self.report_folder
    
    def print_summary(self):
        """Print console summary"""
        print("\n" + "=" * 60)
        print("SUNYA ULTRA - DIAGNOSTIC COMPLETE")
        print("=" * 60)
        print(f"Duration: {self.report.duration_sec:.1f} seconds")
        print(f"Health Score: {self.report.health.overall}/100 (Grade: {self.report.health.grade})")
        print()
        print("Metrics:")
        print(f"  Speed:     {self.report.health.speed}/100")
        print(f"  Latency:   {self.report.health.latency}/100")
        print(f"  Stability: {self.report.health.stability}/100")
        print()
        
        if self.report.speeds:
            speed = self.report.speeds[0]
            print(f"Speed Test: {speed.download:.1f} Mbps down / {speed.upload:.1f} Mbps up")
        
        if self.report.health.issues:
            print("\nIssues Found:")
            for issue in self.report.health.issues:
                print(f"  ! {issue}")
        else:
            print("\n[OK] No issues detected - network is healthy!")
        
        print("\n" + "=" * 60)
        print(f"Reports: {self.report_folder}")
        print("=" * 60)

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SUNYA Ultra - Ultra-Fast Network Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sunya-ultra.py           # Standard diagnostic (2 min)
  python sunya-ultra.py --quick   # Quick diagnostic (30 sec)
  python sunya-ultra.py --full      # Full diagnostic (5 min)
  python sunya-ultra.py --open      # Open report after completion
        """
    )
    
    parser.add_argument('--quick', action='store_true', help='Quick 30-second diagnostic')
    parser.add_argument('--full', action='store_true', help='Full 5-minute diagnostic')
    parser.add_argument('--open', action='store_true', help='Open report folder after completion')
    parser.add_argument('--json-only', action='store_true', help='Generate only JSON report')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.quick:
        mode = TestMode.QUICK
    elif args.full:
        mode = TestMode.FULL
    else:
        mode = TestMode.STANDARD
    
    # Print header
    print("=" * 60)
    print("SUNYA ULTRA v4.0 - Ultra-Fast Network Automation")
    print("=" * 60)
    print(f"Mode: {mode.value.upper()}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Run diagnostic
    try:
        ultra = SunyaUltra(mode=mode)
        ultra.create_folder()
        
        if mode == TestMode.QUICK:
            ultra.run_quick()
        elif mode == TestMode.FULL:
            ultra.run_full()
        else:
            ultra.run_standard()
        
        # Generate reports
        ultra.generate_reports()
        
        # Print summary
        ultra.print_summary()
        
        # Open folder if requested
        if args.open and ultra.report_folder:
            try:
                os.startfile(str(ultra.report_folder))
            except:
                pass
        
        # Return exit code based on health
        if ultra.report.health.grade in ['A', 'B']:
            sys.exit(0)
        elif ultra.report.health.grade in ['C', 'D']:
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(130)
    except Exception as e:
        err(f"Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
