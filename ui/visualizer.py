"""
AutoShelf - Visualizer Module
Heatmap and bar chart visualization for file age distribution.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple


# Color scheme for age buckets (green -> red gradient)
BUCKET_COLORS = {
    "0-30 days": "#4CAF50",    # Green - recent
    "31-60 days": "#FFC107",   # Yellow - getting old
    "61-90 days": "#FF9800",   # Orange - old
    "90+ days": "#F44336",     # Red - very old
}

BUCKET_ORDER = ["0-30 days", "31-60 days", "61-90 days", "90+ days"]


class AgeHeatmap(tk.Canvas):
    """
    A visual heatmap showing file count per age bucket.
    """
    
    def __init__(self, parent, width=600, height=200, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg="#1e1e1e", highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.data = {bucket: 0 for bucket in BUCKET_ORDER}
        self.draw_empty()
    
    def draw_empty(self):
        """Draw empty placeholder."""
        self.delete("all")
        self.create_text(
            self.width // 2, self.height // 2,
            text="Select a folder to scan",
            fill="#666666",
            font=("Segoe UI", 12)
        )
    
    def update_data(self, bucket_stats: Dict[str, Dict]):
        """
        Update the heatmap with new data.
        
        Args:
            bucket_stats: Dict with bucket names and their stats (count, total_size)
        """
        self.data = {}
        for bucket in BUCKET_ORDER:
            if bucket in bucket_stats:
                self.data[bucket] = bucket_stats[bucket]["count"]
            else:
                self.data[bucket] = 0
        
        self.draw_bars()
    
    def draw_bars(self):
        """Draw horizontal bar chart."""
        self.delete("all")
        
        padding = 20
        label_width = 100
        bar_start = label_width + padding
        max_bar_width = self.width - bar_start - padding
        bar_height = 35
        bar_spacing = 10
        
        # Find max value for scaling
        max_count = max(self.data.values()) if self.data.values() else 1
        if max_count == 0:
            max_count = 1
        
        # Title
        self.create_text(
            self.width // 2, 15,
            text="Files by Age",
            fill="#ffffff",
            font=("Segoe UI", 11, "bold")
        )
        
        y = 40
        total_files = sum(self.data.values())
        
        for bucket in BUCKET_ORDER:
            count = self.data.get(bucket, 0)
            color = BUCKET_COLORS[bucket]
            
            # Label
            self.create_text(
                label_width, y + bar_height // 2,
                text=bucket,
                fill="#ffffff",
                font=("Segoe UI", 10),
                anchor="e"
            )
            
            # Bar background
            self.create_rectangle(
                bar_start, y,
                bar_start + max_bar_width, y + bar_height,
                fill="#2d2d2d",
                outline=""
            )
            
            # Bar fill
            if count > 0:
                bar_width = int((count / max_count) * max_bar_width)
                bar_width = max(bar_width, 5)  # Minimum visible width
                
                self.create_rectangle(
                    bar_start, y,
                    bar_start + bar_width, y + bar_height,
                    fill=color,
                    outline=""
                )
            
            # Count label
            percentage = (count / total_files * 100) if total_files > 0 else 0
            label = f"{count} files ({percentage:.1f}%)"
            self.create_text(
                bar_start + 10, y + bar_height // 2,
                text=label,
                fill="#ffffff",
                font=("Segoe UI", 9),
                anchor="w"
            )
            
            y += bar_height + bar_spacing
        
        # Total
        self.create_text(
            self.width // 2, y + 10,
            text=f"Total: {total_files} files",
            fill="#888888",
            font=("Segoe UI", 10)
        )


class FileListView(tk.Frame):
    """
    A scrollable list view showing scanned files with age indicators.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#1e1e1e", **kwargs)
        
        # Create treeview with scrollbar
        self.tree = ttk.Treeview(
            self,
            columns=("name", "size", "age", "bucket"),
            show="headings",
            selectmode="extended"
        )
        
        # Configure columns
        self.tree.heading("name", text="File Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("age", text="Age (days)")
        self.tree.heading("bucket", text="Category")
        
        self.tree.column("name", width=300)
        self.tree.column("size", width=100)
        self.tree.column("age", width=80)
        self.tree.column("bucket", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Style tags for age buckets
        self.tree.tag_configure("recent", background="#1b3d1b")
        self.tree.tag_configure("medium", background="#3d3d1b")
        self.tree.tag_configure("old", background="#3d2a1b")
        self.tree.tag_configure("very_old", background="#3d1b1b")
    
    def clear(self):
        """Clear all items."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_files(self, files):
        """
        Add files to the list.
        
        Args:
            files: List of ScannedFile objects
        """
        for file in files:
            # Determine tag based on age
            if file.age_days <= 30:
                tag = "recent"
            elif file.age_days <= 60:
                tag = "medium"
            elif file.age_days <= 90:
                tag = "old"
            else:
                tag = "very_old"
            
            # Format size
            size_kb = file.size / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.1f} KB"
            else:
                size_str = f"{size_kb/1024:.1f} MB"
            
            self.tree.insert(
                "", "end",
                values=(file.path.name, size_str, file.age_days, file.age_bucket),
                tags=(tag,)
            )
    
    def get_selected_count(self) -> int:
        """Get number of selected items."""
        return len(self.tree.selection())


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
