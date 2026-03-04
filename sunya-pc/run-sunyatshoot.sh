#!/bin/bash

echo "=============================================="
echo "  SUNYATSHOOT - Automatic Network Diagnostic"
echo "=============================================="
echo
echo "This tool will automatically start running when launched."
echo "Do not close this window while the diagnostic is running."
echo
echo "Starting Sunyatshoot..."
echo

# Change to script directory
cd "$(dirname "$0")"

# Check if Python is available
if command -v python3 &> /dev/null; then
    python3 sunyatshoot.py
elif command -v python &> /dev/null; then
    python sunyatshoot.py
else
    echo "Error: Python is not installed. Please install Python 3.x to run this tool."
    echo
    read -p "Press any key to exit..."
    exit 1
fi

echo
echo "Diagnostic completed. Press any key to exit..."
read -n 1 -s
