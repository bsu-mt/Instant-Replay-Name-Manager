# Instant Replay Name Manager (IRNM)

**IRNM** is a lightweight, Python-based desktop application designed to streamline the organization and renaming of video clips, specifically tailored for gamers using NVIDIA Instant Replay (ShadowPlay). It provides a user-friendly GUI to quickly tag, rename, and manage video files without navigating through complex file explorers.

## ✨ Features

  * **📂 Folder Management:** Easily select and remember your game recording directories.
  * **🏷️ Smart Tagging System:**
      * Quickly apply common tags (e.g., `ace`, `clutch`, `4k`) to filenames.
      * **Search & Cycle:** Type to filter tags and use the `Tab` key to cycle through matches.
      * **Custom Tags:** Add new tags on the fly; they are saved automatically for future sessions.
  * **⚡ Batch Formatting:** Automatically converts raw NVIDIA filenames (e.g., `Valorant 2025.11.21 - ...DVR.mp4`) into clean, indexed formats (e.g., `Valorant 2025.11.21 - 1.mp4`).
  * **✂️ Trim Replacement Tool:** A utility to replace an original raw clip with a "Trimmed" version (saved from an external player) with a single click.
  * **🎥 Instant Preview:** Double-click any file to open it in your system's default media player.
  * **⚙️ Persistent Config:** Automatically saves your last accessed folder and custom tags.

## 🛠️ Prerequisites

To run the source code or build the application, you need:

  * **Python 3.x** installed.
  * **Windows** (Recommended for the Batch build script) or macOS/Linux.
  * No external PIP dependencies are required for running the script (uses standard libraries).
  * `pyinstaller` is required only if you wish to build the `.exe`.

## 🚀 Getting Started

### Option 1: Running from Source

1.  Clone or download this repository.
2.  Open a terminal/command prompt in the project folder.
3.  Run the script:
    ```bash
    python irnm.py
    ```

### Option 2: Building the Executable (Windows)

A `build.bat` script is included to compile the application into a standalone `.exe` file.

1.  Ensure Python is added to your system PATH.
2.  Double-click `build.bat`.
3.  The script will automatically:
      * Check for Python.
      * Install/Update `pyinstaller`.
      * Build the executable with the included icon.
      * Clean up temporary build files.
4.  Find your ready-to-use application in the `dist/` folder as `IRMN.exe`.

## 📖 Usage Guide

### 1\. Renaming & Tagging

1.  Click **📂 Select Folder** to load your video directory. Files are sorted by date (newest first).
2.  Select a video from the list.
3.  In the **"Add Tags"** section:
      * Check boxes to add tags to the filename.
      * Use the search bar to find tags. Press `Enter` to add a new tag or `Tab` to autocomplete.
4.  Review the **Filename Preview** at the bottom.
5.  Click **✅ Apply Rename**.

### 2\. Batch Formatting (DVR -\> Index)

If your folder is full of long, messy NVIDIA filenames containing "DVR":

1.  Click the **⚠️ Batch Format** button.
2.  The tool will group files by date and rename them sequentially (e.g., `Game - 1.mp4`, `Game - 2.mp4`).

### 3\. Replacing Trimmed Files

If you edit a video (e.g., `Video.mp4`) in an external player and save the cut as `Video Trim.mp4`:

1.  Click **✂️ Replace Trimmed**.
2.  The tool will delete the original `Video.mp4` and rename `Video Trim.mp4` to `Video.mp4`, keeping your folder clean.

## 📂 Project Structure

```text
IRNM/
├── irnm.py           # Main application source code (Tkinter)
├── build.bat         # Windows batch script to build the EXE
├── icon.ico          # Application icon
├── .gitignore        # Git configuration
└── dist/             # Output folder for the compiled EXE and config
    ├── IRMN.exe      # Compiled Application
    └── config.json   # User settings (auto-generated)
```

## 📝 License

This project is open-source. Feel free to modify and distribute it as needed.
