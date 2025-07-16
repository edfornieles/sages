"""
Abstract interfaces for memory system operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .models import MemoryEntry, MemoryQuery, MemoryResult, MemoryContext, MemoryStatistics


class MemoryStore(ABC):
    """Abstract base class for memory storage operations."""
    
    @abstractmethod
    def initialize(self) -> MemoryResult:
        """Initialize the memory store."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the memory store is available."""
        pass


class MemoryRetriever(ABC):
    """Abstract base class for memory retrieval operations."""
    
    @abstractmethod
    def get_memories(self, query: MemoryQuery) -> MemoryResult:
        """Retrieve memories based on query parameters."""
        pass
    
    @abstractmethod
    def get_memory_by_id(self, memory_id: str) -> MemoryResult:
        """Retrieve a specific memory by ID."""
        pass
    
    @abstractmethod
    def get_memory_context(self, context: MemoryContext, limit: int = 10) -> MemoryResult:
        """Get memory context for a specific conversation or user."""
        pass
    
    @abstractmethod
    def get_memory_statistics(self, user_id: str, character_id: str) -> MemoryStatistics:
        """Get statistics about stored memories."""
        pass


class MemoryCreator(ABC):
    """Abstract base class for memory creation operations."""
    
    @abstractmethod
    def create_memory(self, memory: MemoryEntry) -> MemoryResult:
        """Create a new memory entry."""
        pass
    
    @abstractmethod
    def create_memory_from_content(self, content: str, context: MemoryContext, 
                                 memory_type: str = "conversation", 
                                 importance: float = 0.5) -> MemoryResult:
        """Create a memory from content string."""
        pass
    
    @abstractmethod
    def batch_create_memories(self, memories: List[MemoryEntry]) -> MemoryResult:
        """Create multiple memories in a batch."""
        pass


class MemoryUpdater(ABC):
    """Abstract base class for memory update operations."""
    
    @abstractmethod
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> MemoryResult:
        """Update an existing memory."""
        pass
    
    @abstractmethod
    def update_importance(self, memory_id: str, importance: float) -> MemoryResult:
        """Update the importance score of a memory."""
        pass
    
    @abstractmethod
    def update_access_info(self, memory_id: str) -> MemoryResult:
        """Update access information for a memory."""
        pass


class MemoryDeleter(ABC):
    """Abstract base class for memory deletion operations."""
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> MemoryResult:
        """Delete a specific memory."""
        pass
    
    @abstractmethod
    def delete_memories_by_query(self, query: MemoryQuery) -> MemoryResult:
        """Delete memories matching query criteria."""
        pass
    
    @abstractmethod
    def clear_old_memories(self, days_old: int, min_importance: float = 0.3) -> MemoryResult:
        """Clear old memories below importance threshold."""
        pass


class MemoryFormatter(ABC):
    """Abstract base class for memory formatting operations."""
    
    @abstractmethod
    def format_memory_for_agent(self, memory: MemoryEntry) -> str:
        """Format a memory for agent consumption."""
        pass
    
    @abstractmethod
    def format_memory_context(self, memories: List[MemoryEntry]) -> str:
        """Format a list of memories into context string."""
        pass
    
    @abstractmethod
    def format_memory_summary(self, memories: List[MemoryEntry]) -> str:
        """Format memories into a summary."""
        pass
    
    @abstractmethod
    def format_personal_details(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """Extract and format personal details from memories."""
        pass


class MemorySearcher(ABC):
    """Abstract base class for memory search operations."""
    
    @abstractmethod
    def search_memories(self, query: str, context: MemoryContext, limit: int = 10) -> MemoryResult:
        """Search memories by content."""
        pass
    
    @abstractmethod
    def search_by_entities(self, entities: List[str], context: MemoryContext, limit: int = 10) -> MemoryResult:
        """Search memories by related entities."""
        pass
    
    @abstractmethod
    def search_by_topic(self, topic: str, context: MemoryContext, limit: int = 10) -> MemoryResult:
        """Search memories by topic."""
        pass 