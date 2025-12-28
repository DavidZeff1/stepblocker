import tkinter as tk
from .config import *
from .hosts import get_blocked_domains, add_domains, remove_domains
from .unlock import validate_code

class StepBlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StepBlocker")
        self.root.geometry("500x600")
        self.root.configure(bg=BG)
        self.root.minsize(400, 500)
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        tk.Label(header, text="StepBlocker", font=("SF Pro Display", 28, "bold"), bg=BG, fg=TEXT).pack(side=tk.LEFT)
        self.count_label = tk.Label(header, text="", font=("SF Pro Display", 13), bg=BG, fg=TEXT_DIM)
        self.count_label.pack(side=tk.RIGHT, pady=(10, 0))

        # Add domain
        add_frame = tk.Frame(self.root, bg=BG)
        add_frame.pack(fill=tk.X, padx=30, pady=(0, 15))
        
        self.entry = tk.Entry(add_frame, font=("SF Pro Display", 14), bg=BG_LIGHT, fg=TEXT,
                              insertbackground=TEXT, relief=tk.FLAT, highlightthickness=2,
                              highlightbackground=BG_LIGHT, highlightcolor=ACCENT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(0, 10))
        self.entry.insert(0, "enter domain...")
        self.entry.bind("<FocusIn>", lambda e: self.entry.delete(0, tk.END) if self.entry.get() == "enter domain..." else None)
        self.entry.bind("<FocusOut>", lambda e: self.entry.insert(0, "enter domain...") if not self.entry.get() else None)
        self.entry.bind("<Return>", lambda e: self.add_domain())

        self.add_btn = self.make_button(add_frame, "Block", self.add_domain, ACCENT)
        self.add_btn.pack(side=tk.RIGHT)

        # Bulk import button
        bulk_frame = tk.Frame(self.root, bg=BG)
        bulk_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        bulk_btn = self.make_button(bulk_frame, "Bulk Import", self.show_bulk_import, BG_LIGHT, small=True)
        bulk_btn.pack(side=tk.LEFT)

        # Presets
        preset_frame = tk.Frame(self.root, bg=BG)
        preset_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        for name in PRESETS:
            btn = self.make_button(preset_frame, name, lambda n=name: self.toggle_preset(n), BG_LIGHT, small=True)
            btn.pack(side=tk.LEFT, padx=(0, 8))

        # List
        list_frame = tk.Frame(self.root, bg=BG_LIGHT, highlightthickness=0)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        self.listbox = tk.Listbox(list_frame, font=("SF Mono", 12), bg=BG_LIGHT, fg=TEXT,
                                   selectbackground=ACCENT, selectforeground=TEXT,
                                   relief=tk.FLAT, highlightthickness=0, selectmode=tk.EXTENDED,
                                   activestyle='none', borderwidth=0)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=15)

        # Bottom
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill=tk.X, padx=30, pady=(0, 30))
        
        self.remove_btn = self.make_button(bottom, "Remove Selected", self.remove_selected, DANGER)
        self.remove_btn.pack(side=tk.LEFT)
        
        self.status = tk.Label(bottom, text="", font=("SF Pro Display", 11), bg=BG, fg=TEXT_DIM)
        self.status.pack(side=tk.RIGHT)

    def make_button(self, parent, text, command, color, small=False):
        btn = tk.Label(parent, text=text, font=("SF Pro Display", 11 if small else 13, "bold"),
                       bg=color, fg=TEXT, cursor="hand2", padx=16, pady=6 if small else 10)
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.configure(bg=ACCENT_HOVER if color == ACCENT else "#3a3a5a" if color == BG_LIGHT else "#dc2626"))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        return btn

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        domains = sorted(get_blocked_domains())
        for domain in domains:
            self.listbox.insert(tk.END, f"  {domain}")
        self.count_label.config(text=f"{len(domains)} blocked")

    def add_domain(self):
        domain = self.entry.get().strip()
        if not domain or domain == "enter domain...":
            return
        success, count = add_domains([domain])
        if success:
            self.entry.delete(0, tk.END)
            self.refresh_list()
            self.status.config(text=f"✓ Blocked", fg=SUCCESS)
        else:
            self.status.config(text="Cancelled", fg=TEXT_DIM)

    def show_bulk_import(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("")
        dialog.geometry("420x400")
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 420) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = tk.Frame(dialog, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(frame, text="Bulk Import", font=("SF Pro Display", 20, "bold"), bg=BG, fg=TEXT).pack(anchor=tk.W)
        tk.Label(frame, text="Paste domains (one per line)", font=("SF Pro Display", 12), bg=BG, fg=TEXT_DIM).pack(anchor=tk.W, pady=(5, 15))

        text_frame = tk.Frame(frame, bg=BG_LIGHT)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.bulk_text = tk.Text(text_frame, font=("SF Mono", 12), bg=BG_LIGHT, fg=TEXT,
                                  insertbackground=TEXT, relief=tk.FLAT, highlightthickness=0,
                                  padx=15, pady=15)
        self.bulk_text.pack(fill=tk.BOTH, expand=True)
        self.bulk_text.focus()

        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel = tk.Label(btn_frame, text="Cancel", font=("SF Pro Display", 12), bg=BG, fg=TEXT_DIM, cursor="hand2")
        cancel.pack(side=tk.LEFT, padx=(0, 20))
        cancel.bind("<Button-1>", lambda e: dialog.destroy())
        
        def do_import():
            text = self.bulk_text.get("1.0", tk.END)
            domains = [line.strip() for line in text.split("\n") if line.strip()]
            if domains:
                success, count = add_domains(domains)
                if success:
                    dialog.destroy()
                    self.refresh_list()
                    self.status.config(text=f"✓ Blocked {count} domains", fg=SUCCESS)
                else:
                    self.status.config(text="Cancelled", fg=TEXT_DIM)
        
        import_btn = self.make_button(btn_frame, f"Block All", do_import, ACCENT)
        import_btn.pack(side=tk.RIGHT)

    def toggle_preset(self, name):
        domains = PRESETS[name]
        blocked = get_blocked_domains()
        all_blocked = all(d in blocked or f"www.{d}" in blocked for d in domains)
        if all_blocked:
            self.remove_with_challenge(domains + [f"www.{d}" for d in domains])
        else:
            success, count = add_domains(domains)
            if success:
                self.refresh_list()
                self.status.config(text=f"✓ {name} blocked", fg=SUCCESS)

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        domains = [self.listbox.get(i).strip() for i in selection]
        self.remove_with_challenge(domains)

    def remove_with_challenge(self, domains):
        dialog = tk.Toplevel(self.root)
        dialog.title("")
        dialog.geometry("360x340")
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 360) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 340) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = tk.Frame(dialog, bg=BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(frame, text="🚶", font=("SF Pro Display", 40), bg=BG, fg=TEXT).pack()
        tk.Label(frame, text="Step Challenge", font=("SF Pro Display", 20, "bold"), bg=BG, fg=TEXT).pack(pady=(10, 5))
        tk.Label(frame, text="Walk 2,000 steps to unlock", font=("SF Pro Display", 12), bg=BG, fg=TEXT_DIM).pack()

        tk.Label(frame, text="Enter 6-digit code", font=("SF Pro Display", 11), bg=BG, fg=TEXT_DIM).pack(pady=(25, 8))
        
        code_entry = tk.Entry(frame, font=("SF Mono", 24), bg=BG_LIGHT, fg=TEXT, width=8,
                              justify=tk.CENTER, insertbackground=TEXT, relief=tk.FLAT,
                              highlightthickness=2, highlightbackground=BG_LIGHT, highlightcolor=ACCENT)
        code_entry.pack(ipady=8)
        code_entry.focus()

        error_label = tk.Label(frame, text="", font=("SF Pro Display", 11), bg=BG, fg=DANGER)
        error_label.pack(pady=(10, 0))

        def verify():
            code = code_entry.get().strip()
            if len(code) != 6:
                error_label.config(text="Enter 6 digits")
                return
            if validate_code(code):
                dialog.destroy()
                if remove_domains(domains):
                    self.refresh_list()
                    self.status.config(text=f"✓ Removed", fg=SUCCESS)
            else:
                error_label.config(text="Invalid code")
                code_entry.delete(0, tk.END)

        code_entry.bind("<Return>", lambda e: verify())

        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.pack(pady=(20, 0))
        
        cancel = tk.Label(btn_frame, text="Cancel", font=("SF Pro Display", 12), bg=BG, fg=TEXT_DIM, cursor="hand2")
        cancel.pack(side=tk.LEFT, padx=(0, 20))
        cancel.bind("<Button-1>", lambda e: dialog.destroy())
        
        verify_btn = self.make_button(btn_frame, "Verify", verify, ACCENT)
        verify_btn.pack(side=tk.LEFT)
