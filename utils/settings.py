import os
import json
import logging
from typing import NamedTuple, List, Optional

class KillableApp(NamedTuple):
    label: str
    key: str
    executables: List[str]
    install_hint: Optional[str]

KILLABLE_APPS = [
    KillableApp("⚡ Free RAM & Standby Cache", "gm_free_ram",      [],                           None),
    KillableApp("🌐 Kill Chrome",              "gm_kill_chrome",   ["chrome.exe"],               r"Google\Chrome"),
    KillableApp("🌐 Kill Brave",               "gm_kill_brave",    ["brave.exe"],                r"BraveSoftware\Brave-Browser"),
    KillableApp("🌐 Kill Edge",                "gm_kill_edge",     ["msedge.exe"],               r"Microsoft\Edge"),
    KillableApp("🌐 Kill Firefox",             "gm_kill_firefox",  ["firefox.exe"],              r"Mozilla\Firefox"),
    KillableApp("🎵 Kill Spotify",             "gm_kill_spotify",  ["spotify.exe"],              r"Spotify"),
    KillableApp("💬 Kill Discord",             "gm_kill_discord",  ["discord.exe"],              r"discord"),
    KillableApp("🔴 Kill OneDrive",            "gm_kill_onedrive", ["onedrive.exe"],             r"Microsoft\OneDrive"),
    KillableApp("🔴 Kill Teams",               "gm_kill_teams",    ["teams.exe","ms-teams.exe"], r"Microsoft\Teams"),
    KillableApp("🔴 Kill Slack",               "gm_kill_slack",    ["slack.exe"],                r"Slack"),
    KillableApp("🔴 Kill Zoom",                "gm_kill_zoom",     ["zoom.exe"],                 r"Zoom"),
    KillableApp("🔒 Pause Windows Update",     "gm_disable_updates",[],                          None),
    KillableApp("🚀 Set Optimizer CPU Priority High", "gm_high_priority", [],                    None),
    KillableApp("🏆 High Performance Power",   "gm_boost_power",   [],                           None),
]

def get_settings_path():
    """Gets the APPDATA path for saving and loading configurations."""
    appdata = os.environ.get('APPDATA', '')
    dir_path = os.path.join(appdata, 'SystemOptimizer')
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, 'settings.json')

def load_settings():
    """Loads user preferences from the JSON settings file."""
    filepath = get_settings_path()
    defaults = {
        "disk_checkboxes": {},
        "window_pos": None,
        "auto_clean_startup": False,
        "auto_scheduler_enabled": False, 
        "auto_scheduler_interval": "Every 1 hour",
        "sched_clean_ram": True,
        "sched_clean_temp": True,
        "sched_clean_dns": True,
        "sched_ram_threshold": "Always clean",
        "sched_total_runs": 0,
        "sched_last_run": "Never"
    }
    
    off_by_default = {"gm_kill_discord", "gm_kill_spotify"}
    for label, key, exes, hint in KILLABLE_APPS:
        defaults[key] = False if key in off_by_default else True

    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                loaded_settings = json.load(f)
                defaults.update(loaded_settings)
    except Exception as e:
        logging.debug(f"Debug (load settings): {e}")
    return defaults

def save_settings(app):
    """Saves current state and preferences to the JSON settings file."""
    filepath = get_settings_path()
    check_states = {}
    if hasattr(app, 'disk_checkboxes'):
        for var, name, path in app.disk_checkboxes:
            check_states[name] = bool(var.get())

    scheduler_enabled = False
    scheduler_interval = "Every 1 hour"
    if hasattr(app, 'auto_clean_var'):
        scheduler_enabled = app.auto_clean_var.get()
    if hasattr(app, 'auto_scheduler_interval'):
        scheduler_interval = app.auto_scheduler_interval.get()

    settings = {
        "disk_checkboxes": check_states,
        "window_pos": getattr(app, '_cached_geometry', None),
        "auto_clean_startup": app.auto_clean_var.get() if hasattr(app, 'auto_clean_var') else False,
        "auto_scheduler_enabled": scheduler_enabled,
        "auto_scheduler_interval": scheduler_interval,
        "sched_clean_ram": app.sched_clean_ram.get() if hasattr(app, 'sched_clean_ram') else True,
        "sched_clean_temp": app.sched_clean_temp.get() if hasattr(app, 'sched_clean_temp') else True,
        "sched_clean_dns": app.sched_clean_dns.get() if hasattr(app, 'sched_clean_dns') else True,
        "sched_ram_threshold": app.sched_ram_threshold.get() if hasattr(app, 'sched_ram_threshold') else "Always clean",
        "sched_total_runs": app.settings.get("sched_total_runs", 0),
        "sched_last_run": app.settings.get("sched_last_run", "Never")
    }

    if hasattr(app, '_gm_vars'):
        for label, key, exes, hint in KILLABLE_APPS:
            if key in app._gm_vars:
                settings[key] = app._gm_vars[key].get()
            else:
                settings[key] = app.settings.get(key, True)

    try:
        with open(filepath, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logging.debug(f"Debug (save settings): {e}")