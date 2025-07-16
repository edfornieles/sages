"""
Database layer for memory system.
"""

from .connection import (
    get_memory_db_path,
    create_connection,
    close_connection,
    ensure_database_exists
)

from .schema import (
    create_memory_tables,
    create_indexes,
    migrate_schema,
    get_schema_version
)

__all__ = [
    # Connection management
    'get_memory_db_path',
    'create_connection', 
    'close_connection',
    'ensure_database_exists',
    
    # Schema management
    'create_memory_tables',
    'create_indexes',
    'migrate_schema',
    'get_schema_version'
]
