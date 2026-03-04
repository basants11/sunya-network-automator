#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA MASTER DIAGNOSTIC TOOL v5.0.0
Unified Network Diagnostic & Automation Platform
Combines all diagnostic capabilities into one powerful tool

Usage: python sunya-master.py [--quick|--standard|--full|--monitor]
"""

import os
import sys
import time
import json
import socket
import subprocess
import platform
import datetime
import threading
import tempfile
import re
import gc
import psutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

__version__ = "5.0.0"
__author__ = "SUNYA Networking"

class TestMode(Enum):
    QUICK = "quick"
    STANDARD = "standard"
    FULL = "full"
    MONITOR = "monitor"

MODE_CONFIG = {
    TestMode.QUICK: {
        'ping_count': 4,
        'ping_timeout': 2,
        'traceroute_max_hops': 10,
        'load_test_duration': 10,
        'parallel_workers': 4,
        'description': 'Quick 30-second network health check'
    },
    TestMode.STANDARD: {
        'ping_count': 10,
        'ping_timeout': 3,
        'traceroute_max_hops': 15,
        'load_test_duration': 30,
        'parallel_workers': 8,
        'description': 'Standard 2-minute comprehensive diagnostic'
    },
    TestMode.FULL: {
        'ping_count': 20,
        'ping_timeout': 5,
        'traceroute_max_hops': 30,
        'load_test_duration': 60,
        'parallel_workers': 16,
        'description': 'Full 5-minute deep diagnostic analysis'
    },
}

TARGETS = {
    'gateway': ['192.168.1.1', '192.168.0.1', '192.168.100.1', '10.0.0.1'],
    'dns': ['8.8.8.8', '1.1.1.1', '208.67.222.222'],
    'public': ['1.1.1.1', '8.8.4.4'],
    'websites': ['google.com', 'cloudflare.com']
}

@dataclass
class PingResult:
    target: str = ""
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0
    avg_latency: float = 0.0
    jitter: float = 0.0
    success: bool = False
    timestamp: str = ""

@dataclass
class SpeedResult:
    source: str = ""
    download_speed: float = 0.0
    upload_speed: float = 0.0
    latency: float = 0.0
    server_name: str = ""
    success: bool = False
    timestamp: str = ""

@dataclass
class RouteHop:
    number: int = 0
    host: str = ""
    ip: str = ""
    latency_ms: float = 0.0
    loss_percent: float = 0.0

@dataclass
class TracerouteResult:
    target: str = ""
    total_hops: int = 0
    hops: List[RouteHop] = field(default_factory=list)
    worst_hop: int = 0
    worst_latency: float = 0.0
    bottleneck_detected: bool = False
    success: bool = False

@dataclass
class LoadTestResult:
    target: str = ""
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    avg_latency: float = 0.0
    stability_score: float = 0.0
    success: bool = False

@dataclass
class HealthScore:
    overall: int = 0
    speed: int = 0
    latency: int = 0
    loss_score: int = 0
    stability: int = 0
    grade: str = "F"
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class TestSuiteResult:
    timestamp: str = ""
    mode: str = ""
    duration_seconds: float = 0.0
    ping_results: List[PingResult] = field(default_factory=list)
    speed_results: List[SpeedResult] = field(default_factory=list)
    traceroute_results: List[TracerouteResult] = field(default_factory=list)
    load_test_results: List[LoadTestResult] = field(default_factory=list)
    health_score: HealthScore = field(default_factory=HealthScore)

class SunyaMasterDiagnostic:
    """Unified diagnostic tool combining all SUNYA capabilities"""
    
    def __init__(self, mode: TestMode = TestMode.STANDARD, output_dir: Optional[str] = None):
        self.mode = mode
        self.config = MODE_CONFIG[mode]
        self.platform = platform.system().lower()
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.start_time = time.time()
        
        # Output directories
        if output_dir:
            self.base_dir = output_dir
        else:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            self.base_dir = os.path.join(desktop, f"SUNYA_Master_{self.timestamp}")
        
        self.subdirs = {}
        self.results = TestSuiteResult(timestamp=self.timestamp, mode=mode.value)
        self.executor = ThreadPoolExecutor(max_workers=self.config['parallel_workers'])
        
        self._create_directories()
        self._print_banner()
    
    def _print_banner(self):
        """Print SUNYA banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║              SUNYA MASTER DIAGNOSTIC TOOL v5.0.0              ║
