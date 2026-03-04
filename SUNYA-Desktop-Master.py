#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA DESKTOP MASTER LAUNCHER v6.0.0
====================================
One tool to rule them all - Launch all SUNYA operations from Desktop

Features:
- Launch any diagnostic tool with one click
- System tray integration for quick access
- Desktop shortcut management
- Operation scheduling
- Unified dashboard
- Auto-update checker

Usage:
    Double-click SUNYA-Desktop-Master.bat or run this Python script directly
"""

import os
import sys
import json
import time
import subprocess
import platform
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket

__version__ = "6.0.0"
__author__ = "SUNYA Networking"

# Tool definitions
TOOLS = {
    "master_diagnostic": {
        "name": "🎯 Master Diagnostic",
        "description": "Unified network diagnostic platform with multiple modes",
        "script": "sunya-master.py",
        "batch": "run-sunya-master.bat",
        "category": "Core Diagnostics",
        "modes": ["Quick (30s)", "Standard (2min)", "Full (5min)"],
        "icon": "🔍"
    },
    "comprehensive": {
        "name": "🔬 Comprehensive Diagnostic",
        "description": "Deep network analysis with detailed reports",
        "script": "comprehensive-network-diagnostic.py",
        "batch": "run-comprehensive-diagnostic.bat",
        "category": "Advanced Diagnostics",
        "icon": "🔬"
    },
    "high_performance": {
        "name": "⚡ High Performance",
        "description": "Optimized for speed and efficiency",
        "script": "sunya-high-performance-diagnostic.py",
        "batch": "run-high-performance-diagnostic.bat",
        "category": "Advanced Diagnostics",
        "icon": "⚡"
    },
    "unified_autonomous": {
        "name": "🤖 Unified Autonomous",
        "description": "Self-healing network diagnostic system",
        "script": "sunya-unified-autonomous-utility.py",
        "batch": "run-unified-autonomous.bat",
        "category": "Advanced Diagnostics",
        "icon": "🤖"
    },
    "ultra": {
        "name": "🚀 Ultra Diagnostic",
        "description": "Maximum depth network analysis",
        "script": "sunya-ultra.py",
        "batch": "run-ultra.bat",
        "category": "Advanced Diagnostics",
        "icon": "🚀"
    },
    "complete": {
        "name": "📊 Complete Diagnostic",
        "description": "Full system and network analysis",
        "script": "sunya-complete-diagnostic.py",
        "batch": "run-complete-diagnostic.bat",
        "category": "System Tools",
        "icon": "📊"
    },
    "one_click": {
        "name": "🖱️ One-Click Automation",
        "description": "Browser-based automation with Selenium",
        "script": "one-click-automation.py",
        "batch": "run-oneclick.bat",
        "category": "Automation",
        "icon": "🖱️"
    },
    "net_high_perf": {
        "name": "🌐 SunyaNet High Performance",
        "description": "Advanced network testing suite",
        "script": "sunyanet-high-performance.py",
        "batch": "run-sunyanet.bat",
        "category": "Network Tools",
        "icon": "🌐"
    },
    "troubleshoot": {
        "name": "🔧 SunyaTroubleshoot",
        "description": "Quick troubleshooting and fixes",
        "script": "sunyatshoot.py",
        "batch": "run-sunyatshoot.bat",
        "category": "Troubleshooting",
        "icon": "🔧"
    },
    "automated": {
        "name": "🎨 Automated Tool",
        "description": "Automated diagnostic with PDF reports",
        "script": "automated-diagnostic-tool.py",
        "batch": None,
        "category": "Automation",
        "icon": "🎨"
    },
    "service": {
        "name": "🔔 Service Mode",
        "description": "Background monitoring service",
        "script": "sunya-service.py",
        "batch": None,
        "category": "System Tools",
        "icon": "🔔"
    },
    "dashboard": {
        "name": "📈 Web Dashboard",
        "description": "Interactive HTML dashboard",
        "script": "dashboard.html",
        "batch": None,
        "category": "Visualization",
        "is_html": True,
        "icon": "📈"
    }
}


class ToolRunner:
    """Manages running tools and processes"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.pc_path = self.base_path / "sunya-pc"
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.output_log: List[str] = []
        
    def get_tool_path(self, tool_id: str) -> Optional[Path]:
        """Get the full path to a tool"""
        tool = TOOLS.get(tool_id)
        if not tool:
            return None
            
        script = tool.get("script")
        
        # Check in sunya-pc first
        if (self.pc_path / script).exists():
            return self.pc_path / script
        
        # Check in root
        if (self.base_path / script).exists():
            return self.base_path / script
            
        return None
    
    def run_tool(self, tool_id: str, mode: str = None, args: List[str] = None) -> bool:
        """Run a specific tool"""
        tool_path = self.get_tool_path(tool_id)
        if not tool_path:
            return False
        
        try:
            cmd = [sys.executable, str(tool_path)]
            
            if args:
                cmd.extend(args)
            elif mode:
                cmd.extend([f"--{mode}"])
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == 'Windows' else 0
            )
            
            self.running_processes[tool_id] = process
            self.log(f"Started {tool_id} (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Error running {tool_id}: {e}")
            return False
    
    def run_batch(self, batch_name: str) -> bool:
        """Run a batch file"""
        batch_path = self.pc_path / batch_name
        if not batch_path.exists():
            batch_path = self.base_path / batch_name
            
        if batch_path.exists():
            try:
                subprocess.Popen(
                    str(batch_path),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == 'Windows' else 0
                )
                self.log(f"Started batch: {batch_name}")
                return True
            except Exception as e:
                self.log(f"Error running batch {batch_name}: {e}")
                return False
        return False
    
    def open_dashboard(self) -> bool:
        """Open the HTML dashboard"""
        dashboard_path = self.pc_path / "dashboard.html"
        if dashboard_path.exists():
            webbrowser.open(str(dashboard_path.absolute()))
            return True
        return False
    
    def stop_tool(self, tool_id: str) -> bool:
        """Stop a running tool"""
        if tool_id in self.running_processes:
            process = self.running_processes[tool_id]
            try:
                process.terminate()
                self.log(f"Stopped {tool_id}")
                del self.running_processes[tool_id]
                return True
            except:
                return False
        return False
    
    def stop_all(self):
        """Stop all running tools"""
        for tool_id in list(self.running_processes.keys()):
            self.stop_tool(tool_id)
    
    def log(self, message: str):
        """Add to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.output_log.append(log_entry)
        print(log_entry)


class DesktopMasterGUI:
    """Main GUI for Desktop Master"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SUNYA Desktop Master v6.0.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set icon and colors
        self.root.configure(bg='#1a1a2e')
        self.colors = {
            'bg': '#1a1a2e',
            'fg': '#eee',
            'accent': '#16213e',
            'highlight': '#0f3460',
            'success': '#00d9ff',
            'warning': '#e94560'
        }
        
        # Initialize runner
        self.runner = ToolRunner(os.path.dirname(os.path.abspath(__file__)))
        
        # Build UI
        self._build_ui()
        
        # Start status checker
        self._check_status()
    
    def _build_ui(self):
        """Build the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Frame(main_frame, bg=self.colors['highlight'], height=80)
        header.pack(fill=tk.X, pady=(0, 10))
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🌐 SUNYA DESKTOP MASTER",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['highlight'],
            fg=self.colors['success']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(
            header,
            text="v6.0.0",
            font=('Segoe UI', 10),
            bg=self.colors['highlight'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, pady=20)
        
        # Quick actions bar
        quick_frame = tk.Frame(main_frame, bg=self.colors['accent'])
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        quick_actions = [
            ("⚡ Quick Diagnostic", lambda: self._quick_run("master_diagnostic", "quick")),
            ("🔬 Full Diagnostic", lambda: self._quick_run("master_diagnostic", "full")),
            ("📊 Dashboard", self._open_dashboard),
            ("⏹ Stop All", self._stop_all)
        ]
        
        for text, command in quick_actions:
            btn = tk.Button(
                quick_frame,
                text=text,
                font=('Segoe UI', 10),
                bg=self.colors['highlight'],
                fg=self.colors['fg'],
                activebackground=self.colors['success'],
                activeforeground='#000',
                cursor='hand2',
                command=command
            )
            btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Content area (split)
        content = tk.Frame(main_frame, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left: Tool categories
        left_frame = tk.Frame(content, bg=self.colors['bg'], width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_frame.pack_propagate(False)
        
        # Create notebook for categories
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['accent'], foreground=self.colors['fg'])
        style.map('TNotebook.Tab', background=[('selected', self.colors['highlight'])])
        
        # Group tools by category
        categories = {}
        for tool_id, tool_info in TOOLS.items():
            cat = tool_info.get('category', 'Other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((tool_id, tool_info))
        
        # Create tabs for each category
        for category, tools in sorted(categories.items()):
            tab = tk.Frame(notebook, bg=self.colors['bg'])
            notebook.add(tab, text=category)
            
            # Scrollable frame for tools
            canvas = tk.Canvas(tab, bg=self.colors['bg'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=360)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add tools to category
            for i, (tool_id, tool_info) in enumerate(tools):
                self._create_tool_card(scrollable_frame, tool_id, tool_info, i)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right: Status and Log
        right_frame = tk.Frame(content, bg=self.colors['bg'], width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Status panel
        status_frame = tk.LabelFrame(
            right_frame,
            text=" System Status ",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['success']
        )
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_labels = {}
        status_items = [
            ("Network", "Checking..."),
            ("Python", f"{sys.version.split()[0]}"),
            ("Platform", platform.system()),
            ("Running", "0 tools")
        ]
        
        for name, value in status_items:
            row = tk.Frame(status_frame, bg=self.colors['bg'])
            row.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(
                row,
                text=f"{name}:",
                font=('Segoe UI', 10),
                bg=self.colors['bg'],
                fg=self.colors['fg'],
                width=12,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            self.status_labels[name] = tk.Label(
                row,
                text=value,
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['success']
            )
            self.status_labels[name].pack(side=tk.LEFT)
        
        # Log panel
        log_frame = tk.LabelFrame(
            right_frame,
            text=" Activity Log ",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['success']
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#0a0a14',
            fg='#00ff00',
            insertbackground='#00ff00'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log initial message
        self._log("SUNYA Desktop Master v6.0.0 initialized")
        self._log("Ready to launch operations")
    
    def _create_tool_card(self, parent, tool_id: str, tool_info: dict, index: int):
        """Create a tool selection card"""
        card = tk.Frame(parent, bg=self.colors['accent'], relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
        
        # Header row
        header = tk.Frame(card, bg=self.colors['accent'])
        header.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            header,
            text=f"{tool_info.get('icon', '🔧')} {tool_info['name']}",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['success']
        ).pack(side=tk.LEFT)
        
        # Description
        tk.Label(
            card,
            text=tool_info['description'],
            font=('Segoe UI', 9),
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            wraplength=320,
            justify=tk.LEFT
        ).pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Buttons frame
        btn_frame = tk.Frame(card, bg=self.colors['accent'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Run button
        run_btn = tk.Button(
            btn_frame,
            text="▶ Run",
            font=('Segoe UI', 9),
            bg=self.colors['success'],
            fg='#000',
            activebackground='#00aaff',
            cursor='hand2',
            command=lambda tid=tool_id: self._run_tool(tid)
        )
        run_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Mode selection for tools with modes
        if 'modes' in tool_info and tool_info['modes']:
            self.mode_var = tk.StringVar(value="standard")
            mode_menu = ttk.Combobox(
                btn_frame,
                textvariable=self.mode_var,
                values=tool_info['modes'],
                width=15,
                state='readonly'
            )
            mode_menu.pack(side=tk.LEFT)
        
        # Batch button if available
        if tool_info.get('batch'):
            batch_btn = tk.Button(
                btn_frame,
                text="📦 Batch",
                font=('Segoe UI', 9),
                bg=self.colors['highlight'],
                fg=self.colors['fg'],
                cursor='hand2',
                command=lambda b=tool_info['batch']: self._run_batch(b)
            )
            batch_btn.pack(side=tk.RIGHT)
    
    def _run_tool(self, tool_id: str):
        """Run a tool"""
        mode = None
        if hasattr(self, 'mode_var'):
            mode_str = self.mode_var.get()
            if 'Quick' in mode_str:
                mode = 'quick'
            elif 'Full' in mode_str:
                mode = 'full'
            elif 'Standard' in mode_str:
                mode = 'standard'
        
        self._log(f"Starting {TOOLS[tool_id]['name']}...")
        
        if TOOLS[tool_id].get('is_html'):
            self._open_dashboard()
        else:
            success = self.runner.run_tool(tool_id, mode=mode)
            if success:
                self._log(f"✓ {TOOLS[tool_id]['name']} launched")
            else:
                self._log(f"✗ Failed to launch {tool_id}")
    
    def _quick_run(self, tool_id: str, mode: str):
        """Quick run with mode"""
        self._log(f"Quick launch: {TOOLS[tool_id]['name']} ({mode} mode)")
        self.runner.run_tool(tool_id, mode=mode)
    
    def _run_batch(self, batch_name: str):
        """Run a batch file"""
        self._log(f"Starting batch: {batch_name}")
        success = self.runner.run_batch(batch_name)
        if success:
            self._log(f"✓ Batch {batch_name} launched")
        else:
            self._log(f"✗ Batch {batch_name} not found")
    
    def _open_dashboard(self):
        """Open the dashboard"""
        self._log("Opening Dashboard...")
        if self.runner.open_dashboard():
            self._log("✓ Dashboard opened in browser")
        else:
            self._log("✗ Dashboard not found")
    
    def _stop_all(self):
        """Stop all running tools"""
        self._log("Stopping all tools...")
        self.runner.stop_all()
        self._log("✓ All tools stopped")
    
    def _log(self, message: str):
        """Add to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def _check_status(self):
        """Check and update system status"""
        # Check network
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.status_labels["Network"].config(text="✓ Online", fg=self.colors['success'])
        except:
            self.status_labels["Network"].config(text="✗ Offline", fg=self.colors['warning'])
        
        # Update running count
        running = len(self.runner.running_processes)
        self.status_labels["Running"].config(
            text=f"{running} tool{'s' if running != 1 else ''}",
            fg=self.colors['success'] if running > 0 else self.colors['fg']
        )
        
        # Schedule next check
        self.root.after(5000, self._check_status)
    
    def on_closing(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Stop all running tools and exit?"):
            self.runner.stop_all()
            self.root.destroy()


def create_desktop_shortcut():
    """Create a desktop shortcut (Windows only)"""
    if platform.system() != 'Windows':
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        shortcut_path = os.path.join(desktop, "SUNYA Desktop Master.lnk")
        target = os.path.join(base_path, "SUNYA-Desktop-Master.bat")
        icon = os.path.join(base_path, "sunya-pc", "icon.ico")  # If exists
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = base_path
        shortcut.Description = "SUNYA Desktop Master Launcher"
        if os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.save()
        
        return True
    except:
        return False


def main():
    """Main entry point"""
    # Check for command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == '--create-shortcut':
            if create_desktop_shortcut():
                print("✓ Desktop shortcut created!")
            else:
                print("✗ Could not create shortcut")
            return
    
    # Start GUI
    root = tk.Tk()
    
    # Try to set a modern theme
    try:
        root.tk.call('source', 'azure.tcl')  # If theme file exists
    except:
        pass
    
    app = DesktopMasterGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
