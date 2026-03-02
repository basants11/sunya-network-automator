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
            
    def run_parallel_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic modules in parallel with optimized performance"""
        logger.info("Starting parallel diagnostics...")
        
        if not self.report_dir:
            logger.error("No report directory created")
            return {}
        
        # Define diagnostic tasks
        diagnostic_tasks = [
            ('ping', self.run_ping_tests),
            ('traceroute', self.run_traceroute),
            ('speedtest', self.run_speedtest),
            ('mtr', self.run_mtr)
        ]
        
        results = {}
        
        try:
            # Use ProcessPoolExecutor for better parallelism (CPU bound tasks)
            from concurrent.futures import ProcessPoolExecutor
            
            # Determine optimal number of workers (CPU count * 1.5 for I/O bound tasks)
            import multiprocessing
            max_workers = min(multiprocessing.cpu_count() * 2, 8)  # Cap at 8 workers
            
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_task = {executor.submit(task): name for name, task in diagnostic_tasks}
                
                # Collect results
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        result = future.result(timeout=120)  # Reduce timeout to 2 minutes
                        results[task_name] = result
                        logger.info(f"{task_name} completed successfully")
                    except Exception as e:
                        logger.error(f"{task_name} failed: {e}")
                        results[task_name] = {'error': str(e)}
                        
            self.diagnostics_results = results
            logger.info("All diagnostics completed")
            return results
            
        except Exception as e:
            logger.error(f"Parallel diagnostics failed: {e}")
            return {}
            
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
                
            # Step 6: Generate PDF report
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