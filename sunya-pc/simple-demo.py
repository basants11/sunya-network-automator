#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple demo script for Comprehensive Network Diagnostic Tool
Tests the tool without Unicode characters to avoid encoding issues
"""

import os
import sys
import importlib.util
import subprocess

def main():
    """Main demo function"""
    print("=" * 60)
    print("  SUNYA NETWORKING - COMPREHENSIVE DIAGNOSTIC TOOL DEMO")
    print("=" * 60)
    print()
    
    # Check if script exists
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comprehensive-network-diagnostic.py')
    if not os.path.exists(script_path):
        print("ERROR: Comprehensive network diagnostic script not found!")
        print(f"Looking for: {script_path}")
        return 1
    
    print("Script found at:", script_path)
    print()
    
    # Check Python version
    print("Checking Python version...")
    python_version = sys.version_info
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("WARNING: Python 3.6 or higher is recommended")
    print()
    
    # Check dependencies
    print("Checking required dependencies...")
    required_modules = [
        'psutil', 'ping3', 'speedtest', 'pyautogui', 
        'selenium', 'webdriver_manager', 'fpdf', 'wmi'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"OK {module}")
        except ImportError:
            print(f"NO {module}")
            missing_modules.append(module)
        except Exception as e:
            print(f"ER {module} (error: {e})")
            missing_modules.append(module)
    
    if missing_modules:
        print()
        print("ERROR: Missing required modules. Please install them with:")
        print(f"pip install {' '.join(missing_modules)}")
        return 1
    
    print()
    print("All dependencies installed!")
    print()
    
    # Test basic functionality
    print("Testing basic functionality...")
    
    try:
        # Import the module
        spec = importlib.util.spec_from_file_location("comprehensive-network-diagnostic", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Initialize the tool
        print("1. Initializing diagnostic tool...")
        tool = module.ComprehensiveNetworkDiagnostic()
        
        # Create report folder
        print("2. Creating report folder...")
        folder = tool.create_report_folder()
        print(f"   Folder created at: {folder}")
        
        # Get PC details
        print("3. Collecting PC information...")
        tool.get_pc_details()
        pc_info = tool.test_results['pc_details']
        print(f"   System: {pc_info['system']} {pc_info['release']}")
        print(f"   Hostname: {pc_info['hostname']}")
        print(f"   IP Address: {pc_info['ip_address']}")
        print(f"   Interfaces: {len(pc_info['interfaces'])}")
        
        # Check gigabit interfaces
        gigabit_interfaces = [iface['name'] for iface in pc_info['interfaces'] if iface.get('is_gigabit')]
        if gigabit_interfaces:
            print(f"   Gigabit Interfaces: {', '.join(gigabit_interfaces)}")
        else:
            print(f"   No gigabit-capable interfaces detected")
        
        # Test ping
        print("4. Testing ping functionality...")
        tool.ping_targets(['127.0.0.1'])
        if '127.0.0.1' in tool.test_results['pings']:
            result = tool.test_results['pings']['127.0.0.1']
            if 'error' not in result:
                print(f"   Ping to localhost: OK")
                print(f"     Packet Loss: {result['packet_loss']:.1f}%")
                print(f"     Avg RTT: {result['avg_rtt']:.2f}ms")
            else:
                print(f"   Ping to localhost: ERROR - {result['error']}")
                
        print()
        print("=" * 60)
        print("  DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("To run the full diagnostic test:")
        print(f"  Double-click: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run-comprehensive-diagnostic.bat')}")
        print()
        print("Or from command prompt:")
        print(f"  python {script_path}")
        
        return 0
        
    except Exception as e:
        print()
        print("ERROR:", str(e))
        import traceback
        print("\nDetailed error:")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
