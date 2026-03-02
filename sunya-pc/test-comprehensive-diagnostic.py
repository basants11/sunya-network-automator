#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Comprehensive Network Diagnostic Tool
"""

import os
import sys
import unittest
import subprocess
from pathlib import Path

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestComprehensiveNetworkDiagnostic(unittest.TestCase):
    """Test cases for ComprehensiveNetworkDiagnostic class"""
    
    def test_script_execution(self):
        """Test if the script can be executed"""
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comprehensive-network-diagnostic.py')
            
            # Test script can be imported and run with --help or test mode
            result = subprocess.run([
                sys.executable, script_path, '--help'
            ], capture_output=True, text=True, timeout=10)
            
            self.assertEqual(result.returncode, 0)
            
        except Exception as e:
            self.fail(f"Failed to execute script: {e}")
    
    def test_dependencies(self):
        """Test if required dependencies are installed"""
        required_modules = [
            'psutil', 'ping3', 'speedtest', 'pyautogui', 
            'selenium', 'webdriver_manager', 'fpdf', 'wmi'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                self.fail(f"Required module '{module}' not installed: {e}")
    
    def test_report_folder_creation(self):
        """Test if report folder can be created properly"""
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comprehensive-network-diagnostic.py')
            
            # Test report folder creation
            result = subprocess.run([
                sys.executable, '-c', 
                '''
import sys
sys.path = ['{}'] + sys.path
import importlib.util
spec = importlib.util.spec_from_file_location("comprehensive-network-diagnostic", '{}/comprehensive-network-diagnostic.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tool = module.ComprehensiveNetworkDiagnostic()
folder = tool.create_report_folder()
print(folder)
'''.format(os.path.dirname(script_path), os.path.dirname(script_path))
            ], capture_output=True, text=True, timeout=10)
            
            self.assertEqual(result.returncode, 0)
            
            folder_path = result.stdout.strip()
            self.assertTrue(os.path.exists(folder_path))
            self.assertTrue(os.path.isdir(folder_path))
            
            # Cleanup
            import shutil
            shutil.rmtree(folder_path)
            
        except Exception as e:
            self.fail(f"Failed to test report folder creation: {e}")
    
    def test_basic_pc_info(self):
        """Test if PC details can be collected"""
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comprehensive-network-diagnostic.py')
            
            # Test PC details collection
            result = subprocess.run([
                sys.executable, '-c', 
                '''
import sys
sys.path = ['{}'] + sys.path
import importlib.util
spec = importlib.util.spec_from_file_location("comprehensive-network-diagnostic", '{}/comprehensive-network-diagnostic.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tool = module.ComprehensiveNetworkDiagnostic()
tool.get_pc_details()
print(len(tool.test_results['pc_details']['interfaces']))
'''.format(os.path.dirname(script_path), os.path.dirname(script_path))
            ], capture_output=True, text=True, timeout=10)
            
            self.assertEqual(result.returncode, 0)
            
            interface_count = int(result.stdout.strip())
            self.assertGreater(interface_count, 0)
            
        except Exception as e:
            self.fail(f"Failed to test PC details collection: {e}")

if __name__ == '__main__':
    print("Running Comprehensive Network Diagnostic Tool tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestComprehensiveNetworkDiagnostic)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print(f"Total tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
