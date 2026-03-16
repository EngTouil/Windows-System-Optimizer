import os
import sys
import time
import threading
import shutil
import subprocess
import winreg
import re
import csv
import ctypes
import logging
from io import StringIO
import customtkinter as ctk
from collections import deque
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# --- Core & Utility Imports ---
from core.system_tools import ensure_single_instance, elevate_privileges, CREATE_NO_WINDOW
from utils.settings import load_settings, save_settings, get_settings_path
from utils.history import read_history, clear_history

# --- UI Component Imports ---
from ui.memory import MemoryUI
from ui.disk import DiskUI
from ui.process import ProcessUI
from ui.scheduler import SchedulerUI
from ui.gamemode import GameModeUI

logging.basicConfig(
    filename=os.path.join(
        os.environ.get('APPDATA', ''), 
        'SystemOptimizer', 'debug.log'),
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- ENABLED FOR PRODUCTION (.EXE) ---

class CleanOptimizer(ctk.CTk):
    """Main application class for the System Optimizer."""
    
    ALL_NAV = ['memory', 'disk', 'startup', 'process', 'scheduler', 'gamemode', 'history']

    def __init__(self):
        super().__init__()

        # --- Base App State ---
        self.is_first_run = not os.path.exists(get_settings_path())
        self.settings = load_settings()
        self._cached_geometry = ""
        
        # --- Shared UI Variables ---
        self.auto_clean_var = ctk.BooleanVar(value=self.settings.get("auto_clean_startup", False))
        self._startup_scanned = False
        self.ram_history = deque([0] * 60, maxlen=60)  

        # --- Theme & Window Setup ---
        self.title("System Optimizer")
        app_width = 900
        app_height = 650  
        
        if self.settings.get("window_pos"):
            self.geometry(self.settings["window_pos"])
        else:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = int((screen_width / 2) - (app_width / 2))
            y = int((screen_height / 2) - (app_height / 2))
            self.geometry(f"{app_width}x{app_height}+{x}+{y}")
            
        self.attributes("-alpha", 0.95) 
        self.after(10, self.apply_windows_glass_effect)
        
        # --- PyInstaller Icon ---
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "assets", "icon.ico")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "icon.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            pass
        
        self.bg_color = "#09090B"      
        self.sidebar_color = "#0E0E12" 
        self.card_color = "#1E1E23"    
        self.card_hover = "#282830"    
        self.accent_color = "#6366F1"

        self.text_active = "#FFFFFF"
        self.text_disabled = "#4A4A5A"
        self.subtext_active = "#8F8F9D"
        self.subtext_disabled = "#383846"

        self.pad_grid = 30 
        self.container_rad = 20
        self.btn_rad = 16
        
        self.configure(fg_color=self.bg_color) 
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        threading.Thread(target=self.setup_tray, daemon=True).start()

        # ==========================================
        # SIDEBAR UI
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False) 
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="⚡ Optimizer", font=("Century Gothic", 28, "bold"), text_color="#FFFFFF")
        self.logo_label.grid(row=0, column=0, padx=25, pady=(45, 50)) 

        self.btn_memory = ctk.CTkButton(self.sidebar_frame, text="Memory Clean", corner_radius=self.btn_rad, height=50,
                                        font=("Century Gothic", 13, "bold"), fg_color=self.card_color, hover_color=self.card_hover, 
                                        anchor="w", command=self.show_memory_frame)
        self.btn_memory.grid(row=1, column=0, padx=20, pady=8, sticky="ew")

        self.btn_disk = ctk.CTkButton(self.sidebar_frame, text="Disk Cleaner", corner_radius=self.btn_rad, height=50,
                                         font=("Century Gothic", 13, "bold"), fg_color="transparent", text_color="#8F8F9D", 
                                         hover_color=self.card_hover, anchor="w", command=self.show_disk_frame)
        self.btn_disk.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_startup = ctk.CTkButton(self.sidebar_frame, text="Startup Apps", corner_radius=self.btn_rad, height=50,
                                         font=("Century Gothic", 13, "bold"), fg_color="transparent", text_color="#8F8F9D", 
                                         hover_color=self.card_hover, anchor="w", command=self.show_startup_frame)
        self.btn_startup.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.btn_process = ctk.CTkButton(self.sidebar_frame, text="Processes", corner_radius=self.btn_rad, height=50,
                                         font=("Century Gothic", 13, "bold"), fg_color="transparent", text_color="#8F8F9D", 
                                         hover_color=self.card_hover, anchor="w", command=self.show_process_frame)
        self.btn_process.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        self.btn_scheduler = ctk.CTkButton(self.sidebar_frame, text="Auto Scheduler", corner_radius=self.btn_rad, height=50,
                                         font=("Century Gothic", 13, "bold"), fg_color="transparent", text_color="#8F8F9D", 
                                         hover_color=self.card_hover, anchor="w", command=self.show_scheduler_frame)
        self.btn_scheduler.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        self.btn_gamemode = ctk.CTkButton(self.sidebar_frame, text="🎮  Game Mode", corner_radius=self.btn_rad, height=50,
                                         font=("Century Gothic", 13, "bold"), fg_color="transparent", text_color="#8F8F9D",
                                         hover_color=self.card_hover, anchor="w", command=self.show_gamemode_frame)
        self.btn_gamemode.grid(row=6, column=0, padx=20, pady=8, sticky="ew")

        self.btn_history = ctk.CTkButton(self.sidebar_frame, text="History", corner_radius=self.btn_rad, height=50,
                                         font=("Century Gothic", 13, "bold"), fg_color="transparent", text_color="#8F8F9D", 
                                         hover_color=self.card_hover, anchor="w", command=self.show_history_frame)
        self.btn_history.grid(row=7, column=0, padx=20, pady=8, sticky="ew")

        # ==========================================
        # MAIN CONTENT FRAMES
        # ==========================================
        self.memory_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent")
        self.disk_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent")
        self.startup_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent")
        self.process_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent") 
        self.scheduler_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent")
        self.gamemode_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent")
        self.history_frame = ctk.CTkFrame(self, corner_radius=self.container_rad, fg_color="transparent")

        # Initialize Module UIs
        self.memory_ui = MemoryUI(self, self.memory_frame)
        self.disk_ui = DiskUI(self, self.disk_frame)
        self.process_ui = ProcessUI(self, self.process_frame)
        self.scheduler_ui = SchedulerUI(self, self.scheduler_frame)
        self.gamemode_ui = GameModeUI(self, self.gamemode_frame)
        
        # Initialize embedded UIs
        self.build_startup_ui()
        self.build_history_ui()

        self.show_memory_frame()

        if self.is_first_run:
            self.after(500, self.show_welcome_screen)

        if self.auto_clean_var.get() and not self.is_first_run:
            self.after(1000, self.run_clean) 

        self._setup_smooth_scroll()
        
        for sf in [
            self.disk_ui.disk_scroll,
            self.startup_scroll,
            self.process_ui.process_scroll,
            self.history_scroll,
            self.gamemode_ui._gm_scroll,
        ]:
            self._register_scroll_frames(sf)

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        if event.widget is self:
            self._cached_geometry = self.geometry()

    def run_clean(self):
        """Proxy to trigger deep clean from anywhere in the app."""
        self.memory_ui.run_clean()

    # ==========================================
    # CORE SYSTEM EVENT HANDLERS
    # ==========================================
    def _setup_smooth_scroll(self):
        self._scroll_frames = []
        def register(sf):
            self._scroll_frames.append(sf)
        self._register_scroll_frames = register

        def on_mousewheel(event):
            mx = self.winfo_pointerx()
            my = self.winfo_pointery()
            for sf in self._scroll_frames:
                try:
                    if not sf.winfo_ismapped():
                        continue
                    x1 = sf.winfo_rootx()
                    y1 = sf.winfo_rooty()
                    x2 = x1 + sf.winfo_width()
                    y2 = y1 + sf.winfo_height()
                    if x1 <= mx <= x2 and y1 <= my <= y2:
                        direction = -1 if event.delta > 0 else 1
                        amount = max(1, abs(int(event.delta / 120))) * 15
                        sf._parent_canvas.yview_scroll(direction * amount, "units")
                        return
                except Exception as e:
                    continue
        self.bind_all("<MouseWheel>", on_mousewheel)

    def show_welcome_screen(self):
        welcome = ctk.CTkToplevel(self)
        welcome.title("Welcome to System Optimizer")
        
        w, h = 500, 380
        x = int((self.winfo_screenwidth() / 2) - (w / 2))
        y = int((self.winfo_screenheight() / 2) - (h / 2))
        welcome.geometry(f"{w}x{h}+{x}+{y}")
        welcome.resizable(False, False)
        welcome.configure(fg_color=self.bg_color)
        welcome.attributes("-topmost", True) 

        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "assets", "icon.ico")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets", "icon.ico")
            welcome.iconbitmap(icon_path)
        except Exception as e:
            pass

        ctk.CTkLabel(welcome, text="⚡ System Optimizer", font=("Century Gothic", 28, "bold"), text_color="#FFFFFF").pack(pady=(40, 20))

        bullets_frame = ctk.CTkFrame(welcome, fg_color="transparent")
        bullets_frame.pack(pady=10, padx=50, fill="x")

        bullets = [
            "🚀 Instantly free up RAM and clear standby memory.",
            "🗑️ Deep clean junk files, temp data, and browser caches.",
            "⚙️ Manage startup apps to boost boot times safely.",
            "⏰ Schedule auto-cleaning for hands-free performance."
        ]

        for bullet in bullets:
            ctk.CTkLabel(bullets_frame, text=bullet, font=("Century Gothic", 14), text_color="#8F8F9D", anchor="w", justify="left").pack(fill="x", pady=5)

        ctk.CTkButton(welcome, text="Get Started", height=45, width=200, corner_radius=16,
                            font=("Century Gothic", 15, "bold"), fg_color=self.accent_color, hover_color="#4F46E5",
                            text_color="#FFFFFF", command=welcome.destroy).pack(pady=(30, 20))

        welcome.grab_set()

    def hide_window(self):
        save_settings(self)
        self.withdraw()

    def show_window(self, icon, item):
        self.after(0, self.deiconify)

    def quick_clean_tray(self, icon, item):
        self.after(0, self.run_clean)

    def quit_window(self, icon, item):
        save_settings(self)
      
        if hasattr(self, '_scheduler_after_id') and self._scheduler_after_id:
            self.after_cancel(self._scheduler_after_id)
        if hasattr(self, '_toast_after'):
            self.after_cancel(self._toast_after)
        icon.stop()
        self.after(0, self.destroy)

    def create_tray_image(self):
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((8, 8, 56, 56), fill=self.accent_color)
        return image

    def setup_tray(self):
        try:
            image = self.create_tray_image()
            menu = pystray.Menu(
                item('Open Optimizer', self.show_window, default=True),
                item('Quick Clean', self.quick_clean_tray),
                item('Exit', self.quit_window)
            )
            self.tray_icon = pystray.Icon("SystemOptimizer", image, "System Optimizer", menu)
            self.tray_icon.run()
        except Exception as e:
            pass

    def apply_windows_glass_effect(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(ctypes.c_int(3)), ctypes.sizeof(ctypes.c_int))
        except Exception as e:
            pass

    def show_toast(self, message, color="#10B981"):
        if not hasattr(self, 'toast_label') or not self.toast_label.winfo_exists():
            self.toast_label = ctk.CTkLabel(self, text="", font=("Century Gothic", 13, "bold"), 
                                       fg_color=self.card_color, 
                                       corner_radius=8, padx=20, pady=10)
        self.toast_label.configure(text=message, text_color=color)
        self.toast_label.place(relx=0.5, rely=0.92, anchor="center")
        if hasattr(self, '_toast_after'):
            self.after_cancel(self._toast_after)
        self._toast_after = self.after(3000, lambda: self.toast_label.place_forget())

    # ==========================================
    # NAVIGATION HANDLERS
    # ==========================================
    def show_frame(self, name):
        self._proc_refresh_active = False
        if hasattr(self, '_proc_loop_id'): 
            self.after_cancel(self._proc_loop_id)
            
        for f in self.ALL_NAV:
            getattr(self, f + '_frame').grid_forget()
            getattr(self, 'btn_' + f).configure(fg_color="transparent", text_color="#8F8F9D")
            
        getattr(self, name + '_frame').grid(row=0, column=1, sticky="nsew", padx=40, pady=25)
        getattr(self, 'btn_' + name).configure(fg_color=self.card_color, text_color="#FFFFFF")
        
        if name == 'process':
            self._proc_refresh_active = True
            self.process_ui.process_page_loop()
        if name == 'startup' and not self._startup_scanned:
            self._startup_scanned = True
            self.refresh_startup_apps()
        if name == 'history':
            self.refresh_history_ui()

    def show_memory_frame(self): self.show_frame('memory')
    def show_disk_frame(self): self.show_frame('disk')
    def show_startup_frame(self): self.show_frame('startup')
    def show_process_frame(self): self.show_frame('process')
    def show_scheduler_frame(self): self.show_frame('scheduler')
    def show_gamemode_frame(self): self.show_frame('gamemode')
    def show_history_frame(self): self.show_frame('history')

    # ==========================================
    # STARTUP MANAGER EMBEDDED UI
    # ==========================================
    def build_startup_ui(self):
        self.startup_title = ctk.CTkLabel(self.startup_frame, text="Startup Manager", font=("Century Gothic", 18, "bold"), text_color="#FFFFFF")
        self.startup_title.pack(pady=(10, 25))

        self.startup_scroll = ctk.CTkScrollableFrame(self.startup_frame, fg_color="transparent", corner_radius=0,
                                                     scrollbar_button_color="#27272A", scrollbar_button_hover_color="#3F3F46")
        self.startup_scroll.pack(fill="both", expand=True, pady=5)

        self.refresh_btn = ctk.CTkButton(self.startup_frame, text="Rescan System", height=55, corner_radius=self.btn_rad,
                                         fg_color=self.card_color, hover_color=self.card_hover, text_color="#FFFFFF",
                                         font=("Century Gothic", 13, "bold"), 
                                         command=self.refresh_startup_apps) 
        self.refresh_btn.pack(fill="x", pady=(25, 0))

    def refresh_startup_apps(self):
        self.refresh_btn.configure(state="disabled", text="Scanning Registry & Folders...", fg_color=self.bg_color)
        if hasattr(self, 'startup_items'):
            for widget in self.startup_items:
                try: widget.destroy()
                except Exception as e: pass
        self.startup_items = []
        
        self.loading_label = ctk.CTkLabel(self.startup_scroll, text="Gathering system background processes...\nPlease wait.", 
                                          font=("Century Gothic", 14), text_color=self.accent_color)
        self.loading_label.pack(pady=40)
        self.startup_items.append(self.loading_label)

        threading.Thread(target=self._scan_startup_apps_thread, daemon=True).start()

    def _scan_startup_apps_thread(self):
        found_apps = []
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Registry • User"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "Registry • System"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "Registry • Sys (32-bit)"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "Registry • User (RunOnce)"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "Registry • System (RunOnce)"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce", "Registry • Sys32 (RunOnce)")
        ]

        all_reg_entries = []  
        for hkey, base_path, scope in registry_paths:
            for suffix in ["", "_Disabled"]:
                full_path = base_path + suffix
                try:
                    key = winreg.OpenKey(hkey, full_path, 0, winreg.KEY_READ)
                    for i in range(winreg.QueryInfoKey(key)[1]):
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if value and isinstance(value, str) and name not in all_reg_entries:
                                if self.is_safe_to_disable(name, value, scope):
                                    all_reg_entries.append(name)
                                    found_apps.append({
                                        "raw_name": name, 
                                        "friendly_name": self.get_friendly_name(name, value),
                                        "loc1": hkey, 
                                        "loc2": base_path,
                                        "scope": scope + (" (Disabled)" if suffix else ""),
                                        "is_active": (suffix == ""), 
                                        "app_type": "reg",
                                        "cmd_path": value
                                    })
                        except Exception as e:
                            pass
                    winreg.CloseKey(key)
                except OSError: 
                    pass

        folder_locations = [
            (os.path.join(os.getenv('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"), "Folder • User"),
            (r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup", "Folder • System"),
        ]
        allowed_exts = ('.exe', '.bat', '.cmd', '.vbs', '.ps1', '.lnk')

        for active_dir, scope in folder_locations:
            disabled_dir = active_dir + "_Disabled"
            os.makedirs(disabled_dir, exist_ok=True)

            if os.path.exists(active_dir):
                for file in os.listdir(active_dir):
                    if file.lower().endswith(allowed_exts):
                        if self.is_safe_to_disable(file, active_dir, scope):
                            found_apps.append({
                                "raw_name": file, "friendly_name": self.get_friendly_name(file),
                                "loc1": active_dir, "loc2": disabled_dir, "scope": scope, 
                                "is_active": True, "app_type": "folder",
                                "cmd_path": os.path.join(active_dir, file)
                            })

            if os.path.exists(disabled_dir):
                for file in os.listdir(disabled_dir):
                    if file.lower().endswith(allowed_exts):
                        if self.is_safe_to_disable(file, disabled_dir, scope):
                            found_apps.append({
                                "raw_name": file, "friendly_name": self.get_friendly_name(file),
                                "loc1": active_dir, "loc2": disabled_dir, "scope": scope + " (Disabled)", 
                                "is_active": False, "app_type": "folder",
                                "cmd_path": os.path.join(disabled_dir, file)
                            })

        try:
            output = subprocess.run(['schtasks', '/query', '/fo', 'csv', '/nh'], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout
            reader = csv.reader(StringIO(output))
            for row in reader:
                if len(row) >= 4 and 'Logon' in row[3]: 
                    task_name = row[0].strip('"')
                    friendly = os.path.splitext(os.path.basename(task_name))[0]
                    if self.is_safe_to_disable(task_name, "", "Scheduled Task"):
                        found_apps.append({
                            "raw_name": task_name, "friendly_name": friendly,
                            "loc1": None, "loc2": None, "scope": "Scheduled Task", 
                            "is_active": True, "app_type": "task",
                            "cmd_path": task_name
                        })
        except Exception as e:
            pass

        self.after(0, lambda: self._render_startup_apps(found_apps))

    def _render_startup_apps(self, apps_data):
        if hasattr(self, 'startup_items'):
            for widget in self.startup_items:
                try: widget.destroy()
                except Exception: pass
        self.startup_items = []

        def render_batch(start):
            batch = apps_data[start:start+5]
            for app in batch:
                self.create_startup_row(**app)
            if start + 5 < len(apps_data):
                self.after(16, lambda: render_batch(start + 5))
            else:
                if len(self.startup_items) == 0:
                    empty_label = ctk.CTkLabel(self.startup_scroll, text="No safe startup entries found.", font=("Century Gothic", 13), text_color="#8F8F9D")
                    empty_label.pack(pady=40)
                    self.startup_items.append(empty_label)
                self.refresh_btn.configure(state="normal", text="Rescan System", fg_color=self.card_color)

        if apps_data:
            render_batch(0)
        else:
            empty_label = ctk.CTkLabel(self.startup_scroll, text="Your system is incredibly clean.\nNo safe bloatware found.", font=("Century Gothic", 13), text_color="#8F8F9D")
            empty_label.pack(pady=40)
            self.startup_items.append(empty_label)
            self.refresh_btn.configure(state="normal", text="Rescan System", fg_color=self.card_color)

    def get_friendly_name(self, raw_name, command_str=""):
        cleanups = {
            "matlab": "MATLAB Service", "onedrive": "Microsoft OneDrive", "discord": "Discord",
            "spotify": "Spotify", "steam": "Steam", "epicgameslauncher": "Epic Games",
            "battlenet": "Battle.net", "uplay": "Ubisoft Connect", "gog galaxy": "GOG Galaxy"
        }
        if ".lnk" in raw_name.lower(): return raw_name.replace(".lnk", "").replace(".LNK", "")
        match = re.search(r'([a-zA-Z0-9_ -]+)\.exe', str(command_str), re.IGNORECASE)
        if match:
            exe_name = match.group(1).strip()
            return cleanups.get(exe_name.lower(), exe_name.title())
        
        name_clean = raw_name.replace("_", " ").replace("-", " ").split(".")[0]
        return cleanups.get(raw_name.lower(), name_clean.capitalize())

    def is_safe_to_disable(self, name, command_str, scope):
        name_lower = str(name).lower()
        cmd_lower = str(command_str).lower()
        if "system32" in cmd_lower or "syswow64" in cmd_lower or "windows nt" in cmd_lower: return False
        if "Scheduled Task" in scope and "\\" in name:
            if "microsoft\\windows" in name_lower: return False
        
        danger_zone = [
            "ctfmon", "dwm", "winlogon", "lsass", "services", "svchost",
            "taskhostw", "sihost", "fontdrvhost", "rundll32", "conhost",
            "defender", "antivirus", "malwarebytes", "kaspersky", "vanguard",
            "faceit", "easyanticheat", "battleye", "nvdisplay", "nvidiacontainer", 
            "amdow", "igcc", "igcctray", "realtek", "riched", "hid",
        ]
        for keyword in danger_zone:
            if keyword in name_lower or keyword in cmd_lower: return False
        return True

    def bind_hover(self, widget, color_enter, color_leave):
        def on_enter(e): widget.configure(fg_color=color_enter)
        def on_leave(e): widget.configure(fg_color=color_leave)
        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")
        for child in widget.winfo_children():
            child.bind("<Enter>", on_enter, add="+")
            child.bind("<Leave>", on_leave, add="+")

    def create_startup_row(self, raw_name, friendly_name, loc1, loc2, scope, is_active, app_type, cmd_path):
        initial_bg = self.card_color if is_active else "#15151A"
        row_frame = ctk.CTkFrame(self.startup_scroll, fg_color=initial_bg, corner_radius=self.btn_rad)
        row_frame.pack(fill="x", pady=8, padx=8) 
        self.startup_items.append(row_frame)
        hover_bg = self.card_hover if is_active else "#1A1A20"
        self.bind_hover(row_frame, hover_bg, initial_bg)

        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=0)

        info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=18)

        t_color = self.text_active if is_active else self.text_disabled
        s_color = self.subtext_active if is_active else self.subtext_disabled

        name_lbl = ctk.CTkLabel(info_frame, text=friendly_name, font=("Century Gothic", 13, "bold"), text_color=t_color)
        name_lbl.pack(anchor="w", pady=(0, 2)) 
        
        display_cmd = (str(cmd_path)[:45] + "...") if len(str(cmd_path)) > 45 else str(cmd_path)
        scope_lbl = ctk.CTkLabel(info_frame, text=f"{scope}  |  {display_cmd}", font=("Century Gothic", 13), text_color=s_color)
        scope_lbl.pack(anchor="w")

        switch_var = ctk.IntVar(value=1 if is_active else 0)
        toggle = ctk.CTkSwitch(row_frame, text="", width=45, button_color="#FFFFFF", progress_color=self.accent_color, variable=switch_var,
                               command=lambda t=app_type, l1=loc1, l2=loc2, n=raw_name, sv=switch_var, nl=name_lbl, sl=scope_lbl, rf=row_frame: 
                               self.toggle_app(t, l1, l2, n, sv, nl, sl, rf))
        toggle.grid(row=0, column=1, padx=25, pady=18)

    def toggle_app(self, app_type, loc1, loc2, name, switch_var, name_lbl, scope_lbl, row_frame):
        is_on = switch_var.get()
        success = True
        try:
            if app_type == "reg":
                active_path, disabled_path = loc2, loc2 + "_Disabled"
                hkey = loc1
                if is_on:
                    k_dis = winreg.OpenKey(hkey, disabled_path, 0, winreg.KEY_READ)
                    cmd, r_type = winreg.QueryValueEx(k_dis, name)
                    winreg.CloseKey(k_dis)
                    k_act = winreg.OpenKey(hkey, active_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(k_act, name, 0, r_type, cmd)
                    winreg.CloseKey(k_act)
                    k_dw = winreg.OpenKey(hkey, disabled_path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(k_dw, name)
                    winreg.CloseKey(k_dw)
                else:
                    k_act = winreg.OpenKey(hkey, active_path, 0, winreg.KEY_READ)
                    cmd, r_type = winreg.QueryValueEx(k_act, name)
                    winreg.CloseKey(k_act)
                    try: k_dis = winreg.OpenKey(hkey, disabled_path, 0, winreg.KEY_SET_VALUE)
                    except Exception: k_dis = winreg.CreateKey(hkey, disabled_path)
                    winreg.SetValueEx(k_dis, name, 0, r_type, cmd)
                    winreg.CloseKey(k_dis)
                    k_aw = winreg.OpenKey(hkey, active_path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(k_aw, name)
                    winreg.CloseKey(k_aw)
            elif app_type == "folder":
                src = os.path.join(loc2 if is_on else loc1, name)
                dst = os.path.join(loc1 if is_on else loc2, name)
                if os.path.exists(src): shutil.move(src, dst)
            elif app_type == "task":
                task_name = name
                if is_on: subprocess.run(['schtasks', '/change', '/enable', '/tn', task_name], capture_output=True, creationflags=CREATE_NO_WINDOW)
                else: subprocess.run(['schtasks', '/change', '/disable', '/tn', task_name], capture_output=True, creationflags=CREATE_NO_WINDOW)
        except Exception as e:
            success = False
            switch_var.set(not is_on) 
            self.show_toast("⚠ Could not toggle — permission denied.", "#EF4444")

        if success:
            if is_on:
                name_lbl.configure(text_color=self.text_active)
                scope_lbl.configure(text_color=self.subtext_active)
                row_frame.configure(fg_color=self.card_color)
                self.bind_hover(row_frame, self.card_hover, self.card_color)
            else:
                name_lbl.configure(text_color=self.text_disabled)
                scope_lbl.configure(text_color=self.subtext_disabled)
                row_frame.configure(fg_color="#15151A") 
                self.bind_hover(row_frame, "#1A1A20", "#15151A")

    # ==========================================
    # HISTORY VIEWER EMBEDDED UI
    # ==========================================
    def build_history_ui(self):
        self.history_title = ctk.CTkLabel(self.history_frame, text="Cleaning History", font=("Century Gothic", 18, "bold"), text_color="#FFFFFF")
        self.history_title.pack(pady=(10, 25))

        self.history_scroll = ctk.CTkScrollableFrame(self.history_frame, fg_color="transparent", corner_radius=0,
                                                     scrollbar_button_color="#27272A", scrollbar_button_hover_color="#3F3F46")
        self.history_scroll.pack(fill="both", expand=True, pady=5)

        self.btn_clear_history = ctk.CTkButton(self.history_frame, text="Clear History", height=50, corner_radius=self.btn_rad,
                                         fg_color=self.card_color, hover_color=self.card_hover, text_color="#EF4444",
                                         font=("Century Gothic", 13, "bold"), command=self.ui_clear_history)
        self.btn_clear_history.pack(fill="x", pady=(15, 0))

    def refresh_history_ui(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        data = read_history()
        if not data:
            empty_lbl = ctk.CTkLabel(self.history_scroll, text="No cleaning history recorded yet.", font=("Century Gothic", 13), text_color="#8F8F9D")
            empty_lbl.pack(pady=40)
            return

        for entry in reversed(data):
            card = ctk.CTkFrame(self.history_scroll, fg_color=self.card_color, corner_radius=8)
            card.pack(fill="x", pady=6, padx=8)

            dt_lbl = ctk.CTkLabel(card, text=entry.get("timestamp", "Unknown Date"), font=("Century Gothic", 13, "bold"), text_color="#FFFFFF")
            dt_lbl.pack(anchor="w", padx=15, pady=(10, 2))

            stats_str = f"RAM Freed: {entry.get('freed_ram_mb', 0)} MB   |   Temp Freed: {entry.get('freed_temp_mb', 0)} MB"
            stats_lbl = ctk.CTkLabel(card, text=stats_str, font=("Century Gothic", 12), text_color="#10B981")
            stats_lbl.pack(anchor="w", padx=15, pady=(0, 10))

    def ui_clear_history(self):
        clear_history()
        self.refresh_history_ui()

if __name__ == "__main__":
    ensure_single_instance()
    elevate_privileges()
    ctk.set_appearance_mode("dark")
    app = CleanOptimizer()
    app.mainloop()