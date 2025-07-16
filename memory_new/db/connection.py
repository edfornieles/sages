"""
Database connection management for memory system.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def get_memory_db_path(character_id: str, user_id: str) -> Path:
    """Get the database path for a specific character-user combination."""
    memories_dir = Path("memories")
    memories_dir.mkdir(exist_ok=True)
    return memories_dir / f"{character_id}_{user_id}_memory.db"


def create_connection(db_path: Path) -> sqlite3.Connection:
    """Create a new database connection."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        raise


def close_connection(conn: sqlite3.Connection) -> None:
    """Close a database connection."""
    try:
        if conn:
            conn.close()
    except Exception as e:
        logger.error(f"Failed to close database connection: {e}")


@contextmanager
def get_connection(db_path: Path):
    """Context manager for database connections."""
    conn = None
    try:
        conn = create_connection(db_path)
        yield conn
    finally:
        close_connection(conn)


def ensure_database_exists(db_path: Path) -> bool:
    """Ensure the database file exists and is accessible."""
    try:
        # Create parent directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Test connection
        with get_connection(db_path) as conn:
            # Test basic query
            conn.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Failed to ensure database exists: {e}")
        return False


def get_database_info(db_path: Path) -> dict:
    """Get information about the database."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            size_bytes = page_count * page_size
            
            return {
                "path": str(db_path),
                "tables": tables,
                "size_bytes": size_bytes,
                "page_count": page_count,
                "page_size": page_size
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)} 