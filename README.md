# Desktop Declutter

A lightweight, modern Python desktop application built with Tkinter to automatically organize cluttered directories into clean, categorized folders by file type.

---

## Features

* **One-Click Organization:** Automatically scans top-level files in any selected directory and organizes them into categorized folders (Images, Documents, Media, Code, Archives, Installers, and Other).
* **Live Action Console:** Embedded real-time log window displaying detailed file movements and scan summaries.
* **Safety First:** Prevents overwriting duplicate filenames and gracefully skips active system directories.
* **Modern UI:** Built with a clean, flat aesthetic and dedicated options sidebar.

---

## Planned Features & Roadmap

The following features are actively in development:

* [ ] **Delete Empty Folders:** Post-scan cleanup to safely remove empty top-level subdirectories.
* [ ] **Custom Category & Extension Editor:** Profile manager saving custom folder rules and file mappings to `settings.json`.
* [ ] **File Lock Handling:** Graceful error handling for permission-restricted and in-use files (`PermissionError`, `WinError 32`).
* [ ] **Duplicate File Detection:** Byte-level content hashing (MD5/SHA-256) to identify and isolate duplicate files.
* [ ] **Undo Action:** Transaction history logging to reverse the last declutter run and restore original file locations.
* [ ] **Sort by Date:** Optional chronological subfolder sorting based on file creation and modification timestamps.
* [ ] **Background Execution & Progress Bar:** Offloading scan I/O to a background thread with real-time visual progress tracking.

---

## Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** Tkinter
* **File Management:** Standard Library (`os`, `shutil`, `pathlib`)
* **Executable Build:** PyInstaller

---

## Getting Started

### Prerequisites

* Python 3.10+ installed on your system.

### Installation & Local Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/desktop-declutter.git](https://github.com/your-username/desktop-declutter.git)
   cd desktop-declutter
2. **Rune the applicatoin:
   ```bash
   python gui.py

### Project Structure

desktop-declutter/
├── src/
│   ├── cleaner.py      # Core file scanning, categorization, and filesystem movement logic
│   ├── gui.py          # Tkinter UI layout, event loop, and live logging console
│   └── Logo.png        # Application window and taskbar icon
├── .gitignore          # Git ignore file (excludes __pycache__, build artifacts, etc.)
└── README.md           # Project documentation and roadmap
