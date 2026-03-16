import os

_cached_targets = None

def get_disk_targets():
    """Returns a list of tuples containing the name and path of potential junk file locations."""
    global _cached_targets
    if _cached_targets is not None:
        return _cached_targets

    candidates = []
    win = os.environ.get('WINDIR', '')
    local = os.environ.get('LOCALAPPDATA', '')
    appdata = os.environ.get('APPDATA', '')
    temp = os.environ.get('TEMP', '')
    
    candidates.append(("Windows Temp",       os.path.join(win, 'Temp')))
    candidates.append(("User Temp",          temp))
    candidates.append(("Prefetch",           os.path.join(win, 'Prefetch')))
    candidates.append(("Thumbnail Cache",    os.path.join(local, r'Microsoft\Windows\Explorer')))
    candidates.append(("Windows Error Logs", os.path.join(local, r'CrashDumps')))
    
    browsers = [
        ("Chrome Cache",   os.path.join(local, r'Google\Chrome\User Data\Default\Cache\Cache_Data')),
        ("Chrome GPU",     os.path.join(local, r'Google\Chrome\User Data\Default\GPUCache')),
        ("Edge Cache",     os.path.join(local, r'Microsoft\Edge\User Data\Default\Cache\Cache_Data')),
        ("Edge GPU",       os.path.join(local, r'Microsoft\Edge\User Data\Default\GPUCache')),
        ("Brave Cache",    os.path.join(local, r'BraveSoftware\Brave-Browser\User Data\Default\Cache\Cache_Data')),
        ("Opera Cache",    os.path.join(appdata, r'Opera Software\Opera Stable\Cache\Cache_Data')),
        ("Vivaldi Cache",  os.path.join(local, r'Vivaldi\User Data\Default\Cache\Cache_Data')),
        ("Firefox Cache",  os.path.join(local, r'Mozilla\Firefox\Profiles')),
    ]
    for name, path in browsers:
        if os.path.exists(path):
            candidates.append((name, path))
            
    apps = [
        ("Discord Cache",      os.path.join(appdata, r'discord\Cache\Cache_Data')),
        ("Discord GPU",        os.path.join(appdata, r'discord\GPUCache')),
        ("Spotify Cache",      os.path.join(local, r'Spotify\Storage')),
        ("Steam HTML Cache",   os.path.join(local, r'Steam\htmlcache\Cache\Cache_Data')),
        ("Teams Cache",        os.path.join(appdata, r'Microsoft\Teams\Cache\Cache_Data')),
        ("Teams GPU",          os.path.join(appdata, r'Microsoft\Teams\GPUCache')),
        ("VS Code Cache",      os.path.join(appdata, r'Code\Cache\Cache_Data')),
        ("VS Code GPU",        os.path.join(appdata, r'Code\GPUCache')),
        ("Zoom Cache",         os.path.join(appdata, r'Zoom\data')),
        ("WhatsApp Cache",     os.path.join(local, r'WhatsApp\Cache\Cache_Data')),
        ("Slack Cache",        os.path.join(appdata, r'Slack\Cache\Cache_Data')),
        ("Epic Games Cache",   os.path.join(local, r'EpicGamesLauncher\Saved\webcache')),
        ("Battle.net Cache",   os.path.join(local, r'Battle.net\Cache')),
        ("Origin Cache",       os.path.join(local, r'Origin\Cache')),
        ("EA Desktop Cache",   os.path.join(local, r'Electronic Arts\EA Desktop\Cache')),
        ("Ubisoft Cache",      os.path.join(local, r'Ubisoft Game Launcher\cache')),
    ]
    for name, path in apps:
        if os.path.exists(path):
            candidates.append((name, path))
            
    _cached_targets = candidates
    return candidates

def is_file_in_use(filepath: str) -> bool:
    try:
        fd = os.open(filepath, os.O_RDWR)
        os.close(fd)
        return False
    except OSError:
        return True
    except Exception:
        return True