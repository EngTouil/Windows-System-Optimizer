import psutil
from datetime import datetime
import customtkinter as ctk
from utils.settings import save_settings

class SchedulerUI:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = parent_frame
        
        self.app.auto_clean_var = ctk.BooleanVar(value=self.app.settings.get("auto_clean_startup", False))
        self.app.sched_clean_ram = ctk.BooleanVar(value=self.app.settings.get("sched_clean_ram", True))
        self.app.sched_clean_temp = ctk.BooleanVar(value=self.app.settings.get("sched_clean_temp", True))
        self.app.sched_clean_dns = ctk.BooleanVar(value=self.app.settings.get("sched_clean_dns", True))
        self.app.sched_ram_threshold = ctk.StringVar(value=self.app.settings.get("sched_ram_threshold", "Always clean"))
        self.app.auto_scheduler_interval = ctk.StringVar(value=self.app.settings.get("auto_scheduler_interval", "Every 1 hour"))
        
        self.app._scheduler_after_id = None
        self.app._scheduler_remaining = 0
        
        self.build_ui()
        
        if self.app.auto_clean_var.get():
            self.app.after(1500, self.start_auto_scheduler)

    def build_ui(self):
        """Constructs the Auto-Clean Scheduler UI elements."""
        self.scheduler_title = ctk.CTkLabel(self.frame, text="Auto-Clean Scheduler", font=("Century Gothic", 18, "bold"), text_color="#FFFFFF")
        self.scheduler_title.pack(pady=(10, 25))

        card1 = ctk.CTkFrame(self.frame, fg_color=self.app.card_color, corner_radius=self.app.container_rad)
        card1.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(card1, text="Background Scheduler", font=("Century Gothic", 14, "bold"), text_color="#FFFFFF").grid(row=0, column=0, sticky="w", padx=30, pady=(20, 10))
        self.auto_clean_switch = ctk.CTkSwitch(card1, text="Enabled", variable=self.app.auto_clean_var, 
                                               font=("Century Gothic", 13, "bold"), text_color="#FFFFFF", progress_color=self.app.accent_color,
                                               command=lambda: self.start_auto_scheduler() if self.app.auto_clean_var.get() else self.stop_auto_scheduler())
        self.auto_clean_switch.grid(row=0, column=1, sticky="e", padx=30, pady=(20, 10))

        ctk.CTkLabel(card1, text="Interval", font=("Century Gothic", 13), text_color="#8F8F9D").grid(row=1, column=0, sticky="w", padx=30, pady=10)
        
        ctk.CTkOptionMenu(card1, variable=self.app.auto_scheduler_interval,
                          values=["Every 30 min", "Every 1 hour", "Every 2 hours", "Every 6 hours", "Every 12 hours", "Every 24 hours"],
                          fg_color=self.app.card_hover, button_color=self.app.accent_color, button_hover_color="#4F46E5",
                          font=("Century Gothic", 13), dropdown_font=("Century Gothic", 13)).grid(row=1, column=1, sticky="e", padx=30, pady=10)

        self.scheduler_countdown_lbl = ctk.CTkLabel(card1, text="Scheduler is currently disabled.", font=("Century Gothic", 13), text_color=self.app.accent_color)
        self.scheduler_countdown_lbl.grid(row=2, column=0, columnspan=2, pady=(10, 20))

        card1.grid_columnconfigure(0, weight=1)
        card1.grid_columnconfigure(1, weight=1)

        card2 = ctk.CTkFrame(self.frame, fg_color=self.app.card_color, corner_radius=self.app.container_rad)
        card2.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(card2, text="Cleaning Targets", font=("Century Gothic", 14, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(20, 10))
        
        cb_ram = ctk.CTkCheckBox(card2, text="Clean RAM & Standby Cache", variable=self.app.sched_clean_ram, font=("Century Gothic", 13), text_color="#E4E4E7", fg_color=self.app.accent_color, hover_color="#4F46E5")
        cb_ram.pack(anchor="w", padx=30, pady=8)
        
        cb_temp = ctk.CTkCheckBox(card2, text="Delete Temp Files", variable=self.app.sched_clean_temp, font=("Century Gothic", 13), text_color="#E4E4E7", fg_color=self.app.accent_color, hover_color="#4F46E5")
        cb_temp.pack(anchor="w", padx=30, pady=8)
        
        cb_dns = ctk.CTkCheckBox(card2, text="Flush DNS Cache", variable=self.app.sched_clean_dns, font=("Century Gothic", 13), text_color="#E4E4E7", fg_color=self.app.accent_color, hover_color="#4F46E5")
        cb_dns.pack(anchor="w", padx=30, pady=(8, 20))

        card3 = ctk.CTkFrame(self.frame, fg_color=self.app.card_color, corner_radius=self.app.container_rad)
        card3.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(card3, text="Smart Triggers", font=("Century Gothic", 14, "bold"), text_color="#FFFFFF").grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(card3, text="Only clean when RAM usage is:", font=("Century Gothic", 13), text_color="#8F8F9D").grid(row=1, column=0, sticky="w", padx=30, pady=(0, 20))
        ctk.CTkOptionMenu(card3, variable=self.app.sched_ram_threshold,
                          values=["Always clean", "Above 50%", "Above 60%", "Above 70%", "Above 80%", "Above 90%"],
                          fg_color=self.app.card_hover, button_color=self.app.accent_color, button_hover_color="#4F46E5",
                          font=("Century Gothic", 13), dropdown_font=("Century Gothic", 13)).grid(row=1, column=1, sticky="e", padx=30, pady=(0, 20))
                          
        card3.grid_columnconfigure(0, weight=1)
        card3.grid_columnconfigure(1, weight=1)

        card4 = ctk.CTkFrame(self.frame, fg_color=self.app.card_color, corner_radius=self.app.container_rad)
        card4.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(card4, text="Scheduler Statistics", font=("Century Gothic", 14, "bold"), text_color="#FFFFFF").grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(20, 10))
        
        total_runs = self.app.settings.get("sched_total_runs", 0)
        ctk.CTkLabel(card4, text="Total auto-cleans run:", font=("Century Gothic", 13), text_color="#8F8F9D").grid(row=1, column=0, sticky="w", padx=30, pady=5)
        self.sched_total_runs_lbl = ctk.CTkLabel(card4, text=str(total_runs), font=("Century Gothic", 13, "bold"), text_color="#10B981")
        self.sched_total_runs_lbl.grid(row=1, column=1, sticky="e", padx=30, pady=5)
        
        last_run = self.app.settings.get("sched_last_run", "Never")
        ctk.CTkLabel(card4, text="Last auto-clean:", font=("Century Gothic", 13), text_color="#8F8F9D").grid(row=2, column=0, sticky="w", padx=30, pady=(5, 20))
        self.sched_last_run_lbl = ctk.CTkLabel(card4, text=last_run, font=("Century Gothic", 13, "bold"), text_color="#10B981")
        self.sched_last_run_lbl.grid(row=2, column=1, sticky="e", padx=30, pady=(5, 20))
        
        card4.grid_columnconfigure(0, weight=1)
        card4.grid_columnconfigure(1, weight=1)

    def start_auto_scheduler(self):
        """Calculates the requested interval and begins the scheduling loop."""
        if hasattr(self.app, '_scheduler_after_id') and self.app._scheduler_after_id:
            self.app.after_cancel(self.app._scheduler_after_id)
            self.app._scheduler_after_id = None
        
        interval_map = {
            "Every 30 min": 30 * 60,
            "Every 1 hour": 60 * 60,
            "Every 2 hours": 2 * 60 * 60,
            "Every 6 hours": 6 * 60 * 60,
            "Every 12 hours": 12 * 60 * 60,
            "Every 24 hours": 24 * 60 * 60,
        }
        self.app._scheduler_remaining = interval_map.get(
            self.app.auto_scheduler_interval.get(), 3600)
        self._tick_scheduler()

    def stop_auto_scheduler(self):
        """Halts the scheduling background loop."""
        if hasattr(self.app, '_scheduler_after_id') and self.app._scheduler_after_id:
            self.app.after_cancel(self.app._scheduler_after_id)
            self.app._scheduler_after_id = None
        if hasattr(self, 'scheduler_countdown_lbl'):
            self.scheduler_countdown_lbl.configure(text="Scheduler is currently disabled.")

    def _tick_scheduler(self):
        """Evaluates thresholds, runs clean if applicable, and updates UI countdown timer."""
        if not self.app.auto_clean_var.get():
            if hasattr(self, 'scheduler_countdown_lbl'):
                self.scheduler_countdown_lbl.configure(text="Scheduler is currently disabled.")
            return

        if self.app._scheduler_remaining <= 0:
            threshold_map = {
                "Always clean": 0, "Above 50%": 50, "Above 60%": 60, 
                "Above 70%": 70, "Above 80%": 80, "Above 90%": 90
            }
            threshold = threshold_map.get(self.app.sched_ram_threshold.get(), 0)
            current_ram = psutil.virtual_memory().percent

            if current_ram >= threshold:
                if hasattr(self.app, 'memory_ui'):
                    self.app.memory_ui.run_clean()
                
                runs = self.app.settings.get("sched_total_runs", 0) + 1
                last = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                self.app.settings["sched_total_runs"] = runs
                self.app.settings["sched_last_run"] = last
                
                if hasattr(self, 'sched_total_runs_lbl'):
                    self.sched_total_runs_lbl.configure(text=str(runs))
                    self.sched_last_run_lbl.configure(text=last)
                    
                save_settings(self.app)

            self.start_auto_scheduler()
            return

        mins, secs = divmod(self.app._scheduler_remaining, 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            t = f"Next auto-clean in: {hrs:02d}:{mins:02d}:{secs:02d}"
        else:
            t = f"Next auto-clean in: {mins:02d}:{secs:02d}"
            
        if hasattr(self, 'scheduler_countdown_lbl'):
            self.scheduler_countdown_lbl.configure(text=t)
            
        self.app._scheduler_remaining -= 1
        self.app._scheduler_after_id = self.app.after(1000, self._tick_scheduler)