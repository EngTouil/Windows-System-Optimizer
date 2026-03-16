import sys
import os
import ctypes
import logging
from ctypes import wintypes

# ---------------------------------------------------------
# CONSTANTS & SINGLE INSTANCE ENFORCEMENT
# ---------------------------------------------------------
CREATE_NO_WINDOW = 0x08000000
HIGH_PRIORITY_CLASS = 0x00000080
PROCESS_SET_QUOTA = 0x0100
PROCESS_QUERY_INFORMATION = 0x0400
_MUTEX_HANDLE = None

def ensure_single_instance():
    """Prevents multiple instances of the application from running simultaneously."""
    global _MUTEX_HANDLE
    _MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(None, False, "SystemOptimizerMutex_v1")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        sys.exit(0)

# ---------------------------------------------------------
# ADMIN PRIVILEGE HANDLER
# ---------------------------------------------------------
def is_admin():
    """Checks if the current script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.debug(f"Debug (is_admin): {e}")
        return False

def elevate_privileges():
    """Relaunches the script with Administrator privileges if not already elevated."""
    if not is_admin():
        # Use sys.argv[0] to ensure we relaunch main.py, not this utility file
        script = os.path.abspath(sys.argv[0])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
        except Exception as e:
            logging.debug(f"Debug (elevation failed): {e}")
        sys.exit()

# ---------------------------------------------------------
# WINDOWS API SETUP & PRIVILEGES
# ---------------------------------------------------------
SYSTEM_MEMORY_LIST_COMMAND = 4
MEM_FLUSH_MODIFIED_LIST = 2
MEM_FLUSH_STANDBY_LIST  = 3
MEM_PURGE_STANDBY_LIST  = 4
SystemMemoryListInformation = 80   

class SYSTEM_MEMORY_LIST_INFORMATION(ctypes.Structure):
    _fields_ = [("MemoryListType", wintypes.ULONG)]

ntdll = ctypes.WinDLL('ntdll.dll')
NtSetSystemInformation = ntdll.NtSetSystemInformation
NtSetSystemInformation.argtypes = (wintypes.INT, ctypes.c_void_p, wintypes.ULONG)
NtSetSystemInformation.restype = wintypes.LONG

# --- Token Privilege Structures ---
SE_PRIVILEGE_ENABLED = 0x00000002
TOKEN_ADJUST_PRIVILEGES = 0x00000020
TOKEN_QUERY = 0x00000008

class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD),
                ("HighPart", wintypes.LONG)]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Luid", LUID),
                ("Attributes", wintypes.DWORD)]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [("PrivilegeCount", wintypes.DWORD),
                ("Privileges", LUID_AND_ATTRIBUTES * 1)]

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def enable_privilege(privilege_name):
    """Enables a specific Windows security privilege for the current process."""
    kernel32 = ctypes.windll.kernel32
    advapi32 = ctypes.windll.advapi32

    token = wintypes.HANDLE()
    process = kernel32.GetCurrentProcess()
    
    if not advapi32.OpenProcessToken(process, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token)):
        return False

    luid = LUID()
    if not advapi32.LookupPrivilegeValueW(None, privilege_name, ctypes.byref(luid)):
        return False

    tp = TOKEN_PRIVILEGES()
    tp.PrivilegeCount = 1
    tp.Privileges[0].Luid = luid
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED

    result = advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), ctypes.sizeof(tp), None, None)
    last_error = ctypes.get_last_error()
    kernel32.CloseHandle(token)
    
    if result == 0 or last_error != 0:
        return False
    return True