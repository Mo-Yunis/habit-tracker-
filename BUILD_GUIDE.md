# 📦 Packaging Guide: Habit Tracker

This guide explains how to convert your Python code into a standalone executable for **Linux** and **Windows**.

## 🛠️ Prerequisites
You need to install `PyInstaller`, which is the tool that bundles your code and its dependencies into a single file.

```bash
pip install pyinstaller
```

---

## 🐧 Building for Linux (Pop!_OS / Ubuntu)

### 1. Build the binary
Run this command in the project folder:
```bash
pyinstaller --noconsole --onefile --icon=assets/icon.png --name "HabitTracker" main.py
```

### 2. Create a Desktop Icon (Shortcut)
To make the app appear in your Linux application menu:
1. Create a new file called `habit_tracker.desktop` in the project folder.
2. Paste the following (replace `/path/to/your/folder` with the actual path):
```ini
[Desktop Entry]
Name=Habit Tracker
Exec=/path/to/your/folder/dist/HabitTracker
Icon=/path/to/your/folder/assets/icon.png
Type=Application
Terminal=false
Categories=Utility;
```
3. Copy this file to your local applications folder:
```bash
cp habit_tracker.desktop ~/.local/share/applications/
```

---

## 🪟 Building for Windows (.exe)

### Option A: GitHub Actions (Recommended) 🚀
The GitHub Action in `.github/workflows/build.yml` is now updated to build **both** Windows and Linux versions automatically.
1. Push your code to GitHub.
2. Download the binaries from the **Actions** tab.

### Option B: Manual Build on Windows
Run this in PowerShell/CMD:
```powershell
pip install pyinstaller PyQt5 matplotlib
pyinstaller --noconsole --onefile --icon=assets/icon.png --name "HabitTracker" main.py
```

---

## 📝 Troubleshooting & Notes
- **Icon Quality**: For the best look on Windows, convert `icon.png` to `icon.ico`.
- **Wayland (Pop!_OS)**: If the app doesn't start, try: `QT_QPA_PLATFORM=xcb ./dist/HabitTracker`.
- **Executable Size**: The first run might take a few seconds as it unpacks the bundled libraries.
