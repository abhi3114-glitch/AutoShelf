"""
AutoShelf - File Scanner Module
Scans folders and categorizes files by age (last accessed time).
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class ScannedFile:
    """Represents a scanned file with metadata."""
    path: Path
    size: int
    last_accessed: datetime
    last_modified: datetime
    age_days: int
    age_bucket: str


def get_file_age(filepath: Path) -> Tuple[datetime, datetime, int]:
    """
    Get file timestamps and age in days.
    
    Returns:
        Tuple of (last_accessed, last_modified, age_days)
    """
    stat = filepath.stat()
    last_accessed = datetime.fromtimestamp(stat.st_atime)
    last_modified = datetime.fromtimestamp(stat.st_mtime)
    
    # Use last modified time instead of accessed time
    # (Access time is often updated by Windows indexing/thumbnails, keeping files "new")
    age_days = (datetime.now() - last_modified).days
    
    return last_accessed, last_modified, age_days


def get_age_bucket(age_days: int) -> str:
    """Categorize age into buckets."""
    if age_days <= 30:
        return "0-30 days"
    elif age_days <= 60:
        return "31-60 days"
    elif age_days <= 90:
        return "61-90 days"
    else:
        return "90+ days"


def scan_folder(folder_path: Path, recursive: bool = True, extensions: List[str] = None) -> List[ScannedFile]:
    """
    Scan a folder and return list of ScannedFile objects.
    
    Args:
        folder_path: Path to folder to scan
        recursive: Whether to scan subdirectories
        extensions: Optional list of extensions to include (e.g. ['.txt', '.log'])
        
    Returns:
        List of ScannedFile objects
    """
    files = []
    folder_path = Path(folder_path)
    
    # Normalize extensions to lowercase
    if extensions:
        extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
    
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not folder_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")
    
    try:
        if recursive:
            iterator = folder_path.rglob("*")
        else:
            iterator = folder_path.glob("*")
        
        for item in iterator:
            if item.is_file():
                # Check extension filter
                if extensions and item.suffix.lower() not in extensions:
                    continue
                    
                try:
                    last_accessed, last_modified, age_days = get_file_age(item)
                    
                    scanned = ScannedFile(
                        path=item,
                        size=item.stat().st_size,
                        last_accessed=last_accessed,
                        last_modified=last_modified,
                        age_days=age_days,
                        age_bucket=get_age_bucket(age_days)
                    )
                    files.append(scanned)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
    except PermissionError:
        raise PermissionError(f"Permission denied accessing: {folder_path}")
    
    return files


def categorize_files(files: List[ScannedFile]) -> Dict[str, List[ScannedFile]]:
    """
    Group files by age bucket.
    
    Returns:
        Dictionary with bucket names as keys and lists of files as values
    """
    buckets = {
        "0-30 days": [],
        "31-60 days": [],
        "61-90 days": [],
        "90+ days": []
    }
    
    for file in files:
        buckets[file.age_bucket].append(file)
    
    return buckets


def get_bucket_stats(categorized: Dict[str, List[ScannedFile]]) -> Dict[str, Dict]:
    """
    Get statistics for each bucket.
    
    Returns:
        Dictionary with bucket stats (count, total_size)
    """
    stats = {}
    for bucket, files in categorized.items():
        total_size = sum(f.size for f in files)
        stats[bucket] = {
            "count": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    return stats


def filter_old_files(files: List[ScannedFile], min_age_days: int = 30) -> List[ScannedFile]:
    """Filter files older than specified days."""
    return [f for f in files if f.age_days >= min_age_days]
