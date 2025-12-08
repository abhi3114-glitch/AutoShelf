# AutoShelf 📂

**AutoShelf** is a smart desktop utility designed to keep your folders clean and organized. It scans for old, unused files and safely moves them to an organized archive, keeping your active workspace clutter-free.

Unlike standard cleaners, AutoShelf is **non-destructive** (files are moved, not deleted) and offers **full undo capability**.

## ✨ Features

- **Smart Scanning**: identifies files based on their last modification date.
- **Visual Insights**: Color-coded heatmap shows the age distribution of your files at a glance.
- **Safe Archiving**: Moves files to a designated Archive folder, organized by `YYYY-MM`.
- **Undo Capability**: Made a mistake? One click restores all files from the last batch to their original locations.
- **Custom Filters**:
  - **Age Threshold**: Choose any number of days (e.g., 30, 45, 120).
  - **File Extensions**: Filter by specific types (e.g., `.log`, `.tmp`) or use built-in **presets** for Images and Videos.
- **Custom Destination**: Choose exactly where you want your archived files to go.
- **Dark Mode UI**: A modern, eye-friendly interface built with Tkinter.

## 🚀 Installation

### Option 1: Standalone Executable (Windows)
Simply download and run `AutoShelf.exe`. No Python installation required.

### Option 2: Run from Source
1. **Clone the repository**:
   ```bash
   git clone https://github.com/abhi3114-glitch/AutoShelf.git
   cd AutoShelf
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: AutoShelf uses only standard library components plus `watchdog` for future features, so dependencies are minimal.)*
3. **Run the app**:
   ```bash
   python main.py
   ```

## 📖 Usage Guide

1. **Select a Folder**:
   - Click **Browse** to choose the folder you want to clean.
   - Or click **Demo Mode** to generate a dummy folder with fake files for testing.

2. **Configure Settings (Optional)**:
   - **Minimum Age**: Set how old a file must be to be archived (default: 30 days).
   - **Extensions**: Enter specific extensions (e.g., `.jpg, .png`) or click the **Images/Videos** buttons.
   - **Archive To**: Choose a custom destination folder.

3. **Scan**:
   - Click **Scan**. The heatmap will show you how many old files you have (Red = Old, Green = New).

4. **Archive**:
   - Click **Archive Unused Files**.
   - Review the confirmation dialog.
   - Files will be moved to your Archive folder (e.g., `~/Archive/2025-12/`).

5. **Undo**:
   - If you change your mind, immediately click **Undo Last Archive** to restore everything.

## 🛠️ Technical Details

- **Language**: Python 3.10+
- **GUI Framework**: Tkinter (Native)
- **Database**: SQLite (for tracking file movements)
- **Age Logic**: Uses `st_mtime` (Last Modified Time) to avoid issues with Windows updating Access Time during thumbnail generation.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
