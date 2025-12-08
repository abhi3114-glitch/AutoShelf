#!/usr/bin/env python3
"""
AutoShelf - Smart Folder Cleaner for Old & Unused Files

A lightweight desktop utility that scans folders, detects old/unused files,
and moves them to an Archive folder with full undo support.

Usage:
    python main.py          # Launch GUI
    python main.py --demo   # Launch with demo folder
"""

import sys
import argparse
from pathlib import Path

# Ensure the project root is in path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AutoShelf - Smart Folder Cleaner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py              Launch the application
    python main.py --demo       Launch with demo folder pre-created
        """
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Create a demo folder with sample files and auto-scan it"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="AutoShelf 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Initialize database
    from database import init_database
    init_database()
    
    if args.demo:
        # Create demo folder before launching
        from demo import create_demo_folder
        print("Creating demo folder...")
        demo_path = create_demo_folder()
        print(f"Demo folder created at: {demo_path}")
    
    # Launch UI
    from ui.app import AutoShelfApp
    
    app = AutoShelfApp()
    
    if args.demo:
        # Auto-populate folder path and scan
        from demo import DEMO_FOLDER
        app.after(100, lambda: _auto_demo(app))
    
    app.mainloop()


def _auto_demo(app):
    """Auto-populate demo folder and scan."""
    from demo import DEMO_FOLDER
    app.folder_entry.delete(0, "end")
    app.folder_entry.insert(0, str(DEMO_FOLDER))
    app.current_folder = DEMO_FOLDER
    app._scan_folder()


if __name__ == "__main__":
    main()
