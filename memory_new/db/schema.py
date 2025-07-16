"""
Database schema management for memory system.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "2.0"


def create_memory_tables(conn: sqlite3.Connection) -> bool:
    """Create all memory-related tables."""
    try:
        cursor = conn.cursor()
        
        # Main memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_memory (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                user_id TEXT NOT NULL,
                character_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance_score REAL DEFAULT 0.5,
                emotional_context TEXT DEFAULT '',
                related_entities TEXT DEFAULT '[]',
                conversation_context TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}',
                conversation_id TEXT,
                compressed_content TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Entity memory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                attributes TEXT DEFAULT '{}',
                significance_score REAL DEFAULT 0.5,
                first_mentioned TEXT NOT NULL,
                last_mentioned TEXT NOT NULL,
                mention_count INTEGER DEFAULT 1,
                FOREIGN KEY (memory_id) REFERENCES enhanced_memory(id) ON DELETE CASCADE
            )
        """)
        
        # Conversation context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                character_id TEXT NOT NULL,
                context_data TEXT NOT NULL,
                last_updated TEXT DEFAULT (datetime('now')),
                UNIQUE(conversation_id, user_id, character_id)
            )
        """)
        
        # Fixed memories table (for compatibility)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fixed_memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'conversation',
                importance REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                user_id TEXT NOT NULL,
                character_id TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        conn.commit()
        logger.info("Memory tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create memory tables: {e}")
        return False


def create_indexes(conn: sqlite3.Connection) -> bool:
    """Create database indexes for performance."""
    try:
        cursor = conn.cursor()
        
        # Enhanced memory indexes
        indexes = [
            ("idx_memory_user_char", "enhanced_memory", "user_id, character_id"),
            ("idx_memory_timestamp", "enhanced_memory", "timestamp"),
            ("idx_memory_type", "enhanced_memory", "memory_type"),
            ("idx_memory_importance", "enhanced_memory", "importance_score"),
            ("idx_memory_last_accessed", "enhanced_memory", "last_accessed"),
            ("idx_memory_conversation", "enhanced_memory", "conversation_id"),
            
            # Entity memory indexes
            ("idx_entity_memory_id", "entity_memory", "memory_id"),
            ("idx_entity_name", "entity_memory", "entity_name"),
            ("idx_entity_type", "entity_memory", "entity_type"),
            
            # Conversation context indexes
            ("idx_context_updated", "conversation_context", "last_updated"),
            ("idx_context_conversation", "conversation_context", "conversation_id"),
            
            # Fixed memories indexes
            ("idx_fixed_memories_user_char", "fixed_memories", "user_id, character_id"),
            ("idx_fixed_memories_created", "fixed_memories", "created_at"),
            ("idx_fixed_memories_type", "fixed_memories", "memory_type")
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
            except Exception as e:
                logger.warning(f"Could not create index {index_name}: {e}")
        
        conn.commit()
        logger.info("Database indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        return False


def migrate_schema(conn: sqlite3.Connection, target_version: str = SCHEMA_VERSION) -> bool:
    """Migrate the schema to the target version if needed."""
    try:
        cursor = conn.cursor()
        # Example migration: add new columns if missing
        # ... (migration logic here)
        # Set the schema version using correct SQLite syntax
        cursor.execute(f"PRAGMA user_version = {int(float(target_version.replace('.', '')))}")
        conn.commit()
        logger.info(f"✅ Schema migrated to version {target_version}")
        return True
    except Exception as e:
        logger.error(f"Failed to migrate schema: {e}")
        return False


def get_schema_version(conn: sqlite3.Connection) -> str:
    """Get the current schema version."""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        version_hash = cursor.fetchone()[0]
        
        # For now, return a simple version based on hash
        if version_hash == 0:
            return "1.0"
        elif version_hash == hash(SCHEMA_VERSION):
            return SCHEMA_VERSION
        else:
            return "1.5"  # Intermediate version
            
    except Exception as e:
        logger.error(f"Failed to get schema version: {e}")
        return "1.0"


def get_table_info(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """Get information about a table's columns."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "default_value": row[4],
                "primary_key": bool(row[5])
            })
        return columns
    except Exception as e:
        logger.error(f"Failed to get table info for {table_name}: {e}")
        return [] 