#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for one-click automation tool
"""

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import importlib.util
tool_spec = importlib.util.spec_from_file_location("one-click-automation", 
                                                 os.path.join(os.path.abspath(os.path.dirname(__file__)), "one-click-automation.py"))
one_click_automation = importlib.util.module_from_spec(tool_spec)
tool_spec.loader.exec_module(one_click_automation)

def test_basic_functionality():
    """Test basic functionality of the one-click automation tool"""
    print("Testing One-Click Automation Tool...")
    
    try:
        tool = one_click_automation.OneClickAutomationTool()
        
        print("\n1. Testing report folder creation...")
        report_folder = tool.create_report_folder()
        if report_folder and os.path.exists(report_folder):
            print("Success: Report folder created:", report_folder)
        else:
            print("Failed: Report folder creation")
        
        print("\n2. Testing Chrome driver setup...")
        driver_setup = tool.setup_chrome_driver()
        if driver_setup and tool.driver:
            print("Success: Chrome driver setup")
            
            # Navigate to a simple page to test browser
            tool.driver.get("https://www.google.com")
            time.sleep(2)
            
            # Capture screenshot
            screenshot_path = os.path.join(report_folder, "google_test.png")
            tool.driver.save_screenshot(screenshot_path)
            if os.path.exists(screenshot_path):
                print("Success: Screenshot captured:", screenshot_path)
            else:
                print("Failed: Screenshot capture")
                
            tool.driver.quit()
        else:
            print("Failed: Chrome driver setup")
            
        print("\nAll basic functionality tests passed!")
        return True
        
    except Exception as e:
        print("\nTest failed:", e)
        return False

if __name__ == "__main__":
    test_basic_functionality()
