"""
AutoShelf - Demo Mode Module
Creates a simulated folder structure with files of various ages for testing.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import random


# Demo folder location
DEMO_FOLDER = Path.home() / "AutoShelf_Demo"


# Sample file contents by type
SAMPLE_CONTENTS = {
    ".txt": "This is a sample text file created by AutoShelf Demo Mode.\nIt contains placeholder text for testing purposes.",
    ".md": "# Sample Markdown\n\nThis is a **demo** file created by AutoShelf.\n\n- Item 1\n- Item 2\n- Item 3",
    ".csv": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago",
    ".json": '{"name": "demo", "type": "autoshelf", "version": "1.0"}',
    ".log": "[INFO] 2024-01-01 12:00:00 - Application started\n[DEBUG] 2024-01-01 12:00:01 - Loading configuration",
    ".html": "<!DOCTYPE html>\n<html>\n<head><title>Demo</title></head>\n<body><h1>AutoShelf Demo</h1></body>\n</html>",
    ".py": '# Demo Python file\n\ndef hello():\n    print("Hello from AutoShelf Demo!")\n\nif __name__ == "__main__":\n    hello()',
    ".css": "body {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}",
    ".js": 'console.log("AutoShelf Demo JS File");\n\nfunction demo() {\n    return "Hello!";\n}',
}

# File names for demo
DEMO_FILES = [
    # Recent files (0-30 days)
    ("recent_notes.txt", 5),
    ("project_draft.md", 10),
    ("meeting_minutes.txt", 15),
    ("budget_2024.csv", 20),
    ("config.json", 25),
    
    # Medium age files (31-60 days)
    ("old_report.txt", 35),
    ("archive_data.csv", 40),
    ("backup_notes.md", 45),
    ("server_logs.log", 50),
    ("legacy_styles.css", 55),
    
    # Older files (61-90 days)
    ("outdated_doc.txt", 65),
    ("ancient_data.csv", 70),
    ("deprecated_script.py", 75),
    ("old_index.html", 80),
    ("vintage_notes.md", 85),
    
    # Very old files (90+ days)
    ("forgotten_file.txt", 100),
    ("dusty_archive.log", 120),
    ("prehistoric_data.csv", 150),
    ("ancient_code.py", 180),
    ("relic_styles.css", 200),
    ("fossil_script.js", 250),
    ("antique_page.html", 300),
]

# Subfolder structure
DEMO_SUBFOLDERS = [
    "Documents",
    "Downloads",
    "Projects",
    "Projects/Old",
    "Backup",
]


def set_file_times(filepath: Path, days_old: int) -> None:
    """Set file access and modification times to simulate age."""
    target_time = datetime.now() - timedelta(days=days_old)
    timestamp = target_time.timestamp()
    
    os.utime(filepath, (timestamp, timestamp))


def create_demo_file(filepath: Path, days_old: int) -> None:
    """Create a demo file with appropriate content and age."""
    ext = filepath.suffix.lower()
    content = SAMPLE_CONTENTS.get(ext, f"Demo file: {filepath.name}\nCreated by AutoShelf")
    
    # Add some size variation
    if random.random() > 0.5:
        content = content * random.randint(1, 10)
    
    filepath.write_text(content, encoding="utf-8")
    set_file_times(filepath, days_old)


def create_demo_folder(base_path: Path = DEMO_FOLDER) -> Path:
    """
    Create a demo folder structure with files of various ages.
    
    Args:
        base_path: Where to create the demo folder
        
    Returns:
        Path to the created demo folder
    """
    # Remove existing demo folder if present
    if base_path.exists():
        import shutil
        shutil.rmtree(base_path)
    
    # Create base folder
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Create subfolders
    for subfolder in DEMO_SUBFOLDERS:
        (base_path / subfolder).mkdir(parents=True, exist_ok=True)
    
    # Create files in root
    for filename, days_old in DEMO_FILES[:5]:
        filepath = base_path / filename
        create_demo_file(filepath, days_old)
    
    # Create files in subfolders
    subfolder_files = DEMO_FILES[5:]
    for i, (filename, days_old) in enumerate(subfolder_files):
        subfolder = DEMO_SUBFOLDERS[i % len(DEMO_SUBFOLDERS)]
        filepath = base_path / subfolder / filename
        create_demo_file(filepath, days_old)
    
    return base_path


def cleanup_demo_folder(base_path: Path = DEMO_FOLDER) -> bool:
    """Remove the demo folder."""
    if base_path.exists():
        import shutil
        shutil.rmtree(base_path)
        return True
    return False


def get_demo_info() -> dict:
    """Get information about the demo folder."""
    if not DEMO_FOLDER.exists():
        return {"exists": False}
    
    file_count = sum(1 for _ in DEMO_FOLDER.rglob("*") if _.is_file())
    folder_count = sum(1 for _ in DEMO_FOLDER.rglob("*") if _.is_dir())
    
    return {
        "exists": True,
        "path": str(DEMO_FOLDER),
        "files": file_count,
        "folders": folder_count
    }


if __name__ == "__main__":
    # Quick test
    print("Creating demo folder...")
    path = create_demo_folder()
    print(f"Demo folder created at: {path}")
    print(f"Info: {get_demo_info()}")
