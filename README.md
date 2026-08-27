# Desktop Declutter

A lightweight, modern Python desktop application built with Tkinter to automatically organize cluttered directories into clean, categorized folders by file type.

---

## Features

* **One-Click Organization:** Automatically scans top-level files in any selected directory and organizes them into categorized folders (Images, Documents, Media, Code, Archives, Installers, and Other).
* **Duplicate File Detection & Removal:** Accurate, byte-level content hashing (MD5) to identify and safely delete duplicate files regardless of differing filenames.
* **Delete Only Mode:** Perform targeted cleanups (e.g., removing duplicates or pruning empty directories) without sorting files into subfolders.
* **Empty Directory Cleanup:** Safely scans and prunes empty top-level directories post-operation.
* **Threaded Background Execution & Progress Bar:** Offloads scan I/O to a background daemon thread with real-time visual progress tracking to prevent UI lockups.
* **Live Action Console:** Embedded real-time log window displaying detailed file movements, skipped items, and operation summaries.
* **Safety First:** Prevents overwriting duplicate filenames and gracefully handles locked or permission-restricted system files.
* **Modern UI:** Built with a clean, flat aesthetic and dedicated options sidebar.

---

## Planned Features & Roadmap

The following features are actively in development:

* [x] **Delete Empty Folders:** Post-scan cleanup to safely remove empty top-level subdirectories.
* [x] **Delete Only Mode:** Bypass category organization to execute targeted deletions and cleanup tasks.
* [x] **Duplicate File Detection:** Byte-level content hashing (MD5) to identify and isolate duplicate files.
* [x] **Background Execution & Progress Bar:** Offloading scan I/O to a background thread with real-time visual progress tracking.
* [ ] **Custom Category & Extension Editor:** Profile manager saving custom folder rules and file mappings to `settings.json`.
* [ ] **File Lock Handling:** Graceful error handling for permission-restricted and in-use files (`PermissionError`, `WinError 32`).
* [ ] **Undo Action:** Transaction history logging to reverse the last declutter run and restore original file locations.
* [ ] **Sort by Date:** Optional chronological subfolder sorting based on file creation and modification timestamps.

---

## Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** Tkinter / ttk
* **Concurrency:** `threading`
* **File Management & Hashing:** Standard Library (`os`, `shutil`, `hashlib`, `pathlib`)
* **Executable Build:** PyInstaller

---

## Getting Started

### Prerequisites

* Python 3.10+ installed on your system.

### Installation & Local Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Tyler-Gushue/desktop-declutter.git](https://github.com/Tyler-Gushue/desktop-declutter.git)
   cd desktop-declutter
2. **Rune the applicatoin:**
   ```bash
   python src/gui.py

### Project Structure
    desktop-declutter/
    ├── src/
    │   ├── cleaner.py      # Core file scanning, categorization, and filesystem movement logic
    │   ├── gui.py          # Tkinter UI layout, event loop, and live logging console
    │   └── Logo.png        # Application window and taskbar icon
    ├── .gitignore          # Git ignore file (excludes __pycache__, build artifacts, etc.)
    └── README.md           # Project documentation and roadmap
