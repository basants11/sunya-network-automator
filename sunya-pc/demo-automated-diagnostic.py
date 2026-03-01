#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script to run the complete automated diagnostic process
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import importlib.util
tool_spec = importlib.util.spec_from_file_location("automated-diagnostic-tool", 
                                                 os.path.join(os.path.abspath(os.path.dirname(__file__)), "automated-diagnostic-tool.py"))
automated_diagnostic_tool = importlib.util.module_from_spec(tool_spec)
tool_spec.loader.exec_module(automated_diagnostic_tool)

def run_demo():
    """Run a demo of the automated diagnostic tool"""
    print("==============================================")
    print("  SUNYA Networking - Automated Diagnostic Demo")
    print("==============================================")
    print()
    
    # Create tool instance
    tool = automated_diagnostic_tool.AutomatedDiagnosticTool()
    
    # Run complete diagnostic
    print("Starting complete diagnostic process...")
    print("Note: This will open applications and capture screenshots")
    print()
    
    # Wait for user to be ready
    input("Press Enter to continue...")
    
    print()
    print("Running diagnostic...")
    print("=" * 50)
    
    success = tool.run_complete_diagnostic()
    
    print()
    print("=" * 50)
    
    if success:
        print("Diagnostic process completed successfully!")
        print(f"Report saved to: {tool.report_folder}")
    else:
        print("Diagnostic process failed!")
    
    print()
    print("==============================================")

if __name__ == "__main__":
    run_demo()
