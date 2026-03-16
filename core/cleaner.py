import os
import shutil
import ctypes
import logging
from ctypes import wintypes
import psutil
import subprocess

from core.system_tools import (
    enable_privilege,
    SYSTEM_MEMORY_LIST_INFORMATION,
    NtSetSystemInformation,
    SystemMemoryListInformation,
    CREATE_NO_WINDOW,
    PROCESS_SET_QUOTA,
    PROCESS_QUERY_INFORMATION,
    MEM_FLUSH_MODIFIED_LIST,
    MEM_FLUSH_STANDBY_LIST,
    MEM_PURGE_STANDBY_LIST
)

def clear_temp_cache():
    """Clears the Windows temporary directory and returns the freed space in MB."""
    temp_dir = os.environ.get('TEMP')
    freed_mb = 0
    if temp_dir and os.path.exists(temp_dir):
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    os.remove(item_path)
                    freed_mb += size / (1024 * 1024)
                elif os.path.isdir(item_path):
                    if os.path.islink(item_path):
                        os.remove(item_path)
                        continue
                    size = 0
                    for root, dirs, files in os.walk(item_path):
                        for f in files:
                            try: 
                                size += os.path.getsize(os.path.join(root, f))
                            except Exception as e: 
                                logging.debug(f'[cleaner] {e}')
                    try:
                        shutil.rmtree(item_path)
                        freed_mb += size / (1024 * 1024)  
                    except Exception as e:
                        logging.debug(f'[cleaner] rmtree failed: {e}')
            except Exception as e: 
                logging.debug(f'[cleaner] {e}')
    return round(freed_mb, 1)

def trim_all_processes():
    """Iterates through all running processes and empties their working set memory."""
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    EmptyWorkingSet = psapi.EmptyWorkingSet
    EmptyWorkingSet.argtypes = [wintypes.HANDLE]
    EmptyWorkingSet.restype = wintypes.BOOL
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            handle = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid) 
            if handle:
                try:
                    EmptyWorkingSet(handle)
                finally:
                    kernel32.CloseHandle(handle)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            logging.debug(f'[cleaner] {e}')

def clear_standby_memory():
    """Uses undocumented Windows APIs to flush standby and modified memory lists."""
    if not enable_privilege("SeDebugPrivilege"):
        logging.warning("Could not acquire SeDebugPrivilege")
    if not enable_privilege("SeProfileSingleProcessPrivilege"):
        logging.warning("Could not acquire SeProfileSingleProcessPrivilege")
    if not enable_privilege("SeIncreaseQuotaPrivilege"):
        logging.warning("Could not acquire SeIncreaseQuotaPrivilege")
    
    info = SYSTEM_MEMORY_LIST_INFORMATION()
    for cmd in [MEM_FLUSH_MODIFIED_LIST, MEM_FLUSH_STANDBY_LIST, MEM_PURGE_STANDBY_LIST]:
        info.MemoryListType = cmd
        NtSetSystemInformation(SystemMemoryListInformation, ctypes.byref(info), ctypes.sizeof(info))

def flush_dns():
    """Flushes the Windows DNS resolver cache."""
    try: 
        subprocess.run(["ipconfig", "/flushdns"], creationflags=CREATE_NO_WINDOW, capture_output=True)
    except Exception as e: 
        logging.debug(f'[cleaner] {e}')