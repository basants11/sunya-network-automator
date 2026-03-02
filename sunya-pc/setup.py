#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sunya Networking Setup Script
For Windows and Linux platforms
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import json

def main():
    """Main setup function"""
    print("==============================================")
    print("  Sunya Networking Setup")
    print("==============================================")
    print()
    
    current_os = platform.system().lower()
    
    if current_os not in ['windows', 'linux']:
        print(f"ERROR: Unsupported OS: {current_os}")
        sys.exit(1)
        
    print(f"Detected OS: {current_os}")
    print()
    
    # Create directories
    print("Creating directories...")
    base_dir = os.path.join(os.path.expanduser('~'), '.sunya-networking')
    config_dir = os.path.join(base_dir, 'config')
    data_dir = os.path.join(base_dir, 'data')
    
    for directory in [base_dir, config_dir, data_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print(f"Base directory: {base_dir}")
    print(f"Config directory: {config_dir}")
    print(f"Data directory: {data_dir}")
    print()
    
    # Install dependencies
    print("Installing required dependencies...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            'requests', 'psutil', 'speedtest-cli', 'ping3', 'pandas',
            'matplotlib', 'seaborn', 'fpdf', 'pytest', 'scipy', 'numpy',
            'pyautogui', 'selenium', 'webdriver-manager'
        ], check=True)
        
        if current_os == 'windows':
            print("Installing Windows-specific dependencies...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'pywin32'
            ], check=True)
            
        print("Dependencies installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        sys.exit(1)
        
    print()
    
    # Create default configuration
    print("Creating default configuration...")
    config = {
        'general': {
            'log_level': 'INFO',
            'report_location': os.path.join(data_dir, 'reports'),
            'max_reports': 50,
            'auto_cleanup': True
        },
        'diagnostics': {
            'ping': {
                'count': 20,
                'payload_size': 1400,
                'timeout': 2
            },
            'traceroute': {
                'max_hops': 30,
                'timeout': 2
            },
            'speedtest': {
                'server_count': 5,
                'max_time': 300
            },
            'mtr': {
                'count': 5,
                'interval': 1
            }
        },
        'monitoring': {
            'check_interval': 30,  # seconds
            'skip_duplicate': True,
            'network_change_threshold': 30  # seconds
        }
    }
    
    config_file = os.path.join(config_dir, 'config.json')
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"Configuration created: {config_file}")
        
    except Exception as e:
        print(f"ERROR: Failed to create configuration: {e}")
        sys.exit(1)
        
    print()
    
    # Create startup script or service
    print("Setting up startup configuration...")
    if current_os == 'windows':
        setup_windows()
    elif current_os == 'linux':
        setup_linux()
        
    print()
    print("==============================================")
    print("  Setup Complete!")
    print("==============================================")
    print()
    
    if current_os == 'windows':
        print("1. To install Sunya Networking as a Windows service:")
        print("   python sunya-service.py --install")
        print()
        print("2. To run Sunya Networking directly:")
        print("   python sunya-service.py --run")
        
    elif current_os == 'linux':
        print("1. To install Sunya Networking as a systemd service:")
        print("   sudo python sunya-service.py --install")
        print()
        print("2. To run Sunya Networking directly:")
        print("   python sunya-service.py --run")
        
def setup_windows():
    """Setup for Windows platform"""
    print("Windows setup...")
    
    try:
        import winreg
        
        # Create registry entries for startup
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "SunyaNetworking"
        exe_path = os.path.abspath(sys.argv[0])
        
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, exe_path)
            
        print("Startup registry entry created")
        
    except Exception as e:
        print(f"WARNING: Failed to create startup registry entry: {e}")
        print("You can still run Sunya Networking manually")
        
def setup_linux():
    """Setup for Linux platform"""
    print("Linux setup...")
    
    # Create desktop entry
    desktop_content = '''[Desktop Entry]
Name=Sunya Networking
Comment=Professional network automation and diagnostics
Exec=/usr/bin/python3 {0} --run
Icon=network
Terminal=false
Type=Application
Categories=System;Network;Utility;
X-GNOME-Autostart-enabled=true
'''.format(os.path.abspath(sys.argv[0]))
    
    autostart_dir = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
    Path(autostart_dir).mkdir(parents=True, exist_ok=True)
    
    desktop_file = os.path.join(autostart_dir, 'sunya-networking.desktop')
    
    try:
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
            
        os.chmod(desktop_file, 0o755)
        print("Autostart desktop entry created")
        
    except Exception as e:
        print(f"WARNING: Failed to create autostart entry: {e}")
        print("You can still run Sunya Networking manually")
        
if __name__ == "__main__":
    main()