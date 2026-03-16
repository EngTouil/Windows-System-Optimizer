import tkinter as tk
import customtkinter as ctk
import psutil
import gc
import threading
import ctypes
import logging

from core.system_tools import MEMORYSTATUSEX
from core.cleaner import (
    clear_temp_cache, 
    trim_all_processes, 
    clear_standby_memory, 
    flush_dns
)
from utils.history import add_history_entry

class MemoryUI:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = parent_frame
        
        self._is_cleaning = False
        self._stats_running = False
        self.freed_temp_mb = 0
        
        self._chart_poly = None
        self._chart_line = None
        
        self.build_ui()
        self.update_stats()

    def build_ui(self):
        """Constructs the Memory Architecture UI elements."""
        self.memory_inner = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.memory_inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85)

        self.header_label = ctk.CTkLabel(self.memory_inner, text="System Architecture", font=("Century Gothic", 18, "bold"), text_color="#FFFFFF")
        self.header_label.pack(pady=(0, 10)) 

        self.ram_val = ctk.CTkLabel(self.memory_inner, text="--%", font=("Century Gothic", 36, "bold"), text_color=self.app.accent_color)
        self.ram_val.pack(pady=(0, 0)) 

        self.ram_subtext = ctk.CTkLabel(self.memory_inner, text="Physical Memory In Use", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.ram_subtext.pack(pady=(0, 20)) 

        self.details_frame = ctk.CTkFrame(self.memory_inner, fg_color=self.app.card_color, corner_radius=self.app.container_rad)
        self.details_frame.pack(fill="x", pady=5) 

        self.cache_label = ctk.CTkLabel(self.details_frame, text="Standby Cache", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.cache_label.grid(row=0, column=0, sticky="w", padx=30, pady=(15, 8)) 
        self.cache_val = ctk.CTkLabel(self.details_frame, text="-- MB", font=("Century Gothic", 18, "bold"), text_color="#E4E4E7")
        self.cache_val.grid(row=0, column=1, sticky="e", padx=30, pady=(15, 8))

        self.page_label = ctk.CTkLabel(self.details_frame, text="Page File Used", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.page_label.grid(row=1, column=0, sticky="w", padx=30, pady=8)
        self.page_val = ctk.CTkLabel(self.details_frame, text="-- GB", font=("Century Gothic", 18, "bold"), text_color="#E4E4E7")
        self.page_val.grid(row=1, column=1, sticky="e", padx=30, pady=8)

        self.cpu_label = ctk.CTkLabel(self.details_frame, text="CPU Load", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.cpu_label.grid(row=2, column=0, sticky="w", padx=30, pady=8)
        self.cpu_val = ctk.CTkLabel(self.details_frame, text="-- %", font=("Century Gothic", 18, "bold"), text_color="#E4E4E7")
        self.cpu_val.grid(row=2, column=1, sticky="e", padx=30, pady=8)

        self.avail_label = ctk.CTkLabel(self.details_frame, text="Available RAM", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.avail_label.grid(row=3, column=0, sticky="w", padx=30, pady=(8, 15)) 
        self.avail_val = ctk.CTkLabel(self.details_frame, text="-- GB", font=("Century Gothic", 18, "bold"), text_color="#10B981") 
        self.avail_val.grid(row=3, column=1, sticky="e", padx=30, pady=(8, 15))

        self.details_frame.grid_columnconfigure(0, weight=1)
        self.details_frame.grid_columnconfigure(1, weight=1)

        self.chart_canvas = tk.Canvas(self.memory_inner, height=80, bg=self.app.bg_color, highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=(15, 5))

        self.progress_bar = ctk.CTkProgressBar(self.memory_inner, height=6, corner_radius=3, fg_color=self.app.bg_color, progress_color=self.app.accent_color)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(15, 15)) 

        self.clean_button = ctk.CTkButton(self.memory_inner, text="Execute Deep Clean", 
                                          command=self.run_clean,
                                          width=250, height=45, corner_radius=self.app.btn_rad, 
                                          font=("Century Gothic", 16, "bold"),
                                          fg_color=self.app.accent_color, text_color="#FFFFFF", 
                                          hover_color="#4F46E5")
        self.clean_button.pack(pady=(0, 10)) 

        self.status_label = ctk.CTkLabel(self.memory_inner, text="System memory mapped.", font=("Century Gothic", 13), text_color="#8F8F9D")
        self.status_label.pack(pady=(5, 0))

    def update_stats(self):
        """Fetches memory statistics on a background thread and updates the UI."""
        if self._stats_running: return
        self._stats_running = True

        def worker():
            try:
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                cpu = psutil.cpu_percent(interval=0.1)
                
                statEx = MEMORYSTATUSEX()
                statEx.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(statEx))
                
                total_ram  = statEx.ullTotalPhys
                avail_ram  = statEx.ullAvailPhys
                free_ram   = mem.free
                standby_bytes = max(0, avail_ram - free_ram)
                
                self._stat_ram_pct    = mem.percent
                self._stat_standby_mb = standby_bytes / (1024 * 1024)
                self._stat_swap_gb    = swap.used / (1024 ** 3)
                self._stat_cpu_pct    = cpu
                self._stat_avail_gb   = avail_ram / (1024 ** 3)

                self.app.after(0, self._apply_stats)
            except Exception as e:
                logging.debug(f"[memory] update_stats: {e}")
            finally:
                self._stats_running = False
                self.app.after(2500, self.update_stats)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_stats(self):
        """Applies the fetched memory statistics to the UI elements."""
        if hasattr(self, '_stat_ram_pct'):
            self.ram_val.configure(text=f"{self._stat_ram_pct:.1f}%")
            self.cache_val.configure(text=f"{self._stat_standby_mb:.0f} MB")
            self.page_val.configure(text=f"{self._stat_swap_gb:.2f} GB")
            self.cpu_val.configure(text=f"{self._stat_cpu_pct:.1f} %")
            self.avail_val.configure(text=f"{self._stat_avail_gb:.2f} GB")
            
            self.app.ram_history.append(self._stat_ram_pct)
            self.update_chart()

    def update_chart(self):
        """Redraws the animated RAM usage chart."""
        try:
            width = self.chart_canvas.winfo_width()
            height = self.chart_canvas.winfo_height()
            if width <= 1: width = 500  
            if height <= 1: height = 80
        except Exception as e:
            return

        max_val = 100
        points = []
        history = list(self.app.ram_history)
        x_step = width / max(1, len(history) - 1)
        
        for i, val in enumerate(history):
            x = i * x_step
            y = (height - 2) - ((val / max_val) * (height - 4))
            points.append(x)
            points.append(y)
            
        if len(points) >= 4:
            poly_points = list(points)
            poly_points.extend([width, height, 0, height])
            
            dimmed_accent = "#1F2040"  
            
            if self._chart_poly is None:
                self._chart_poly = self.chart_canvas.create_polygon(poly_points, fill=dimmed_accent, outline="")
                self._chart_line = self.chart_canvas.create_line(points, fill=self.app.accent_color, width=2)
            else:
                self.chart_canvas.coords(self._chart_poly, poly_points)
                self.chart_canvas.coords(self._chart_line, points)

    def animate_progress(self, start, target, duration=0.2, callback=None):
        """Smoothly animates the UI progress bar."""
        steps = 20
        delay_ms = int((duration / steps) * 1000)
        increment = (target - start) / steps

        def step_animation(current_step, current_val):
            if current_step < steps:
                current_val += increment
                self.progress_bar.set(current_val)
                self.app.after(delay_ms, step_animation, current_step + 1, current_val)
            else:
                self.progress_bar.set(target)
                if callback: callback()
                    
        self.app.after(0, step_animation, 0, start)

    def run_clean(self):
        """Triggers the primary system cleaning sequence on a background thread."""
        if self._is_cleaning: return
        self._is_cleaning = True
        
        self.clean_button.configure(state="disabled", text="Purging System...", fg_color=self.app.card_color, text_color="#8F8F9D")
        self.status_label.configure(text="Trimming all process working sets...", text_color=self.app.accent_color)
        threading.Thread(target=self._clean_process, daemon=True).start()

    def _clean_process(self):
        """Executes the multi-stage system cleaning logic and UI progress updates."""
        before_mem = psutil.virtual_memory().available
        self.freed_temp_mb = 0 

        def finish_clean():
            after_mem = psutil.virtual_memory().available
            freed_ram_mb = max(0, (after_mem - before_mem) / (1024 * 1024))
            
            self.status_label.configure(text=f"Massive Purge Complete: Freed {freed_ram_mb:.0f}MB RAM & {self.freed_temp_mb}MB Temp.", text_color="#10B981")
            self.clean_button.configure(state="normal", text="Execute Deep Clean", fg_color=self.app.accent_color, text_color="#FFFFFF")
            self.progress_bar.set(0)
            add_history_entry(freed_ram_mb, self.freed_temp_mb)
            self._is_cleaning = False

        def _run_step(work_fn, anim_start, anim_end, duration, next_fn):
            work_done = threading.Event()
            def worker():
                work_fn()
                work_done.set()
            def check_fn():
                if work_done.is_set():
                    if next_fn: next_fn()
                else: self.app.after(50, check_fn)
            threading.Thread(target=worker, daemon=True).start()
            self.animate_progress(anim_start, anim_end, duration=duration, callback=check_fn)

        def step4():
            self.status_label.configure(text="Flushing DNS cache...")
            _run_step(flush_dns, 0.8, 1.0, 0.2, finish_clean)

        def step3():
            self.status_label.configure(text="Clearing temporary files...")
            def clean_temp():
                self.freed_temp_mb = clear_temp_cache()
                gc.collect()
            _run_step(clean_temp, 0.6, 0.8, 0.3, step4)

        def step2():
            self.status_label.configure(text="Releasing standby & modified lists...")
            _run_step(clear_standby_memory, 0.3, 0.6, 0.3, step3)

        _run_step(trim_all_processes, 0.0, 0.3, 0.3, step2)