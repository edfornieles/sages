"""
Base module for memory system interfaces and abstract classes.
"""

from .interfaces import (
    MemoryStore,
    MemoryRetriever,
    MemoryCreator,
    MemoryUpdater,
    MemoryDeleter,
    MemoryFormatter,
    MemorySearcher
)

from .models import (
    MemoryEntry,
    MemoryType,
    MemoryContext,
    MemoryQuery,
    MemoryResult
)

__all__ = [
    # Interfaces
    'MemoryStore',
    'MemoryRetriever', 
    'MemoryCreator',
    'MemoryUpdater',
    'MemoryDeleter',
    'MemoryFormatter',
    'MemorySearcher',
    
    # Models
    'MemoryEntry',
    'MemoryType',
    'MemoryContext',
    'MemoryQuery',
    'MemoryResult'
]
