<div align="center">

# ⏰ Smart Alarm

**A modern, privacy-first, feature-rich Alarm, Stopwatch, Countdown Timer & Clock application.**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![Pygame](https://img.shields.io/badge/Audio-Pygame-green?style=for-the-badge)](https://www.pygame.org)
[![SQLite](https://img.shields.io/badge/Storage-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)]()

[Features](#-features) • [Installation](#-installation) • [Usage](#-how-to-run) • [Architecture](#-project-structure) • [Testing](#-testing) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**Smart Alarm** is a premium, privacy-conscious suite designed to streamline daily scheduling and productivity. Built with modern architecture, it offers both a native **Python Desktop Application** (using CustomTkinter, Pygame, and SQLite) and a lightweight **Web Application** (HTML5, CSS3, ES Modules).

Whether tracking focus sessions with the countdown timer, logging workout splits on the stopwatch, or configuring flexible alarm schedules, Smart Alarm delivers an intuitive, responsive interface with offline sound synthesis and persistent storage.

---

## ✨ Features

### ⏰ Alarm Management
- **Flexible Repeat Schedules**: Once, Every day, Weekdays, Weekends, or Custom Day selection.
- **Duplicate Prevention**: Intelligently prevents creating alarms with matching time and repeat rules.
- **Occurrence Key Tracking**: Guarantees alarms trigger exactly once per scheduled minute without duplicates.
- **Ringing Alert & Snooze**: Full-screen / Top-Level modal alert with animated ringing bell, audio ringtone playback, Snooze (configurable 1–30 min), Dismiss, and Stop actions.

### 🎵 Audio Ringtones & Volume
- **8 Offline Synthesized WAV Tones**: `Classic Bell`, `Digital Alarm`, `Morning Birds`, `Soft Piano`, `Nature`, `Electronic`, `Gentle Chime`, and `Sunrise`.
- **Live Sound Preview**: Test ringtones and master volume levels directly from Settings or the Alarm Editor.

### ⏱ Productivity Tools
- **Live Clock**: Synchronized digital clock with AM/PM (12h/24h), live seconds, full date, and animated canvas analog clock.
- **Precision Stopwatch**: Track elapsed time down to centiseconds with start/pause/resume, reset, and split-lap recording table.
- **Countdown Timer**: Hour, minute, and second controls with start/pause/reset and completion audio notification.

### ⚙ Customization & Storage
- **Appearance Modes**: Dark Mode, Light Mode, and System Theme integration.
- **SQLite Persistence**: Relational storage for user preferences, alarm schedules, and execution history logs.

---

## 🛠 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic and object-oriented architecture |
| **GUI Framework** | CustomTkinter | Modern, hardware-accelerated desktop interface |
| **Audio Engine** | Pygame Mixer | Multi-channel audio playback and volume control |
| **Database** | SQLite3 | Local persistence for alarms, preferences, and history |
| **Testing** | Unittest | Automated unit testing framework |

---

## 📁 Project Structure

```text
Smart-Alarm/
├── src/
│   ├── models/            # Core data models (Alarm, Settings, AlarmHistory)
│   ├── storage/           # SQLite Database Manager (smart_alarm.db)
│   ├── services/          # Business logic (Audio, Scheduler, Stopwatch, Timer)
│   ├── utils/             # Helpers, Logger, and WAV Tone Generator
│   └── gui/               # CustomTkinter UI views, Dialogs & Ringing window
├── tests/                 # Unit test suite
├── assets/
│   ├── audio/             # 8 synthesized WAV ringtones
│   └── icons/             # Graphical UI assets
├── logs/                  # Application runtime logs
├── css/                   # Web interface styling
├── js/                    # Web interface ES modules
├── index.html             # Web entrypoint
├── main.py                # Desktop application entrypoint
├── requirements.txt       # Dependencies (customtkinter, pygame, pillow)
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/) installed on your system.

### 1. Clone Repository
```bash
git clone https://github.com/KiranB-25/Smart-Alarm.git
cd Smart-Alarm
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

---

## 💻 How to Run

### Desktop Application
To launch the native desktop GUI:
```bash
python main.py
```

### Web Application
To serve the static web interface:
```bash
python -m http.server 8080
```
Then open `http://localhost:8080` in your web browser.

---

## 🧪 Testing

Run the automated test suite with Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests
```

---

## 🛡 Key Architecture Principles

1. **Thread Safety**: Background alarm scheduling operates on a dedicated daemon thread. GUI updates are safely dispatched to the main thread via Tkinter's event loop (`root.after()`).
2. **Clean Separation of Concerns**: Decoupled UI widgets, service classes, and data access layers.
3. **Robust Error Handling**: Standardized logger writing events and errors to `logs/app.log`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

Developed with ❤️ by **Kiran Bukhari**

</div>
