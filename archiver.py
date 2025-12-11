"""
AutoShelf - Archiver Module
Moves old files to archive with logging for undo functionality.
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass

from scanner import ScannedFile
import database as db


# Default archive location
DEFAULT_ARCHIVE_BASE = Path.home() / "Archive"


@dataclass
class ArchiveResult:
    """Result of an archive operation."""
    batch_id: str
    files_moved: int
    files_failed: int
    total_size: int
    archive_path: Path
    errors: List[str]


def get_archive_path(file: ScannedFile, archive_base: Path) -> Path:
    """
    Generate destination path in archive with monthly subfolder.
    
    Example: ~/Archive/2024-12/document.pdf
    """
    month_folder = datetime.now().strftime("%Y-%m")
    return archive_base / month_folder / file.path.name


def ensure_unique_path(dest: Path) -> Path:
    """
    Ensure destination path is unique by adding suffix if needed.
    
    Example: document.pdf -> document_1.pdf -> document_2.pdf
    """
    if not dest.exists():
        return dest
    
    base = dest.stem
    ext = dest.suffix
    parent = dest.parent
    counter = 1
    
    while True:
        new_path = parent / f"{base}_{counter}{ext}"
        if not new_path.exists():
            return new_path
        counter += 1


def archive_files(
    files: List[ScannedFile], 
    archive_base: Path = DEFAULT_ARCHIVE_BASE,
    min_age_days: int = 30
) -> ArchiveResult:
    """
    Archive files older than min_age_days.
    
    
    Args:
        files: List of ScannedFile objects to potentially archive
        archive_base: Base path for archive (default: ~/Archive)
        min_age_days: Minimum age in days to archive (default: 30)
    
    Returns:
        ArchiveResult with operation details
    """
    # Initialize database
    db.init_database()
    
    # Generate batch ID for this operation
    batch_id = db.generate_batch_id()
    
    # Filter files by age
    files_to_archive = [f for f in files if f.age_days >= min_age_days]
    
    moved = 0
    failed = 0
    total_size = 0
    errors = []
    
    # Ensure archive base exists
    archive_base.mkdir(parents=True, exist_ok=True)
    
    for file in files_to_archive:
        try:
            # Generate destination path
            dest = get_archive_path(file, archive_base)
            dest = ensure_unique_path(dest)
            
            # Create parent directories
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(file.path), str(dest))
            
            # Log the movement
            db.log_movement(batch_id, file.path, dest, file.size)
            
            moved += 1
            total_size += file.size
            
        except PermissionError as e:
            errors.append(f"Permission denied: {file.path}")
            failed += 1
        except Exception as e:
            errors.append(f"Error moving {file.path}: {str(e)}")
            failed += 1
    
    return ArchiveResult(
        batch_id=batch_id,
        files_moved=moved,
        files_failed=failed,
        total_size=total_size,
        archive_path=archive_base / datetime.now().strftime("%Y-%m"),
        errors=errors
    )


def undo_last_archive() -> Tuple[bool, str, int]:
    """
    Undo the most recent archive operation.
    
    Returns:
        Tuple of (success, message, files_restored)
    """
    # Get last batch
    last = db.get_last_batch()
    
    if not last:
        return (False, "No archive operations to undo", 0)
    
    batch_id, file_count, timestamp = last
    
    return undo_batch(batch_id)


def undo_batch(batch_id: str) -> Tuple[bool, str, int]:
    """
    Undo a specific batch by ID.
    
    Returns:
        Tuple of (success, message, files_restored)
    """
    movements = db.get_batch_movements(batch_id)
    
    if not movements:
        return (False, f"No movements found for batch {batch_id}", 0)
    
    if movements[0].undone:
        return (False, f"Batch {batch_id} has already been undone", 0)
    
    restored = 0
    errors = []
    
    for movement in movements:
        try:
            dest = Path(movement.dest_path)
            source = Path(movement.source_path)
            
            if not dest.exists():
                errors.append(f"File no longer exists: {dest}")
                continue
            
            # Recreate source directory if needed
            source.parent.mkdir(parents=True, exist_ok=True)
            
            # Move back to original location
            shutil.move(str(dest), str(source))
            restored += 1
            
        except Exception as e:
            errors.append(f"Error restoring {movement.source_path}: {str(e)}")
    
    # Mark batch as undone
    db.mark_batch_undone(batch_id)
    
    # Try to clean up empty archive folders
    try:
        cleanup_empty_archive_folders()
    except:
        pass  # Non-critical
    
    if errors:
        return (True, f"Restored {restored} files with {len(errors)} errors", restored)
    
    return (True, f"Successfully restored {restored} files", restored)


def cleanup_empty_archive_folders(archive_base: Path = DEFAULT_ARCHIVE_BASE) -> int:
    """Remove empty folders in archive directory."""
    removed = 0
    
    if not archive_base.exists():
        return 0
    
    for folder in archive_base.iterdir():
        if folder.is_dir():
            try:
                # Only remove if empty
                if not any(folder.iterdir()):
                    folder.rmdir()
                    removed += 1
            except:
                pass
    
    return removed


def get_archive_info(archive_base: Path = DEFAULT_ARCHIVE_BASE) -> dict:
    """Get information about the archive folder."""
    if not archive_base.exists():
        return {"exists": False, "folders": 0, "files": 0, "total_size": 0}
    
    folders = 0
    files = 0
    total_size = 0
    
    for item in archive_base.rglob("*"):
        if item.is_dir():
            folders += 1
        else:
            files += 1
            try:
                total_size += item.stat().st_size
            except:
                pass
    
    return {
        "exists": True,
        "path": str(archive_base),
        "folders": folders,
        "files": files,
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }
