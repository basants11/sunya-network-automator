#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUNYA Simple Desktop Analyzer v1.0
==================================
Single-purpose tool: Click button → Analyze → View Report

No modes, no options, no menus. Just one button.
"""

import os
import sys
import json
import time
import socket
import subprocess
import platform
import threading
import webbrowser
import tempfile
from pathlib import Path
from datetime import datetime
from tkinter import Tk, Frame, Label, Button, scrolledtext, messagebox, END
from tkinter.ttk import Progressbar
import psutil

__version__ = "1.0.0"


class SimpleAnalyzer:
    """Single-purpose network and system analyzer"""
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or self._get_default_output_dir()
        self.report_file = None
        self.results = {}
        
    def _get_default_output_dir(self):
        """Get default output directory on Desktop"""
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = desktop / f"SUNYA_Analysis_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def analyze(self, progress_callback=None):
        """Run complete analysis"""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system": {},
            "network": {},
            "performance": {},
            "connectivity": []
        }
        
        steps = [
            ("Gathering system information...", self._analyze_system),
            ("Testing network connectivity...", self._analyze_network),
            ("Measuring performance...", self._analyze_performance),
            ("Checking internet connectivity...", self._check_connectivity),
            ("Generating report...", self._generate_report)
        ]
        
        total_steps = len(steps)
        for i, (message, func) in enumerate(steps):
            if progress_callback:
                progress_callback(i / total_steps * 100, message)
            func()
            time.sleep(0.5)  # Small delay for UX
        
        if progress_callback:
            progress_callback(100, "Complete!")
        
        return self.report_file
    
    def _analyze_system(self):
        """Analyze system information"""
        self.results["system"] = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "hostname": socket.gethostname(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
            "disk_percent": psutil.disk_usage('/').percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _analyze_network(self):
        """Analyze network configuration"""
        net_io = psutil.net_io_counters()
        net_if = psutil.net_if_addrs()
        
        interfaces = {}
        for iface_name, addrs in net_if.items():
            iface_info = {"ipv4": [], "ipv6": [], "mac": None}
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    iface_info["ipv4"].append(addr.address)
                elif addr.family == socket.AF_INET6:
                    iface_info["ipv6"].append(addr.address)
                elif addr.family == psutil.AF_LINK:
                    iface_info["mac"] = addr.address
            interfaces[iface_name] = iface_info
        
        self.results["network"] = {
            "interfaces": interfaces,
            "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errors_in": net_io.errin,
            "errors_out": net_io.errout
        }
    
    def _analyze_performance(self):
        """Analyze system performance"""
        # CPU benchmark (simple)
        cpu_start = time.time()
        _ = sum(i**2 for i in range(100000))
        cpu_duration = time.time() - cpu_start
        
        # Memory benchmark
        mem_start = time.time()
        _ = [0] * 1000000  # Allocate memory
        mem_duration = time.time() - mem_start
        
        self.results["performance"] = {
            "cpu_benchmark_ms": round(cpu_duration * 1000, 2),
            "memory_benchmark_ms": round(mem_duration * 1000, 2),
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
            "processes_running": len(psutil.pids())
        }
    
    def _check_connectivity(self):
        """Check internet connectivity"""
        targets = [
            ("Google DNS", "8.8.8.8", 53),
            ("Cloudflare", "1.1.1.1", 53),
            ("Google", "google.com", 80),
            ("Cloudflare HTTP", "cloudflare.com", 80)
        ]
        
        connectivity = []
        for name, host, port in targets:
            try:
                socket.create_connection((host, port), timeout=3)
                latency = self._ping_host(host)
                connectivity.append({
                    "name": name,
                    "host": host,
                    "status": "Online",
                    "latency_ms": latency
                })
            except:
                connectivity.append({
                    "name": name,
                    "host": host,
                    "status": "Offline",
                    "latency_ms": None
                })
        
        self.results["connectivity"] = connectivity
    
    def _ping_host(self, host, count=2):
        """Simple ping to measure latency"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', str(count), '-w', '1000', host]
            else:
                cmd = ['ping', '-c', str(count), '-W', '1', host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            # Extract average time
            if platform.system().lower() == 'windows':
                import re
                match = re.search(r'Average\s*=\s*(\d+)ms', output)
                if match:
                    return int(match.group(1))
            else:
                import re
                match = re.search(r'rtt min/avg/max.*?=\s*[\d.]+/([\d.]+)', output)
                if match:
                    return float(match.group(1))
        except:
            pass
        return None
    
    def _generate_report(self):
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hostname = socket.gethostname()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUNYA Analysis Report - {hostname}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 40px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
        }}
        h1 {{
            color: #00d9ff;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-align: center;
        }}
        .subtitle {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }}
        .timestamp {{
            text-align: center;
            color: #00d9ff;
            font-size: 0.9em;
            margin-bottom: 40px;
        }}
        .section {{
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
        }}
        .section h2 {{
            color: #00d9ff;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #0f3460;
            padding-bottom: 10px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .item {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
        }}
        .item-label {{
            color: #888;
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        .item-value {{
            color: #fff;
            font-size: 1.1em;
            font-weight: bold;
        }}
        .status-online {{ color: #00ff88; }}
        .status-offline {{ color: #ff4444; }}
        .good {{ color: #00ff88; }}
        .warning {{ color: #ffaa00; }}
        .critical {{ color: #ff4444; }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 SUNYA Analysis Report</h1>
        <p class="subtitle">System & Network Diagnostic Report</p>
        <p class="timestamp">Generated: {timestamp} | Host: {hostname}</p>
        
        <div class="section">
            <h2>💻 System Information</h2>
            <div class="grid">
                <div class="item">
                    <div class="item-label">Platform</div>
                    <div class="item-value">{self.results['system'].get('platform', 'N/A')}</div>
                </div>
                <div class="item">
                    <div class="item-label">Processor</div>
                    <div class="item-value">{self.results['system'].get('processor', 'N/A')[:50]}...</div>
                </div>
                <div class="item">
                    <div class="item-label">Architecture</div>
                    <div class="item-value">{self.results['system'].get('architecture', 'N/A')}</div>
                </div>
                <div class="item">
                    <div class="item-label">Python Version</div>
                    <div class="item-value">{self.results['system'].get('python_version', 'N/A')}</div>
                </div>
                <div class="item">
                    <div class="item-label">CPU Cores</div>
                    <div class="item-value">{self.results['system'].get('cpu_count', 'N/A')}</div>
                </div>
                <div class="item">
                    <div class="item-label">CPU Usage</div>
                    <div class="item-value {'good' if self.results['system'].get('cpu_percent', 0) < 50 else 'warning' if self.results['system'].get('cpu_percent', 0) < 80 else 'critical'}">{self.results['system'].get('cpu_percent', 0)}%</div>
                </div>
                <div class="item">
                    <div class="item-label">Memory Usage</div>
                    <div class="item-value {'good' if self.results['system'].get('memory_percent', 0) < 60 else 'warning' if self.results['system'].get('memory_percent', 0) < 85 else 'critical'}">{self.results['system'].get('memory_percent', 0)}% ({self.results['system'].get('memory_available_gb', 0)} GB free)</div>
                </div>
                <div class="item">
                    <div class="item-label">Disk Usage</div>
                    <div class="item-value {'good' if self.results['system'].get('disk_percent', 0) < 70 else 'warning' if self.results['system'].get('disk_percent', 0) < 90 else 'critical'}">{self.results['system'].get('disk_percent', 0)}% ({self.results['system'].get('disk_free_gb', 0)} GB free)</div>
                </div>
                <div class="item">
                    <div class="item-label">Uptime Since</div>
                    <div class="item-value">{self.results['system'].get('boot_time', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🌐 Network Information</h2>
            <div class="grid">
                <div class="item">
                    <div class="item-label">Data Sent</div>
                    <div class="item-value">{self.results['network'].get('bytes_sent_mb', 0)} MB</div>
                </div>
                <div class="item">
                    <div class="item-label">Data Received</div>
                    <div class="item-value">{self.results['network'].get('bytes_recv_mb', 0)} MB</div>
                </div>
                <div class="item">
                    <div class="item-label">Packets Sent</div>
                    <div class="item-value">{self.results['network'].get('packets_sent', 0):,}</div>
                </div>
                <div class="item">
                    <div class="item-label">Packets Received</div>
                    <div class="item-value">{self.results['network'].get('packets_recv', 0):,}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Connectivity Status</h2>
            <div class="grid">
"""
        
        for conn in self.results['connectivity']:
            status_class = 'status-online' if conn['status'] == 'Online' else 'status-offline'
            latency = f"{conn['latency_ms']:.1f} ms" if conn['latency_ms'] else 'N/A'
            html += f"""
                <div class="item">
                    <div class="item-label">{conn['name']}</div>
                    <div class="item-value {status_class}">{conn['status']} ({latency})</div>
                </div>
"""
        
        html += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>⚡ Performance Metrics</h2>
            <div class="grid">
                <div class="item">
                    <div class="item-label">CPU Benchmark</div>
                    <div class="item-value">{self.results['performance'].get('cpu_benchmark_ms', 0)} ms</div>
                </div>
                <div class="item">
                    <div class="item-label">Memory Benchmark</div>
                    <div class="item-value">{self.results['performance'].get('memory_benchmark_ms', 0)} ms</div>
                </div>
                <div class="item">
                    <div class="item-label">Running Processes</div>
                    <div class="item-value">{self.results['performance'].get('processes_running', 0)}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SUNYA Simple Desktop Analyzer v{__version__}</p>
            <p>Report saved to: {self.output_dir}</p>
        </div>
    </div>
</body>
</html>"""
        
        # Save HTML report
        self.report_file = self.output_dir / "analysis_report.html"
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Also save JSON for reference
        json_file = self.output_dir / "analysis_data.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)


class SimpleAnalyzerGUI:
    """Ultra-simple GUI with just one button"""
    
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("SUNYA Simple Analyzer")
        self.root.geometry("600x400")
        self.root.minsize(500, 350)
        self.root.configure(bg='#1a1a2e')
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (300)
        y = (self.root.winfo_screenheight() // 2) - (200)
        self.root.geometry(f"+{x}+{y}")
        
        self.analyzer = None
        self.is_analyzing = False
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the simplest possible UI"""
        # Main container
        main = Frame(self.root, bg='#1a1a2e')
        main.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Title
        Label(
            main,
            text="🌐 SUNYA",
            font=('Segoe UI', 32, 'bold'),
            bg='#1a1a2e',
            fg='#00d9ff'
        ).pack(pady=(0, 5))
        
        Label(
            main,
            text="Simple Desktop Analyzer",
            font=('Segoe UI', 14),
            bg='#1a1a2e',
            fg='#888'
        ).pack(pady=(0, 30))
        
        # Status label
        self.status_label = Label(
            main,
            text="Ready to analyze",
            font=('Segoe UI', 11),
            bg='#1a1a2e',
            fg='#ccc'
        )
        self.status_label.pack(pady=(0, 15))
        
        # Progress bar (hidden initially)
        self.progress = Progressbar(
            main,
            length=400,
            mode='determinate',
            maximum=100
        )
        self.progress.pack(pady=(0, 30))
        
        # THE BUTTON
        self.start_button = Button(
            main,
            text="▶  START ANALYSIS",
            font=('Segoe UI', 16, 'bold'),
            bg='#00d9ff',
            fg='#1a1a2e',
            activebackground='#00aaff',
            activeforeground='#1a1a2e',
            cursor='hand2',
            width=20,
            height=2,
            relief='flat',
            command=self._start_analysis
        )
        self.start_button.pack()
        
        # Result label (hidden initially)
        self.result_label = Label(
            main,
            text="",
            font=('Segoe UI', 10),
            bg='#1a1a2e',
            fg='#00ff88',
            wraplength=500
        )
    
    def _start_analysis(self):
        """Start the analysis process"""
        if self.is_analyzing:
            return
        
        self.is_analyzing = True
        self.start_button.config(state='disabled', text="⏳  ANALYZING...")
        self.status_label.config(text="Initializing...", fg='#00d9ff')
        self.progress['value'] = 0
        
        # Hide result if showing
        self.result_label.pack_forget()
        
        # Run analysis in thread
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()
    
    def _run_analysis(self):
        """Run analysis in background thread"""
        try:
            self.analyzer = SimpleAnalyzer()
            
            def update_progress(percent, message):
                self.root.after(0, lambda: self._update_ui(percent, message))
            
            report_file = self.analyzer.analyze(progress_callback=update_progress)
            
            self.root.after(0, lambda: self._analysis_complete(report_file))
            
        except Exception as e:
            self.root.after(0, lambda: self._analysis_error(str(e)))
    
    def _update_ui(self, percent, message):
        """Update progress UI"""
        self.progress['value'] = percent
        self.status_label.config(text=message)
    
    def _analysis_complete(self, report_file):
        """Handle analysis completion"""
        self.is_analyzing = False
        self.start_button.config(state='normal', text="▶  START ANALYSIS")
        self.status_label.config(text="Analysis complete!", fg='#00ff88')
        self.progress['value'] = 100
        
        # Show result
        self.result_label.config(
            text=f"✓ Report generated successfully!\n{report_file}",
            fg='#00ff88'
        )
        self.result_label.pack(pady=(20, 0))
        
        # Ask to open report
        if messagebox.askyesno("Analysis Complete", "Open report in browser?"):
            webbrowser.open(f"file://{report_file}")
    
    def _analysis_error(self, error_msg):
        """Handle analysis error"""
        self.is_analyzing = False
        self.start_button.config(state='normal', text="▶  START ANALYSIS")
        self.status_label.config(text="Analysis failed", fg='#ff4444')
        
        messagebox.showerror("Error", f"Analysis failed:\n{error_msg}")


def main():
    """Main entry point"""
    root = Tk()
    app = SimpleAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
