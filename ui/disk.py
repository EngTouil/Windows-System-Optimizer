import os
import time
import threading
import logging
import customtkinter as ctk

from core.disk_utils import get_disk_targets, is_file_in_use

def _walk_with_depth(path, max_depth=3):
    for root, dirs, files in os.walk(path):
        depth = root[len(path):].count(os.sep)
        if depth >= max_depth:
            dirs.clear()
        yield root, dirs, files

class DiskUI:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = parent_frame
        
        self.app.disk_checkboxes = []
        self.disk_path_labels = {}
        self._active_targets = []
        
        self.build_ui()

    def build_ui(self):
        """Constructs the Disk Cleaner UI elements."""
        self.disk_title = ctk.CTkLabel(self.frame, text="Disk Cleaner", font=("Century Gothic", 18, "bold"), text_color="#FFFFFF")
        self.disk_title.pack(pady=(10, 25))

        self.disk_scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent", corner_radius=0,
                                                     scrollbar_button_color="#27272A", scrollbar_button_hover_color="#3F3F46")
        self.disk_scroll.pack(fill="both", expand=True, pady=5)

        self.disk_status_label = ctk.CTkLabel(self.frame, text="Ready to scan for junk files.", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.disk_status_label.pack(pady=(15, 5))

        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_scan_disk = ctk.CTkButton(btn_frame, text="Scan Files", height=50, corner_radius=self.app.btn_rad,
                                         fg_color=self.app.card_color, hover_color=self.app.card_hover, text_color="#FFFFFF",
                                         font=("Century Gothic", 14, "bold"), command=self.run_disk_scan)
        self.btn_scan_disk.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_clean_disk = ctk.CTkButton(btn_frame, text="Preview Clean", height=50, corner_radius=self.app.btn_rad,
                                         fg_color=self.app.accent_color, hover_color="#4F46E5", text_color="#FFFFFF",
                                         font=("Century Gothic", 14, "bold"), command=self.run_disk_preview)
        self.btn_clean_disk.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        self.btn_execute_clean = ctk.CTkButton(self.frame, text="Execute Clean", height=50, corner_radius=self.app.btn_rad,
                                         fg_color="#EF4444", hover_color="#B91C1C", text_color="#FFFFFF",
                                         font=("Century Gothic", 14, "bold"), command=self.run_disk_clean)

        disk_targets_raw = get_disk_targets()
        saved_checks = self.app.settings.get("disk_checkboxes", {})

        for name, path in disk_targets_raw:
            row_frame = ctk.CTkFrame(self.disk_scroll, fg_color=self.app.card_color, corner_radius=8)
            row_frame.pack(fill="x", pady=6, padx=8)
            
            initial_val = 1 if saved_checks.get(name, True) else 0
            var = ctk.IntVar(value=initial_val)
            
            self.app.disk_checkboxes.append((var, name, path))
            
            cb = ctk.CTkCheckBox(row_frame, text=name, variable=var, font=("Century Gothic", 13, "bold"), 
                                 text_color="#FFFFFF", fg_color=self.app.accent_color, hover_color="#4F46E5",
                                 checkmark_color="#FFFFFF")
            cb.pack(side="left", padx=15, pady=15)
            
            lbl_path = ctk.CTkLabel(row_frame, text=path if path else "Path not found", font=("Century Gothic", 11), text_color="#4A4A5A")
            lbl_path.pack(side="right", padx=15, pady=15)
            self.disk_path_labels[name] = lbl_path

    def run_disk_scan(self):
        """Initializes the background thread to safely scan disk cache targets."""
        self._active_targets = [
            (name, path) for var, name, path in self.app.disk_checkboxes if var.get() == 1
        ]
        self.btn_scan_disk.configure(state="disabled", fg_color=self.app.bg_color, text_color="#8F8F9D")
        self.btn_clean_disk.configure(state="disabled")
        self.btn_execute_clean.pack_forget()
        self.disk_status_label.configure(text="Scanning directories...", text_color=self.app.accent_color)
        threading.Thread(target=self._scan_disk_thread, args=(False,), daemon=True).start()

    def run_disk_preview(self):
        """Initializes the background thread to preview exactly what files will be deleted."""
        self._active_targets = [
            (name, path) for var, name, path in self.app.disk_checkboxes if var.get() == 1
        ]
        self.btn_scan_disk.configure(state="disabled")
        self.btn_clean_disk.configure(state="disabled", fg_color=self.app.bg_color, text_color="#8F8F9D")
        self.btn_execute_clean.pack_forget()
        self.disk_status_label.configure(text="Scanning what will be deleted...", text_color=self.app.accent_color)
        threading.Thread(target=self._scan_disk_thread, args=(True,), daemon=True).start()

    def _scan_disk_thread(self, is_preview=False):
        """Executes the disk scanning logic (either info scan or preview clean) on a background thread."""
        total_size_bytes = 0
        skipped_in_use = 0
        skipped_recent = 0
        
        for name, path in self._active_targets:
            category_bytes = 0
            lbl_path = self.disk_path_labels.get(name)
            
            if path and os.path.exists(path):
                for root, dirs, files in _walk_with_depth(path, max_depth=3):
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            if not os.path.islink(fp):
                                if is_preview:
                                    if is_file_in_use(fp):
                                        skipped_in_use += 1
                                        continue
                                    age_seconds = time.time() - os.path.getmtime(fp)
                                    if age_seconds < 86400:
                                        skipped_recent += 1
                                        continue
                                        
                                category_bytes += os.path.getsize(fp)
                        except Exception as e:
                            logging.debug(f"[disk] {e}")
                        
            total_size_bytes += category_bytes
            
            cat_mb = category_bytes / (1024 * 1024)
            cat_str = f"{cat_mb / 1024:.2f} GB" if cat_mb >= 1024 else f"{cat_mb:.2f} MB"
                
            display_path = path if path else "Path not found"
            if lbl_path:
                self.app.after(0, lambda l=lbl_path, p=display_path, s=cat_str: l.configure(text=f"{p}  —  {s}"))
        
        size_mb = total_size_bytes / (1024 * 1024)
        size_str = f"{size_mb / 1024:.2f} GB" if size_mb >= 1024 else f"{size_mb:.2f} MB"

        if is_preview:
            skipped_parts = []
            if skipped_in_use > 0:
                skipped_parts.append(f"{skipped_in_use} files in use")
            if skipped_recent > 0:
                skipped_parts.append(f"{skipped_recent} recent files")
                
            skipped_msg = " + ".join(skipped_parts) + " skipped, " if skipped_parts else ""
            msg = f"Preview: {skipped_msg}{size_str} will be freed — click Execute Clean to confirm"
            
            self.app.after(0, lambda m=msg: self.disk_status_label.configure(text=m, text_color="#10B981"))
            self.app.after(0, lambda: self.btn_execute_clean.pack(fill="x", pady=(10, 0)))
        else:
            self.app.after(0, lambda s=size_str: self.disk_status_label.configure(text=f"Scan Complete: {s} of junk detected.", text_color="#10B981"))
            
        self.app.after(0, lambda: self.btn_scan_disk.configure(state="normal", fg_color=self.app.card_color, text_color="#FFFFFF"))
        self.app.after(0, lambda: self.btn_clean_disk.configure(state="normal", fg_color=self.app.accent_color, text_color="#FFFFFF"))

    def run_disk_clean(self):
        """Initializes the background thread to permanently delete selected junk files."""
        self._active_targets = [
            (name, path) for var, name, path in self.app.disk_checkboxes if var.get() == 1
        ]
        self.btn_scan_disk.configure(state="disabled")
        self.btn_clean_disk.configure(state="disabled")
        self.btn_execute_clean.configure(state="disabled", fg_color=self.app.bg_color, text_color="#8F8F9D")
        self.disk_status_label.configure(text="Annihilating junk files...", text_color="#EF4444")
        threading.Thread(target=self._clean_disk_thread, daemon=True).start()

    def _clean_disk_thread(self):
        """Executes the file deletion logic on a background thread."""
        freed_bytes = 0
        skipped_in_use = 0
        skipped_recent = 0
        
        for name, path in self._active_targets:
            if path and os.path.exists(path):
                for root, dirs, files in _walk_with_depth(path, max_depth=3):
                    for f in files:
                        item_path = os.path.join(root, f)
                        try:
                            if os.path.isfile(item_path) and not os.path.islink(item_path):
                                if is_file_in_use(item_path):
                                    skipped_in_use += 1
                                    continue
                                    
                                age_seconds = time.time() - os.path.getmtime(item_path)
                                if age_seconds < 86400:
                                    skipped_recent += 1
                                    continue
                                
                                size = os.path.getsize(item_path)
                                os.remove(item_path)
                                freed_bytes += size
                        except Exception as e:
                            logging.debug(f"[disk] {e}")
                            continue
                    
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        try:
                            if not os.listdir(dir_path):
                                os.rmdir(dir_path)
                        except Exception as e:
                            logging.debug(f"[disk] {e}")

        size_mb = freed_bytes / (1024 * 1024)
        size_str = f"{size_mb / 1024:.2f} GB" if size_mb >= 1024 else f"{size_mb:.2f} MB"

        skipped_parts = []
        if skipped_in_use > 0:
            skipped_parts.append(f"{skipped_in_use} in use")
        if skipped_recent > 0:
            skipped_parts.append(f"{skipped_recent} recent files")
            
        skipped_msg = "  |  " + " + ".join(skipped_parts) + " skipped" if skipped_parts else ""

        self.app.after(0, lambda s=size_str, m=skipped_msg: self.disk_status_label.configure(text=f"Purge Complete: Freed {s}{m}", text_color="#10B981"))
        self.app.after(0, lambda: self.btn_scan_disk.configure(state="normal"))
        self.app.after(0, lambda: self.btn_clean_disk.configure(state="normal", fg_color=self.app.accent_color, text_color="#FFFFFF"))
        self.app.after(0, lambda: self.btn_execute_clean.configure(state="normal", fg_color="#EF4444", text_color="#FFFFFF"))
        self.app.after(0, lambda: self.btn_execute_clean.pack_forget())