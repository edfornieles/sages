"""
Core data models for the memory system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


class MemoryType(Enum):
    """Types of memories that can be stored."""
    BUFFER = "buffer"
    SUMMARY = "summary"
    ENTITY = "entity"
    EMOTIONAL = "emotional"
    RELATIONSHIP = "relationship"
    CONVERSATION = "conversation"
    PERSONAL = "personal"
    TEMPORAL = "temporal"


@dataclass
class MemoryEntry:
    """Represents a memory entry with enhanced metadata."""
    id: str
    content: str
    memory_type: MemoryType
    user_id: str
    character_id: str
    timestamp: datetime
    importance_score: float = 0.5
    emotional_context: str = ""
    related_entities: List[str] = field(default_factory=list)
    conversation_context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    conversation_id: Optional[str] = None
    compressed_content: Optional[str] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0


@dataclass
class MemoryContext:
    """Context information for memory operations."""
    user_id: str
    character_id: str
    conversation_id: Optional[str] = None
    emotional_context: str = ""
    current_topic: str = ""
    relationship_stage: str = "acquaintance"


@dataclass
class MemoryQuery:
    """Query parameters for memory retrieval."""
    user_id: str
    character_id: str
    limit: int = 10
    memory_type: Optional[MemoryType] = None
    search_query: Optional[str] = None
    min_importance: float = 0.0
    max_importance: float = 1.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    conversation_id: Optional[str] = None


@dataclass
class MemoryResult:
    """Result of a memory operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryStatistics:
    """Statistics about memory usage."""
    total_memories: int
    memory_types: Dict[MemoryType, int]
    average_importance: float
    oldest_memory: Optional[datetime]
    newest_memory: Optional[datetime]
    total_size_bytes: int
    compression_ratio: float = 1.0 