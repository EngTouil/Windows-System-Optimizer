# ⚡ System Optimizer

> A lightweight, fast, and modern Windows system optimization tool built with Python.

![Version](https://img.shields.io/badge/version-2.1-6366F1?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-active-10B981?style=flat-square)
![V3](https://img.shields.io/badge/V3-in%20development-F59E0B?style=flat-square)

---

## What is this?

System Optimizer is a standalone Windows desktop application that helps you free up RAM, clean junk files, manage startup programs, monitor processes, and boost performance with one click. No bloatware. No subscriptions. No nonsense.

Built as a real compiled `.exe` — no Python installation required on the target machine.

---

## Features

| Feature | Description |
|---|---|
| 🧠 **Memory Cleaner** | Trims process working sets, clears standby cache, flushes modified memory lists using Windows API |
| 🗑️ **Disk Cleaner** | Scans and removes junk from Windows Temp, browser caches (Chrome, Edge, Brave, Firefox, Opera, Vivaldi), app caches (Discord, Spotify, Teams, VS Code, Slack, Zoom, Steam and more) |
| 🚀 **Startup Manager** | Scans registry, startup folders and scheduled tasks — safely enable or disable startup entries |
| 📊 **Process Viewer** | Live top-10 memory process list with one-click kill |
| ⏰ **Auto Scheduler** | Schedule automatic cleaning every 30 min / 1h / 2h / 6h / 12h / 24h with smart RAM threshold triggers |
| 🎮 **Game Mode** | Kill background apps, pause Windows Update, set high performance power plan and boost CPU priority in one click |
| 📜 **History** | Full log of every cleaning session with RAM and temp freed |
| 🔔 **System Tray** | Runs in the background with Quick Clean from tray |

---

## Screenshots

> Coming soon

---

## Download

Go to the [Releases](../../releases) page and download the latest `SystemOptimizer.exe`.

- No installation needed
- Just double-click and run
- Requires Windows 10 or later
- Requires Administrator privileges (the app will prompt automatically)

---

## Tech Stack

- **Python** — core language
- **CustomTkinter** — modern UI framework
- **psutil** — process and memory data
- **pystray** — system tray integration
- **Pillow** — tray icon rendering
- **Windows API (ctypes)** — direct memory list manipulation, privilege elevation, DWM glass effect
- **PyInstaller** — compiled to standalone `.exe`

---

## Project Structure

```
app/
├── main.py              # Main window and app entry point
├── core/
│   ├── system_tools.py  # Windows API constants, privilege helpers
│   ├── cleaner.py       # RAM, standby, DNS, temp cleaning logic
│   └── disk_utils.py    # Disk scanning and file-in-use detection
├── ui/
│   ├── memory.py        # Memory tab UI
│   ├── disk.py          # Disk Cleaner tab UI
│   ├── process.py       # Process Viewer tab UI
│   ├── scheduler.py     # Auto Scheduler tab UI
│   └── gamemode.py      # Game Mode tab UI
├── utils/
│   ├── settings.py      # Save/load settings to JSON
│   └── history.py       # Save/load cleaning history to JSON
├── assets/
│   └── icon.ico         # App icon
└── build.bat            # PyInstaller build script
```

---

## Build From Source

**Requirements:**
```
pip install customtkinter psutil pystray Pillow pyinstaller
```

**Build:**
```
build.bat
```

Output will be in `dist/SystemOptimizer.exe`

---

## 🚧 V2 — In Development

V2 is currently being planned and will include:

- [ ] Proper installer with Start Menu shortcut and uninstaller
- [ ] Auto-updater — get new versions automatically
- [ ] Crash reporting — so bugs get fixed faster
- [ ] Code signing certificate — no more SmartScreen warning
- [ ] Unit tests — for a more stable and reliable codebase

---

## Known Limitations

- Windows only — this app uses Windows-specific APIs and will not run on macOS or Linux
- Requires Administrator privileges to perform memory and system operations
- Some antivirus software may flag the exe as a false positive — this is common with PyInstaller compiled apps

---

## License

This project is for personal and educational use.
All rights reserved © 2026

---

## Author

Built by a second-year Engineering student .
Feedback, issues and suggestions are welcome — open an issue or reach out directly.

> ⚡ *If this saved you some RAM, consider leaving a star.*
