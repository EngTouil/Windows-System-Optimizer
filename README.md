# ⚡ System Optimizer v1.0.0 (Beta)

> A lightweight, fast, and modern Windows system optimization tool built for high performance.

![Version](https://img.shields.io/badge/version-1.0.0--beta-6366F1?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-initial%20release-10B981?style=flat-square)

---

## 🚀 Welcome to the First Release!

System Optimizer is a standalone Windows desktop application designed to squeeze every bit of performance out of your machine. This is the **initial Beta launch**, focusing on direct memory control, junk file elimination, and automated maintenance—all without the bloat of traditional "cleaner" apps.

Built as a standalone `.exe` — no Python installation required.

---

## ✨ Core Features

| Feature | What's Inside |
|---|---|
| 🧠 **Memory Controller** | Direct Windows API integration to trim process working sets and clear standby cache for instant RAM recovery. |
| 🗑️ **Deep Junk Cleaner** | High-accuracy scanning logic that targets temp files, browser caches, and app-specific data (Discord, Spotify, VS Code, etc.). |
| 🚀 **Startup Manager** | A clean interface to view and manage registry-level startup entries and scheduled tasks. |
| 🎮 **Game Mode** | Instant optimization that kills background overhead, pauses Windows Update, and sets your CPU to high priority. |
| ⏰ **Smart Scheduler** | Background monitoring that triggers cleaning sessions based on custom time intervals or RAM thresholds. |
| 📊 **Live Monitor** | Real-time tracking of the top memory-consuming processes with the ability to kill them instantly. |

---

## 📦 Getting Started

1. Go to the **[Releases](../../releases)** page.
2. Download the latest **`SystemOptimizer.exe`**.
3. Double-click to run (it's 100% portable, no install needed).
4. Accept the **Administrator prompt** so the app can access system-level optimization tools.

---

## 🛠️ Tech Stack

- **Python** — Core logic and automation.
- **CustomTkinter** — For a modern, sleek UI.
- **Windows API (ctypes)** — Direct low-level system manipulation.
- **psutil & pystray** — For system monitoring and tray integration.
- **PyInstaller** — Compiled to a single standalone executable.

---

## 📂 Project Structure

Gemini said
You're totally right—if it's the first release, it should sound like a grand opening, not a repair shop!

Here is the "Fresh Version" of your project README.md. I’ve updated the features to sound like core capabilities and fixed the author section to include ISGA.

Copy and paste this into your project README.md:
Markdown
# ⚡ System Optimizer v1.0.0 (Beta)

> A lightweight, fast, and modern Windows system optimization tool built for high performance.

![Version](https://img.shields.io/badge/version-1.0.0--beta-6366F1?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-initial%20release-10B981?style=flat-square)

---

## 🚀 Welcome to the First Release!

System Optimizer is a standalone Windows desktop application designed to squeeze every bit of performance out of your machine. This is the **initial Beta launch**, focusing on direct memory control, junk file elimination, and automated maintenance—all without the bloat of traditional "cleaner" apps.

Built as a standalone `.exe` — no Python installation required.

---

## ✨ Core Features

| Feature | What's Inside |
|---|---|
| 🧠 **Memory Controller** | Direct Windows API integration to trim process working sets and clear standby cache for instant RAM recovery. |
| 🗑️ **Deep Junk Cleaner** | High-accuracy scanning logic that targets temp files, browser caches, and app-specific data (Discord, Spotify, VS Code, etc.). |
| 🚀 **Startup Manager** | A clean interface to view and manage registry-level startup entries and scheduled tasks. |
| 🎮 **Game Mode** | Instant optimization that kills background overhead, pauses Windows Update, and sets your CPU to high priority. |
| ⏰ **Smart Scheduler** | Background monitoring that triggers cleaning sessions based on custom time intervals or RAM thresholds. |
| 📊 **Live Monitor** | Real-time tracking of the top memory-consuming processes with the ability to kill them instantly. |

---

## 📦 Getting Started

1. Go to the **[Releases](../../releases)** page.
2. Download the latest **`SystemOptimizer.exe`**.
3. Double-click to run (it's 100% portable, no install needed).
4. Accept the **Administrator prompt** so the app can access system-level optimization tools.

---

## 🛠️ Tech Stack

- **Python** — Core logic and automation.
- **CustomTkinter** — For a modern, sleek UI.
- **Windows API (ctypes)** — Direct low-level system manipulation.
- **psutil & pystray** — For system monitoring and tray integration.
- **PyInstaller** — Compiled to a single standalone executable.

---

## 📂 Project Structure

app/
├── main.py              # App entry point
├── core/
│   ├── system_tools.py  # API constants & privilege helpers
│   ├── cleaner.py       # RAM & standby optimization logic
│   └── disk_utils.py    # Deep scanning & file detection
├── ui/
│   ├── memory.py        # RAM control interface
│   ├── disk.py          # Junk cleaner interface
│   └── gamemode.py      # Performance boost interface
├── utils/
│   ├── settings.py      # JSON config management
│   └── history.py       # Logging & session tracking
└── assets/
└── icon.ico         # Visual assets

---

## 🚧 What’s Next (Roadmap)

Now that the core engine is live, I’m working on:
- [ ] A dedicated Installer with Start Menu shortcuts.
- [ ] Auto-update system to keep you on the latest version.
- [ ] Expanded browser support for cleaner profiles.

---

## 👨‍💻 Author

Built by **Mohammed**, a 2nd-year Engineering student at **ISGA**.  
Driven by a passion for system optimization and building tools that actually work.

> ⚡ *If this tool helped your system, feel free to leave a star!*