#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-Click Automation Tool
Runs all network tests from within Chrome browser using Selenium
"""

import os
import sys
import time
import logging
import subprocess
import platform
import datetime
import tempfile
from pathlib import Path
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('one-click-automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OneClickAutomationTool:
    """One-click automation tool for network diagnostics from Chrome browser"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.report_folder = None
        self.screenshots = []
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.driver = None
    
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
            
            self.report_folder = os.path.join(desktop_path, f"OneClick_Diagnostic_Report_{self.timestamp}")
            os.makedirs(self.report_folder, exist_ok=True)
            logger.info(f"Report folder created: {self.report_folder}")
            
            return self.report_folder
            
        except Exception as e:
            logger.error(f"Failed to create report folder: {e}")
            return None
    
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
    
    def capture_screenshot(self, name):
        """Capture and save a screenshot from the browser"""
        try:
            logger.info(f"Capturing screenshot: {name}")
            
            # Wait for page to stabilize
            time.sleep(2)
            
            # Capture screenshot
            screenshot_path = os.path.join(self.report_folder, f"{name}_{self.timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            
            self.screenshots.append(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def run_speedtest_in_browser(self):
        """Run speed test using fast.com from within Chrome"""
        logger.info("Running speed test in Chrome browser...")
        
        try:
            # Navigate to fast.com
            self.driver.get("https://fast.com")
            
            # Wait for speed test to start and complete
            logger.info("Waiting for speed test to complete...")
            
            # Wait for initial download test
            time.sleep(30)
            
            # Click "Show more info" to see upload speed
            try:
                show_more_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "show-more-details-link"))
                )
                show_more_btn.click()
                logger.info("Show more details clicked")
            except Exception as e:
                logger.warning(f"Could not click 'Show more info': {e}")
            
            # Wait for upload test to complete
            time.sleep(30)
            
            # Capture speed test results
            download_speed = None
            upload_speed = None
            
            try:
                download_element = self.driver.find_element(By.ID, "speed-value")
                download_speed = download_element.text
                
                upload_element = self.driver.find_element(By.ID, "upload-value")
                upload_speed = upload_element.text
                
                logger.info(f"Speed test results: {download_speed} Mbps down, {upload_speed} Mbps up")
            except Exception as e:
                logger.warning(f"Could not extract speed test results: {e}")
            
            # Save results
            speedtest_file = os.path.join(self.report_folder, f"speedtest_results_{self.timestamp}.txt")
            with open(speedtest_file, 'w') as f:
                f.write(f"Speed Test Results ({self.timestamp})\n")
                f.write("=" * 40 + "\n")
                f.write(f"Download Speed: {download_speed} Mbps\n")
                f.write(f"Upload Speed: {upload_speed} Mbps\n")
                f.write(f"Source: fast.com\n")
            
            # Capture screenshot
            self.capture_screenshot("speedtest_browser")
            
            return True
            
        except Exception as e:
            logger.error(f"Speed test failed: {e}")
            return False
    
    def run_ping_test(self, target="8.8.8.8", count=20):
        """Run ping test using online tool in Chrome"""
        logger.info(f"Running ping test to {target}")
        
        try:
            # Navigate to ping test website
            self.driver.get(f"https://www.pingtest.net/")
            
            # Wait for page to load
            time.sleep(5)
            
            # Capture screenshot
            self.capture_screenshot("ping_test")
            
            # Also run local ping test
            if self.platform == 'windows':
                cmd = f"ping -n {count} -l 1400 {target}"
            else:
                cmd = f"ping -c {count} -s 1400 {target}"
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            ping_file = os.path.join(self.report_folder, f"ping_results_{self.timestamp}.txt")
            with open(ping_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\nErrors:\n{result.stderr}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ping test failed: {e}")
            return False
    
    def run_traceroute_test(self, target="8.8.8.8"):
        """Run traceroute test using online tool in Chrome"""
        logger.info(f"Running traceroute to {target}")
        
        try:
            # Navigate to traceroute test website
            self.driver.get(f"https://www.traceroute.org/")
            
            # Wait for page to load
            time.sleep(5)
            
            # Capture screenshot
            self.capture_screenshot("traceroute_test")
            
            # Also run local traceroute test
            if self.platform == 'windows':
                cmd = f"tracert -d {target}"
            else:
                cmd = f"traceroute {target}"
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            traceroute_file = os.path.join(self.report_folder, f"traceroute_results_{self.timestamp}.txt")
            with open(traceroute_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\nErrors:\n{result.stderr}")
            
            return True
            
        except Exception as e:
            logger.error(f"Traceroute failed: {e}")
            return False
    
    def run_speedtest_cli(self):
        """Run speed test using speedtest-cli (fallback)"""
        logger.info("Running speed test using speedtest-cli...")
        
        try:
            import speedtest
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 10**6  # Mbps
            upload_speed = st.upload() / 10**6  # Mbps
            ping_result = st.results.ping
            
            # Save speed test results
            speedtest_file = os.path.join(self.report_folder, f"speedtest_cli_results_{self.timestamp}.txt")
            with open(speedtest_file, 'w') as f:
                f.write(f"Speed Test Results ({self.timestamp})\n")
                f.write("=" * 40 + "\n")
                f.write(f"Download Speed: {download_speed:.2f} Mbps\n")
                f.write(f"Upload Speed: {upload_speed:.2f} Mbps\n")
                f.write(f"Ping: {ping_result:.2f} ms\n")
                f.write(f"Server: {st.results.server['name']}, {st.results.server['country']}\n")
                f.write(f"Sponsor: {st.results.server['sponsor']}\n")
            
            logger.info(f"Speed test completed: {download_speed:.2f} Mbps down, {upload_speed:.2f} Mbps up")
            
            return True
            
        except Exception as e:
            logger.error(f"Speed test failed: {e}")
            return False
    
    def compile_pdf_report(self):
        """Compile all screenshots and results into a PDF report"""
        logger.info("Compiling PDF report...")
        
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Add report title
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f"One-Click Network Diagnostic Report - {self.timestamp}", 0, 1, 'C')
            pdf.ln(10)
            
            # Add system information
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f"Platform: {platform.system()} {platform.release()}", 0, 1)
            pdf.cell(0, 8, f"Architecture: {platform.machine()}", 0, 1)
            pdf.cell(0, 8, f"Python Version: {sys.version}", 0, 1)
            pdf.ln(10)
            
            # Add test results section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, "Test Results", 0, 1)
            pdf.set_font('Arial', '', 12)
            
            # Add ping test results
            ping_file = os.path.join(self.report_folder, f"ping_results_{self.timestamp}.txt")
            if os.path.exists(ping_file):
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, "Ping Test Results:", 0, 1)
                pdf.set_font('Arial', '', 10)
                with open(ping_file, 'r') as f:
                    ping_result = f.read()
                    for line in ping_result.splitlines():
                        pdf.cell(0, 5, line, 0, 1)
            
            # Add traceroute test results
            traceroute_file = os.path.join(self.report_folder, f"traceroute_results_{self.timestamp}.txt")
            if os.path.exists(traceroute_file):
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, "Traceroute Test Results:", 0, 1)
                pdf.set_font('Arial', '', 10)
                with open(traceroute_file, 'r') as f:
                    traceroute_result = f.read()
                    for line in traceroute_result.splitlines():
                        pdf.cell(0, 5, line, 0, 1)
            
            # Add speed test results
            speedtest_file = os.path.join(self.report_folder, f"speedtest_results_{self.timestamp}.txt")
            if os.path.exists(speedtest_file):
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, "Browser-based Speed Test Results:", 0, 1)
                pdf.set_font('Arial', '', 10)
                with open(speedtest_file, 'r') as f:
                    speedtest_result = f.read()
                    for line in speedtest_result.splitlines():
                        pdf.cell(0, 5, line, 0, 1)
            
            speedtest_cli_file = os.path.join(self.report_folder, f"speedtest_cli_results_{self.timestamp}.txt")
            if os.path.exists(speedtest_cli_file):
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, "CLI Speed Test Results:", 0, 1)
                pdf.set_font('Arial', '', 10)
                with open(speedtest_cli_file, 'r') as f:
                    speedtest_result = f.read()
                    for line in speedtest_result.splitlines():
                        pdf.cell(0, 5, line, 0, 1)
            
            # Add screenshots
            if self.screenshots:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, "Screenshots", 0, 1)
                pdf.ln(5)
                
                for screenshot_path in self.screenshots:
                    if os.path.exists(screenshot_path):
                        try:
                            # Add screenshot to PDF
                            pdf.image(screenshot_path, x=10, y=pdf.get_y(), w=190)
                            pdf.ln(10)
                            pdf.cell(0, 8, os.path.basename(screenshot_path), 0, 1)
                            pdf.ln(5)
                        except Exception as e:
                            logger.warning(f"Failed to add screenshot {screenshot_path} to PDF: {e}")
            
            # Save the PDF
            pdf_file = os.path.join(self.report_folder, f"OneClick_Diagnostic_Report_{self.timestamp}.pdf")
            pdf.output(pdf_file)
            
            logger.info(f"PDF report created: {pdf_file}")
            
            return pdf_file
            
        except Exception as e:
            logger.error(f"Failed to compile PDF report: {e}")
            return None
    
    def run_complete_diagnostic(self):
        """Run complete diagnostic process from Chrome browser"""
        logger.info("Starting one-click diagnostic process...")
        
        try:
            # Step 1: Create report folder
            report_folder = self.create_report_folder()
            if not report_folder:
                return False
            
            # Step 2: Setup Chrome driver
            if not self.setup_chrome_driver():
                return False
            
            # Step 3: Run all tests from Chrome
            logger.info("Running all tests from Chrome browser...")
            
            # Run browser-based speed test
            self.run_speedtest_in_browser()
            
            # Run ping test
            self.run_ping_test()
            
            # Run traceroute test
            self.run_traceroute_test()
            
            # Run CLI speed test as fallback
            self.run_speedtest_cli()
            
            # Step 4: Compile PDF report
            pdf_file = self.compile_pdf_report()
            
            # Close browser
            self.driver.quit()
            
            if pdf_file:
                logger.info("Diagnostic process completed successfully!")
                logger.info(f"Report saved to: {self.report_folder}")
                logger.info(f"PDF Report: {pdf_file}")
                return True
            else:
                logger.error("Failed to generate PDF report")
                return False
                
        except Exception as e:
            logger.error(f"Diagnostic process failed: {e}")
            if self.driver:
                self.driver.quit()
            return False

def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("SUNYA Networking - One-Click Automation Tool")
    logger.info("=" * 50)
    
    tool = OneClickAutomationTool()
    
    print("SUNYA Networking - One-Click Automation Tool")
    print("=" * 50)
    print(f"Starting diagnostic process...")
    print(f"Timestamp: {tool.timestamp}")
    print()
    
    if tool.run_complete_diagnostic():
        print("\n✅ One-click diagnostic process completed successfully!")
        print(f"📁 Report folder created: {tool.report_folder}")
    else:
        print("\n❌ Diagnostic process failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
