<div align="center">

<img src="https://img.shields.io/badge/System%20Optimizer-v1.0.0--beta-6366F1?style=for-the-badge&logo=windows&logoColor=white" alt="Version"/>

# ⚡ Windows System Optimizer

**A lightweight, fast, and modern Windows system optimization tool — built for real performance gains.**

[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows)](https://github.com/EngTouil/Windows-System-Optimizer)
[![Status](https://img.shields.io/badge/Status-Beta-10B981?style=flat-square)](https://github.com/EngTouil/Windows-System-Optimizer/releases)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/EngTouil/Windows-System-Optimizer?style=flat-square&color=gold)](https://github.com/EngTouil/Windows-System-Optimizer/stargazers)



</div>

---

## 🧭 Overview

**Windows System Optimizer** is a standalone desktop application that gives you direct, low-level control over your Windows system's performance — without the bloat, subscriptions, or misleading promises found in traditional "cleaner" tools.

Engineered for developers, power users, and gamers who want a *real* impact on their machine's speed and responsiveness.

> Built as a single portable `.exe` — no installation, no Python runtime required.

---

## ✨ Features

### 🧠 Memory Controller
Interfaces directly with the Windows API to trim process working sets and flush the standby cache, recovering usable RAM instantly — no reboot required.

### 🗑️ Deep Junk Cleaner
High-accuracy scan engine that hunts down temporary files, browser caches, and app-specific debris from tools like Discord, Spotify, VS Code, and more.

### 🚀 Startup Manager
A clean, transparent interface for managing registry-level startup entries and scheduled tasks — know exactly what runs when your machine boots.

### 🎮 Game Mode
One-click performance boost that terminates background overhead, suspends Windows Update activity, and sets your CPU process to high priority for maximum frame throughput.

### ⏰ Smart Scheduler
Background daemon that automatically triggers optimization sessions based on configurable time intervals or custom RAM usage thresholds.

### 📊 Live Process Monitor
Real-time view of the top memory-consuming processes on your system, with the ability to terminate any of them instantly from within the app.

---

## 📥 Getting Started

1. Navigate to the [**Releases**](../../releases) page.
2. Download the latest **`SystemOptimizer.exe`**.
3. Double-click to launch — it's fully portable, no setup needed.
4. Approve the **Administrator prompt** to enable system-level access.

> **Note:** Administrator privileges are required for memory management and startup control features.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Core Logic | Python 3.10+ |
| UI Framework | CustomTkinter |
| System Access | Windows API via `ctypes` |
| Process Monitoring | `psutil` |
| Tray Integration | `pystray` |
| Distribution | PyInstaller (single `.exe`) |

---

## 📂 Project Structure

```
app/
├── main.py                 # Application entry point
├── core/
│   ├── system_tools.py     # API constants & privilege helpers
│   ├── cleaner.py          # RAM & standby cache optimization
│   └── disk_utils.py       # Deep scan & file detection logic
├── ui/
│   ├── memory.py           # RAM control interface
│   ├── disk.py             # Junk cleaner interface
│   └── gamemode.py         # Performance boost interface
├── utils/
│   ├── settings.py         # JSON-based config management
│   └── history.py          # Session logging & history tracking
└── assets/
    └── icon.ico            # Application icon
```

---

## 🗺️ Roadmap

The core engine is live. Here's what's coming next:

| Feature | Status |
|---|---|
| Dedicated installer with Start Menu integration | ![Planned](https://img.shields.io/badge/Planned-6366F1?style=flat-square) |
| Auto-update system for seamless version management | ![Planned](https://img.shields.io/badge/Planned-6366F1?style=flat-square) |
| Expanded browser support (Firefox, Edge profiles) | ![Planned](https://img.shields.io/badge/Planned-6366F1?style=flat-square) |
| Per-app optimization profiles | ![In%20Progress](https://img.shields.io/badge/In%20Progress-F59E0B?style=flat-square) |
| Dark / Light theme toggle | ![Planned](https://img.shields.io/badge/Planned-6366F1?style=flat-square) |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**Mohammed Touil** — 2nd-Year Engineering Student at **ISGA**

[![GitHub](https://img.shields.io/badge/GitHub-EngTouil-181717?style=flat-square&logo=github)](https://github.com/EngTouil)

Driven by a passion for systems programming and building tools that deliver genuine, measurable results.

---

<div align="center">

**If this tool improved your system's performance, consider leaving a ⭐ — it helps more than you think.**

</div>
