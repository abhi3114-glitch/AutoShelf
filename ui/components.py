"""
AutoShelf - UI Components
Reusable styled components for the application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


# Theme colors
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "text": "#eaeaea",
    "text_dim": "#888888",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#F44336",
}


class StyledButton(tk.Button):
    """A styled button with hover effects."""
    
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        # Determine colors based on style
        if style == "primary":
            bg = COLORS["accent"]
            hover = COLORS["accent_hover"]
            fg = "white"
        elif style == "success":
            bg = COLORS["success"]
            hover = "#66BB6A"
            fg = "white"
        elif style == "warning":
            bg = COLORS["warning"]
            hover = "#FFD54F"
            fg = "black"
        elif style == "danger":
            bg = COLORS["error"]
            hover = "#EF5350"
            fg = "white"
        else:  # secondary
            bg = COLORS["bg_light"]
            hover = "#1a4a7a"
            fg = COLORS["text"]
        
        # Handle padding and font overrides
        pad_x = kwargs.pop('padx', 20)
        pad_y = kwargs.pop('pady', 10)
        font_style = kwargs.pop('font', ("Segoe UI", 10, "bold"))
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief="flat",
            font=font_style,
            cursor="hand2",
            padx=pad_x,
            pady=pad_y,
            **kwargs
        )
        
        self.default_bg = bg
        self.hover_bg = hover
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.configure(bg=self.default_bg)


class StatusBar(tk.Frame):
    """A status bar showing current operation status."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_dark"], **kwargs)
        
        self.status_label = tk.Label(
            self,
            text="Ready",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.stats_label = tk.Label(
            self,
            text="",
            bg=COLORS["bg_dark"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9),
            anchor="e"
        )
        self.stats_label.pack(side="right", padx=10, pady=5)
    
    def set_status(self, message: str, status_type: str = "info"):
        """Update status message."""
        color = COLORS["text_dim"]
        if status_type == "success":
            color = COLORS["success"]
        elif status_type == "warning":
            color = COLORS["warning"]
        elif status_type == "error":
            color = COLORS["error"]
        
        self.status_label.configure(text=message, fg=color)
    
    def set_stats(self, message: str):
        """Update stats display."""
        self.stats_label.configure(text=message)


class ProgressDialog(tk.Toplevel):
    """A modal dialog showing operation progress."""
    
    def __init__(self, parent, title="Processing...", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.geometry("400x150")
        self.configure(bg=COLORS["bg_medium"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")
        
        # Message
        self.message_label = tk.Label(
            self,
            text="Please wait...",
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 11)
        )
        self.message_label.pack(pady=20)
        
        # Progress bar
        style = ttk.Style()
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS["bg_dark"],
            background=COLORS["accent"]
        )
        
        self.progress = ttk.Progressbar(
            self,
            style="Custom.Horizontal.TProgressbar",
            length=350,
            mode="indeterminate"
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Details
        self.details_label = tk.Label(
            self,
            text="",
            bg=COLORS["bg_medium"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9)
        )
        self.details_label.pack(pady=5)
    
    def set_message(self, message: str):
        """Update the main message."""
        self.message_label.configure(text=message)
        self.update()
    
    def set_details(self, details: str):
        """Update the details text."""
        self.details_label.configure(text=details)
        self.update()
    
    def set_progress(self, value: int, maximum: int = 100):
        """Set determinate progress."""
        self.progress.stop()
        self.progress.configure(mode="determinate", maximum=maximum, value=value)
        self.update()


class InfoPanel(tk.Frame):
    """A panel showing scan summary information."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_medium"], **kwargs)
        
        self.labels = {}
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create info rows
        self._create_row("folder", "Selected Folder:", "-", 0)
        self._create_row("total", "Total Files:", "-", 1)
        self._create_row("old", "Files to Archive:", "-", 2)
        self._create_row("size", "Total Size:", "-", 3)
    
    def _create_row(self, key: str, label: str, value: str, row: int):
        """Create an info row."""
        lbl = tk.Label(
            self,
            text=label,
            bg=COLORS["bg_medium"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 10),
            anchor="e"
        )
        lbl.grid(row=row, column=0, sticky="e", padx=(10, 5), pady=5)
        
        val = tk.Label(
            self,
            text=value,
            bg=COLORS["bg_medium"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        )
        val.grid(row=row, column=1, sticky="w", padx=(5, 10), pady=5)
        
        self.labels[key] = val
    
    def update_info(self, key: str, value: str):
        """Update an info value."""
        if key in self.labels:
            self.labels[key].configure(text=value)
    
    def clear(self):
        """Reset all values."""
        for key in self.labels:
            self.labels[key].configure(text="-")


def configure_styles():
    """Configure ttk styles for the application."""
    style = ttk.Style()
    
    # Use clam theme as base
    style.theme_use("clam")
    
    # Configure Treeview
    style.configure(
        "Treeview",
        background=COLORS["bg_medium"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["bg_medium"],
        borderwidth=0,
        font=("Segoe UI", 9)
    )
    
    style.configure(
        "Treeview.Heading",
        background=COLORS["bg_light"],
        foreground=COLORS["text"],
        font=("Segoe UI", 9, "bold")
    )
    
    style.map(
        "Treeview",
        background=[("selected", COLORS["accent"])],
        foreground=[("selected", "white")]
    )
    
    # Configure Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["bg_light"],
        troughcolor=COLORS["bg_dark"],
        borderwidth=0,
        arrowsize=14
    )


class SettingsPanel(tk.Frame):
    """A panel for configuring custom scan and archive settings."""
    
    def __init__(self, parent, on_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_medium"], **kwargs)
        self.on_change = on_change
        
        # 1. Age Threshold
        tk.Label(
            self,
            text="Minimum Age (days):",
            bg=COLORS["bg_medium"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10, pady=(10, 2))
        
        self.age_var = tk.StringVar(value="30")
        self.age_entry = tk.Entry(
            self,
            textvariable=self.age_var,
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            width=10
        )
        self.age_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        # 2. File Extensions (Filter)
        tk.Label(
            self,
            text="Extensions (e.g. .txt, .log):",
            bg=COLORS["bg_medium"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10, pady=(5, 2))
        
        # Presets
        preset_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        preset_frame.pack(anchor="w", padx=10, pady=(0, 2))
        
        StyledButton(
            preset_frame, text="Images", 
            command=lambda: self._set_exts(".jpg, .jpeg, .png, .gif, .bmp, .webp"),
            style="secondary", width=6, padx=5, pady=2, font=("Segoe UI", 8)
        ).pack(side="left", padx=(0, 5))
        
        StyledButton(
            preset_frame, text="Videos", 
            command=lambda: self._set_exts(".mp4, .mov, .avi, .mkv, .wmv"),
            style="secondary", width=6, padx=5, pady=2, font=("Segoe UI", 8)
        ).pack(side="left", padx=(0, 5))
        
        StyledButton(
            preset_frame, text="Clear", 
            command=lambda: self._set_exts(""),
            style="secondary", width=6, padx=5, pady=2, font=("Segoe UI", 8)
        ).pack(side="left")
        
        self.ext_var = tk.StringVar()
        self.ext_entry = tk.Entry(
            self,
            textvariable=self.ext_var,
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            width=25
        )
        self.ext_entry.pack(anchor="w", padx=10, pady=(5, 10))
    
        
        # 3. Archive Destination
        tk.Label(
            self,
            text="Archive To:",
            bg=COLORS["bg_medium"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10, pady=(5, 2))
        
        self.path_var = tk.StringVar(value="Default (~/Archive)")
        self.custom_path = None
        
        path_frame = tk.Frame(self, bg=COLORS["bg_medium"])
        path_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.path_entry = tk.Entry(
            path_frame,
            textvariable=self.path_var,
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            state="readonly"
        )
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        StyledButton(
            path_frame,
            text="...",
            command=self._browse_path,
            style="secondary",
            width=2,
            padx=5, 
            pady=2
        ).pack(side="left", padx=(5, 0))
        
    def _browse_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Archive Destination")
        if path:
            self.custom_path = path
            self.path_var.set(path)

    def get_settings(self):
        """Return current settings dict."""
        import re
        try:
            age = int(self.age_var.get())
        except ValueError:
            age = 30
            
        exts = self.ext_var.get().strip()
        if exts:
            # Split by comma or whitespace
            extensions = [e.strip() for e in re.split(r'[,\s]+', exts) if e.strip()]
        else:
            extensions = None
            
        # Remove empty strings and None
        if extensions and not extensions:
            extensions = None
                
        return {
            "min_age": age,
            "extensions": extensions,
            "archive_path": self.custom_path
        }

    def _set_exts(self, exts):
        self.ext_var.set(exts)
