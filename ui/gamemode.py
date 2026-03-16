import os
import psutil
import subprocess
import threading
import ctypes
import logging
import customtkinter as ctk

from core.system_tools import CREATE_NO_WINDOW, HIGH_PRIORITY_CLASS
from utils.settings import KILLABLE_APPS, save_settings

class GameModeUI:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = parent_frame
        
        self._game_mode_active = False
        self.app._gm_vars = {}
        
        self.build_ui()

    def build_ui(self):
        """Constructs the Game Mode UI elements."""
        ctk.CTkLabel(self.frame, text="🎮",
            font=("Century Gothic", 32), text_color="#FFFFFF").pack(pady=(15, 0))
        ctk.CTkLabel(self.frame, text="Game Mode",
            font=("Century Gothic", 18, "bold"), text_color="#FFFFFF").pack(pady=(2, 4))

        self.gm_status_lbl = ctk.CTkLabel(self.frame, text="● INACTIVE",
            font=("Century Gothic", 13, "bold"), text_color="#4A4A5A")
        self.gm_status_lbl.pack(pady=(0, 15))

        self.gm_toggle_btn = ctk.CTkButton(
            self.frame, text="Activate Game Mode",
            height=55, corner_radius=self.app.btn_rad,
            font=("Century Gothic", 15, "bold"),
            fg_color=self.app.accent_color, hover_color="#4F46E5",
            text_color="#FFFFFF", command=self.toggle_game_mode)
        self.gm_toggle_btn.pack(fill="x", padx=20, pady=(0, 15))

        self._gm_scroll = ctk.CTkScrollableFrame(self.frame, fg_color="transparent",
            corner_radius=0, scrollbar_button_color="#27272A",
            scrollbar_button_hover_color="#3F3F46")
        self._gm_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        local = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')

        def is_installed(path_hint):
            if path_hint is None: return True
            return (os.path.exists(os.path.join(local, path_hint)) or
                    os.path.exists(os.path.join(appdata, path_hint)))

        system_items = [(l, k, e, h) for l, k, e, h in KILLABLE_APPS if not e]
        app_items    = [(l, k, e, h) for l, k, e, h in KILLABLE_APPS if e and is_installed(h)]

        def make_card(parent, title, items):
            card = ctk.CTkFrame(parent, fg_color=self.app.card_color, corner_radius=self.app.container_rad)
            card.pack(fill="x", padx=20, pady=(0, 16))

            ctk.CTkLabel(card, text=title, font=("Century Gothic", 11, "bold"), text_color="#6366F1").pack(anchor="w", padx=22, pady=(16, 8))

            for i, (label, key, exes, hint) in enumerate(items):
                off_by_default = key in ("gm_kill_discord", "gm_kill_spotify")
                default = False if off_by_default else True
                var = ctk.BooleanVar(value=self.app.settings.get(key, default))
                self.app._gm_vars[key] = var

                if i > 0:
                    ctk.CTkFrame(card, height=1, fg_color="#2A2A35").pack(fill="x", padx=22)

                ctk.CTkCheckBox(card, text=label, variable=var,
                    fg_color=self.app.accent_color, hover_color="#4F46E5",
                    font=("Century Gothic", 13), text_color="#E4E4E7",
                    height=42, corner_radius=6
                ).pack(anchor="w", padx=22, pady=(6, 6))

            ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

        make_card(self._gm_scroll, "SYSTEM OPTIMIZATIONS", system_items)
        if app_items:
            make_card(self._gm_scroll, "APPS TO CLOSE", app_items)

        self.gm_log_frame = ctk.CTkScrollableFrame(self._gm_scroll, fg_color=self.app.card_color,
            corner_radius=self.app.container_rad, height=120)
        self.gm_log_frame.pack(fill="x", padx=20, pady=(0, 14))

        self.gm_log_lbl = ctk.CTkLabel(self.gm_log_frame,
            text="Activate Game Mode to see actions taken.",
            font=("Century Gothic", 12), text_color="#8F8F9D",
            justify="left", anchor="w", wraplength=480)
        self.gm_log_lbl.pack(anchor="w", padx=15, pady=10)

    def _gm_get(self, key: str, default: bool = False) -> bool:
        var = self.app._gm_vars.get(key)
        return var.get() if var else default

    def toggle_game_mode(self):
        """Switches the Game Mode state and visually updates the UI."""
        self.gm_toggle_btn.configure(state="disabled")
        if not self._game_mode_active:
            self._game_mode_active = True
            self.gm_toggle_btn.configure(
                text="Deactivate Game Mode",
                fg_color="#EF4444", hover_color="#B91C1C")
            self.gm_status_lbl.configure(text="● ACTIVE", text_color="#10B981")
            threading.Thread(target=self._activate_game_mode, daemon=True).start()
        else:
            self._game_mode_active = False
            self.gm_toggle_btn.configure(
                text="Activate Game Mode",
                fg_color=self.app.accent_color, hover_color="#4F46E5")
            self.gm_status_lbl.configure(text="● INACTIVE", text_color="#4A4A5A")
            threading.Thread(target=self._deactivate_game_mode, daemon=True).start()

    def _activate_game_mode(self):
        """Applies configured optimizations and kills targeted processes on a background thread."""
        log = []

        if self._gm_get("gm_free_ram"):
            if hasattr(self.app, 'memory_ui'):
                self.app.after(0, self.app.memory_ui.run_clean)
            log.append("✅ RAM freed and standby cache cleared")

        kill_targets = []
        for label, key, exes, hint in KILLABLE_APPS:
            if exes and self._gm_get(key):
                kill_targets += exes

        killed = []
        kill_set = {t.lower() for t in kill_targets}
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() in kill_set:
                    proc.terminate()
                    killed.append(proc.info['name'])
            except Exception as e:
                logging.debug(f"[gamemode] {e}")

        if killed:
            unique_killed = list(set(killed))
            log.append(f"✅ Terminated: {', '.join(unique_killed)}")
        else:
            if kill_targets:
                log.append("ℹ️ No background apps were running to kill")

        if self._gm_get("gm_disable_updates"):
            try:
                subprocess.run(["sc", "stop", "wuauserv"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.run(["sc", "config", "wuauserv", "start=disabled"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                log.append("✅ Windows Update service paused")
            except Exception as e:
                log.append(f"⚠️ Could not pause Windows Update: {e}")

        if self._gm_get("gm_high_priority"):
            try:
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                ctypes.windll.kernel32.SetPriorityClass(handle, HIGH_PRIORITY_CLASS)
                log.append("✅ Optimizer CPU priority set to High")
            except Exception as e:
                log.append(f"⚠️ Could not set CPU priority: {e}")

        if self._gm_get("gm_boost_power"):
            try:
                subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                log.append("✅ Power plan set to High Performance")
            except Exception as e:
                log.append(f"⚠️ Could not switch power plan: {e}")

        log_text = "\n".join(log) if log else "Nothing was configured to run."
        self.app.after(0, lambda: self.gm_log_lbl.configure(text=log_text, text_color="#E4E4E7"))
        self.app.after(0, lambda: save_settings(self.app))
        self.app.after(0, lambda: self.gm_toggle_btn.configure(state="normal"))

    def _deactivate_game_mode(self):
        """Restores background services and default power settings on a background thread."""
        log = []

        if self._gm_get("gm_disable_updates"):
            try:
                subprocess.run(["sc", "config", "wuauserv", "start=auto"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.run(["sc", "start", "wuauserv"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                log.append("✅ Windows Update re-enabled")
            except Exception as e:
                log.append(f"⚠️ Could not re-enable Windows Update: {e}")

        if self._gm_get("gm_boost_power"):
            try:
                subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                log.append("✅ Power plan restored to Balanced")
            except Exception as e:
                log.append(f"⚠️ Could not restore power plan: {e}")

        log_text = "Game Mode deactivated.\n" + "\n".join(log)
        self.app.after(0, lambda: self.gm_log_lbl.configure(text=log_text, text_color="#8F8F9D"))
        save_settings(self.app)
        self.app.after(0, lambda: self.gm_toggle_btn.configure(state="normal"))