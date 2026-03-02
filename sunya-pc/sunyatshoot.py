#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sunyatshoot - Automatic Network Diagnostic Tool
Automatically starts network diagnostics when launched
"""

import os
import sys
import time
import logging
import platform
import datetime
import tempfile
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sunyatshoot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add core directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../sunya-core')))

from core import SunyaCore

class SunyatShootTool:
    """Sunyatshoot automatic network diagnostic tool"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.core = SunyaCore()
        self.report_folder = None
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.test_results = {}
        
    def create_report_folder(self):
        """Create a new folder to store report files"""
        logger.info("Creating report folder...")
        
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
            
            self.report_folder = os.path.join(desktop_path, f"SunyatShoot_Report_{self.timestamp}")
            os.makedirs(self.report_folder, exist_ok=True)
            logger.info(f"Report folder created: {self.report_folder}")
            
            return self.report_folder
            
        except Exception as e:
            logger.error(f"Failed to create report folder: {e}")
            return None
    
    def run_quick_diagnostics(self):
        """Run quick network diagnostics"""
        logger.info("Starting quick network diagnostics...")
        
        try:
            results = {}
            
            # Run ping test
            logger.info("Running ping test...")
            ping_result = self.core.ping_test('8.8.8.8', count=10, payload_size=1400)
            results['ping'] = ping_result
            
            # Run speed test
            logger.info("Running speed test...")
            speed_result = self.core.run_speedtest()
            results['speedtest'] = speed_result
            
            # Run traceroute
            logger.info("Running traceroute...")
            traceroute_result = self.core.traceroute('8.8.8.8', max_hops=20)
            results['traceroute'] = traceroute_result
            
            # Run MTR test
            logger.info("Running MTR test...")
            mtr_result = self.core.mtr_test('8.8.8.8', count=5)
            results['mtr'] = mtr_result
            
            # Get system information
            logger.info("Collecting system information...")
            system_info = self.core.get_system_info()
            results['system_info'] = system_info
            
            # Get network interfaces
            logger.info("Collecting network interface information...")
            network_info = self.core.get_network_interfaces()
            results['network_info'] = network_info
            
            self.test_results = results
            logger.info("Quick diagnostics completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running quick diagnostics: {e}")
            return None
    
    def generate_report(self):
        """Generate diagnostic report"""
        logger.info("Generating diagnostic report...")
        
        try:
            if not self.report_folder:
                if not self.create_report_folder():
                    logger.error("Failed to create report folder")
                    return None
            
            # Type annotation to fix type error
            assert self.report_folder is not None
            report_path = os.path.join(self.report_folder, f"sunyatshoot-report-{self.timestamp}.txt")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("         SUNYATSHOOT - NETWORK DIAGNOSTIC REPORT\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # System Information
                if 'system_info' in self.test_results:
                    f.write("=== SYSTEM INFORMATION ===\n")
                    for key, value in self.test_results['system_info'].items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                # Network Interfaces
                if 'network_info' in self.test_results:
                    f.write("=== NETWORK INTERFACES ===\n")
                    for interface in self.test_results['network_info']:
                        f.write(f"\nInterface: {interface.get('name', 'Unknown')}\n")
                        for key, value in interface.items():
                            if key != 'name':
                                f.write(f"  {key}: {value}\n")
                    f.write("\n")
                
                # Ping Results
                if 'ping' in self.test_results and self.test_results['ping']:
                    f.write("=== PING TEST RESULTS ===\n")
                    ping = self.test_results['ping']
                    f.write(f"Target: {ping.get('target', 'Unknown')}\n")
                    f.write(f"Packets Sent: {ping.get('packets_sent', 0)}\n")
                    f.write(f"Packets Received: {ping.get('packets_received', 0)}\n")
                    f.write(f"Packet Loss: {ping.get('packet_loss', 0)}%\n")
                    if 'rtt' in ping:
                        f.write(f"Min RTT: {ping['rtt'].get('min', 0)}ms\n")
                        f.write(f"Avg RTT: {ping['rtt'].get('avg', 0)}ms\n")
                        f.write(f"Max RTT: {ping['rtt'].get('max', 0)}ms\n")
                    f.write("\n")
                
                # Speed Test Results
                if 'speedtest' in self.test_results and self.test_results['speedtest']:
                    f.write("=== SPEED TEST RESULTS ===\n")
                    speed = self.test_results['speedtest']
                    f.write(f"Download: {speed.get('download', 0):.2f} Mbps\n")
                    f.write(f"Upload: {speed.get('upload', 0):.2f} Mbps\n")
                    f.write(f"Ping: {speed.get('ping', 0):.2f} ms\n")
                    f.write(f"Server: {speed.get('server_name', 'Unknown')} ({speed.get('server_country', 'Unknown')})\n")
                    f.write("\n")
                
                # Traceroute Results
                if 'traceroute' in self.test_results and self.test_results['traceroute']:
                    f.write("=== TRACEROUTE RESULTS ===\n")
                    for hop in self.test_results['traceroute']:
                        f.write(f"{hop.get('hop', 'Unknown')}: {hop.get('ip', 'Unknown')} ({hop.get('hostname', 'Unknown')})\n")
                    f.write("\n")
                
                # MTR Results
                if 'mtr' in self.test_results and self.test_results['mtr']:
                    f.write("=== MTR TEST RESULTS ===\n")
                    mtr = self.test_results['mtr']
                    for hop in mtr:
                        f.write(f"{hop.get('hop', 'Unknown')}: {hop.get('ip', 'Unknown')} ({hop.get('hostname', 'Unknown')})\n")
                        if 'statistics' in hop:
                            stats = hop['statistics']
                            f.write(f"  Loss: {stats.get('packet_loss', 0)}%, Avg: {stats.get('avg_rtt', 0)}ms\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("Report generated successfully\n")
            
            logger.info(f"Report generated: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def run_full_analysis(self):
        """Run comprehensive network analysis"""
        logger.info("Starting comprehensive network analysis...")
        
        try:
            # Create report folder
            if not self.create_report_folder():
                return False
            
            # Run quick diagnostics
            if not self.run_quick_diagnostics():
                logger.error("Quick diagnostics failed")
                return False
            
            # Generate comprehensive report
            report_path = self.generate_report()
            if not report_path:
                logger.error("Report generation failed")
                return False
            
            logger.info("Full analysis completed successfully")
            logger.info(f"Report location: {self.report_folder}")
            
            # Try to open the report folder
            try:
                if self.report_folder:
                    if self.platform == 'windows':
                        os.startfile(self.report_folder)
                    elif self.platform == 'linux':
                        subprocess.run(['xdg-open', self.report_folder])
                    elif self.platform == 'darwin':
                        subprocess.run(['open', self.report_folder])
            except Exception as e:
                logger.warning(f"Failed to open report folder: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error running full analysis: {e}")
            return False

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("  SUNYATSHOOT - Automatic Network Diagnostic Tool")
    logger.info("=" * 60)
    logger.info(f"Starting at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info("")
    
    try:
        # Create and run the tool
        tool = SunyatShootTool()
        success = tool.run_full_analysis()
        
        if success:
            logger.info("\nDiagnostic completed successfully!")
            logger.info("Report saved to your desktop")
        else:
            logger.error("\nDiagnostic failed! Check sunyatshoot.log for details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nDiagnostic canceled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        logger.error("Check sunyatshoot.log for detailed error information")
        sys.exit(1)
    finally:
        logger.info("")
        logger.info("=" * 60)
        logger.info("Diagnostic session ended")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()
