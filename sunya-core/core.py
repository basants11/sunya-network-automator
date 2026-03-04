#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sunya Networking Core Engine
Professional Network Automation & Diagnostics Suite
"""

import os
import sys
import time
import json
import logging
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Any
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sunya.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SunyaCore:
    """Core engine for Sunya Networking diagnostics platform"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.report_dir = None
        self.network_fingerprint = None
        self.diagnostics_results = {}
        self.test_config = {
            'test_depth': 'standard',  # 'quick', 'standard', 'deep'
            'max_test_duration': 300,  # 5 minutes
            'short_circuit': True,
            'cache_enabled': True,
            'confidence_threshold': 0.7  # 70% confidence required for diagnosis
        }
        self.test_cache = {}
        self.start_time = None
        
    def generate_network_fingerprint(self) -> Dict[str, Any]:
        """Generate unique network fingerprint for duplicate detection"""
        logger.info("Generating network fingerprint...")
        
        try:
            import psutil
            import socket
            
            fingerprint = {
                'timestamp': datetime.now().isoformat(),
                'platform': self.platform,
                'interfaces': [],
                'gateway': None,
                'dns_servers': []
            }
            
            # Get network interfaces
            if_addrs = psutil.net_if_addrs()
            for interface, addrs in if_addrs.items():
                if_info = {
                    'name': interface,
                    'type': 'unknown',
                    'ip_addresses': []
                }
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        if_info['ip_addresses'].append(addr.address)
                        
                # Determine interface type (Wi-Fi, Ethernet, etc.)
                if 'wi-fi' in interface.lower() or 'wireless' in interface.lower():
                    if_info['type'] = 'wifi'
                elif 'ethernet' in interface.lower() or 'eth' in interface.lower():
                    if_info['type'] = 'ethernet'
                elif 'loopback' in interface.lower() or 'lo' in interface.lower():
                    if_info['type'] = 'loopback'
                elif 'bluetooth' in interface.lower():
                    if_info['type'] = 'bluetooth'
                    
                fingerprint['interfaces'].append(if_info)
                
            # Get default gateway
            if self.platform == 'windows':
                try:
                    output = subprocess.check_output(['ipconfig'], universal_newlines=True)
                    for line in output.splitlines():
                        if 'Default Gateway' in line:
                            gateway = line.split(':')[-1].strip()
                            if gateway:
                                fingerprint['gateway'] = gateway
                except Exception as e:
                    logger.error(f"Failed to get gateway on Windows: {e}")
                    
            elif self.platform in ['linux', 'darwin']:
                try:
                    command = 'ip route' if self.platform == 'linux' else 'netstat -rn'
                    output = subprocess.check_output(command.split(), universal_newlines=True)
                    for line in output.splitlines():
                        if 'default' in line.lower():
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                fingerprint['gateway'] = parts[1]
                except Exception as e:
                    logger.error(f"Failed to get gateway on {self.platform}: {e}")
                    
            # Get DNS servers
            if self.platform == 'windows':
                try:
                    output = subprocess.check_output(['ipconfig', '/all'], universal_newlines=True)
                    dns_servers = []
                    in_dns_section = False
                    for line in output.splitlines():
                        if 'DNS Servers' in line:
                            in_dns_section = True
                            dns = line.split(':')[-1].strip()
                            if dns:
                                dns_servers.append(dns)
                        elif in_dns_section and line.strip() and not line.startswith('   '):
                            in_dns_section = False
                    fingerprint['dns_servers'] = dns_servers
                except Exception as e:
                    logger.error(f"Failed to get DNS servers on Windows: {e}")
                    
            elif self.platform in ['linux', 'darwin']:
                try:
                    resolv_conf = '/etc/resolv.conf'
                    if os.path.exists(resolv_conf):
                        with open(resolv_conf, 'r') as f:
                            for line in f:
                                if line.strip().startswith('nameserver'):
                                    parts = line.strip().split()
                                    if len(parts) >= 2:
                                        fingerprint['dns_servers'].append(parts[1])
                except Exception as e:
                    logger.error(f"Failed to get DNS servers on {self.platform}: {e}")
                    
            self.network_fingerprint = fingerprint
            logger.info("Network fingerprint generated successfully")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Failed to generate network fingerprint: {e}")
            return {}
            
    def create_report_directory(self) -> str:
        """Create unique report directory based on timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_dir = f"SUNYA_Networking/Auto_Report_{timestamp}"
        
        try:
            os.makedirs(report_dir, exist_ok=True)
            for subdir in ['ping', 'traceroute', 'mtr', 'speedtest', 'analysis']:
                os.makedirs(f"{report_dir}/{subdir}", exist_ok=True)
                
            self.report_dir = report_dir
            logger.info(f"Report directory created: {report_dir}")
            return report_dir
            
        except Exception as e:
            logger.error(f"Failed to create report directory: {e}")
            return None
            
    def watchdog_monitor(self, future, task_name: str):
        """Monitor a task future with watchdog timeout and recovery"""
        try:
            result = future.result(timeout=self.test_config['max_test_duration'])
            return result
        except TimeoutError:
            logger.error(f"{task_name} timeout - terminating and attempting recovery")
            # Attempt to recover from timeout
            return self.recover_from_timeout(task_name)
        except Exception as e:
            logger.error(f"{task_name} failed - {e}")
            return self.recover_from_failure(task_name, e)
    
    def recover_from_timeout(self, task_name: str):
        """Attempt recovery from task timeout"""
        recovery_methods = {
            'ping': self.run_quick_ping_tests,
            'traceroute': self.run_simple_traceroute,
            'speedtest': self.run_quick_speedtest,
            'mtr': None  # No fallback for MTR
        }
        
        recovery_func = recovery_methods.get(task_name)
        if recovery_func:
            logger.warning(f"Attempting recovery for {task_name}")
            try:
                return recovery_func()
            except Exception as e:
                logger.error(f"Recovery for {task_name} failed - {e}")
        
        # Default recovery: return error result
        return {'error': f"Timeout - {task_name} failed to complete in time"}
    
    def recover_from_failure(self, task_name: str, exception: Exception):
        """Attempt recovery from task failure"""
        return {'error': str(exception)}
    
    def run_simple_traceroute(self):
        """Simple traceroute fallback with reduced packet count"""
        logger.warning("Using simple traceroute fallback")
        return self.run_traceroute(packet_count=3)
    
    def run_quick_speedtest(self):
        """Quick speedtest fallback with reduced duration"""
        logger.warning("Using quick speedtest fallback")
        return self.run_speedtest(duration=10)
    
    def is_network_available(self) -> bool:
        """Check if internet connectivity is available"""
        logger.info("Checking network connectivity...")
        
        try:
            import socket
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            logger.info("Internet connectivity available")
            return True
        except Exception as e:
            logger.warning(f"No internet connectivity: {e}")
            return False
    
    def run_parallel_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic modules with intelligent parallel execution and smart short-circuiting"""
        logger.info("Starting intelligent parallel diagnostics...")
        
        if not self.report_dir:
            logger.error("No report directory created")
            return {}
            
        self.start_time = time.time()
        
        # Check cache validity first
        self.load_cache()
        
        # Check if network is available
        network_available = self.is_network_available()
        
        if not network_available:
            logger.warning("No internet connectivity, running offline diagnostics only")
            return self.run_offline_diagnostics()
            
        # Run quick initial tests to determine network quality
        initial_results = self.run_initial_quick_tests()
        
        # Adjust test depth based on initial results
        self.adjust_test_depth(initial_results)
        
        # Define diagnostic tasks with priority
        diagnostic_tasks = self.get_priority_tasks()
        
        results = initial_results.copy()
        
        try:
            # Use ProcessPoolExecutor for better parallelism (CPU bound tasks)
            from concurrent.futures import ProcessPoolExecutor
            
            # Determine optimal number of workers (CPU count * 1.5 for I/O bound tasks)
            import multiprocessing
            max_workers = min(multiprocessing.cpu_count() * 2, 8)  # Cap at 8 workers
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks with watchdog monitoring
                future_to_task = {executor.submit(task): name for name, task in diagnostic_tasks}
                
                # Collect results with watchdog monitoring
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        # Check for test timeout
                        time_elapsed = time.time() - self.start_time
                        if time_elapsed > self.test_config['max_test_duration']:
                            logger.warning("Test duration exceeded, stopping diagnostics")
                            break
                            
                        # Monitor task with watchdog
                        result = self.watchdog_monitor(future, task_name)
                        results[task_name] = result
                        
                        if 'error' in result:
                            logger.warning(f"{task_name} completed with errors")
                        else:
                            logger.info(f"{task_name} completed successfully")
                        
                        # Smart short-circuiting: Stop tests if critical failures detected
                        if self.test_config['short_circuit'] and self.should_stop_early(results):
                            logger.warning("Critical failure detected, stopping further diagnostics")
                            break
                            
                    except Exception as e:
                        logger.error(f"{task_name} failed: {e}")
                        results[task_name] = {'error': str(e)}
                        
            self.diagnostics_results = results
            logger.info("All diagnostics completed")
            
            # Save cache for next run
            self.save_cache()
            
            return results
            
        except Exception as e:
            logger.error(f"Parallel diagnostics failed: {e}")
            return {}
    
    def run_initial_quick_tests(self) -> Dict[str, Any]:
        """Run quick initial tests (30 seconds max) to determine network quality"""
        logger.info("Running quick initial tests...")
        
        initial_tests = [
            ('quick_ping', self.run_quick_ping_tests),
            ('dns_resolution', self.run_dns_resolution_tests),
            ('gateway_check', self.run_gateway_check)
        ]
        
        results = {}
        
        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_task = {executor.submit(task): name for name, task in initial_tests}
                
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        result = future.result(timeout=10)
                        results[task_name] = result
                        logger.info(f"{task_name} completed")
                    except Exception as e:
                        logger.error(f"{task_name} failed: {e}")
                        results[task_name] = {'error': str(e)}
                        
        except Exception as e:
            logger.error(f"Initial tests failed: {e}")
            
        return results
    
    def run_quick_ping_tests(self) -> Dict[str, Any]:
        """Run quick ping tests with minimal packets"""
        from ping3 import ping
        
        targets = {
            'gateway': self.network_fingerprint.get('gateway', '192.168.1.1'),
            'google_dns': '8.8.8.8'
        }
        
        results = {}
        
        for target_name, target_ip in targets.items():
            if not target_ip or target_ip == '':
                continue
                
            logger.info(f"Quick pinging {target_name} ({target_ip})")
            
            try:
                import subprocess
                
                if self.platform == 'windows':
                    output = subprocess.check_output(
                        ['ping', '-n', '3', '-l', '56', target_ip],  # 3 packets, small size
                        universal_newlines=True,
                        stderr=subprocess.STDOUT,
                        timeout=5
                    )
                else:
                    output = subprocess.check_output(
                        ['ping', '-c', '3', '-s', '56', target_ip],  # 3 packets, small size
                        universal_newlines=True,
                        stderr=subprocess.STDOUT,
                        timeout=5
                    )
                    
                results[target_name] = self.parse_ping_output(output)
                
            except Exception as e:
                logger.error(f"Quick ping to {target_name} failed: {e}")
                results[target_name] = {'error': str(e)}
                
        return results
    
    def run_dns_resolution_tests(self) -> Dict[str, Any]:
        """Run quick DNS resolution tests"""
        logger.info("Testing DNS resolution...")
        
        targets = ['google.com', 'cloudflare.com']
        results = {}
        
        for target in targets:
            try:
                import socket
                start_time = time.time()
                socket.getaddrinfo(target, 80)
                resolution_time = (time.time() - start_time) * 1000
                results[target] = {
                    'success': True,
                    'resolution_time_ms': resolution_time
                }
                logger.info(f"DNS resolution to {target}: {resolution_time:.2f}ms")
                
            except Exception as e:
                logger.error(f"DNS resolution to {target} failed: {e}")
                results[target] = {
                    'success': False,
                    'error': str(e)
                }
                
        return results
    
    def run_gateway_check(self) -> Dict[str, Any]:
        """Check if gateway is reachable"""
        logger.info("Checking gateway reachability...")
        
        gateway = self.network_fingerprint.get('gateway', None)
        if not gateway:
            return {'error': 'No gateway configured'}
            
        try:
            from ping3 import ping
            response_time = ping(gateway, timeout=2)
            if response_time:
                return {
                    'reachable': True,
                    'response_time_ms': response_time * 1000
                }
            else:
                return {
                    'reachable': False,
                    'response_time_ms': None
                }
                
        except Exception as e:
            logger.error(f"Gateway check failed: {e}")
            return {'error': str(e)}
    
    def adjust_test_depth(self, initial_results: Dict[str, Any]):
        """Adjust test depth based on initial results"""
        logger.info("Adjusting test depth based on initial results...")
        
        # Analyze initial results
        has_critical_failure = False
        has_excellent_quality = True
        
        # Check for critical failures
        if 'quick_ping' in initial_results:
            for target, result in initial_results['quick_ping'].items():
                if 'error' in result or result.get('packet_loss', 0) > 50:
                    has_critical_failure = True
                    break
                    
        if 'dns_resolution' in initial_results:
            for target, result in initial_results['dns_resolution'].items():
                if not result.get('success', False):
                    has_critical_failure = True
                    break
                    
        if 'gateway_check' in initial_results:
            if not initial_results['gateway_check'].get('reachable', False):
                has_critical_failure = True
                
        # Check for excellent network quality
        if 'quick_ping' in initial_results:
            for target, result in initial_results['quick_ping'].items():
                if 'error' in result:
                    has_excellent_quality = False
                    break
                if result.get('packet_loss', 0) > 0 or result.get('avg_latency', 0) > 50:
                    has_excellent_quality = False
                    break
                    
        if 'dns_resolution' in initial_results:
            for target, result in initial_results['dns_resolution'].items():
                if not result.get('success', False) or result.get('resolution_time_ms', 1000) > 50:
                    has_excellent_quality = False
                    break
                    
        if 'gateway_check' in initial_results:
            if not initial_results['gateway_check'].get('reachable', False) or \
               initial_results['gateway_check'].get('response_time_ms', 1000) > 50:
                has_excellent_quality = False
                
        # Determine test depth
        if has_critical_failure:
            self.test_config['test_depth'] = 'quick'
            logger.warning("Critical failure detected, switching to quick test mode")
        elif has_excellent_quality:
            self.test_config['test_depth'] = 'quick'
            logger.info("Excellent network quality detected, switching to quick test mode")
        else:
            self.test_config['test_depth'] = 'standard'
            logger.info("Standard network quality detected, using standard test depth")
            
        logger.info(f"Test depth set to: {self.test_config['test_depth']}")
    
    def get_priority_tasks(self):
        """Get diagnostic tasks with priority based on test depth"""
        tasks = []
        
        if self.test_config['test_depth'] in ['quick', 'standard', 'deep']:
            tasks.extend([
                ('ping', self.run_ping_tests),
                ('traceroute', self.run_traceroute)
            ])
            
        if self.test_config['test_depth'] in ['standard', 'deep']:
            tasks.extend([
                ('speedtest', self.run_speedtest)
            ])
            
        if self.test_config['test_depth'] == 'deep':
            tasks.extend([
                ('mtr', self.run_mtr),
                ('advanced', self.run_advanced_tests)
            ])
            
        logger.info(f"Selected {len(tasks)} diagnostic tasks for {self.test_config['test_depth']} depth")
        return tasks
    
    def should_stop_early(self, results: Dict[str, Any]) -> bool:
        """Determine if we should stop testing early due to critical failures"""
        # Stop if gateway is unreachable
        if 'gateway_check' in results and not results['gateway_check'].get('reachable', False):
            logger.warning("Gateway unreachable, stopping all tests")
            return True
            
        # Stop if both DNS servers failed
        if 'dns_resolution' in results:
            failed_dns = 0
            for result in results['dns_resolution'].values():
                if not result.get('success', False):
                    failed_dns += 1
            if failed_dns >= 2:
                logger.warning("All DNS servers failed, stopping all tests")
                return True
                
        # Stop if ping tests show 100% packet loss
        if 'quick_ping' in results:
            complete_loss = 0
            for target, result in results['quick_ping'].items():
                if 'error' in result or result.get('packet_loss', 0) == 100:
                    complete_loss += 1
            if complete_loss >= 2:
                logger.warning("Multiple targets showing 100% packet loss, stopping all tests")
                return True
                
        return False
            
    def run_ping_tests(self) -> Dict[str, Any]:
        """Run optimized ping tests with parallel execution"""
        from ping3 import ping, verbose_ping
        
        targets = {
            'gateway': self.network_fingerprint.get('gateway', '192.168.1.1'),
            'dns_1': self.network_fingerprint.get('dns_servers', ['8.8.8.8'])[0],
            'dns_2': self.network_fingerprint.get('dns_servers', ['8.8.4.4'])[1] if len(self.network_fingerprint.get('dns_servers', [])) > 1 else '8.8.4.4',
            'google_dns': '8.8.8.8',
            'cloudflare_dns': '1.1.1.1'
        }
        
        results = {}
        
        # Run ping tests in parallel for faster execution
        def run_single_ping(target_name, target_ip):
            if not target_ip or target_ip == '':
                return target_name, {'error': 'Invalid IP address'}
                
            logger.info(f"Pinging {target_name} ({target_ip})")
            
            try:
                import subprocess
                
                if self.platform == 'windows':
                    output = subprocess.check_output(
                        ['ping', '-n', '10', '-l', '1400', target_ip],  # Reduce to 10 pings for speed
                        universal_newlines=True,
                        stderr=subprocess.STDOUT,
                        timeout=30
                    )
                else:
                    output = subprocess.check_output(
                        ['ping', '-c', '10', '-s', '1400', target_ip],  # Reduce to 10 pings for speed
                        universal_newlines=True,
                        stderr=subprocess.STDOUT,
                        timeout=30
                    )
                    
                # Save raw output
                with open(f"{self.report_dir}/ping/{target_name}.txt", 'w') as f:
                    f.write(output)
                    
                return target_name, self.parse_ping_output(output)
                
            except Exception as e:
                logger.error(f"Ping to {target_name} failed: {e}")
                return target_name, {'error': str(e)}
                
        # Use ThreadPoolExecutor for parallel ping execution
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(targets)) as executor:
            future_to_target = {
                executor.submit(run_single_ping, name, ip): name 
                for name, ip in targets.items()
            }
            
            for future in as_completed(future_to_target):
                target_name, result = future.result()
                results[target_name] = result
                
        return results
        
    def parse_ping_output(self, output: str) -> Dict[str, Any]:
        """Parse ping output for metrics"""
        metrics = {
            'packet_loss': 0,
            'avg_latency': 0,
            'min_latency': 0,
            'max_latency': 0,
            'jitter': 0
        }
        
        try:
            # Parse packet loss
            if 'packet loss' in output:
                for line in output.splitlines():
                    if 'packet loss' in line:
                        packet_loss_str = line.split('%')[0].split()[-1]
                        metrics['packet_loss'] = float(packet_loss_str)
                        
            # Parse latency statistics
            if 'average' in output.lower() or 'avg' in output.lower():
                for line in output.splitlines():
                    if 'average' in line.lower() or 'avg' in line.lower():
                        if self.platform == 'windows':
                            parts = line.split()
                            if len(parts) >= 3 and 'ms' in parts[-1]:
                                ms_parts = parts[-2].split('/')
                                if len(ms_parts) == 3:
                                    metrics['min_latency'] = float(ms_parts[0])
                                    metrics['avg_latency'] = float(ms_parts[1])
                                    metrics['max_latency'] = float(ms_parts[2])
                        else:
                            parts = line.split('=')
                            if len(parts) > 1:
                                ms_parts = parts[-1].split('/')
                                if len(ms_parts) >= 3:
                                    metrics['min_latency'] = float(ms_parts[0])
                                    metrics['avg_latency'] = float(ms_parts[1])
                                    metrics['max_latency'] = float(ms_parts[2])
                                    
            # Calculate jitter (simplified)
            metrics['jitter'] = metrics['max_latency'] - metrics['min_latency']
                
        except Exception as e:
            logger.error(f"Failed to parse ping output: {e}")
            
        return metrics
        
    def run_traceroute(self) -> Dict[str, Any]:
        """Run traceroute with ICMP and UDP"""
        targets = [
            '8.8.8.8',
            '1.1.1.1'
        ]
        
        results = {}
        
        for target in targets:
            logger.info(f"Running traceroute to {target}")
            
            try:
                if self.platform == 'windows':
                    output = subprocess.check_output(
                        ['tracert', '-d', target],
                        universal_newlines=True,
                        stderr=subprocess.STDOUT
                    )
                else:
                    output = subprocess.check_output(
                        ['traceroute', target],
                        universal_newlines=True,
                        stderr=subprocess.STDOUT
                    )
                    
                # Save raw output
                with open(f"{self.report_dir}/traceroute/traceroute_{target}.txt", 'w') as f:
                    f.write(output)
                    
                results[target] = self.parse_traceroute_output(output)
                
            except Exception as e:
                logger.error(f"Traceroute to {target} failed: {e}")
                results[target] = {'error': str(e)}
                
        return results
        
    def parse_traceroute_output(self, output: str) -> Dict[str, Any]:
        """Parse traceroute output"""
        hops = []
        
        try:
            for line in output.splitlines():
                if line.strip() and not line.startswith('traceroute') and not line.startswith('Tracing'):
                    parts = line.strip().split()
                    if parts:
                        hop_number = parts[0]
                        hop_info = {'hop': hop_number, 'details': []}
                        
                        for part in parts[1:]:
                            if part != '*':
                                hop_info['details'].append(part)
                                
                        hops.append(hop_info)
                        
        except Exception as e:
            logger.error(f"Failed to parse traceroute output: {e}")
            
        return {'hops': hops}
        
    def run_speedtest(self) -> Dict[str, Any]:
        """Run speed test using speedtest-cli"""
        logger.info("Running speed test...")
        
        try:
            import speedtest
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 10**6  # Mbps
            upload_speed = st.upload() / 10**6  # Mbps
            ping_result = st.results.ping
            
            # Save details
            result_details = st.results.dict()
            with open(f"{self.report_dir}/speedtest/details.json", 'w') as f:
                json.dump(result_details, f, indent=2)
                
            result = {
                'download_speed': round(download_speed, 2),
                'upload_speed': round(upload_speed, 2),
                'ping': round(ping_result, 2),
                'server': {
                    'name': st.results.server['name'],
                    'country': st.results.server['country'],
                    'sponsor': st.results.server['sponsor']
                },
                'bytes_sent': result_details['bytes_sent'],
                'bytes_received': result_details['bytes_received']
            }
            
            logger.info(f"Speed test completed: {result['download_speed']} Mbps down, {result['upload_speed']} Mbps up")
            
            return result
            
        except Exception as e:
            logger.error(f"Speed test failed: {e}")
            return {'error': str(e)}
            
    def load_cache(self):
        """Load test cache from previous runs if fingerprint matches"""
        cache_file = 'sunya-test-cache.json'
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                    
                # Check if fingerprint matches (consider time-based expiration)
                if 'fingerprint' in cache and 'timestamp' in cache:
                    cache_age = time.time() - datetime.fromisoformat(cache['timestamp']).timestamp()
                    if cache_age < 3600:  # Cache valid for 1 hour
                        self.test_cache = cache
                        logger.info("Test cache loaded (valid)")
                    else:
                        logger.info("Test cache expired")
                else:
                    logger.info("Invalid cache format")
                    
        except Exception as e:
            logger.error(f"Failed to load test cache: {e}")
    
    def save_cache(self):
        """Save current test results to cache"""
        cache_file = 'sunya-test-cache.json'
        
        try:
            cache = {
                'timestamp': datetime.now().isoformat(),
                'fingerprint': self.network_fingerprint,
                'results': self.diagnostics_results,
                'test_config': self.test_config
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache, f)
                
            logger.info("Test cache saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save test cache: {e}")
    
    def run_advanced_tests(self) -> Dict[str, Any]:
        """Run advanced network tests for deep diagnosis"""
        logger.info("Running advanced network tests...")
        
        results = {
            'mtu_test': self.run_mtu_test(),
            'port_scan': self.run_port_scan()
        }
        
        return results
    
    def run_mtu_test(self) -> Dict[str, Any]:
        """Test maximum transmission unit"""
        logger.info("Testing MTU size...")
        
        results = {
            'best_mtu': None,
            'path_mtu': None
        }
        
        try:
            # Simple MTU test using ping with don't fragment flag
            for mtu in range(1500, 1400, -10):
                try:
                    if self.platform == 'windows':
                        output = subprocess.check_output(
                            ['ping', '-n', '1', '-l', str(mtu), '-f', self.network_fingerprint.get('gateway', '192.168.1.1')],
                            universal_newlines=True,
                            stderr=subprocess.STDOUT,
                            timeout=2
                        )
                    else:
                        output = subprocess.check_output(
                            ['ping', '-c', '1', '-s', str(mtu), '-M', 'do', self.network_fingerprint.get('gateway', '192.168.1.1')],
                            universal_newlines=True,
                            stderr=subprocess.STDOUT,
                            timeout=2
                        )
                        
                    if 'unreachable' not in output.lower() and 'fragmentation' not in output.lower():
                        results['best_mtu'] = mtu
                        logger.info(f"Found working MTU: {mtu}")
                        break
                        
                except Exception as e:
                    logger.debug(f"MTU {mtu} failed: {e}")
                    
        except Exception as e:
            logger.error(f"MTU test failed: {e}")
            
        return results
    
    def run_port_scan(self) -> Dict[str, Any]:
        """Scan common ports on network targets"""
        logger.info("Scanning common ports...")
        
        targets = [self.network_fingerprint.get('gateway', '192.168.1.1')]
        ports = [53, 80, 443]
        results = {}
        
        try:
            import socket
            for target in targets:
                target_results = {}
                for port in ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((target, port))
                        target_results[port] = 'open' if result == 0 else 'closed'
                        sock.close()
                    except Exception as e:
                        target_results[port] = f'error: {e}'
                        
                results[target] = target_results
                
        except Exception as e:
            logger.error(f"Port scan failed: {e}")
            
        return results
    
    def run_mtr(self) -> Dict[str, Any]:
        """Run MTR (My TraceRoute) for comprehensive route analysis"""
        logger.info("Running MTR test...")
        
        results = {}
        
        if self.platform == 'windows':
            logger.warning("MTR not available on Windows, using alternative...")
            return {'error': 'MTR not available on Windows'}
            
        targets = ['8.8.8.8', '1.1.1.1']
        
        for target in targets:
            try:
                output = subprocess.check_output(
                    ['mtr', '--report', '5', target],
                    universal_newlines=True,
                    stderr=subprocess.STDOUT
                )
                
                with open(f"{self.report_dir}/mtr/mtr_{target}.txt", 'w') as f:
                    f.write(output)
                    
                results[target] = self.parse_mtr_output(output)
                
            except Exception as e:
                logger.error(f"MTR to {target} failed: {e}")
                results[target] = {'error': str(e)}
                
        return results
        
    def parse_mtr_output(self, output: str) -> Dict[str, Any]:
        """Parse MTR output"""
        hops = []
        
        try:
            for line in output.splitlines():
                if line.strip() and line[0].isdigit():
                    parts = line.strip().split()
                    if len(parts) >= 7:
                        hop_info = {
                            'hop': parts[0],
                            'loss': parts[2],
                            'snt': parts[3],
                            'last': parts[4],
                            'avg': parts[5],
                            'best': parts[6],
                            'wrst': parts[7]
                        }
                        hops.append(hop_info)
                        
        except Exception as e:
            logger.error(f"Failed to parse MTR output: {e}")
            
        return {'hops': hops}
        
    def run_analysis(self) -> Dict[str, Any]:
        """Run intelligent analysis engine with confidence scoring and pattern matching"""
        logger.info("Running intelligent analysis engine...")
        
        analysis = {
            'issues': [],
            'diagnosis': '',
            'recommendations': [],
            'confidence_score': 0.0,
            'patterns': []
        }
        
        # Check if we have internet connectivity information
        network_available = self.is_network_available()
        
        if not network_available:
            analysis['diagnosis'] = "No internet connectivity detected - only local network diagnostics available"
            analysis['confidence_score'] = 95.0
            analysis['recommendations'] = [
                "Check physical network connections",
                "Verify modem/router is powered and operational",
                "Restart modem/router if necessary",
                "Contact ISP if issue persists"
            ]
            
            # Analyze local network issues
            if 'quick_ping' in self.diagnostics_results:
                self.analyze_ping_issues(analysis, [])
                
            if 'gateway_check' in self.diagnostics_results:
                gateway_result = self.diagnostics_results['gateway_check']
                if gateway_result.get('reachable', False) is False:
                    analysis['issues'].append({
                        'type': 'gateway_unreachable',
                        'severity': 'critical',
                        'target': 'Gateway',
                        'value': 'Unreachable',
                        'description': 'Default gateway is not reachable'
                    })
            
            logger.info(f"Analysis completed with {analysis['confidence_score']:.1f}% confidence (offline)")
            return analysis
        
        # Calculate base confidence
        base_confidence = self.calculate_base_confidence()
        
        # Analyze results using pattern matching
        patterns = self.detect_network_patterns()
        analysis['patterns'] = patterns
        
        # Identify specific issues
        if 'ping' in self.diagnostics_results:
            self.analyze_ping_issues(analysis, patterns)
            
        if 'traceroute' in self.diagnostics_results:
            self.analyze_traceroute_issues(analysis, patterns)
            
        if 'speedtest' in self.diagnostics_results:
            self.analyze_speedtest_issues(analysis, patterns)
            
        # Calculate final confidence score
        analysis['confidence_score'] = self.calculate_final_confidence(base_confidence, patterns)
        
        # Determine diagnosis and recommendations
        self.determine_diagnosis(analysis, patterns)
        
        logger.info(f"Analysis completed with {analysis['confidence_score']:.1f}% confidence")
        return analysis
    
    def calculate_base_confidence(self) -> float:
        """Calculate base confidence score from available evidence"""
        evidence_count = 0
        successful_tests = 0
        
        if 'quick_ping' in self.diagnostics_results:
            evidence_count += 1
            successful_tests += 1
            
        if 'dns_resolution' in self.diagnostics_results:
            evidence_count += 1
            successful_tests += 1
            
        if 'gateway_check' in self.diagnostics_results:
            evidence_count += 1
            successful_tests += 1
            
        if 'ping' in self.diagnostics_results:
            evidence_count += 1
            successful_tests += 1
            
        if 'traceroute' in self.diagnostics_results:
            evidence_count += 1
            successful_tests += 1
            
        if 'speedtest' in self.diagnostics_results:
            evidence_count += 1
            successful_tests += 1
            
        base_confidence = (successful_tests / evidence_count) * 0.7  # 70% weight for evidence count
        logger.debug(f"Base confidence from evidence count: {base_confidence:.3f}")
        return base_confidence
    
    def detect_first_bad_hop(self):
        """Identify the first bad hop with high certainty using MTR and traceroute correlation"""
        logger.info("Detecting first bad hop...")
        
        first_bad_hop = None
        
        if 'traceroute' in self.diagnostics_results and 'mtr' in self.diagnostics_results:
            traceroute = self.diagnostics_results['traceroute']
            mtr = self.diagnostics_results['mtr']
            
            # Find the first hop with both traceroute latency spike and MTR loss
            for i, (trace_hop, mtr_hop) in enumerate(zip(traceroute.get('hops', []), mtr.get('hops', []))):
                if i == 0:  # Skip localhost
                    continue
                    
                # Check for latency spike in traceroute
                has_latency_spike = False
                if i > 1 and len(traceroute.get('hops', [])) > i+1:
                    prev_hop = traceroute.get('hops', [])[i-1]
                    curr_hop = trace_hop
                    next_hop = traceroute.get('hops', [])[i+1]
                    
                    prev_latency = prev_hop.get('avg_latency', 0)
                    curr_latency = curr_hop.get('avg_latency', 0)
                    next_latency = next_hop.get('avg_latency', 0)
                    
                    # Check if current hop has significant latency spike
                    if curr_latency > prev_latency * 2 and curr_latency > next_latency * 1.5:
                        has_latency_spike = True
                
                # Check for packet loss in MTR
                has_packet_loss = False
                packet_loss = mtr_hop.get('loss', 0)
                if isinstance(packet_loss, (int, float)) and packet_loss > 10:
                    has_packet_loss = True
                elif isinstance(packet_loss, str):
                    try:
                        loss_value = float(packet_loss.replace('%', ''))
                        if loss_value > 10:
                            has_packet_loss = True
                    except ValueError:
                        pass
                
                # If both conditions met, consider this the first bad hop
                if has_latency_spike and has_packet_loss:
                    first_bad_hop = {
                        'hop': i+1,
                        'ip_address': trace_hop.get('ip', 'Unknown'),
                        'hostname': trace_hop.get('hostname', 'Unknown'),
                        'latency': trace_hop.get('avg_latency', 0),
                        'packet_loss': packet_loss,
                        'confidence': 95  # High confidence due to dual verification
                    }
                    logger.info(f"First bad hop detected at hop {i+1}")
                    break
        
        return first_bad_hop
    
    def detect_network_patterns(self):
        """Detect known network issue patterns from test results"""
        logger.info("Detecting network patterns...")
        
        patterns = []
        
        if self.has_wifi_interference_pattern():
            patterns.append('wifi_interference')
            
        if self.has_mtu_blackhole_pattern():
            patterns.append('mtu_blackhole')
            
        if self.has_isp_congestion_pattern():
            patterns.append('isp_congestion')
            
        if self.has_dns_manipulation_pattern():
            patterns.append('dns_manipulation')
            
        if self.has_routing_asymmetry_pattern():
            patterns.append('routing_asymmetry')
            
        logger.info(f"Detected patterns: {', '.join(patterns) if patterns else 'none'}")
        return patterns
    
    def has_wifi_interference_pattern(self) -> bool:
        """Check if test results match WiFi interference pattern"""
        if 'ping' in self.diagnostics_results:
            ping_results = self.diagnostics_results['ping']
            if 'gateway' in ping_results and 'packet_loss' in ping_results['gateway']:
                if ping_results['gateway']['packet_loss'] > 10:
                    return True
        return False
    
    def has_mtu_blackhole_pattern(self) -> bool:
        """Check if test results match MTU blackhole pattern"""
        if 'advanced' in self.diagnostics_results and 'mtu_test' in self.diagnostics_results['advanced']:
            if self.diagnostics_results['advanced']['mtu_test']['best_mtu'] is not None:
                best_mtu = self.diagnostics_results['advanced']['mtu_test']['best_mtu']
                if best_mtu < 1460:
                    return True
        return False
    
    def has_isp_congestion_pattern(self) -> bool:
        """Check if test results match ISP congestion pattern"""
        if 'speedtest' in self.diagnostics_results:
            if 'download' in self.diagnostics_results['speedtest'] and \
               self.diagnostics_results['speedtest']['download'] < 10:  # Less than 10 Mbps
                return True
        return False
    
    def has_dns_manipulation_pattern(self) -> bool:
        """Check if test results match DNS manipulation pattern"""
        if 'dns_resolution' in self.diagnostics_results:
            for domain, result in self.diagnostics_results['dns_resolution'].items():
                if not result.get('success', False):
                    return True
        return False
    
    def has_routing_asymmetry_pattern(self) -> bool:
        """Check if test results match routing asymmetry pattern"""
        return False  # To be implemented with more advanced routing analysis
    
    def analyze_ping_issues(self, analysis, patterns):
        """Analyze ping test results for issues"""
        if 'ping' in self.diagnostics_results:
            ping_results = self.diagnostics_results['ping']
            
            for target, metrics in ping_results.items():
                if 'error' not in metrics:
                    if metrics['packet_loss'] > 5:
                        analysis['issues'].append({
                            'type': 'packet_loss',
                            'severity': 'high',
                            'target': target,
                            'value': f"{metrics['packet_loss']}%",
                            'description': f"High packet loss detected to {target}"
                        })
                        
                    if metrics['avg_latency'] > 100:
                        analysis['issues'].append({
                            'type': 'high_latency',
                            'severity': 'medium',
                            'target': target,
                            'value': f"{metrics['avg_latency']}ms",
                            'description': f"High latency detected to {target}"
                        })
                        
                    if metrics['jitter'] > 50:
                        analysis['issues'].append({
                            'type': 'jitter',
                            'severity': 'medium',
                            'target': target,
                            'value': f"{metrics['jitter']}ms",
                            'description': f"High jitter detected to {target}"
                        })
    
    def analyze_traceroute_issues(self, analysis, patterns):
        """Analyze traceroute test results for issues"""
        if 'traceroute' in self.diagnostics_results:
            traceroute_results = self.diagnostics_results['traceroute']
            
            if isinstance(traceroute_results, dict):
                for target, trace in traceroute_results.items():
                    if 'hops' in trace:
                        for hop in trace['hops']:
                            if hop.get('loss', 0) > 10:
                                analysis['issues'].append({
                                    'type': 'hop_loss',
                                    'severity': 'high',
                                    'target': f"Hop {hop['hop']}",
                                    'value': f"{hop['loss']}%",
                                    'description': f"High packet loss at hop {hop['hop']}"
                                })
                        
                            if hop.get('avg', 0) > 200:
                                analysis['issues'].append({
                                    'type': 'hop_latency',
                                    'severity': 'medium',
                                    'target': f"Hop {hop['hop']}",
                                    'value': f"{hop['avg']}ms",
                                    'description': f"High latency at hop {hop['hop']}"
                                })
    
    def analyze_speedtest_issues(self, analysis, patterns):
        """Analyze speed test results for issues"""
        if 'speedtest' in self.diagnostics_results:
            speedtest_results = self.diagnostics_results['speedtest']
            
            if 'download' in speedtest_results and speedtest_results['download'] < 10:
                analysis['issues'].append({
                    'type': 'slow_download',
                    'severity': 'high',
                    'target': 'Download',
                    'value': f"{speedtest_results['download']:.2f} Mbps",
                    'description': 'Download speed is significantly below expected'
                })
                
            if 'upload' in speedtest_results and speedtest_results['upload'] < 5:
                analysis['issues'].append({
                    'type': 'slow_upload',
                    'severity': 'medium',
                    'target': 'Upload',
                    'value': f"{speedtest_results['upload']:.2f} Mbps",
                    'description': 'Upload speed is below expected'
                })
    
    def calculate_final_confidence(self, base_confidence: float, patterns: list) -> float:
        """Calculate final confidence score by combining base confidence and pattern matching"""
        pattern_bonus = 0.0
        
        # Bonus for each matching pattern (each pattern adds 5-10% confidence)
        for pattern in patterns:
            if pattern == 'wifi_interference':
                pattern_bonus += 0.10
            elif pattern == 'mtu_blackhole':
                pattern_bonus += 0.10
            elif pattern == 'isp_congestion':
                pattern_bonus += 0.08
            elif pattern == 'dns_manipulation':
                pattern_bonus += 0.05
            elif pattern == 'routing_asymmetry':
                pattern_bonus += 0.05
                
        final_confidence = min(base_confidence + pattern_bonus, 0.95)
        return final_confidence * 100
    
    def run_offline_diagnostics(self) -> Dict[str, Any]:
        """Run diagnostic tests when internet connectivity is not available"""
        logger.info("Running offline diagnostics...")
        
        results = {}
        
        # Offline tests (no internet required)
        offline_tests = [
            ('quick_ping', self.run_quick_ping_tests),
            ('gateway_check', self.run_gateway_check)
        ]
        
        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_to_task = {executor.submit(task): name for name, task in offline_tests}
                
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        result = future.result(timeout=30)
                        results[task_name] = result
                        logger.info(f"{task_name} completed")
                    except Exception as e:
                        logger.error(f"{task_name} failed: {e}")
                        results[task_name] = {'error': str(e)}
                        
        except Exception as e:
            logger.error(f"Offline tests failed: {e}")
            
        # Always run analysis on offline results
        if self.run_analysis:
            results['analysis'] = self.run_analysis()
            
        return results
    
    def get_pattern_description(self, pattern: str) -> str:
        """Get human-readable description for network patterns"""
        pattern_descriptions = {
            'wifi_interference': 'WiFi Interference - Likely caused by neighboring networks or devices',
            'mtu_blackhole': 'MTU Blackhole - Network path cannot handle standard MTU size',
            'isp_congestion': 'ISP Congestion - Network congestion affecting performance',
            'dns_manipulation': 'DNS Resolution Issues - DNS servers unresponsive or misconfigured',
            'routing_asymmetry': 'Routing Asymmetry - Traffic takes different paths in each direction'
        }
        
        return pattern_descriptions.get(pattern, pattern)
    
    def generate_alerts(self, analysis):
        """Generate actionable alerts based on analysis results"""
        logger.info("Generating alerts...")
        
        alerts = []
        
        if 'analysis' not in self.diagnostics_results:
            logger.warning("No analysis results to generate alerts from")
            return alerts
        
        # Analyze issues for alerts
        if 'issues' in analysis:
            for issue in analysis['issues']:
                alert = self.create_alert_from_issue(issue, analysis)
                if alert:
                    alerts.append(alert)
        
        # Analyze patterns for alerts
        if 'patterns' in analysis and analysis['patterns']:
            for pattern in analysis['patterns']:
                alert = self.create_alert_from_pattern(pattern, analysis)
                if alert:
                    alerts.append(alert)
        
        # Analyze performance metrics for alerts
        alerts.extend(self.create_performance_alerts(analysis))
        
        logger.info(f"Generated {len(alerts)} alert(s)")
        return alerts
    
    def create_alert_from_issue(self, issue, analysis):
        """Create an alert from a specific issue"""
        severity = issue.get('severity', 'medium')
        
        alert = {
            'id': f"{issue['type']}_{int(time.time())}",
            'type': issue['type'],
            'severity': severity,
            'message': issue['description'],
            'target': issue['target'],
            'value': issue['value'],
            'confidence': analysis['confidence_score'],
            'timestamp': datetime.now().isoformat(),
            'action_suggestion': self.get_action_suggestion(issue['type'])
        }
        
        return alert
    
    def create_alert_from_pattern(self, pattern, analysis):
        """Create an alert from a network pattern"""
        patterns = {
            'wifi_interference': {
                'message': 'WiFi interference likely affecting performance',
                'severity': 'medium',
                'action_suggestion': 'Try changing WiFi channel or moving closer to router'
            },
            'mtu_blackhole': {
                'message': 'MTU blackhole detected in network path',
                'severity': 'high',
                'action_suggestion': 'Contact ISP to investigate MTU path issues'
            },
            'isp_congestion': {
                'message': 'ISP congestion affecting network performance',
                'severity': 'medium',
                'action_suggestion': 'Consider testing during off-peak hours or upgrading plan'
            },
            'dns_manipulation': {
                'message': 'DNS resolution issues detected',
                'severity': 'high',
                'action_suggestion': 'Try changing DNS servers to 8.8.8.8 or 1.1.1.1'
            },
            'routing_asymmetry': {
                'message': 'Routing asymmetry detected',
                'severity': 'medium',
                'action_suggestion': 'Contact ISP to investigate routing issues'
            }
        }
        
        pattern_info = patterns.get(pattern, {})
        
        alert = {
            'id': f"pattern_{pattern}_{int(time.time())}",
            'type': 'pattern',
            'pattern_type': pattern,
            'severity': pattern_info.get('severity', 'medium'),
            'message': pattern_info.get('message', f"Network pattern detected: {pattern}"),
            'confidence': analysis['confidence_score'],
            'timestamp': datetime.now().isoformat(),
            'action_suggestion': pattern_info.get('action_suggestion', 'Contact support for assistance')
        }
        
        return alert
    
    def create_performance_alerts(self, analysis):
        """Create alerts based on performance metrics"""
        alerts = []
        
        if 'speedtest' in self.diagnostics_results:
            speedtest = self.diagnostics_results['speedtest']
            if 'download' in speedtest and speedtest['download'] < 10:
                alerts.append({
                    'id': f"slow_download_{int(time.time())}",
                    'type': 'performance',
                    'subtype': 'download_speed',
                    'severity': 'high',
                    'message': f"Download speed {speedtest['download']:.2f} Mbps is too slow",
                    'value': f"{speedtest['download']:.2f} Mbps",
                    'confidence': analysis['confidence_score'],
                    'timestamp': datetime.now().isoformat(),
                    'action_suggestion': 'Check for bandwidth-consuming applications or contact ISP'
                })
        
        return alerts
    
    def get_action_suggestion(self, issue_type):
        """Get action suggestion based on issue type"""
        suggestions = {
            'packet_loss': 'Check physical connections, restart router, or contact ISP',
            'high_latency': 'Check for network congestion or WiFi interference',
            'jitter': 'Check for packet loss or network stability issues',
            'gateway_unreachable': 'Check physical connections, restart router',
            'dns_failure': 'Try changing DNS servers to 8.8.8.8 or 1.1.1.1',
            'hop_loss': 'Contact ISP with traceroute information',
            'hop_latency': 'Contact ISP with traceroute information',
            'slow_download': 'Check for bandwidth-consuming applications or contact ISP',
            'slow_upload': 'Check for bandwidth-consuming applications or contact ISP'
        }
        
        return suggestions.get(issue_type, 'Contact support for assistance')
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file for integrity verification"""
        try:
            import hashlib
            
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files efficiently
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
                    
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None
    
    def generate_evidence_summary(self) -> Dict[str, str]:
        """Generate evidence integrity summary with file hashes"""
        logger.info("Generating evidence integrity summary...")
        
        evidence_summary = {
            'generated_at': datetime.now().isoformat(),
            'files': []
        }
        
        if not self.report_dir:
            logger.warning("Report directory not initialized")
            return evidence_summary
            
        # Check for common report files
        report_files = [
            'results.json',
            'network_info.txt',
            'alerts.json',
            'analysis-summary.json'
        ]
        
        for filename in report_files:
            file_path = os.path.join(self.report_dir, filename)
            if os.path.exists(file_path):
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    evidence_summary['files'].append({
                        'filename': filename,
                        'hash': file_hash,
                        'hash_algorithm': 'SHA-256',
                        'size': os.path.getsize(file_path),
                        'modified_at': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
        
        return evidence_summary
    
    def save_evidence_summary(self):
        """Save evidence integrity summary to file"""
        if not self.report_dir:
            logger.warning("Cannot save evidence summary: Report directory not initialized")
            return False
            
        try:
            evidence_summary = self.generate_evidence_summary()
            summary_file = os.path.join(self.report_dir, 'evidence-integrity.json')
            
            with open(summary_file, 'w') as f:
                json.dump(evidence_summary, f, indent=2, default=str)
                
            logger.info(f"Evidence integrity summary saved to {summary_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save evidence summary: {e}")
            return False
    
    def verify_evidence_integrity(self, summary_file: str = None) -> Dict[str, bool]:
        """Verify the integrity of report files against hash summary"""
        logger.info("Verifying evidence integrity...")
        
        if not summary_file:
            summary_file = os.path.join(self.report_dir, 'evidence-integrity.json')
            
        if not os.path.exists(summary_file):
            logger.warning(f"Evidence summary file not found: {summary_file}")
            return {}
            
        try:
            with open(summary_file, 'r') as f:
                evidence_summary = json.load(f)
                
            verification_results = {}
            
            for file_info in evidence_summary.get('files', []):
                filename = file_info.get('filename')
                expected_hash = file_info.get('hash')
                
                file_path = os.path.join(self.report_dir, filename)
                if os.path.exists(file_path):
                    actual_hash = self.calculate_file_hash(file_path)
                    verification_results[filename] = (actual_hash == expected_hash)
                    
                    if not verification_results[filename]:
                        logger.warning(f"Hash mismatch for {filename}: expected {expected_hash[:16]}..., got {actual_hash[:16]}...")
                else:
                    verification_results[filename] = False
                    logger.warning(f"File not found: {filename}")
                    
            return verification_results
            
        except Exception as e:
            logger.error(f"Evidence integrity verification failed: {e}")
            return {}
    
    def save_alerts(self, alerts):
        """Save alerts to JSON file"""
        try:
            if not self.report_dir:
                logger.warning("Cannot save alerts: Report directory not initialized")
                return False
                
            alerts_file = os.path.join(self.report_dir, 'alerts.json')
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            logger.info(f"Alerts saved to {alerts_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
            return False
    
    def generate_isp_ticket_text(self, analysis):
        """Generate ISP-ticket-ready text based on diagnosis"""
        if not analysis:
            return "No diagnosis available"
            
        ticket_text = "**ISP Support Ticket Information**\n\n"
        ticket_text += f"**Issue Reported:** {analysis.get('diagnosis', 'Network performance issue')}\n"
        ticket_text += f"**Confidence Level:** {analysis.get('confidence_score', 0):.1f}%\n\n"
        
        if 'patterns' in analysis and analysis['patterns']:
            ticket_text += "**Detected Network Patterns:**\n"
            for pattern in analysis['patterns']:
                ticket_text += f"- {self.get_pattern_description(pattern)}\n"
            ticket_text += "\n"
        
        if 'issues' in analysis and analysis['issues']:
            ticket_text += "**Specific Issues:**\n"
            for issue in analysis['issues']:
                ticket_text += f"- {issue['description']} ({issue['severity']})\n"
            ticket_text += "\n"
        
        if 'recommendations' in analysis and analysis['recommendations']:
            ticket_text += "**Action Suggestions:**\n"
            for rec in analysis['recommendations']:
                ticket_text += f"- {rec}\n"
            ticket_text += "\n"
        
        ticket_text += "**Evidence Summary:**\n"
        ticket_text += "- Network diagnostic tests have been conducted\n"
        ticket_text += "- Detailed report with all test results is available\n"
        ticket_text += "- Confidence score indicates reliability of diagnosis\n"
        
        return ticket_text
    
    def determine_diagnosis(self, analysis, patterns):
        """Determine final diagnosis and recommendations based on patterns and issues"""
        if patterns:
            primary_pattern = patterns[0]
            
            if primary_pattern == 'wifi_interference':
                analysis['diagnosis'] = "WiFi interference likely causing performance issues"
                analysis['recommendations'] = [
                    "Move closer to WiFi router",
                    "Change WiFi channel",
                    "Check for other WiFi networks or devices causing interference",
                    "Consider upgrading to 5GHz WiFi"
                ]
                
            elif primary_pattern == 'mtu_blackhole':
                analysis['diagnosis'] = "MTU blackhole detected in network path"
                analysis['recommendations'] = [
                    "Try lowering MTU setting on router",
                    "Enable path MTU discovery (PMTUD)",
                    "Contact ISP if issue persists"
                ]
                
            elif primary_pattern == 'isp_congestion':
                analysis['diagnosis'] = "ISP congestion affecting connection"
                analysis['recommendations'] = [
                    "Try testing at different times of day",
                    "Contact ISP about bandwidth issues",
                    "Consider upgrading internet plan"
                ]
                
            elif primary_pattern == 'dns_manipulation':
                analysis['diagnosis'] = "DNS resolution failures or manipulation"
                analysis['recommendations'] = [
                    "Try using alternative DNS servers (Google DNS: 8.8.8.8/8.8.4.4)",
                    "Flush DNS cache",
                    "Check for malware or DNS hijacking",
                    "Contact ISP if issue persists"
                ]
                
            elif primary_pattern == 'routing_asymmetry':
                analysis['diagnosis'] = "Routing asymmetry detected"
                analysis['recommendations'] = [
                    "Contact ISP to investigate routing issues",
                    "Try traceroute from multiple locations",
                    "Consider VPN to bypass problematic routes"
                ]
                
        elif analysis['issues']:
            # No patterns detected, use generic diagnosis
            high_issues = [issue for issue in analysis['issues'] if issue['severity'] == 'high']
            if high_issues:
                analysis['diagnosis'] = "Multiple high-severity issues detected"
                analysis['recommendations'] = [
                    "Investigate high-severity issues first",
                    "Check physical network connections",
                    "Restart modem/router",
                    "Contact ISP if issues persist"
                ]
            else:
                analysis['diagnosis'] = "Network performance issues detected"
                analysis['recommendations'] = [
                    "Monitor connection for further issues",
                    "Check for background processes consuming bandwidth",
                    "Update network drivers and firmware"
                ]
        else:
            # No issues detected
            analysis['diagnosis'] = "Network performance is normal"
            analysis['recommendations'] = [
                "Network performance is within normal parameters",
                "No immediate action required",
                "Consider testing at different times"
            ]
        """Run intelligent analysis engine"""
        logger.info("Running intelligent analysis...")
        
        analysis = {
            'issues': [],
            'diagnosis': '',
            'recommendations': []
        }
        
        try:
            # Analyze ping results
            if 'ping' in self.diagnostics_results:
                ping_results = self.diagnostics_results['ping']
                
                for target, metrics in ping_results.items():
                    if 'error' not in metrics:
                        if metrics['packet_loss'] > 5:
                            analysis['issues'].append({
                                'type': 'packet_loss',
                                'severity': 'high',
                                'target': target,
                                'value': f"{metrics['packet_loss']}%",
                                'description': f"High packet loss detected to {target}"
                            })
                            
                        if metrics['avg_latency'] > 100:
                            analysis['issues'].append({
                                'type': 'high_latency',
                                'severity': 'medium',
                                'target': target,
                                'value': f"{metrics['avg_latency']}ms",
                                'description': f"High latency detected to {target}"
                            })
                            
                        if metrics['jitter'] > 50:
                            analysis['issues'].append({
                                'type': 'jitter',
                                'severity': 'medium',
                                'target': target,
                                'value': f"{metrics['jitter']}ms",
                                'description': f"High jitter detected to {target}"
                            })
                            
            # Analyze traceroute results
            if 'traceroute' in self.diagnostics_results:
                traceroute_results = self.diagnostics_results['traceroute']
                
                for target, result in traceroute_results.items():
                    if 'error' not in result:
                        # Check for consistent packet loss starting at specific hops
                        for hop in result['hops']:
                            if len(hop['details']) < 3 and hop['hop'] not in ['1', '2']:
                                analysis['issues'].append({
                                    'type': 'packet_loss_zone',
                                    'severity': 'high',
                                    'hop': hop['hop'],
                                    'target': target,
                                    'description': f"Packet loss starts at hop {hop['hop']}"
                                })
                                
            # Analyze speed test results
            if 'speedtest' in self.diagnostics_results:
                speed_result = self.diagnostics_results['speedtest']
                
                if 'error' not in speed_result:
                    # Check if speeds are below expected thresholds (adjust based on your needs)
                    if speed_result['download_speed'] < 10:
                        analysis['issues'].append({
                            'type': 'slow_download',
                            'severity': 'high',
                            'value': f"{speed_result['download_speed']} Mbps",
                            'description': "Download speed is significantly slower than expected"
                        })
                        
                    if speed_result['upload_speed'] < 5:
                        analysis['issues'].append({
                            'type': 'slow_upload',
                            'severity': 'medium',
                            'value': f"{speed_result['upload_speed']} Mbps",
                            'description': "Upload speed is slower than expected"
                        })
                        
            # Generate diagnosis and recommendations
            if analysis['issues']:
                issues_text = '\n'.join([
                    f"- {issue['description']}" for issue in analysis['issues']
                ])
                
                analysis['diagnosis'] = (
                    "Sunya Networking has identified several potential network issues:\n"
                    f"{issues_text}"
                )
                
                analysis['recommendations'] = [
                    "Check physical connections and cable quality",
                    "Restart your modem/router if experiencing packet loss",
                    "Contact your ISP if high latency persists",
                    "Consider a wired connection if Wi-Fi issues are suspected"
                ]
                
            else:
                analysis['diagnosis'] = (
                    "Sunya Networking diagnostics completed without finding major issues.\n"
                    "Network performance appears to be within normal parameters."
                )
                
                analysis['recommendations'] = [
                    "Network is functioning normally",
                    "Monitor for any future connectivity changes"
                ]
                
            # Save analysis to file
            with open(f"{self.report_dir}/analysis/diagnosis.txt", 'w') as f:
                f.write(analysis['diagnosis'])
                
            with open(f"{self.report_dir}/analysis/recommendations.txt", 'w') as f:
                for rec in analysis['recommendations']:
                    f.write(f"• {rec}\n")
                    
            logger.info("Analysis completed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {'error': str(e)}
            
    def generate_pdf_report(self) -> str:
        """Generate SUNYA format PDF report"""
        logger.info("Generating PDF report...")
        
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Add cover page
            pdf.add_page()
            
            # Title
            pdf.set_font('Arial', 'B', 24)
            pdf.cell(0, 20, 'Sunya Networking', 0, 1, 'C')
            
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, 'Professional Network Automation & Diagnostics Suite', 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, f"Report Generated: {self.network_fingerprint['timestamp']}", 0, 1, 'C')
            
            # Executive Summary
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Executive Summary', 0, 1, 'L')
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.5)
            pdf.line(10, 33, 200, 33)
            
            pdf.set_font('Arial', '', 10)
            pdf.ln(10)
            
            # Confidence Score
            if 'analysis' in self.diagnostics_results:
                analysis = self.diagnostics_results['analysis']
                confidence_score = analysis.get('confidence_score', 0)
                
                # Determine color based on score
                if confidence_score >= 80:
                    color = (0, 128, 0)  # Green
                elif confidence_score >= 60:
                    color = (255, 165, 0)  # Orange
                else:
                    color = (255, 0, 0)  # Red
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"Diagnosis Confidence Score: {confidence_score:.1f}%", 0, 1, 'L')
                pdf.ln(5)
                
                # Primary Diagnosis
                if 'diagnosis' in analysis and analysis['diagnosis']:
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, 'Primary Diagnosis:', 0, 1, 'L')
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 8, analysis['diagnosis'])
                    pdf.ln(5)
                
                # Detected Patterns
                if 'patterns' in analysis and analysis['patterns']:
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, 'Detected Network Patterns:', 0, 1, 'L')
                    pdf.set_font('Arial', '', 10)
                    for pattern in analysis['patterns']:
                        pdf.cell(0, 8, f"• {self.get_pattern_description(pattern)}", 0, 1, 'L')
                    pdf.ln(5)
                
                # Recommendations
                if 'recommendations' in analysis and analysis['recommendations']:
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, 'Recommendations:', 0, 1, 'L')
                    pdf.set_font('Arial', '', 10)
                    for rec in analysis['recommendations']:
                        pdf.cell(0, 8, f"• {rec}", 0, 1, 'L')
                    pdf.ln(5)
            
            # Network Fingerprint
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Network Fingerprint', 0, 1, 'L')
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.5)
            pdf.line(10, 33, 200, 33)
            
            pdf.set_font('Arial', '', 10)
            pdf.ln(10)
            
            # Platform
            pdf.cell(50, 10, f"Platform: {self.network_fingerprint['platform']}", 0, 1, 'L')
            
            # Interfaces
            pdf.cell(50, 10, "Interfaces:", 0, 1, 'L')
            for iface in self.network_fingerprint['interfaces']:
                pdf.cell(50, 8, f"  • {iface['name']} ({iface['type']}):", 0, 0, 'L')
                ips = ', '.join(iface['ip_addresses'])
                pdf.cell(0, 8, ips, 0, 1, 'L')
                
            # Gateway
            gateway = self.network_fingerprint.get('gateway', 'Not found')
            pdf.cell(50, 8, f"Gateway: {gateway}", 0, 1, 'L')
            
            # DNS Servers
            dns_servers = self.network_fingerprint.get('dns_servers', [])
            if dns_servers:
                pdf.cell(50, 8, "DNS Servers:", 0, 0, 'L')
                pdf.cell(0, 8, ', '.join(dns_servers), 0, 1, 'L')
                
            # Diagnostics Results
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Diagnostics Results', 0, 1, 'L')
            pdf.set_line_width(0.5)
            pdf.line(10, 33, 200, 33)
            
            # Speed Test
            if 'speedtest' in self.diagnostics_results:
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'Speed Test Results', 0, 1, 'L')
                
                speed_result = self.diagnostics_results['speedtest']
                if 'error' not in speed_result:
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(50, 8, f"Download Speed: {speed_result['download_speed']} Mbps", 0, 1, 'L')
                    pdf.cell(50, 8, f"Upload Speed: {speed_result['upload_speed']} Mbps", 0, 1, 'L')
                    pdf.cell(50, 8, f"Ping: {speed_result['ping']} ms", 0, 1, 'L')
                    
                    server = speed_result['server']
                    pdf.cell(50, 8, f"Server: {server['name']}, {server['country']}", 0, 1, 'L')
                    pdf.cell(50, 8, f"Sponsor: {server['sponsor']}", 0, 1, 'L')
                    
            # Ping Results
            if 'ping' in self.diagnostics_results:
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'Ping Results (1400 bytes)', 0, 1, 'L')
                
                for target, metrics in self.diagnostics_results['ping'].items():
                    if 'error' not in metrics:
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(50, 8, f"{target}:", 0, 0, 'L')
                        pdf.cell(0, 8, f"Loss: {metrics['packet_loss']}%, Avg: {metrics['avg_latency']}ms", 0, 1, 'L')
                
            # Analysis
            if self.diagnostics_results:
                analysis = self.run_analysis()
                
                pdf.add_page()
                pdf.set_font('Arial', 'B', 16)
                pdf.cell(0, 10, 'Analysis & Diagnostics', 0, 1, 'L')
                pdf.set_line_width(0.5)
                pdf.line(10, 33, 200, 33)
                
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'Diagnosis:', 0, 1, 'L')
                
                pdf.set_font('Arial', '', 10)
                for line in analysis['diagnosis'].split('\n'):
                    pdf.cell(0, 8, line, 0, 1, 'L')
                
                if analysis['recommendations']:
                    pdf.ln(10)
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 8, 'Recommendations:', 0, 1, 'L')
                    
                    pdf.set_font('Arial', '', 10)
                    for rec in analysis['recommendations']:
                        pdf.cell(50, 8, f"• {rec}", 0, 1, 'L')
                        
            # Save PDF
            pdf_path = f"{self.report_dir}/Sunya_Network_Report.pdf"
            pdf.output(pdf_path)
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return None
            
    def run_full_diagnostic_cycle(self) -> str:
        """Run complete diagnostic cycle from start to finish"""
        logger.info("Starting full diagnostic cycle...")
        
        try:
            # Step 1: Generate network fingerprint
            fingerprint = self.generate_network_fingerprint()
            if not fingerprint:
                logger.error("Failed to generate network fingerprint")
                return None
                
            # Step 2: Create report directory
            report_dir = self.create_report_directory()
            if not report_dir:
                logger.error("Failed to create report directory")
                return None
                
            # Step 3: Save network information
            with open(f"{report_dir}/network_info.txt", 'w') as f:
                for key, value in fingerprint.items():
                    if isinstance(value, list):
                        f.write(f"{key}:\n")
                        for item in value:
                            f.write(f"  - {str(item)}\n")
                    else:
                        f.write(f"{key}: {str(value)}\n")
                        
            # Step 4: Run diagnostics in parallel
            results = self.run_parallel_diagnostics()
            if not results:
                logger.error("Diagnostics failed to run")
                return None
                
            # Step 5: Save results to JSON
            with open(f"{report_dir}/results.json", 'w') as f:
                json.dump(results, f, indent=2, default=str)
                
            # Step 6: Run analysis
            analysis = self.run_analysis()
            
            # Step 7: Generate and save alerts
            alerts = self.generate_alerts(analysis)
            if alerts:
                self.save_alerts(alerts)
                
            # Step 8: Generate evidence integrity summary
            self.save_evidence_summary()
            
            # Step 9: Generate PDF report
            pdf_path = self.generate_pdf_report()
            if not pdf_path:
                logger.error("PDF report generation failed")
                return None
                
            logger.info("Full diagnostic cycle completed successfully")
            return report_dir
            
        except Exception as e:
            logger.error(f"Diagnostic cycle failed: {e}")
            return None
            
# Main entry point for testing
if __name__ == "__main__":
    logger.info("Sunya Networking Core Engine")
    logger.info("===========================")
    
    sunya = SunyaCore()
    
    # Run full diagnostic cycle
    report_dir = sunya.run_full_diagnostic_cycle()
    
    if report_dir:
        logger.info(f"Report created at: {report_dir}")
    else:
        logger.error("Diagnostic cycle failed")