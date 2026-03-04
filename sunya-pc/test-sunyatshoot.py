#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for sunyatshoot tool
"""

import os
import sys
import time
import subprocess
import platform

def test_sunyatshoot():
    """Test sunyatshoot tool functionality"""
    print("=" * 60)
    print("  SUNYATSHOOT - Test Script")
    print("=" * 60)
    print()
    
    # Check if Python is available
    if not any(
        subprocess.run([python_exe, "--version"], capture_output=True, text=True).returncode == 0 
        for python_exe in ["python3", "python"]
    ):
        print("ERROR: Python is not installed. Please install Python 3.x to run this tool.")
        return False
    
    print("✓ Python is available")
    print()
    
    # Check if sunyatshoot.py exists
    script_path = "sunyatshoot.py"
    if not os.path.exists(script_path):
        print(f"ERROR: {script_path} not found in current directory")
        return False
    
    print(f"✓ {script_path} exists")
    print()
    
    # Run sunyatshoot.py with --help
    print("Testing sunyatshoot tool...")
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        print(f"Return code: {result.returncode}")
        print()
        print("Output:")
        print("-" * 50)
        print(result.stdout)
        
        if result.stderr:
            print()
            print("Errors:")
            print("-" * 50)
            print(result.stderr)
            
        if result.returncode == 0:
            print()
            print("✓ Sunyatshoot tool executed successfully!")
            return True
        else:
            print()
            print(f"ERROR: Sunyatshoot tool exited with code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print()
        print("ERROR: Test timed out")
        return False
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_sunyatshoot()