║              Unified Network Diagnostic Platform              ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"Mode: {self.mode.value.upper()}")
        print(f"Output: {self.base_dir}")
        print(f"Description: {self.config['description']}")
        print()
    
    def _create_directories(self):
        """Create output directory structure"""
        subdirs = ['reports', 'screenshots', 'raw_data', 'ping_tests', 'speed_tests', 'traceroute', 'load_tests']
        for subdir in subdirs:
            path = os.path.join(self.base_dir, subdir)
            os.makedirs(path, exist_ok=True)
            self.subdirs[subdir] = path
    
    def run_ping_test(self, target: str, count: int = None, timeout: int = None) -> PingResult:
        """Run ping test to target"""
        count = count or self.config['ping_count']
        timeout = timeout or self.config['ping_timeout']
        result = PingResult(target=target, packets_sent=count)
        result.timestamp = datetime.datetime.now().isoformat()
        
        try:
            if self.platform == 'windows':
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), target]
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout), target]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=count * timeout + 10)
            output = process.stdout
            
            # Parse packet loss
            loss_match = re.search(r'(\d+)% loss|(\d+)% packet loss', output, re.IGNORECASE)
            if loss_match:
                result.packet_loss_percent = float(loss_match.group(1) or loss_match.group(2))
                result.packets_received = int(count * (100 - result.packet_loss_percent) / 100)
            
            # Parse latency stats
            if self.platform == 'windows':
                stats_match = re.search(r'Minimum\s*=\s*(\d+)ms[^,]*,\s*Maximum\s*=\s*(\d+)ms[^,]*,\s*Average\s*=\s*(\d+)ms', output)
                if stats_match:
                    result.min_latency = float(stats_match.group(1))
                    result.max_latency = float(stats_match.group(2))
                    result.avg_latency = float(stats_match.group(3))
            else:
                stats_match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
                if stats_match:
                    result.min_latency = float(stats_match.group(1))
                    result.avg_latency = float(stats_match.group(2))
                    result.max_latency = float(stats_match.group(3))
                    result.jitter = float(stats_match.group(4))
            
            result.success = True
        except Exception as e:
            result.packet_loss_percent = 100.0
        
        return result
    
    def run_ping_suite(self) -> List[PingResult]:
        """Run comprehensive ping test suite"""
        print("[INFO] Running ping test suite...")
        
        if self.mode == TestMode.QUICK:
            targets = ['8.8.8.8', '1.1.1.1']
        elif self.mode == TestMode.FULL:
            targets = TARGETS['dns'] + TARGETS['public'] + TARGETS['websites']
        else:
            targets = TARGETS['dns'] + TARGETS['websites']
        
        results = []
        futures = {self.executor.submit(self.run_ping_test, target): target for target in targets}
        
        for future in as_completed(futures):
            target = futures[future]
            try:
                result = future.result(timeout=30)
                results.append(result)
                status = "OK" if result.success else "FAIL"
                print(f"  [{status}] {target}: {result.avg_latency:.1f}ms ({result.packet_loss_percent:.0f}% loss)")
            except Exception as e:
                print(f"  [FAIL] {target}: Exception - {e}")
        
        self.results.ping_results = results
        print(f"[INFO] Ping suite completed: {len([r for r in results if r.success])}/{len(results)} successful")
        return results
    
    def run_speedtest(self) -> SpeedResult:
        """Run speedtest using speedtest-cli"""
        result = SpeedResult(source="speedtest-cli")
        result.timestamp = datetime.datetime.now().isoformat()
        
        if not SPEEDTEST_AVAILABLE:
            result.success = False
            return result
        
        try:
            print("[INFO] Running speedtest (this may take 30-60 seconds)...")
            st = speedtest.Speedtest()
            st.get_best_server()
            
            result.server_name = st.results.server.get('sponsor', 'Unknown')
            result.latency = st.results.ping
            
            download_bits = st.download()
            result.download_speed = download_bits / 1_000_000
            
            upload_bits = st.upload()
            result.upload_speed = upload_bits / 1_000_000
            
            result.success = True
            print(f"  [OK] Speedtest: {result.download_speed:.1f} Mbps down / {result.upload_speed:.1f} Mbps up")
        except Exception as e:
            result.success = False
            print(f"  [FAIL] Speedtest failed: {e}")
        
        return result
    
    def run_speed_suite(self) -> List[SpeedResult]:
        """Run speed test suite"""
        print("[INFO] Running speed test suite...")
        results = []
        
        if SPEEDTEST_AVAILABLE:
            result = self.run_speedtest()
            if result.success:
                results.append(result)
        else:
            print("  [SKIP] speedtest-cli not available - install with: pip install speedtest-cli")
        
        self.results.speed_results = results
        return results
    
    def run_traceroute(self, target: str = "8.8.8.8") -> TracerouteResult:
        """Run traceroute to target"""
        max_hops = self.config['traceroute_max_hops']
        result = TracerouteResult(target=target)
        
        try:
            if self.platform == 'windows':
                cmd = ['tracert', '-h', str(max_hops), target]
            else:
                cmd = ['traceroute', '-m', str(max_hops), target]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=max_hops * 3)
            output = process.stdout
            
            # Parse hops
            for line in output.split('\n'):
                hop_match = re.match(r'^\s*(\d+)\s+', line)
                if hop_match:
                    hop_num = int(hop_match.group(1))
                    hop = RouteHop(number=hop_num)
                    
                    if '*' in line:
                        hop.host = "* * *"
                    else:
                        ip_match = re.search(r'\[(\d+\.\d+\.\d+\.\d+)\]|(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            hop.ip = ip_match.group(1) or ip_match.group(2)
                        
                        host_match = re.search(r'\s+([\w\-\.]+)\s*[\[\(]?', line)
                        if host_match:
                            hop.host = host_match.group(1)
                        
                        latencies = re.findall(r'(\d+)\s*ms', line)
                        if latencies:
                            hop.latency_ms = sum(int(l) for l in latencies) / len(latencies)
                    
                    result.hops.append(hop)
            
            result.total_hops = len(result.hops)
            result.success = True
            
            # Find worst hop
            if result.hops:
                latencies = [(h.number, h.latency_ms) for h in result.hops if h.latency_ms > 0]
                if latencies:
                    worst = max(latencies, key=lambda x: x[1])
                    result.worst_hop = worst[0]
                    result.worst_latency = worst[1]
                    result.bottleneck_detected = True
            
        except Exception as e:
            result.success = False
        
        return result
    
    def run_traceroute_suite(self) -> List[TracerouteResult]:
        """Run traceroute suite"""
        print("[INFO] Running traceroute suite...")
        
        targets = ['8.8.8.8', '1.1.1.1'] if self.mode != TestMode.FULL else ['8.8.8.8', '1.1.1.1', 'google.com']
        
        results = []
        for target in targets:
            result = self.run_traceroute(target)
            results.append(result)
            if result.success:
                print(f"  [OK] {target}: {result.total_hops} hops, worst at hop {result.worst_hop}")
            else:
                print(f"  [FAIL] {target}: Failed")
        
        self.results.traceroute_results = results
        return results
    
    def run_load_test(self, target: str = "8.8.8.8") -> LoadTestResult:
        """Run load/stress test"""
        duration = self.config['load_test_duration']
        result = LoadTestResult(target=target, packets_sent=0)
        
        try:
            latencies = []
            packets_sent = 0
            packets_received = 0
            start_time = time.time()
            
            while time.time() - start_time < duration:
                ping_result = self.run_ping_test(target, count=1, timeout=2)
                packets_sent += 1
                if ping_result.success:
                    packets_received += 1
                    if ping_result.avg_latency > 0:
                        latencies.append(ping_result.avg_latency)
                time.sleep(0.1)
            
            result.packets_sent = packets_sent
            result.packets_received = packets_received
            result.packet_loss_percent = ((packets_sent - packets_received) / packets_sent * 100) if packets_sent > 0 else 0
            
            if latencies:
                result.avg_latency = sum(latencies) / len(latencies)
                result.stability_score = 100 - min(100, result.packet_loss_percent * 10)
            
            result.success = True
            print(f"  [OK] Load test: {packets_sent} packets, {result.packet_loss_percent:.1f}% loss")
        except Exception as e:
            result.success = False
            print(f"  [FAIL] Load test failed: {e}")
        
        return result
    
    def run_load_test_suite(self) -> List[LoadTestResult]:
        """Run load test suite"""
        print("[INFO] Running load test suite...")
        
        targets = ['8.8.8.8']
        if self.mode == TestMode.FULL:
            targets.append('1.1.1.1')
        
        results = []
        for target in targets:
            result = self.run_load_test(target)
            results.append(result)
        
        self.results.load_test_results = results
        return results
    
    def calculate_health_score(self) -> HealthScore:
        """Calculate network health score"""
        print("[INFO] Calculating health score...")
        
        score = HealthScore()
        issues = []
        recommendations = []
        
        # Speed score
        if self.results.speed_results:
            speeds = [r.download_speed for r in self.results.speed_results if r.success]
            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                if avg_speed >= 100:
                    score.speed = 100
                elif avg_speed >= 50:
                    score.speed = 80
                elif avg_speed >= 25:
                    score.speed = 60
                elif avg_speed >= 10:
                    score.speed = 40
                else:
                    score.speed = 20
                
                if avg_speed < 10:
                    issues.append(f"Slow download speed: {avg_speed:.1f} Mbps")
                    recommendations.append("Consider upgrading internet plan")
        
        # Latency score
        if self.results.ping_results:
            latencies = [r.avg_latency for r in self.results.ping_results if r.success and r.avg_latency > 0]
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                if avg_latency <= 10:
                    score.latency = 100
                elif avg_latency <= 30:
                    score.latency = 80
                elif avg_latency <= 50:
                    score.latency = 60
                elif avg_latency <= 100:
                    score.latency = 40
                else:
                    score.latency = 20
                
                if avg_latency > 100:
                    issues.append(f"High latency: {avg_latency:.1f}ms")
        
        # Loss score
        if self.results.ping_results:
            losses = [r.packet_loss_percent for r in self.results.ping_results if r.success]
            if losses:
                avg_loss = sum(losses) / len(losses)
                score.loss_score = max(0, 100 - int(avg_loss * 10))
                
                if avg_loss > 5:
                    issues.append(f"High packet loss: {avg_loss:.1f}%")
                    recommendations.append("Check physical connections")
        
        # Stability score
        if self.results.load_test_results:
            stabilities = [r.stability_score for r in self.results.load_test_results if r.success]
            if stabilities:
                score.stability = int(sum(stabilities) / len(stabilities))
        
        # Calculate overall
        weights = {'speed': 0.25, 'latency': 0.25, 'loss': 0.25, 'stability': 0.25}
        score.overall = int(
            score.speed * weights['speed'] +
            score.latency * weights['latency'] +
            score.loss_score * weights['loss'] +
            score.stability * weights['stability']
        )
        
        # Grade
        if score.overall >= 90:
            score.grade = 'A'
        elif score.overall >= 75:
            score.grade = 'B'
        elif score.overall >= 60:
            score.grade = 'C'
        elif score.overall >= 40:
            score.grade = 'D'
        else:
            score.grade = 'F'
        
        score.issues = issues
        score.recommendations = recommendations
        
        self.results.health_score = score
        print(f"[INFO] Health Score: {score.overall}/100 (Grade {score.grade})")
        return score
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        print("[INFO] Generating report...")
        
        report_path = os.path.join(self.subdirs['reports'], f"SUNYA_Master_Report_{self.timestamp}.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("           SUNYA MASTER DIAGNOSTIC REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {self.results.timestamp}\n")
            f.write(f"Mode: {self.mode.value.upper()}\n")
            f.write(f"Duration: {self.results.duration_seconds:.1f} seconds\n\n")
            
            # Health Score
            health = self.results.health_score
            f.write("-" * 70 + "\n")
            f.write("HEALTH SCORE\n")
            f.write("-" * 70 + "\n")
            f.write(f"Overall Score: {health.overall}/100 (Grade {health.grade})\n")
            f.write(f"Speed Score: {health.speed}/100\n")
            f.write(f"Latency Score: {health.latency}/100\n")
            f.write(f"Loss Score: {health.loss_score}/100\n")
            f.write(f"Stability Score: {health.stability}/100\n\n")
            
            if health.issues:
                f.write("Issues Found:\n")
                for issue in health.issues:
                    f.write(f"  - {issue}\n")
                f.write("\n")
            
            if health.recommendations:
                f.write("Recommendations:\n")
                for rec in health.recommendations:
                    f.write(f"  - {rec}\n")
                f.write("\n")
            
            # Ping Results
            f.write("-" * 70 + "\n")
            f.write("PING TEST RESULTS\n")
            f.write("-" * 70 + "\n")
            for result in self.results.ping_results:
                status = "OK" if result.success else "FAIL"
                f.write(f"{result.target}: [{status}] {result.avg_latency:.1f}ms ({result.packet_loss_percent:.0f}% loss)\n")
            f.write("\n")
            
            # Speed Results
            f.write("-" * 70 + "\n")
            f.write("SPEED TEST RESULTS\n")
            f.write("-" * 70 + "\n")
            for result in self.results.speed_results:
                if result.success:
                    f.write(f"Source: {result.source}\n")
                    f.write(f"  Download: {result.download_speed:.2f} Mbps\n")
                    f.write(f"  Upload: {result.upload_speed:.2f} Mbps\n")
                    f.write(f"  Latency: {result.latency:.1f}ms\n")
                    f.write(f"  Server: {result.server_name}\n\n")
            
            # Traceroute Results
            f.write("-" * 70 + "\n")
            f.write("TRACEROUTE RESULTS\n")
            f.write("-" * 70 + "\n")
            for result in self.results.traceroute_results:
                if result.success:
                    f.write(f"Target: {result.target}\n")
                    f.write(f"  Total Hops: {result.total_hops}\n")
                    f.write(f"  Worst Hop: #{result.worst_hop} ({result.worst_latency:.1f}ms)\n")
                    f.write(f"  Bottleneck: {'Yes' if result.bottleneck_detected else 'No'}\n\n")
            
            # Load Test Results
            f.write("-" * 70 + "\n")
            f.write("LOAD TEST RESULTS\n")
            f.write("-" * 70 + "\n")
            for result in self.results.load_test_results:
                if result.success:
                    f.write(f"Target: {result.target}\n")
                    f.write(f"  Packets: {result.packets_sent} sent, {result.packets_received} received\n")
                    f.write(f"  Loss: {result.packet_loss_percent:.1f}%\n")
                    f.write(f"  Avg Latency: {result.avg_latency:.1f}ms\n")
                    f.write(f"  Stability: {result.stability_score:.1f}%\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("End of Report\n")
            f.write("=" * 70 + "\n")
        
        print(f"[INFO] Report saved: {report_path}")
        return report_path
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("\n" + "=" * 70)
        print("STARTING DIAGNOSTIC SUITE")
        print("=" * 70 + "\n")
        
        # Run tests
        self.run_ping_suite()
        self.run_speed_suite()
        self.run_traceroute_suite()
        self.run_load_test_suite()
        
        # Calculate health score
        self.calculate_health_score()
        
        # Update duration
        self.results.duration_seconds = time.time() - self.start_time
        
        # Generate report
        report_path = self.generate_report()
        
        # Print summary
        print("\n" + "=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)
        print(f"Total Duration: {self.results.duration_seconds:.1f} seconds")
        print(f"Health Score: {self.results.health_score.overall}/100 (Grade {self.results.health_score.grade})")
        print(f"Report: {report_path}")
        print("=" * 70)
        
        return self.results
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SUNYA Master Diagnostic Tool')
    parser.add_argument('--quick', action='store_true', help='Quick 30-second mode')
    parser.add_argument('--full', action='store_true', help='Full 5-minute mode')
    parser.add_argument('--monitor', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--output', type=str, help='Custom output directory')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.quick:
        mode = TestMode.QUICK
    elif args.full:
        mode = TestMode.FULL
    elif args.monitor:
        mode = TestMode.MONITOR
    else:
        mode = TestMode.STANDARD
    
    # Create and run diagnostic
    diagnostic = SunyaMasterDiagnostic(mode=mode, output_dir=args.output)
    
    try:
        if mode == TestMode.MONITOR:
            print("Monitor mode not fully implemented in this version")
        else:
            diagnostic.run_all_tests()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    finally:
        diagnostic.cleanup()

if __name__ == "__main__":
    main()
