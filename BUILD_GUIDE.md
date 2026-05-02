# 📦 Packaging Guide: Habit Tracker

This guide explains how to convert your Python code into a standalone executable for **Linux** and **Windows**.

## 🛠️ Prerequisites
You need to install `PyInstaller`, which is the tool that bundles your code and its dependencies into a single file.

```bash
pip install pyinstaller
```

---

## 🐧 Building for Linux (on Pop!_OS)
Since you are already on Linux, this is very straightforward.

### 1. Open your terminal in the project folder
### 2. Run the following command:
```bash
pyinstaller --noconsole --onefile --icon=assets/icon.png --name "HabitTracker" main.py
```

- `--noconsole`: Prevents a black terminal window from opening when you start the app.
- `--onefile`: Bundles everything into a single executable file.
- `--name "HabitTracker"`: Sets the name of your file.

### 3. Find your app
Once finished, you will find the executable inside a new folder called `dist/`. You can double-click it to run it!

---

## 🪟 Building for Windows (.exe)
You have two options for building the Windows version:

### Option A: Automatic Build (GitHub Actions) 🚀
I have created a GitHub Action for you in `.github/workflows/build.yml`. 
1. Push your code to a GitHub repository.
2. Go to the **"Actions"** tab on GitHub.
3. Every time you push code, GitHub will automatically create the Windows `.exe` for you!
4. You can download the result from the "Artifacts" section of the completed run.

### Option B: Manual Build (On a Windows Machine)
**IMPORTANT**: To create a Windows `.exe` manually, you must run these steps on a **Windows** machine.

### 1. Install Python on Windows
Download and install Python from [python.org](https://www.python.org/).

### 2. Install dependencies on Windows
Open **PowerShell** or **Command Prompt** and run:
```powershell
pip install pyinstaller PyQt5 matplotlib
```

### 3. Build the .exe
In the project folder, run:
```powershell
pyinstaller --noconsole --onefile --icon=assets/icon.png --name "HabitTracker" main.py
```

### 4. Find your .exe
Your Windows executable will be in the `dist/` folder.

---

## 📝 Notes
- **Icons**: If you want a custom icon, add `--icon=assets/icon.ico` to the command.
- **Database**: The `habits.db` and `settings.json` files will be created in the same folder as the executable when you run it for the first time.
- **Pop!_OS**: If you encounter issues with "Wayland" on Pop!_OS, you might need to run the app with `QT_QPA_PLATFORM=xcb ./dist/HabitTracker`.
