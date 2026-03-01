#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PDF generation functionality
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import importlib.util
tool_spec = importlib.util.spec_from_file_location("automated-diagnostic-tool", 
                                                 os.path.join(os.path.abspath(os.path.dirname(__file__)), "automated-diagnostic-tool.py"))
automated_diagnostic_tool = importlib.util.module_from_spec(tool_spec)
tool_spec.loader.exec_module(automated_diagnostic_tool)

def test_pdf_generation():
    """Test PDF generation functionality"""
    print("Testing PDF generation...")
    
    try:
        tool = automated_diagnostic_tool.AutomatedDiagnosticTool()
        
        # Create report folder
        report_folder = tool.create_report_folder()
        print("Report folder:", report_folder)
        
        # Run some basic tests to generate data
        tool.run_ping_test(target="8.8.8.8", count=4)
        tool.capture_screenshot("pdf_test_screenshot")
        
        # Generate PDF
        pdf_file = tool.compile_pdf_report()
        
        if pdf_file and os.path.exists(pdf_file):
            print("PDF report generated successfully:", pdf_file)
            print("PDF file size:", os.path.getsize(pdf_file), "bytes")
            return True
        else:
            print("Failed to generate PDF report")
            return False
            
    except Exception as e:
        print("Error:", e)
        return False

if __name__ == "__main__":
    test_pdf_generation()
