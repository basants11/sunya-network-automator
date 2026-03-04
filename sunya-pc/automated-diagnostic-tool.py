#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Network Diagnostic Tool
Runs specified applications, performs network tests with screenshots, and compiles PDF report
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
from pathlib import Path
from fpdf import FPDF

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated-diagnostic-tool.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AutomatedDiagnosticTool:
    """Automated tool for network diagnostics with application automation and screenshot capture"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.report_folder = None
        self.screenshots = []
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
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
            
            self.report_folder = os.path.join(desktop_path, f"Network_Diagnostic_Report_{self.timestamp}")
            os.makedirs(self.report_folder, exist_ok=True)
            logger.info(f"Report folder created: {self.report_folder}")
            
            return self.report_folder
            
        except Exception as e:
            logger.error(f"Failed to create report folder: {e}")
            return None
    
    def open_applications(self):
        """Open specified applications automatically"""
        logger.info("Opening applications...")
        
        try:
            if self.platform == 'windows':
                # Open Terminal (Command Prompt)
                subprocess.Popen(['cmd.exe'])
                time.sleep(2)
                
                # Open Chrome
                try:
                    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                    subprocess.Popen([chrome_path])
                except:
                    try:
                        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                        subprocess.Popen([chrome_path])
                    except Exception as e:
                        logger.warning(f"Failed to open Chrome: {e}")
                
                time.sleep(3)
                
                # Open PowerShell
                subprocess.Popen(['powershell.exe'])
                time.sleep(2)
                
                # Open NMTr (Network MTR tool)
                try:
                    nmtr_path = r"C:\Program Files\NMTr\nmtr.exe"
                    if os.path.exists(nmtr_path):
                        subprocess.Popen([nmtr_path])
                    else:
                        logger.warning("NMTr not found, skipping...")
                except Exception as e:
                    logger.warning(f"Failed to open NMTr: {e}")
                
                time.sleep(3)
                
            elif self.platform == 'linux':
                # Open Terminal
                subprocess.Popen(['gnome-terminal'])
                time.sleep(2)
                
                # Open Chrome
                try:
                    subprocess.Popen(['google-chrome'])
                except Exception as e:
                    logger.warning(f"Failed to open Chrome: {e}")
                
                time.sleep(3)
                
                # Open PowerShell (pwsh if available)
                try:
                    subprocess.Popen(['pwsh'])
                except:
                    try:
                        subprocess.Popen(['powershell'])
                    except Exception as e:
                        logger.warning(f"Failed to open PowerShell: {e}")
                
                time.sleep(2)
                
                # Open MTR (Linux equivalent)
                try:
                    subprocess.Popen(['mtr', '8.8.8.8'])
                except Exception as e:
                    logger.warning(f"Failed to open MTR: {e}")
                
                time.sleep(3)
                
            elif self.platform == 'darwin':
                # Open Terminal
                subprocess.Popen(['open', '-a', 'Terminal'])
                time.sleep(2)
                
                # Open Chrome
                try:
                    subprocess.Popen(['open', '-a', 'Google Chrome'])
                except Exception as e:
                    logger.warning(f"Failed to open Chrome: {e}")
                
                time.sleep(3)
                
                # Open PowerShell (if available)
                try:
                    subprocess.Popen(['pwsh'])
                except Exception as e:
                    logger.warning(f"Failed to open PowerShell: {e}")
                
                time.sleep(2)
                
                # Open MTR (Mac equivalent)
                try:
                    subprocess.Popen(['mtr', '8.8.8.8'])
                except Exception as e:
                    logger.warning(f"Failed to open MTR: {e}")
                
                time.sleep(3)
                
            logger.info("Applications opened successfully")
            
        except Exception as e:
            logger.error(f"Failed to open applications: {e}")
    
    def capture_screenshot(self, name):
        """Capture and save a screenshot"""
        try:
            logger.info(f"Capturing screenshot: {name}")
            
            # Wait for interface to stabilize
            time.sleep(2)
            
            # Capture screenshot
            screenshot_path = os.path.join(self.report_folder, f"{name}_{self.timestamp}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            
            self.screenshots.append(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def run_ping_test(self, target="8.8.8.8", count=20):
        """Run ping test and capture screenshot"""
        logger.info(f"Running ping test to {target}")
        
        try:
            if self.platform == 'windows':
                # Run ping in Command Prompt
                cmd = f"ping -n {count} -l 1400 {target}"
            else:
                cmd = f"ping -c {count} -s 1400 {target}"
                
            # Capture command execution and screenshot
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Save ping results to file
            ping_file = os.path.join(self.report_folder, f"ping_results_{self.timestamp}.txt")
            with open(ping_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\nErrors:\n{result.stderr}")
            
            logger.info(f"Ping test completed, results saved to: {ping_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ping test failed: {e}")
            return False
    
    def run_traceroute_test(self, target="8.8.8.8"):
        """Run traceroute/test test and capture screenshot"""
        logger.info(f"Running traceroute to {target}")
        
        try:
            if self.platform == 'windows':
                cmd = f"tracert -d {target}"
            else:
                cmd = f"traceroute {target}"
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Save traceroute results to file
            traceroute_file = os.path.join(self.report_folder, f"traceroute_results_{self.timestamp}.txt")
            with open(traceroute_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\nErrors:\n{result.stderr}")
            
            logger.info(f"Traceroute completed, results saved to: {traceroute_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Traceroute failed: {e}")
            return False
    
    def run_speedtest(self):
        """Run internet speed test"""
        logger.info("Running speed test...")
        
        try:
            # Install speedtest-cli if not available
            try:
                import speedtest
            except ImportError:
                logger.info("Installing speedtest-cli...")
                subprocess.run([sys.executable, "-m", "pip", "install", "speedtest-cli"], check=True)
                import speedtest
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 10**6  # Mbps
            upload_speed = st.upload() / 10**6  # Mbps
            ping_result = st.results.ping
            
            # Save speed test results
            speedtest_file = os.path.join(self.report_folder, f"speedtest_results_{self.timestamp}.txt")
            with open(speedtest_file, 'w') as f:
                f.write(f"Speed Test Results ({self.timestamp})\n")
                f.write("=" * 40 + "\n")
                f.write(f"Download Speed: {download_speed:.2f} Mbps\n")
                f.write(f"Upload Speed: {upload_speed:.2f} Mbps\n")
                f.write(f"Ping: {ping_result:.2f} ms\n")
                f.write(f"Server: {st.results.server['name']}, {st.results.server['country']}\n")
                f.write(f"Sponsor: {st.results.server['sponsor']}\n")
            
            logger.info(f"Speed test completed, results saved to: {speedtest_file}")
            
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
            pdf.cell(0, 10, f"Network Diagnostic Report - {self.timestamp}", 0, 1, 'C')
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
                    # Add text with proper line breaks
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
                pdf.cell(0, 8, "Speed Test Results:", 0, 1)
                pdf.set_font('Arial', '', 10)
                with open(speedtest_file, 'r') as f:
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
            pdf_file = os.path.join(self.report_folder, f"Network_Diagnostic_Report_{self.timestamp}.pdf")
            pdf.output(pdf_file)
            
            logger.info(f"PDF report created: {pdf_file}")
            
            return pdf_file
            
        except Exception as e:
            logger.error(f"Failed to compile PDF report: {e}")
            return None
    
    def run_complete_diagnostic(self):
        """Run complete diagnostic process"""
        logger.info("Starting complete diagnostic process...")
        
        try:
            # Step 1: Create report folder
            report_folder = self.create_report_folder()
            if not report_folder:
                return False
            
            # Step 2: Open applications
            self.open_applications()
            
            # Step 3: Run network tests
            logger.info("Running network tests...")
            
            # Run ping test
            self.run_ping_test()
            self.capture_screenshot("ping_test")
            
            # Run traceroute test
            self.run_traceroute_test()
            self.capture_screenshot("traceroute_test")
            
            # Run speed test
            self.run_speedtest()
            self.capture_screenshot("speedtest")
            
            # Step 4: Compile PDF report
            pdf_file = self.compile_pdf_report()
            
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
            return False

def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Automated Network Diagnostic Tool")
    logger.info("=" * 50)
    
    tool = AutomatedDiagnosticTool()
    
    print("Automated Network Diagnostic Tool")
    print("=" * 50)
    print(f"Starting diagnostic process...")
    print(f"Timestamp: {tool.timestamp}")
    print()
    
    if tool.run_complete_diagnostic():
        print("\n✅ Diagnostic process completed successfully!")
        print(f"📁 Report folder created: {tool.report_folder}")
    else:
        print("\n❌ Diagnostic process failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
