#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Network Diagnostic Tool
Automates all network testing processes with detailed PDF report generation
"""

import os
import sys
import time
import logging
import subprocess
import platform
import datetime
import pyautogui
import tempfile
import socket
import psutil
from pathlib import Path
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import ping3
import speedtest
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive-network-diagnostic.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveNetworkDiagnostic:
    """Comprehensive network diagnostic tool with all testing capabilities"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.report_folder = None
        self.screenshots = []
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.driver = None
        self.test_results = {
            'pc_details': {},
            'pings': {},
            'traceroutes': {},
            'speed_tests': {},
            'load_tests': {}
        }
    
    def create_report_folder(self):
        """Create a new folder on desktop to store report files"""
        logger.info("Creating report folder on desktop...")
        
        try:
            # Get desktop path
            if self.platform == 'windows':
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            elif self.platform == 'linux':
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            elif self.platform == 'darwin':
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            else:
                desktop_path = tempfile.mkdtemp()
            
            self.report_folder = os.path.join(desktop_path, f"Comprehensive_Network_Report_{self.timestamp}")
            os.makedirs(self.report_folder, exist_ok=True)
            logger.info(f"Report folder created: {self.report_folder}")
            
            return self.report_folder
            
        except Exception as e:
            logger.error(f"Failed to create report folder: {e}")
            return None
    
    def get_pc_details(self):
        """Get comprehensive PC and network interface details"""
        logger.info("Collecting PC details...")
        
        try:
            # System information
            self.test_results['pc_details'] = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'interfaces': []
            }
            
            # Network interfaces with speed capabilities
            interfaces = psutil.net_if_addrs()
            for interface_name, addresses in interfaces.items():
                interface_info = {
                    'name': interface_name,
                    'ip_addresses': [],
                    'speed': 'Unknown',
                    'type': 'Unknown',
                    'is_gigabit': False
                }
                
                # Get IP addresses
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        interface_info['ip_addresses'].append(addr.address)
                
                # Determine interface type
                if 'wi-fi' in interface_name.lower() or 'wireless' in interface_name.lower():
                    interface_info['type'] = 'Wi-Fi'
                elif 'ethernet' in interface_name.lower() or 'eth' in interface_name.lower():
                    interface_info['type'] = 'Ethernet'
                elif 'loopback' in interface_name.lower() or 'lo' in interface_name.lower():
                    interface_info['type'] = 'Loopback'
                elif 'bluetooth' in interface_name.lower():
                    interface_info['type'] = 'Bluetooth'
                
                # Check if interface is gigabit capable (Windows specific)
                if self.platform == 'windows':
                    try:
                        import wmi
                        w = wmi.WMI()
                        for nic in w.Win32_NetworkAdapter():
                            if nic.Name in interface_name or interface_name in nic.Name:
                                if nic.Speed:
                                    speed_mbps = int(nic.Speed) / 1_000_000  # Convert to Mbps
                                    interface_info['speed'] = f"{speed_mbps} Mbps"
                                    interface_info['is_gigabit'] = speed_mbps >= 1000
                    except Exception as e:
                        logger.warning(f"Failed to get interface speed: {e}")
                elif self.platform == 'linux':
                    try:
                        speed_file = f"/sys/class/net/{interface_name}/speed"
                        if os.path.exists(speed_file):
                            with open(speed_file, 'r') as f:
                                speed_mbps = int(f.read().strip())
                                interface_info['speed'] = f"{speed_mbps} Mbps"
                                interface_info['is_gigabit'] = speed_mbps >= 1000
                    except Exception as e:
                        logger.warning(f"Failed to get interface speed: {e}")
                
                self.test_results['pc_details']['interfaces'].append(interface_info)
                
            logger.info("PC details collected successfully")
            
        except Exception as e:
            logger.error(f"Failed to collect PC details: {e}")
    
    def ping_targets(self, targets):
        """Ping multiple target IP addresses and capture results"""
        logger.info("Starting ping tests...")
        
        for target in targets:
            logger.info(f"Pinging {target}...")
            
            try:
                # Capture screenshot before ping
                screenshot_path = os.path.join(self.report_folder, f"ping_{target}_{self.timestamp}.png")
                pyautogui.screenshot(screenshot_path)
                self.screenshots.append(screenshot_path)
                
                # Perform ping
                results = []
                packet_loss = 0
                min_rtt = float('inf')
                max_rtt = float('-inf')
                avg_rtt = 0
                
                for i in range(10):  # Send 10 pings
                    response_time = ping3.ping(target, timeout=2)
                    if response_time:
                        results.append(response_time)
                        if response_time < min_rtt:
                            min_rtt = response_time
                        if response_time > max_rtt:
                            max_rtt = response_time
                    else:
                        packet_loss += 1
                
                if results:
                    avg_rtt = sum(results) / len(results)
                
                # Store results
                self.test_results['pings'][target] = {
                    'packet_loss': (packet_loss / 10) * 100,
                    'min_rtt': min_rtt * 1000 if min_rtt != float('inf') else 0,  # Convert to ms
                    'max_rtt': max_rtt * 1000 if max_rtt != float('-inf') else 0,  # Convert to ms
                    'avg_rtt': avg_rtt * 1000,  # Convert to ms
                    'screenshot': screenshot_path
                }
                
                logger.info(f"Ping to {target} completed: {packet_loss}% loss, avg {avg_rtt*1000:.2f}ms")
                
            except Exception as e:
                logger.error(f"Ping to {target} failed: {e}")
                self.test_results['pings'][target] = {
                    'error': str(e),
                    'screenshot': screenshot_path
                }
            
            # Remove unnecessary delay between pings
    
    def run_traceroute(self, targets):
        """Run traceroute commands on target IP addresses in parallel"""
        logger.info("Starting traceroute tests...")
        
        # Run traceroutes in parallel for faster execution
        from concurrent.futures import ThreadPoolExecutor
        
        def run_single_traceroute(target):
            logger.info(f"Running traceroute to {target}...")
            
            try:
                if self.platform == 'windows':
                    cmd = ['tracert', '-d', target]
                else:
                    cmd = ['traceroute', '-I', target]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=45  # Reduced timeout for faster execution
                )
                
                logger.info(f"Traceroute to {target} completed")
                return target, {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                
            except Exception as e:
                logger.error(f"Traceroute to {target} failed: {e}")
                return target, {'error': str(e)}
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=len(targets)) as executor:
            future_to_target = {
                executor.submit(run_single_traceroute, target): target 
                for target in targets
            }
            
            for future in as_completed(future_to_target):
                target, result = future.result()
                self.test_results['traceroutes'][target] = result
    
    def setup_chrome_driver(self):
        """Setup Chrome driver with appropriate options"""
        logger.info("Setting up Chrome driver...")
        
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--no-sandbox')
            
            # Create driver instance
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Chrome driver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def capture_browser_screenshot(self, name):
        """Capture and save a screenshot from the browser with minimal delay"""
        try:
            logger.info(f"Capturing browser screenshot: {name}")
            
            # Reduced wait time for faster execution
            time.sleep(0.5)
            screenshot_path = os.path.join(self.report_folder, f"{name}_{self.timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            self.screenshots.append(screenshot_path)
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
            
    def run_speed_tests(self):
        """Run speed tests on multiple websites using Chrome with optimized performance"""
        logger.info("Starting speed tests...")
        
        # Reduce number of speed test sites for faster execution
        speed_test_websites = [
            {
                'name': 'Fast.com',
                'url': 'https://fast.com/',
                'start_button': None  # Auto-starts, fastest test
            },
            {
                'name': 'Speedtest.net',
                'url': 'https://www.speedtest.net/',
                'start_button': '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[1]/a/span[4]'
            }
        ]
        
        for site in speed_test_websites:
            logger.info(f"Testing on {site['name']}...")
            
            try:
                self.driver.get(site['url'])
                time.sleep(3)  # Reduced wait time for page load
                
                # Click start button if needed
                if site['start_button']:
                    try:
                        start_button = WebDriverWait(self.driver, 8).until(  # Reduced wait time
                            EC.element_to_be_clickable((By.XPATH, site['start_button']))
                        )
                        start_button.click()
                        logger.info("Start button clicked")
                    except Exception as e:
                        logger.warning(f"Could not click start button: {e}")
                
                # Wait for test to complete - reduced for faster execution
                logger.info(f"Waiting for {site['name']} to complete...")
                if site['name'] == 'Fast.com':
                    time.sleep(30)  # Fast.com is quicker
                else:
                    time.sleep(45)  # Reduced from 60 seconds
                
                # Capture screenshot
                screenshot = self.capture_browser_screenshot(f"speedtest_{site['name']}")
                
                # Extract results if possible (basic parsing)
                try:
                    download_speed = None
                    upload_speed = None
                    ping = None
                    
                    # Try to find speed elements
                    page_source = self.driver.page_source
                    
                    # This is a basic attempt - actual extraction would need to be more robust
                    if 'Mbps' in page_source:
                        # Look for patterns like "100.0 Mbps"
                        import re
                        speeds = re.findall(r'(\d+\.?\d*) Mbps', page_source)
                        if speeds:
                            download_speed = float(speeds[0])
                            if len(speeds) > 1:
                                upload_speed = float(speeds[1])
                    
                    if 'ms' in page_source:
                        pings = re.findall(r'(\d+\.?\d*) ms', page_source)
                        if pings:
                            ping = float(pings[0])
                    
                    self.test_results['speed_tests'][site['name']] = {
                        'download_speed': download_speed,
                        'upload_speed': upload_speed,
                        'ping': ping,
                        'screenshot': screenshot
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to extract speed test results: {e}")
                    self.test_results['speed_tests'][site['name']] = {
                        'screenshot': screenshot,
                        'warning': 'Could not extract results'
                    }
                
                logger.info(f"Speed test on {site['name']} completed")
                
            except Exception as e:
                logger.error(f"Speed test on {site['name']} failed: {e}")
                self.test_results['speed_tests'][site['name']] = {
                    'error': str(e)
                }
            
            time.sleep(3)
    
    def run_speedtest_cli(self):
        """Run speed test using speedtest-cli library for reliability"""
        logger.info("Running CLI speed test...")
        
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            logger.info("Testing download speed...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            
            logger.info("Testing upload speed...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            
            ping_result = st.results.ping
            
            self.test_results['speed_tests']['Speedtest CLI'] = {
                'download_speed': download_speed,
                'upload_speed': upload_speed,
                'ping': ping_result
            }
            
            logger.info(f"CLI Speed Test Results: Download {download_speed:.2f} Mbps, Upload {upload_speed:.2f} Mbps, Ping {ping_result:.2f}ms")
            
        except Exception as e:
            logger.error(f"CLI speed test failed: {e}")
            self.test_results['speed_tests']['Speedtest CLI'] = {
                'error': str(e)
            }
    
    def load_test_targets(self, targets):
        """Perform load testing on target IP addresses"""
        logger.info("Starting load tests...")
        
        for target in targets:
            logger.info(f"Load testing {target}...")
            
            try:
                results = []
                
                # Simulate load by sending multiple concurrent pings
                for i in range(5):
                    thread_results = []
                    
                    def ping_task():
                        for j in range(5):
                            response = ping3.ping(target, timeout=1)
                            if response:
                                thread_results.append(response * 1000)  # Convert to ms
                    
                    # Create multiple threads for concurrent pings
                    import threading
                    threads = []
                    for j in range(3):
                        t = threading.Thread(target=ping_task)
                        threads.append(t)
                        t.start()
                    
                    for t in threads:
                        t.join()
                    
                    results.extend(thread_results)
                    time.sleep(1)
                
                # Calculate statistics
                if results:
                    min_rtt = min(results)
                    max_rtt = max(results)
                    avg_rtt = sum(results) / len(results)
                    packet_loss = (25 - len(results)) / 25 * 100  # Total expected: 5*5=25
                else:
                    min_rtt = 0
                    max_rtt = 0
                    avg_rtt = 0
                    packet_loss = 100
                
                self.test_results['load_tests'][target] = {
                    'packet_loss': packet_loss,
                    'min_rtt': min_rtt,
                    'max_rtt': max_rtt,
                    'avg_rtt': avg_rtt,
                    'total_packets': len(results)
                }
                
                logger.info(f"Load test on {target} completed: {packet_loss:.1f}% loss, avg {avg_rtt:.2f}ms")
                
            except Exception as e:
                logger.error(f"Load test on {target} failed: {e}")
                self.test_results['load_tests'][target] = {
                    'error': str(e)
                }
            
            time.sleep(2)
    
    def generate_pdf_report(self):
        """Generate comprehensive PDF report"""
        logger.info("Generating PDF report...")
        
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font('Arial', 'B', 16)
            
            # Title Page
            pdf.add_page()
            pdf.cell(0, 10, 'COMPREHENSIVE NETWORK DIAGNOSTIC REPORT', 0, 1, 'C')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
            pdf.ln(20)
            
            # PC Details Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '1. SYSTEM INFORMATION', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            pc_details = self.test_results['pc_details']
            pdf.cell(0, 8, f"System: {pc_details['system']} {pc_details['release']}", 0, 1)
            pdf.cell(0, 8, f"Machine: {pc_details['machine']}", 0, 1)
            pdf.cell(0, 8, f"Processor: {pc_details['processor']}", 0, 1)
            pdf.cell(0, 8, f"Hostname: {pc_details['hostname']}", 0, 1)
            pdf.cell(0, 8, f"IP Address: {pc_details['ip_address']}", 0, 1)
            pdf.ln(5)
            
            # Network Interfaces
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Network Interfaces:', 0, 1)
            pdf.set_font('Arial', '', 11)
            
            for interface in pc_details['interfaces']:
                pdf.cell(0, 7, f"- {interface['name']} ({interface['type']})", 0, 1)
                for ip in interface['ip_addresses']:
                    pdf.cell(0, 7, f"  IP: {ip}", 0, 1)
                pdf.cell(0, 7, f"  Speed: {interface['speed']}", 0, 1)
                pdf.cell(0, 7, f"  Gigabit Capable: {'Yes' if interface['is_gigabit'] else 'No'}", 0, 1)
                pdf.ln(2)
            
            pdf.ln(10)
            
            # Ping Tests Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '2. PING TEST RESULTS', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(40, 8, 'Target', 1, 0, 'C')
            pdf.cell(25, 8, 'Loss %', 1, 0, 'C')
            pdf.cell(25, 8, 'Min RTT', 1, 0, 'C')
            pdf.cell(25, 8, 'Max RTT', 1, 0, 'C')
            pdf.cell(25, 8, 'Avg RTT', 1, 0, 'C')
            pdf.ln()
            
            pdf.set_font('Arial', '', 10)
            for target, result in self.test_results['pings'].items():
                if 'error' in result:
                    pdf.cell(40, 8, target, 1, 0)
                    pdf.cell(25, 8, 'Error', 1, 0)
                    pdf.cell(25, 8, '', 1, 0)
                    pdf.cell(25, 8, '', 1, 0)
                    pdf.cell(25, 8, '', 1, 0)
                    pdf.ln()
                else:
                    pdf.cell(40, 8, target, 1, 0)
                    pdf.cell(25, 8, f"{result['packet_loss']:.1f}", 1, 0, 'C')
                    pdf.cell(25, 8, f"{result['min_rtt']:.1f}ms", 1, 0, 'C')
                    pdf.cell(25, 8, f"{result['max_rtt']:.1f}ms", 1, 0, 'C')
                    pdf.cell(25, 8, f"{result['avg_rtt']:.1f}ms", 1, 0, 'C')
                    pdf.ln()
            
            pdf.ln(10)
            
            # Load Test Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '3. LOAD TEST RESULTS', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(40, 8, 'Target', 1, 0, 'C')
            pdf.cell(25, 8, 'Loss %', 1, 0, 'C')
            pdf.cell(25, 8, 'Min RTT', 1, 0, 'C')
            pdf.cell(25, 8, 'Max RTT', 1, 0, 'C')
            pdf.cell(25, 8, 'Avg RTT', 1, 0, 'C')
            pdf.ln()
            
            pdf.set_font('Arial', '', 10)
            for target, result in self.test_results['load_tests'].items():
                if 'error' in result:
                    pdf.cell(40, 8, target, 1, 0)
                    pdf.cell(25, 8, 'Error', 1, 0)
                    pdf.cell(25, 8, '', 1, 0)
                    pdf.cell(25, 8, '', 1, 0)
                    pdf.cell(25, 8, '', 1, 0)
                    pdf.ln()
                else:
                    pdf.cell(40, 8, target, 1, 0)
                    pdf.cell(25, 8, f"{result['packet_loss']:.1f}", 1, 0, 'C')
                    pdf.cell(25, 8, f"{result['min_rtt']:.1f}ms", 1, 0, 'C')
                    pdf.cell(25, 8, f"{result['max_rtt']:.1f}ms", 1, 0, 'C')
                    pdf.cell(25, 8, f"{result['avg_rtt']:.1f}ms", 1, 0, 'C')
                    pdf.ln()
            
            pdf.ln(10)
            
            # Speed Test Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '4. SPEED TEST RESULTS', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(40, 8, 'Test Source', 1, 0, 'C')
            pdf.cell(30, 8, 'Download', 1, 0, 'C')
            pdf.cell(30, 8, 'Upload', 1, 0, 'C')
            pdf.cell(20, 8, 'Ping', 1, 0, 'C')
            pdf.ln()
            
            pdf.set_font('Arial', '', 10)
            for source, result in self.test_results['speed_tests'].items():
                if 'error' in result:
                    pdf.cell(40, 8, source, 1, 0)
                    pdf.cell(30, 8, 'Error', 1, 0)
                    pdf.cell(30, 8, '', 1, 0)
                    pdf.cell(20, 8, '', 1, 0)
                    pdf.ln()
                else:
                    download = f"{result['download_speed']:.2f} Mbps" if result.get('download_speed') else 'N/A'
                    upload = f"{result['upload_speed']:.2f} Mbps" if result.get('upload_speed') else 'N/A'
                    ping = f"{result['ping']:.2f}ms" if result.get('ping') else 'N/A'
                    
                    pdf.cell(40, 8, source, 1, 0)
                    pdf.cell(30, 8, download, 1, 0, 'C')
                    pdf.cell(30, 8, upload, 1, 0, 'C')
                    pdf.cell(20, 8, ping, 1, 0, 'C')
                    pdf.ln()
            
            pdf.ln(10)
            
            # Traceroute Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '5. TRACEROUTE RESULTS', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            for target, result in self.test_results['traceroutes'].items():
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, f"Target: {target}", 0, 1)
                pdf.set_font('Arial', '', 8)
                
                if 'error' in result:
                    pdf.multi_cell(0, 5, f"Error: {result['error']}")
                else:
                    # Write traceroute output with proper formatting
                    traceroute_output = result['stdout']
                    for line in traceroute_output.split('\n'):
                        if line.strip():
                            pdf.multi_cell(0, 5, line)
                
                pdf.ln(5)
            
            pdf.ln(10)
            
            # Screenshots Section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '6. SCREENSHOTS', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            for screenshot in self.screenshots:
                try:
                    if os.path.exists(screenshot):
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, os.path.basename(screenshot), 0, 1)
                        
                        # Add screenshot
                        pdf.image(screenshot, x=10, y=30, w=190)
                        
                except Exception as e:
                    logger.warning(f"Failed to add screenshot {screenshot}: {e}")
                    pdf.cell(0, 10, f"Failed to load screenshot: {os.path.basename(screenshot)}", 0, 1)
            
            # Save PDF
            pdf_filename = os.path.join(self.report_folder, f"Network_Diagnostic_Report_{self.timestamp}.pdf")
            pdf.output(pdf_filename)
            logger.info(f"PDF report generated: {pdf_filename}")
            
            return pdf_filename
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Failed to quit driver: {e}")
    
    def run_diagnostics(self):
        """Run complete diagnostic process"""
        logger.info("Starting comprehensive network diagnostics...")
        
        try:
            # Step 1: Create report folder
            if not self.create_report_folder():
                logger.error("Failed to create report folder")
                return False
            
            # Step 2: Collect PC details
            self.get_pc_details()
            
            # Step 3: Define test targets (network own IPs and common targets)
            test_targets = ['8.8.8.8', '8.8.4.4', '1.1.1.1', 'google.com', 'facebook.com', 'twitter.com']
            
            # Add local network IPs
            for interface in self.test_results['pc_details']['interfaces']:
                for ip in interface['ip_addresses']:
                    if ip and not ip.startswith('127.'):
                        test_targets.append(ip)
            
            test_targets = list(set(test_targets))  # Remove duplicates
            
            # Step 4: Ping tests
            self.ping_targets(test_targets)
            
            # Step 5: Load tests
            self.load_test_targets(test_targets)
            
            # Step 6: Traceroute tests
            self.run_traceroute(test_targets)
            
            # Step 7: Speed tests
            if self.setup_chrome_driver():
                self.run_speed_tests()
                self.driver.quit()
            
            # Step 8: CLI speed test (backup if Chrome fails)
            self.run_speedtest_cli()
            
            # Step 9: Generate report
            pdf_path = self.generate_pdf_report()
            
            if pdf_path:
                logger.info("Diagnostics completed successfully!")
                logger.info(f"Report saved to: {pdf_path}")
                
                # Open the report folder automatically
                if self.platform == 'windows':
                    os.startfile(self.report_folder)
                elif self.platform == 'macos':
                    subprocess.run(['open', self.report_folder])
                elif self.platform == 'linux':
                    subprocess.run(['xdg-open', self.report_folder])
                
                return True
            else:
                logger.error("Report generation failed")
                return False
                
        except Exception as e:
            logger.error(f"Diagnostic process failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function to run the comprehensive network diagnostic tool"""
    
    # Check for help option
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Comprehensive Network Diagnostic Tool")
        print("====================================")
        print("Automates all network testing processes with detailed PDF report generation")
        print("\nUsage:")
        print("  python comprehensive-network-diagnostic.py")
        print("  python comprehensive-network-diagnostic.py --help")
        print("\nOptions:")
        print("  --help    Show this help message and exit")
        return 0
    
    logger.info("============================================")
    logger.info("  Comprehensive Network Diagnostic Tool")
    logger.info("============================================")
    logger.info(f"Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tool = ComprehensiveNetworkDiagnostic()
    
    if tool.run_diagnostics():
        logger.info("============================================")
        logger.info("  Diagnostics Completed Successfully!")
        logger.info("============================================")
        return 0
    else:
        logger.error("============================================")
        logger.error("  Diagnostics Failed!")
        logger.error("============================================")
        return 1

if __name__ == "__main__":
    sys.exit(main())
