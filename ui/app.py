"""
AutoShelf - Main Application UI
The primary Tkinter application window.
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner import scan_folder, categorize_files, get_bucket_stats, filter_old_files
from archiver import archive_files, undo_last_archive, get_archive_info
from database import init_database, get_last_batch, get_stats as get_db_stats
from demo import create_demo_folder, DEMO_FOLDER, get_demo_info
from ui.visualizer import AgeHeatmap, FileListView, format_size
from ui.components import (
    StyledButton, StatusBar, ProgressDialog, InfoPanel, SettingsPanel,
    configure_styles, COLORS
)


class AutoShelfApp(tk.Tk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("AutoShelf - Smart Folder Cleaner")
        self.geometry("900x700")
        self.configure(bg=COLORS["bg_dark"])
        self.minsize(800, 600)
        
        # State
        self.current_folder = None
        self.scanned_files = []
        self.categorized = {}
        
        # Initialize database
        init_database()
        
        # Configure styles
        configure_styles()
        
        # Build UI
        self._create_header()
        self._create_main_content()
        self._create_footer()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_header(self):
        """Create header with title and folder selection."""
        header = tk.Frame(self, bg=COLORS["bg_medium"])
        header.pack(fill="x", padx=0, pady=0)
        
        # Title
        title_frame = tk.Frame(header, bg=COLORS["bg_medium"])
        title_frame.pack(fill="x", padx=20, pady=15)
        
        tk.Label(
            title_frame,
            text="📁 AutoShelf",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 20, "bold")
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text="Smart Folder Cleaner",
            bg=COLORS["bg_medium"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 12)
        ).pack(side="left", padx=10)
        
        # Folder selection
        folder_frame = tk.Frame(header, bg=COLORS["bg_medium"])
        folder_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.folder_entry = tk.Entry(
            folder_frame,
            font=("Segoe UI", 11),
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            width=50
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.folder_entry.insert(0, "Select a folder to scan...")
        
        StyledButton(
            folder_frame,
            text="Browse",
            command=self._browse_folder,
            style="secondary"
        ).pack(side="left", padx=(0, 5))
        
        StyledButton(
            folder_frame,
            text="Scan",
            command=self._scan_folder,
            style="primary"
        ).pack(side="left", padx=(0, 5))
        
        StyledButton(
            folder_frame,
            text="Demo Mode",
            command=self._start_demo,
            style="warning"
        ).pack(side="left")
    
    def _create_main_content(self):
        """Create main content area with visualization and file list."""
        main = tk.Frame(self, bg=COLORS["bg_dark"])
        main.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Info and actions
        left_panel = tk.Frame(main, bg=COLORS["bg_dark"], width=250)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Info panel
        tk.Label(
            left_panel,
            text="Scan Summary",
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        self.info_panel = InfoPanel(left_panel)
        self.info_panel.pack(fill="x", pady=(0, 20))
        
        # Archive settings
        tk.Label(
            left_panel,
            text="Archive Settings",
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(10, 10))
        
        # Settings Panel
        self.settings = SettingsPanel(left_panel)
        self.settings.pack(fill="x", pady=(0, 20))
        
        # Action buttons
        tk.Label(
            left_panel,
            text="Actions",
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(20, 10))
        
        StyledButton(
            left_panel,
            text="🗂️ Archive Unused Files",
            command=self._archive_files,
            style="success"
        ).pack(fill="x", pady=5)
        
        StyledButton(
            left_panel,
            text="↩️ Undo Last Archive",
            command=self._undo_archive,
            style="danger"
        ).pack(fill="x", pady=5)
        
        # Right panel - Visualization and file list
        right_panel = tk.Frame(main, bg=COLORS["bg_dark"])
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Heatmap
        self.heatmap = AgeHeatmap(right_panel, width=600, height=200)
        self.heatmap.pack(fill="x", pady=(0, 10))
        
        # File list
        tk.Label(
            right_panel,
            text="Scanned Files",
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.file_list = FileListView(right_panel)
        self.file_list.pack(fill="both", expand=True)
    
    def _create_footer(self):
        """Create footer with status bar."""
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom")
    
    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Folder to Scan",
            initialdir=str(Path.home())
        )
        
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.current_folder = Path(folder)
    
    def _start_demo(self):
        """Create and scan demo folder."""
        self.status_bar.set_status("Creating demo folder...", "info")
        self.update()
        
        try:
            demo_path = create_demo_folder()
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, str(demo_path))
            self.current_folder = demo_path
            
            self.status_bar.set_status(f"Demo folder created at {demo_path}", "success")
            
            # Auto-scan
            self._scan_folder()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create demo folder:\n{str(e)}")
            self.status_bar.set_status("Demo creation failed", "error")
    
    def _scan_folder(self):
        """Scan the selected folder."""
        folder_path = self.folder_entry.get()
        
        if not folder_path or folder_path == "Select a folder to scan...":
            messagebox.showwarning("No Folder", "Please select a folder to scan first.")
            return
        
        folder = Path(folder_path)
        
        if not folder.exists():
            messagebox.showerror("Error", f"Folder not found: {folder}")
            return
        
        # Show progress
        progress = ProgressDialog(self, "Scanning Folder")
        progress.set_message(f"Scanning {folder.name}...")
        
        try:
            # Get settings
            settings = self.settings.get_settings()
            min_age = settings["min_age"]
            extensions = settings["extensions"]
            
            # Scan folder with extensions
            self.scanned_files = scan_folder(folder, extensions=extensions)
            self.categorized = categorize_files(self.scanned_files)
            bucket_stats = get_bucket_stats(self.categorized)
            
            # Update UI
            self.heatmap.update_data(bucket_stats)
            
            self.file_list.clear()
            self.file_list.add_files(self.scanned_files)
            
            # Update info panel
            total_files = len(self.scanned_files)
            old_files = filter_old_files(self.scanned_files, min_age)
            total_size = sum(f.size for f in self.scanned_files)
            
            self.info_panel.update_info("folder", folder.name)
            self.info_panel.update_info("total", str(total_files))
            self.info_panel.update_info("old", f"{len(old_files)} (>{min_age} days)")
            self.info_panel.update_info("size", format_size(total_size))
            
            self.current_folder = folder
            self.status_bar.set_status(f"Scanned {total_files} files", "success")
            
            # Update stats with archive path info
            archive_path = settings["archive_path"] if settings["archive_path"] else Path.home() / "Archive"
            archive_path = Path(archive_path)
            self.status_bar.set_stats(f"Archive: {get_archive_info(archive_path)['files']} files")
            
        except Exception as e:
            messagebox.showerror("Scan Error", f"Failed to scan folder:\n{str(e)}")
            self.status_bar.set_status("Scan failed", "error")
        
        finally:
            progress.destroy()
    
    def _archive_files(self):
        """Archive old files."""
        if not self.scanned_files:
            messagebox.showwarning("No Files", "Please scan a folder first.")
            return
        
        settings = self.settings.get_settings()
        min_age = settings["min_age"]
        custom_path = settings["archive_path"]
        
        old_files = filter_old_files(self.scanned_files, min_age)
        
        if not old_files:
            messagebox.showinfo("No Old Files", f"No files older than {min_age} days found.")
            return
        
        # Confirm
        total_size = sum(f.size for f in old_files)
        dest_display = custom_path if custom_path else f"~/Archive/{Path.home().name}"
        
        confirm = messagebox.askyesno(
            "Confirm Archive",
            f"Archive {len(old_files)} files ({format_size(total_size)}) older than {min_age} days?\n\n"
            f"Destination: {dest_display}"
        )
        
        if not confirm:
            return
        
        # Show progress
        progress = ProgressDialog(self, "Archiving Files")
        progress.set_message(f"Moving {len(old_files)} files...")
        
        try:
            # Prepare args
            kwargs = {"min_age_days": min_age}
            if custom_path:
                kwargs["archive_base"] = Path(custom_path)
            
            result = archive_files(self.scanned_files, **kwargs)
            
            progress.destroy()
            
            if result.files_moved > 0:
                messagebox.showinfo(
                    "Archive Complete",
                    f"Moved {result.files_moved} files to:\n{result.archive_path}\n\n"
                    f"Total size: {format_size(result.total_size)}\n\n"
                    f"Batch ID: {result.batch_id} (for undo)"
                )
                
                self.status_bar.set_status(
                    f"Archived {result.files_moved} files (Batch: {result.batch_id})", 
                    "success"
                )
                
                # Rescan
                self._scan_folder()
            else:
                messagebox.showwarning("No Files Moved", "No files were archived.")
            
            if result.errors:
                messagebox.showwarning(
                    "Archive Warnings",
                    f"Some files could not be moved:\n\n" + "\n".join(result.errors[:5])
                )
                
        except Exception as e:
            progress.destroy()
            messagebox.showerror("Archive Error", f"Failed to archive files:\n{str(e)}")
            self.status_bar.set_status("Archive failed", "error")
    
    def _undo_archive(self):
        """Undo the last archive operation."""
        last = get_last_batch()
        
        if not last:
            messagebox.showinfo("Nothing to Undo", "No archive operations to undo.")
            return
        
        batch_id, file_count, timestamp = last
        
        confirm = messagebox.askyesno(
            "Confirm Undo",
            f"Undo the last archive operation?\n\n"
            f"Batch ID: {batch_id}\n"
            f"Files: {file_count}\n"
            f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if not confirm:
            return
        
        progress = ProgressDialog(self, "Undoing Archive")
        progress.set_message(f"Restoring {file_count} files...")
        
        try:
            success, message, restored = undo_last_archive()
            
            progress.destroy()
            
            if success:
                messagebox.showinfo("Undo Complete", message)
                self.status_bar.set_status(message, "success")
                
                # Rescan if folder is set
                if self.current_folder and self.current_folder.exists():
                    self._scan_folder()
            else:
                messagebox.showwarning("Undo Failed", message)
                self.status_bar.set_status(message, "warning")
                
        except Exception as e:
            progress.destroy()
            messagebox.showerror("Undo Error", f"Failed to undo:\n{str(e)}")
            self.status_bar.set_status("Undo failed", "error")


def run_app():
    """Run the AutoShelf application."""
    app = AutoShelfApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
