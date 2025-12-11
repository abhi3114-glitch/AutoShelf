"""
AutoShelf - Database Module
SQLite-based logging for file movements to support undo functionality.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass
import uuid


# Database location
DB_DIR = Path.home() / ".autoshelf"
DB_PATH = DB_DIR / "movements.db"


@dataclass
class MovementRecord:
    """Represents a file movement record."""
    id: int
    batch_id: str
    source_path: str
    dest_path: str
    file_size: int
    timestamp: datetime
    undone: bool


def init_database() -> None:
    """Initialize the database and create tables if they don't exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT NOT NULL,
            source_path TEXT NOT NULL,
            dest_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL,
            undone INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_batch_id ON movements(batch_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON movements(timestamp)
    """)
    
    conn.commit()
    conn.close()


def generate_batch_id() -> str:
    """Generate a unique batch ID for an archive operation."""
    return str(uuid.uuid4())[:8]


def log_movement(batch_id: str, source: Path, dest: Path, file_size: int = 0) -> int:
    """
    Log a file movement to the database.
    
    Returns:
        The ID of the inserted record
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO movements (batch_id, source_path, dest_path, file_size, timestamp, undone)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (batch_id, str(source), str(dest), file_size, datetime.now().isoformat()))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def get_batch_movements(batch_id: str) -> List[MovementRecord]:
    """Get all movements for a specific batch."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, batch_id, source_path, dest_path, file_size, timestamp, undone
        FROM movements
        WHERE batch_id = ?
        ORDER BY id DESC
    """, (batch_id,))
    
    records = []
    for row in cursor.fetchall():
        records.append(MovementRecord(
            id=row[0],
            batch_id=row[1],
            source_path=row[2],
            dest_path=row[3],
            file_size=row[4],
            timestamp=datetime.fromisoformat(row[5]),
            undone=bool(row[6])
        ))
    
    conn.close()
    return records


def get_last_batch() -> Optional[Tuple[str, int, datetime]]:
    """
    Get the most recent batch that hasn't been undone.
    
    Returns:
        Tuple of (batch_id, file_count, timestamp) or None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT batch_id, COUNT(*) as file_count, MAX(timestamp) as last_time
        FROM movements
        WHERE undone = 0
        GROUP BY batch_id
        ORDER BY last_time DESC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return (row[0], row[1], datetime.fromisoformat(row[2]))
    return None


def mark_batch_undone(batch_id: str) -> int:
    """
    Mark all movements in a batch as undone.
    
    Returns:
        Number of records updated
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE movements
        SET undone = 1
        WHERE batch_id = ?
    """, (batch_id,))
    
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    return updated


def get_all_batches(limit: int = 10) -> List[Tuple[str, int, datetime, bool]]:
    """
    Get recent batches with summary info.
    
    Returns:
        List of (batch_id, file_count, timestamp, all_undone) tuples
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            batch_id, 
            COUNT(*) as file_count, 
            MAX(timestamp) as last_time,
            MIN(undone) as all_undone
        FROM movements
        GROUP BY batch_id
        ORDER BY last_time DESC
        LIMIT ?
    """, (limit,))
    
    batches = []
    for row in cursor.fetchall():
        batches.append((
            row[0], 
            row[1], 
            datetime.fromisoformat(row[2]),
            bool(row[3])
        ))
    
    conn.close()
    return batches


def clear_old_logs(days: int = 30) -> int:
    """
    Remove log entries older than specified days.
    
    Returns:
        Number of records deleted
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff = datetime.now().isoformat()
    
    cursor.execute("""
        DELETE FROM movements
        WHERE timestamp < datetime(?, '-' || ? || ' days')
        AND undone = 1
    """, (cutoff, days))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted


def get_stats() -> dict:
    """Get database statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM movements")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM movements WHERE undone = 0")
    active = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT batch_id) FROM movements")
    batches = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_records": total,
        "active_movements": active,
        "total_batches": batches
    }
