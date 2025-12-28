#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import tempfile
import uuid
from datetime import datetime, timezone

# ============== CONFIG ==============
SECRET = "hostblocker2024"
PRESETS = {
    "Social": ["facebook.com", "twitter.com", "x.com", "instagram.com", "tiktok.com", "snapchat.com"],
    "LinkedIn": ["linkedin.com"],
    "Reddit": ["reddit.com", "old.reddit.com"],
    "YouTube": ["youtube.com"],
    "News": ["news.ycombinator.com", "cnn.com", "foxnews.com", "bbc.com"],
}

# ============== UNLOCK CODE LOGIC ==============
def validate_code(code):
    now = datetime.now(timezone.utc)
    hour_block = int(now.timestamp() / 3600)
    date_str = now.strftime("%Y-%m-%d")
    
    for offset in range(2):
        check_hour = hour_block - offset
        input_str = f"{SECRET}-{date_str}-{check_hour}"
        hash_val = 0
        for char in input_str:
            hash_val = ((hash_val << 5) - hash_val) + ord(char)
            hash_val = hash_val & 0xFFFFFFFF
            if hash_val >= 0x80000000:
                hash_val -= 0x100000000
        expected = f"{abs(hash_val) % 1000000:06d}"
        if code == expected:
            return True
    return False

# ============== HOSTS FILE LOGIC ==============
def read_hosts():
    try:
        with open("/etc/hosts", "r") as f:
            return f.read()
    except:
        return ""

def get_blocked_domains():
    content = read_hosts()
    blocked = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("127.0.0.1 ") or line.startswith("0.0.0.0 "):
            parts = line.split()
            if len(parts) >= 2:
                domain = parts[1]
                if domain not in ["localhost", "broadcasthost"]:
                    blocked.append(domain)
    return blocked

def clean_domain(d):
    d = d.strip().lower()
    for prefix in ["https://", "http://", "www."]:
        if d.startswith(prefix):
            d = d[len(prefix):]
    d = d.split("/")[0].split(":")[0]
    return d

def write_hosts_file(content):
    temp_path = os.path.join(tempfile.gettempdir(), f"hosts_{uuid.uuid4()}")
    script_path = os.path.join(tempfile.gettempdir(), f"hb_{uuid.uuid4()}.sh")
    
    with open(temp_path, "w") as f:
        f.write(content)
    
    script = f'''#!/bin/bash
cp "{temp_path}" /etc/hosts
rm "{temp_path}"
dscacheutil -flushcache
killall -HUP mDNSResponder 2>/dev/null
exit 0
'''
    with open(script_path, "w") as f:
        f.write(script)
    os.chmod(script_path, 0o755)
    
    apple_script = f'do shell script "{script_path}" with administrator privileges'
    result = subprocess.run(["osascript", "-e", apple_script], capture_output=True)
    
    try:
        os.remove(script_path)
    except:
        pass
    
    return result.returncode == 0

def add_domains(domains):
    content = read_hosts()
    blocked = get_blocked_domains()
    
    to_add = []
    for d in domains:
        d = clean_domain(d)
        if d and "." in d:
            if d not in blocked:
                to_add.append(d)
            www = f"www.{d}" if not d.startswith("www.") else None
            if www and www not in blocked:
                to_add.append(www)
    
    if not to_add:
        return True
    
    if not content.endswith("\n"):
        content += "\n"
    for d in to_add:
        content += f"127.0.0.1 {d}\n"
    
    return write_hosts_file(content)

def remove_domains(domains):
    content = read_hosts()
    to_remove = set(domains)
    
    new_lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("127.0.0.1 ") or stripped.startswith("0.0.0.0 "):
            parts = stripped.split()
            if len(parts) >= 2 and parts[1] in to_remove:
                continue
        new_lines.append(line)
    
    return write_hosts_file("\n".join(new_lines))

# ============== GUI ==============
class StepBlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StepBlocker")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        self.setup_ui()
        self.refresh_list()
    
    def setup_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        header = ttk.Frame(main)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="🛡️ StepBlocker", font=("Helvetica", 18, "bold")).pack(side=tk.LEFT)
        ttk.Button(header, text="↻ Refresh", command=self.refresh_list).pack(side=tk.RIGHT)
        
        add_frame = ttk.LabelFrame(main, text="Block a site", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.new_domain = tk.StringVar()
        entry = ttk.Entry(add_frame, textvariable=self.new_domain)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        entry.bind("<Return>", lambda e: self.add_domain())
        ttk.Button(add_frame, text="+ Block", command=self.add_domain).pack(side=tk.RIGHT)
        
        preset_frame = ttk.LabelFrame(main, text="Quick Block", padding=10)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        for name, domains in PRESETS.items():
            btn = ttk.Button(preset_frame, text=name, command=lambda d=domains, n=name: self.toggle_preset(n, d))
            btn.pack(side=tk.LEFT, padx=2)
        
        list_frame = ttk.LabelFrame(main, text="Blocked Sites", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, font=("Courier", 11))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="🗑️ Remove Selected", command=self.remove_selected).pack(side=tk.LEFT)
        ttk.Label(btn_frame, text="⚠️ Restart browser after changes", foreground="orange").pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.status_var, foreground="gray").pack(pady=(10, 0))
    
    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for domain in sorted(get_blocked_domains()):
            self.listbox.insert(tk.END, domain)
        self.status_var.set(f"{self.listbox.size()} sites blocked")
    
    def add_domain(self):
        domain = self.new_domain.get().strip()
        if not domain:
            return
        
        if add_domains([domain]):
            self.new_domain.set("")
            self.refresh_list()
            self.status_var.set(f"✓ Blocked {domain}")
        else:
            self.status_var.set("✗ Failed or cancelled")
    
    def toggle_preset(self, name, domains):
        blocked = get_blocked_domains()
        all_blocked = all(d in blocked or f"www.{d}" in blocked for d in domains)
        
        if all_blocked:
            self.remove_with_challenge(domains + [f"www.{d}" for d in domains])
        else:
            if add_domains(domains):
                self.refresh_list()
                self.status_var.set(f"✓ Blocked {name}")
            else:
                self.status_var.set("✗ Failed or cancelled")
    
    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select sites to remove")
            return
        
        domains = [self.listbox.get(i) for i in selection]
        self.remove_with_challenge(domains)
    
    def remove_with_challenge(self, domains):
        dialog = tk.Toplevel(self.root)
        dialog.title("Step Challenge Required")
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="🚶 Step Challenge", font=("Helvetica", 16, "bold")).pack(pady=(0, 10))
        ttk.Label(frame, text="Walk 2,000 steps to unlock!", wraplength=300).pack()
        
        ttk.Label(frame, text="\n1. Open step-tracker/index.html on phone\n2. Walk 2,000 steps\n3. Enter the code below", justify=tk.LEFT).pack(pady=10)
        
        ttk.Label(frame, text="Enter 6-digit code:", font=("Helvetica", 12)).pack(pady=(10, 5))
        
        code_var = tk.StringVar()
        code_entry = ttk.Entry(frame, textvariable=code_var, font=("Courier", 18), width=10, justify=tk.CENTER)
        code_entry.pack()
        code_entry.focus()
        
        error_label = ttk.Label(frame, text="", foreground="red")
        error_label.pack(pady=5)
        
        def verify():
            code = code_var.get().strip()
            if len(code) != 6:
                error_label.config(text="Enter 6 digits")
                return
            
            if validate_code(code):
                dialog.destroy()
                if remove_domains(domains):
                    self.refresh_list()
                    self.status_var.set(f"✓ Removed {len(domains)} site(s)")
                else:
                    self.status_var.set("✗ Failed or cancelled")
            else:
                error_label.config(text="Invalid code! Complete the step challenge.")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Verify & Unblock", command=verify).pack(side=tk.LEFT, padx=5)
        
        code_entry.bind("<Return>", lambda e: verify())

if __name__ == "__main__":
    root = tk.Tk()
    app = StepBlockerApp(root)
    root.mainloop()
