import os
import json
from datetime import datetime
import threading
import logging

_history_lock = threading.Lock()

MAX_HISTORY_ENTRIES = 200

def get_history_path():
    """Gets the APPDATA path for saving and loading the cleaning history."""
    appdata = os.environ.get('APPDATA', '')
    dir_path = os.path.join(appdata, 'SystemOptimizer')
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, 'history.json')

def read_history():
    """Reads the cleaning history from the JSON file."""
    filepath = get_history_path()
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        logging.debug(f"Debug (read history): {e}")
        return []

def add_history_entry(ram_mb, temp_mb):
    """Appends a new cleaning record to the history and enforces the maximum entry limit."""
    with _history_lock:
        data = read_history()

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "freed_ram_mb": round(ram_mb, 1),
            "freed_temp_mb": round(temp_mb, 1)
        }
        data.append(entry)
        data = data[-MAX_HISTORY_ENTRIES:]

        filepath = get_history_path()
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logging.debug(f"Debug (write history): {e}")

def clear_history():
    """Wipes all saved cleaning history."""
    with _history_lock:
        filepath = get_history_path()
        try:
            with open(filepath, 'w') as f:
                json.dump([], f)
        except Exception as e:
            logging.debug(f"[history] clear error: {e}")