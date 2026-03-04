#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sunya Networking PC Background Service
Runs silently and automatically on network changes
"""

import os
import sys
import time
import logging
import subprocess
import platform
import threading
import json
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sunya-service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add core directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../sunya-core')))

from core import SunyaCore

class SunyaPCService:
    """Background service for Sunya Networking on PC"""
    
    def __init__(self):
        self.core = SunyaCore()
        self.current_fingerprint = None
        self.is_running = False
        self.monitoring_thread = None
        
        # Load previous fingerprint if available
        self.previous_fingerprint = self.load_previous_fingerprint()
        
    def load_previous_fingerprint(self) -> Dict[str, Any]:
        """Load previous network fingerprint from file"""
        try:
            if os.path.exists('previous_fingerprint.json'):
                with open('previous_fingerprint.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load previous fingerprint: {e}")
            
        return None
        
    def save_fingerprint(self, fingerprint: Dict[str, Any]):
        """Save current network fingerprint to file"""
        try:
            with open('previous_fingerprint.json', 'w') as f:
                json.dump(fingerprint, f, indent=2)
                
            self.previous_fingerprint = fingerprint
            
        except Exception as e:
            logger.error(f"Failed to save fingerprint: {e}")
            
    def is_network_changed(self) -> bool:
        """Check if network configuration has changed"""
        logger.info("Checking for network changes...")
        
        try:
            # Generate current fingerprint
            current = self.core.generate_network_fingerprint()
            
            if not current:
                logger.error("Failed to generate current fingerprint")
                return False
                
            self.current_fingerprint = current
            
            # Check if network changed
            if not self.previous_fingerprint:
                logger.info("First run - network change detected")
                return True
                
            # Compare key fingerprints
            change_detected = False
            
            # Check gateway
            if (current.get('gateway') != self.previous_fingerprint.get('gateway')):
                logger.info(f"Gateway changed from {self.previous_fingerprint.get('gateway')} to {current.get('gateway')}")
                change_detected = True
                
            # Check DNS servers
            current_dns = sorted(current.get('dns_servers', []))
            previous_dns = sorted(self.previous_fingerprint.get('dns_servers', []))
            if current_dns != previous_dns:
                logger.info(f"DNS servers changed from {previous_dns} to {current_dns}")
                change_detected = True
                
            # Check IP addresses on active interfaces
            current_ips = set()
            for iface in current.get('interfaces', []):
                current_ips.update(iface.get('ip_addresses', []))
                
            previous_ips = set()
            for iface in self.previous_fingerprint.get('interfaces', []):
                previous_ips.update(iface.get('ip_addresses', []))
                
            if current_ips != previous_ips:
                logger.info(f"IP addresses changed from {previous_ips} to {current_ips}")
                change_detected = True
                
            return change_detected
            
        except Exception as e:
            logger.error(f"Failed to check network change: {e}")
            return False
            
    def run_diagnostics(self):
        """Run diagnostics on network change"""
        logger.info("Network change detected, running diagnostics...")
        
        try:
            # Run full diagnostic cycle
            report_dir = self.core.run_full_diagnostic_cycle()
            
            if report_dir:
                logger.info(f"Diagnostics completed, report created at: {report_dir}")
                
                # Save new fingerprint
                self.save_fingerprint(self.current_fingerprint)
            else:
                logger.error("Diagnostics failed")
                
        except Exception as e:
            logger.error(f"Diagnostics error: {e}")
            
    def monitor_network(self):
        """Main monitoring loop"""
        logger.info("Starting network monitoring...")
        
        while self.is_running:
            try:
                if self.is_network_changed():
                    self.run_diagnostics()
                    
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait longer before retrying
                
    def start(self):
        """Start the background service"""
        logger.info("Starting Sunya Networking Service...")
        
        self.is_running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_network)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Service started successfully")
        
        # Run initial diagnostics if first run
        if not self.previous_fingerprint:
            logger.info("First run detected, running initial diagnostics...")
            self.run_diagnostics()
            
    def stop(self):
        """Stop the background service"""
        logger.info("Stopping Sunya Networking Service...")
        
        self.is_running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            
        logger.info("Service stopped")
        
def install_as_service():
    """Install Sunya Networking as a system service"""
    logger.info("Installing Sunya Networking as a system service...")
    
    try:
        if platform.system().lower() == 'windows':
            install_windows_service()
        elif platform.system().lower() == 'linux':
            install_linux_service()
        else:
            logger.error("Service installation not supported on this platform")
            
    except Exception as e:
        logger.error(f"Service installation failed: {e}")
        
def install_windows_service():
    """Install as Windows service"""
    logger.info("Installing Windows service...")
    
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import socket
    
    class SunyaWindowsService(win32serviceutil.ServiceFramework):
        _svc_name_ = "SunyaNetworking"
        _svc_display_name_ = "Sunya Networking Service"
        _svc_description_ = "Professional network automation and diagnostics service"
        
        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.service = SunyaPCService()
            
        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.service.stop()
            
        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.service.start()
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SunyaWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SunyaWindowsService)
        
def install_linux_service():
    """Install as Linux systemd service"""
    logger.info("Installing Linux systemd service...")
    
    service_content = '''[Unit]
Description=Sunya Networking Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 {0} --run
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''.format(os.path.abspath(__file__))
    
    service_file = '/etc/systemd/system/sunya-networking.service'
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
            
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        subprocess.run(['systemctl', 'enable', 'sunya-networking.service'], check=True)
        subprocess.run(['systemctl', 'start', 'sunya-networking.service'], check=True)
        
        logger.info("Linux service installed and started successfully")
        
    except Exception as e:
        logger.error(f"Linux service installation failed: {e}")
        
def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Check command-line arguments
        if sys.argv[1] == '--install':
            install_as_service()
            return
        elif sys.argv[1] == '--uninstall':
            uninstall_service()
            return
        elif sys.argv[1] == '--run':
            # Run directly without installing
            service = SunyaPCService()
            service.start()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, stopping service...")
                service.stop()
                
            return
            
    logger.info("Sunya Networking PC Service")
    logger.info("==========================")
    
    print("Usage:")
    print("  python sunya-service.py --install    : Install as system service")
    print("  python sunya-service.py --uninstall  : Uninstall service")
    print("  python sunya-service.py --run        : Run directly")
    
def uninstall_service():
    """Uninstall the service"""
    logger.info("Uninstalling Sunya Networking Service...")
    
    try:
        if platform.system().lower() == 'windows':
            uninstall_windows_service()
        elif platform.system().lower() == 'linux':
            uninstall_linux_service()
        else:
            logger.error("Service uninstallation not supported on this platform")
            
    except Exception as e:
        logger.error(f"Service uninstallation failed: {e}")
        
def uninstall_windows_service():
    """Uninstall Windows service"""
    import win32serviceutil
    import win32service
    import servicemanager
    import socket
    
    class SunyaWindowsService(win32serviceutil.ServiceFramework):
        _svc_name_ = "SunyaNetworking"
        _svc_display_name_ = "Sunya Networking Service"
        _svc_description_ = "Professional network automation and diagnostics service"
        
        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.service = SunyaPCService()
            
        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.service.stop()
            
        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            self.service.start()
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
    win32serviceutil.HandleCommandLine(SunyaWindowsService, [sys.argv[0], 'remove'])
        
def uninstall_linux_service():
    """Uninstall Linux systemd service"""
    logger.info("Uninstalling Linux systemd service...")
    
    try:
        subprocess.run(['systemctl', 'stop', 'sunya-networking.service'], check=True)
        subprocess.run(['systemctl', 'disable', 'sunya-networking.service'], check=True)
        
        service_file = '/etc/systemd/system/sunya-networking.service'
        if os.path.exists(service_file):
            os.remove(service_file)
            
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        
        logger.info("Linux service uninstalled successfully")
        
    except Exception as e:
        logger.error(f"Linux service uninstallation failed: {e}")
        
if __name__ == "__main__":
    main()