#!/usr/bin/env python3
"""
Enhanced Memory System with Entity Tracking

This system combines buffer window memory with summary memory and integrates
entity tracking to provide better context awareness and prevent entity confusion.
"""

import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import os

from .entity_memory_system import EntityMemorySystem, Entity, EntityType

class MemoryType(Enum):
    BUFFER = "buffer"
    SUMMARY = "summary"
    ENTITY = "entity"
    EMOTIONAL = "emotional"
    RELATIONSHIP = "relationship"

@dataclass
class MemoryEntry:
    """Represents a memory entry with enhanced metadata."""
    id: str
    content: str
    memory_type: MemoryType
    user_id: str
    character_id: str
    timestamp: datetime
    importance_score: float
    emotional_context: str
    related_entities: List[str]  # Entity IDs
    conversation_context: str
    metadata: Dict[str, Any]
    conversation_id: str = None  # Add conversation_id field

class EnhancedMemorySystem:
    def __init__(self, character_id: str, user_id: str, memory_db_path: Path):
        """Initialize the enhanced memory system."""
        self.character_id = character_id
        self.user_id = user_id
        self.memory_db_path = memory_db_path
        
        # Initialize entity memory system
        self.entity_system = EntityMemorySystem(character_id, user_id, memory_db_path)
        
        # Memory configuration
        self.buffer_window_size = 50  # Increased from 20 to 50 - more recent memories in buffer
        self.summary_threshold = 100  # Increased from 50 to 100 - more context before summarizing
        self.importance_threshold = 0.5  # Reduced from 0.6 to 0.5 - keep more memories
        self.context_window_size = 15  # New: for response generation context
        self.fast_access_limit = 200  # New: keep this many memories in fast access cache
        
        # Performance optimizations
        self.batch_size = 25  # Process memories in batches for better performance
        self.cache_enabled = True  # Enable memory caching
        self.lazy_loading = True  # Load memories on demand
        self._memory_cache = {}  # In-memory cache for frequently accessed memories
        
        # Initialize database
        self._init_database()
        
        # Load existing memories
        self.buffer_memories: List[MemoryEntry] = self._load_buffer_memories()
        self.summary_memories: List[MemoryEntry] = self._load_summary_memories()
        
    def _init_database(self):
        """Initialize the database, create or migrate as needed."""
        if not os.path.exists(self.memory_db_path):
            self._create_database()
            return
        with sqlite3.connect(self.memory_db_path) as conn:
            cursor = conn.cursor()
            # Check current schema
            cursor.execute("PRAGMA table_info(enhanced_memory)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # If the enhanced_memory table does not exist (empty columns list), create the full schema from scratch
            if not columns:
                print("🆕 enhanced_memory table not found – creating fresh database schema…")
                # Close the temporary connection cleanly before re-creating
                conn.close()
                self._create_database()
                return
            
            # Trigger migration if any critical column is missing
            required_columns = [
                'compressed_content',  # Introduced in v1.1
                'last_accessed',      # Introduced in v1.2
                'created_at'          # Introduced in v1.3
            ]
            if any(col not in columns for col in required_columns):
                print("🔄 Migrating database schema (missing columns detected)...")
                self._migrate_database_schema(cursor)

    def _migrate_database_schema(self, cursor):
        """Migrate database schema to latest version."""
        try:
            # Add missing columns one by one, catching errors for existing columns
            columns_to_add = [
                ("last_accessed", "TEXT"),
                ("access_count", "INTEGER DEFAULT 0"),
                ("compressed_content", "TEXT"),
                ("metadata", "TEXT"),
                ("created_at", "TEXT")
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE enhanced_memory ADD COLUMN {column_name} {column_type}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        continue  # Column already exists
                    else:
                        print(f"Warning: Could not add column {column_name}: {e}")
            
            # Create indexes if they don't exist
            indexes = [
                ("idx_memory_type", "memory_type"),
                ("idx_memory_timestamp", "timestamp"),
                ("idx_memory_importance", "importance"),
                ("idx_memory_user_char", "user_id, character_id"),
                ("idx_memory_content", "content"),
                ("idx_memory_created", "created_at")
            ]
            
            for index_name, index_columns in indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON enhanced_memory ({index_columns})")
                except sqlite3.OperationalError as e:
                    print(f"Warning: Could not create index {index_name}: {e}")
                    
        except Exception as e:
            print(f"Database migration error: {e}")
    
    def _create_indexes_safely(self, cursor):
        """Create database indexes safely, handling missing columns."""
        indexes = [
            ("idx_memory_user_character", "enhanced_memory", "user_id, character_id"),
            ("idx_memory_timestamp", "enhanced_memory", "timestamp"),
            ("idx_memory_type", "enhanced_memory", "memory_type"),
            ("idx_memory_importance", "enhanced_memory", "importance_score"),
            ("idx_memory_last_accessed", "enhanced_memory", "last_accessed"),
            ("idx_entity_memory_id", "entity_memory", "memory_id"),
            ("idx_entity_name", "entity_memory", "entity_name"),
            ("idx_entity_type", "entity_memory", "entity_type"),
            ("idx_context_updated", "conversation_context", "last_updated")
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})")
            except Exception as e:
                if "no such column" in str(e).lower():
                    print(f"Warning: Could not create index {index_name}: no such column")
                else:
                    print(f"Warning: Could not create index {index_name}: {e}")
    
    def _load_buffer_memories(self) -> List[MemoryEntry]:
        """Load recent buffer memories."""
        print('[DEBUG] Entering _load_buffer_memories')
        memories = []
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                print('[DEBUG] Opened connection in _load_buffer_memories')
                cursor = conn.cursor()
                
                # Check available columns
                cursor.execute("PRAGMA table_info(enhanced_memory)")
                columns = {col[1]: idx for idx, col in enumerate(cursor.fetchall())}
                
                # Build dynamic query based on available columns with explicit column names
                selected_columns = []
                column_mapping = {}
                
                # Required columns
                base_columns = ["id", "content", "memory_type", "user_id", "character_id", "timestamp"]
                for i, col in enumerate(base_columns):
                    selected_columns.append(col)
                    column_mapping[col] = i
                
                # Optional columns with defaults
                optional_columns = [
                    ("importance_score", "0.5"),
                    ("emotional_context", "''"),
                    ("related_entities", "'[]'"),
                    ("conversation_context", "''"),
                    ("metadata", "'{}'"),
                    ("conversation_id", "NULL")
                ]
                
                for col_name, default_value in optional_columns:
                    if col_name in columns:
                        selected_columns.append(col_name)
                    else:
                        selected_columns.append(f"{default_value} as {col_name}")
                    column_mapping[col_name] = len(selected_columns) - 1
                
                # Build query
                query = f"""
                    SELECT {', '.join(selected_columns)}
                    FROM enhanced_memory
                    WHERE memory_type = 'buffer'
                    AND user_id = ? AND character_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (self.user_id, self.character_id, self.buffer_window_size))
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        # Use column mapping for safe access
                        def safe_get(col_name, default=""):
                            idx = column_mapping.get(col_name)
                            if idx is not None and idx < len(row):
                                return row[idx] if row[idx] is not None else default
                            return default
                        
                        # Parse related_entities safely
                        related_entities_str = safe_get("related_entities", "[]")
                        try:
                            related_entities = json.loads(related_entities_str) if related_entities_str else []
                        except:
                            related_entities = []
                        
                        # Parse metadata safely
                        metadata_str = safe_get("metadata", "{}")
                        try:
                            metadata = json.loads(metadata_str) if metadata_str else {}
                        except:
                            metadata = {}
                        
                        # Parse timestamp safely
                        timestamp_str = safe_get("timestamp")
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                        except:
                            timestamp = datetime.now()
                        
                        # Create memory entry with safe access
                        memory = MemoryEntry(
                            id=str(safe_get("id", "")),
                            content=str(safe_get("content", "")),
                            memory_type=MemoryType(safe_get("memory_type", "buffer")),
                            user_id=str(safe_get("user_id", "")),
                            character_id=str(safe_get("character_id", "")),
                            timestamp=timestamp,
                            importance_score=float(safe_get("importance_score", 0.5)),
                            emotional_context=str(safe_get("emotional_context", "")),
                            related_entities=related_entities,
                            conversation_context=str(safe_get("conversation_context", "")),
                            metadata=metadata,
                            conversation_id=safe_get("conversation_id", None)
                        )
                        memories.append(memory)
                    except Exception as e:
                        print(f"Error parsing memory row: {e}")
                        print(f"Row data: {row}")
                        continue
                print('[DEBUG] Closing connection in _load_buffer_memories')
        except Exception as e:
            print(f"Error loading buffer memories: {e}")
        print('[DEBUG] Exiting _load_buffer_memories')
        return memories
    
    def _load_summary_memories(self) -> List[MemoryEntry]:
        """Load summary memories."""
        print('[DEBUG] Entering _load_summary_memories')
        memories = []
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                print('[DEBUG] Opened connection in _load_summary_memories')
                cursor = conn.cursor()
                
                # Check available columns
                cursor.execute("PRAGMA table_info(enhanced_memory)")
                columns = {col[1]: idx for idx, col in enumerate(cursor.fetchall())}
                
                # Build dynamic query based on available columns with explicit column names
                selected_columns = []
                column_mapping = {}
                
                # Required columns
                base_columns = ["id", "content", "memory_type", "user_id", "character_id", "timestamp"]
                for i, col in enumerate(base_columns):
                    selected_columns.append(col)
                    column_mapping[col] = i
                
                # Optional columns with defaults
                optional_columns = [
                    ("importance_score", "0.5"),
                    ("emotional_context", "''"),
                    ("related_entities", "'[]'"),
                    ("conversation_context", "''"),
                    ("metadata", "'{}'"),
                    ("conversation_id", "NULL")
                ]
                
                for col_name, default_value in optional_columns:
                    if col_name in columns:
                        selected_columns.append(col_name)
                    else:
                        selected_columns.append(f"{default_value} as {col_name}")
                    column_mapping[col_name] = len(selected_columns) - 1
                
                # Build query
                query = f"""
                    SELECT {', '.join(selected_columns)}
                    FROM enhanced_memory
                    WHERE memory_type = 'summary'
                    AND user_id = ? AND character_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 10
                """
                
                cursor.execute(query, (self.user_id, self.character_id))
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        # Use column mapping for safe access
                        def safe_get(col_name, default=""):
                            idx = column_mapping.get(col_name)
                            if idx is not None and idx < len(row):
                                return row[idx] if row[idx] is not None else default
                            return default
                        
                        # Parse related_entities safely
                        related_entities_str = safe_get("related_entities", "[]")
                        try:
                            related_entities = json.loads(related_entities_str) if related_entities_str else []
                        except:
                            related_entities = []
                        
                        # Parse metadata safely
                        metadata_str = safe_get("metadata", "{}")
                        try:
                            metadata = json.loads(metadata_str) if metadata_str else {}
                        except:
                            metadata = {}
                        
                        # Parse timestamp safely
                        timestamp_str = safe_get("timestamp")
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                        except:
                            timestamp = datetime.now()
                        
                        # Create memory entry with safe access
                        memory = MemoryEntry(
                            id=str(safe_get("id", "")),
                            content=str(safe_get("content", "")),
                            memory_type=MemoryType(safe_get("memory_type", "summary")),
                            user_id=str(safe_get("user_id", "")),
                            character_id=str(safe_get("character_id", "")),
                            timestamp=timestamp,
                            importance_score=float(safe_get("importance_score", 0.5)),
                            emotional_context=str(safe_get("emotional_context", "")),
                            related_entities=related_entities,
                            conversation_context=str(safe_get("conversation_context", "")),
                            metadata=metadata,
                            conversation_id=safe_get("conversation_id", None)
                        )
                        memories.append(memory)
                    except Exception as e:
                        print(f"Error parsing summary memory row: {e}")
                        print(f"Row data: {row}")
                        continue
                print('[DEBUG] Closing connection in _load_summary_memories')
        except Exception as e:
            print(f"Error loading summary memories: {e}")
        print('[DEBUG] Exiting _load_summary_memories')
        return memories
    
    def _save_memory(self, memory: MemoryEntry):
        """Save memory to database."""
        print('[DEBUG] Entering _save_memory')
        with sqlite3.connect(self.memory_db_path) as conn:
            print('[DEBUG] Opened connection in _save_memory')
            cursor = conn.cursor()
            
            # Check available columns
            cursor.execute("PRAGMA table_info(enhanced_memory)")
            columns = {col[1] for col in cursor.fetchall()}
            
            # Build dynamic insert query
            base_columns = ["id", "content", "memory_type", "user_id", "character_id", "timestamp"]
            base_values = [
                memory.id, memory.content, memory.memory_type.value,
                memory.user_id, memory.character_id, memory.timestamp.isoformat()
            ]
            
            optional_columns = []
            optional_values = []
            
            if "importance_score" in columns:
                optional_columns.append("importance_score")
                optional_values.append(memory.importance_score)
            
            if "emotional_context" in columns:
                optional_columns.append("emotional_context")
                optional_values.append(memory.emotional_context)
            
            if "related_entities" in columns:
                optional_columns.append("related_entities")
                optional_values.append(json.dumps(memory.related_entities))
            
            if "conversation_context" in columns:
                optional_columns.append("conversation_context")
                optional_values.append(memory.conversation_context)
            
            if "metadata" in columns:
                optional_columns.append("metadata")
                optional_values.append(json.dumps(memory.metadata))
            
            if "conversation_id" in columns:
                optional_columns.append("conversation_id")
                optional_values.append(memory.conversation_id)
            
            if "created_at" in columns:
                optional_columns.append("created_at")
                optional_values.append(datetime.now().isoformat())
            
            all_columns = base_columns + optional_columns
            all_values = base_values + optional_values
            
            placeholders = ", ".join(["?" for _ in all_columns])
            query = f"""
                INSERT OR REPLACE INTO enhanced_memory 
                ({', '.join(all_columns)})
                VALUES ({placeholders})
            """
            
            cursor.execute(query, all_values)
            
            conn.commit()
            print('[DEBUG] Closing connection in _save_memory')
        print('[DEBUG] Exiting _save_memory')
    
    def process_message(self, message: str, conversation_id: str, 
                       emotional_context: str = "") -> Dict[str, Any]:
        """Process a message and extract/update memories."""
        # Extract entities from the message
        extracted_entities = self.entity_system.extract_entities(message, conversation_id)
        
        # Calculate importance score
        importance_score = self._calculate_importance(message, extracted_entities, emotional_context)
        
        # Create memory entry
        memory_id = self._generate_memory_id(message, conversation_id)
        memory = MemoryEntry(
            id=memory_id,
            content=message,
            memory_type=MemoryType.BUFFER,
            user_id=self.user_id,
            character_id=self.character_id,
            timestamp=datetime.now(),
            importance_score=importance_score,
            emotional_context=emotional_context,
            related_entities=[entity.id for entity, _ in extracted_entities],
            conversation_context=conversation_id,
            metadata={
                "entities": [(entity.name, entity.entity_type.value) for entity, _ in extracted_entities],
                "word_count": len(message.split()),
                "has_questions": "?" in message,
                "has_emotions": bool(emotional_context)
            },
            conversation_id=conversation_id
        )
        
        # Add to buffer memories
        self.buffer_memories.append(memory)
        self._save_memory_optimized(memory)
        
        # Enforce buffer size limit
        self._enforce_buffer_size()
        
        # Create summary if needed
        self._create_memory_summary()
        
        # Auto-compress if we have too many memories
        if len(self.buffer_memories) > 1000:
            compressed_count = self.compress_old_memories(days_old=7, min_importance=0.2)
            if compressed_count > 0:
                print(f"Auto-compressed {compressed_count} old memories for performance")
        
        # Optimize database periodically
        if len(self.buffer_memories) % 100 == 0:
            self.optimize_database()
        
        # Update entity context
        self.entity_system.update_context_window(
            conversation_id, message, 
            [entity for entity, _ in extracted_entities], 
            emotional_context
        )
        
        # Check for ambiguous references
        ambiguous_references = self._detect_ambiguous_references(message)
        
        return {
            "memory_id": memory_id,
            "importance_score": importance_score,
            "extracted_entities": [(entity.name, entity.entity_type.value) for entity, _ in extracted_entities],
            "ambiguous_references": ambiguous_references,
            "buffer_size": len(self.buffer_memories),
            "summary_count": len(self.summary_memories)
        }
    
    def _calculate_importance(self, message: str, entities: List[Tuple[Entity, float]], 
                            emotional_context: str) -> float:
        """Calculate the importance score of a memory."""
        score = 0.5  # Base score
        
        # Entity importance
        if entities:
            score += 0.2
        
        # Emotional content
        if emotional_context:
            score += 0.15
        
        # Question importance
        if "?" in message:
            score += 0.1
        
        # Personal information
        personal_keywords = ['my', 'I', 'me', 'family', 'work', 'home', 'feel', 'think']
        if any(keyword in message.lower() for keyword in personal_keywords):
            score += 0.1
        
        # Length importance (longer messages might be more important)
        if len(message.split()) > 10:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_memory_id(self, content: str, conversation_id: str) -> str:
        """Generate a unique memory ID."""
        base = f"{self.user_id}_{self.character_id}_{conversation_id}_{content[:50]}"
        return hashlib.md5(base.encode()).hexdigest()[:12]
    
    def _detect_ambiguous_references(self, message: str) -> List[str]:
        """Detect potentially ambiguous references in a message."""
        ambiguous_refs = []
        
        # Only check for pronouns in longer messages where ambiguity is more likely
        if len(message.split()) < 5:
            return ambiguous_refs
        
        # Common ambiguous references - but be more selective
        ambiguous_patterns = [
            r'\b(she|he|they|them)\b',  # Removed "it", "her", "his", "their" as they're usually clear from context
            # Removed demonstratives and location references as they're usually clear
        ]
        
        for pattern in ambiguous_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                pronoun = match.group().lower()
                
                # Skip if pronoun is at the beginning of the message (usually clear from context)
                if match.start() < 10:
                    continue
                
                # Skip if there are multiple entities that could match this pronoun
                recent_entities = self.entity_system._get_recent_entities_from_context(message)
                potential_matches = [
                    entity for entity in recent_entities 
                    if self.entity_system._matches_reference(entity, pronoun, message)
                ]
                
                # Only flag as ambiguous if there are multiple potential matches OR no matches with multiple entities present
                if len(potential_matches) > 1:
                    ambiguous_refs.append(pronoun)
                elif len(potential_matches) == 0 and len(recent_entities) > 1:
                    # Only flag if we have multiple entities but can't resolve the pronoun
                    ambiguous_refs.append(pronoun)
        
        return list(set(ambiguous_refs))  # Remove duplicates
    
    def _create_memory_summary(self):
        """Create a summary of recent buffer memories."""
        if len(self.buffer_memories) < 10:
            return
        
        # Get recent memories for summarization
        recent_memories = self.buffer_memories[-self.summary_threshold:]
        
        # Create summary content
        summary_content = self._generate_summary_content(recent_memories)
        
        # Create summary memory entry
        summary_id = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        summary_memory = MemoryEntry(
            id=summary_id,
            content=summary_content,
            memory_type=MemoryType.SUMMARY,
            user_id=self.user_id,
            character_id=self.character_id,
            timestamp=datetime.now(),
            importance_score=0.8,
            emotional_context="",
            related_entities=[],
            conversation_context="",
            metadata={
                "summarized_memories": len(recent_memories),
                "date_range": {
                    "start": recent_memories[0].timestamp.isoformat(),
                    "end": recent_memories[-1].timestamp.isoformat()
                }
            },
            conversation_id=None
        )
        
        # Save summary
        self.summary_memories.append(summary_memory)
        self._save_memory(summary_memory)
        
        # Clear old buffer memories (keep only recent ones)
        self.buffer_memories = self.buffer_memories[-10:]
        
        # Update database to reflect buffer clearing
        self._clear_old_buffer_memories()
    
    def _generate_summary_content(self, memories: List[MemoryEntry]) -> str:
        """Generate a summary of the given memories."""
        if not memories:
            return "No memories to summarize."
        
        # Group by entity and topic
        entity_summaries = {}
        topic_summaries = {}
        
        for memory in memories:
            # Process entities
            for entity_id in memory.related_entities:
                if entity_id not in entity_summaries:
                    entity_summaries[entity_id] = []
                entity_summaries[entity_id].append(memory.content)
            
            # Process topics
            topic = self._extract_topic_from_memory(memory)
            if topic not in topic_summaries:
                topic_summaries[topic] = []
            topic_summaries[topic].append(memory.content)
        
        # Generate summary
        summary_parts = []
        
        # Entity-based summary
        if entity_summaries:
            summary_parts.append("Key interactions:")
            for entity_id, contents in entity_summaries.items():
                entity = self.entity_system.entities.get(entity_id)
                if entity:
                    summary_parts.append(f"- {entity.name}: {len(contents)} mentions")
        
        # Topic-based summary
        if topic_summaries:
            summary_parts.append("\nTopics discussed:")
            for topic, contents in topic_summaries.items():
                if topic != "general":
                    summary_parts.append(f"- {topic}: {len(contents)} times")
        
        # Emotional summary
        emotional_memories = [m for m in memories if m.emotional_context]
        if emotional_memories:
            summary_parts.append(f"\nEmotional interactions: {len(emotional_memories)}")
        
        return "\n".join(summary_parts)
    
    def _extract_topic_from_memory(self, memory: MemoryEntry) -> str:
        """Extract topic from a memory entry."""
        content_lower = memory.content.lower()
        
        if any(word in content_lower for word in ['work', 'job', 'career']):
            return 'work'
        elif any(word in content_lower for word in ['family', 'mom', 'dad', 'parents']):
            return 'family'
        elif any(word in content_lower for word in ['pet', 'cat', 'dog']):
            return 'pets'
        elif any(word in content_lower for word in ['health', 'sick', 'doctor']):
            return 'health'
        elif any(word in content_lower for word in ['project', 'hobby', 'interest']):
            return 'projects'
        else:
            return 'general'
    
    def _clear_old_buffer_memories(self):
        """Clear old buffer memories from database."""
        if len(self.buffer_memories) < self.buffer_window_size:
            return
        
        # Keep only recent memories
        recent_memories = self.buffer_memories[-self.buffer_window_size:]
        recent_ids = [memory.id for memory in recent_memories]
        
        with sqlite3.connect(self.memory_db_path) as conn:
            cursor = conn.cursor()
            
            # Delete old buffer memories
            cursor.execute("""
                DELETE FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ? AND memory_type = 'buffer'
                AND id NOT IN ({})
            """.format(','.join(['?'] * len(recent_ids))), 
            [self.user_id, self.character_id] + recent_ids)
            
            conn.commit()
    
    def get_memory_context(self, conversation_id: str = None) -> Dict[str, Any]:
        """Get memory context for response generation."""
        context = {
            "recent_memories": [],
            "entity_context": {},
            "summary_context": "",
            "emotional_context": "",
            "conversation_topic": ""
        }
        
        # Get recent buffer memories
        recent_memories = self.buffer_memories[-5:]  # Last 5 memories
        context["recent_memories"] = [
            {
                "content": memory.content,
                "timestamp": memory.timestamp.isoformat(),
                "importance": memory.importance_score,
                "entities": memory.related_entities
            }
            for memory in recent_memories
        ]
        
        # Get entity context
        if self.entity_system.entities:
            context["entity_context"] = {
                entity.name: {
                    "type": entity.entity_type.value,
                    "attributes": entity.attributes,
                    "mention_count": entity.mention_count,
                    "last_mentioned": entity.last_mentioned.isoformat()
                }
                for entity in self.entity_system.entities.values()
            }
        
        # Get summary context
        if self.summary_memories:
            latest_summary = self.summary_memories[-1]
            context["summary_context"] = latest_summary.content
        
        # Get emotional context
        emotional_memories = [m for m in self.buffer_memories if m.emotional_context]
        if emotional_memories:
            context["emotional_context"] = emotional_memories[-1].emotional_context
        
        # Get conversation topic
        if self.buffer_memories:
            latest_memory = self.buffer_memories[-1]
            context["conversation_topic"] = self._extract_topic_from_memory(latest_memory)
        
        return context
    
    def get_clarification_prompt(self, ambiguous_reference: str, context: str) -> str:
        """Generate a clarification prompt for ambiguous references."""
        return f"Could you please clarify what you mean by '{ambiguous_reference}'? I want to make sure I understand correctly. For example, are you referring to a specific person, place, or thing mentioned earlier in our conversation?"
    
    def get_memory_summary(self) -> str:
        """Get a comprehensive memory summary."""
        summary = f"🎭 ENHANCED MEMORY SUMMARY\n"
        summary += f"User: {self.user_id}\n"
        summary += f"Character: {self.character_id}\n"
        summary += f"Buffer Memories: {len(self.buffer_memories)}\n"
        summary += f"Summary Memories: {len(self.summary_memories)}\n"
        summary += f"Total Entities: {len(self.entity_system.entities)}\n\n"
        
        # Entity summary
        summary += self.entity_system.get_entity_summary()
        
        # Recent memories
        if self.buffer_memories:
            summary += "\n📝 RECENT MEMORIES:\n"
            for i, memory in enumerate(self.buffer_memories[-5:], 1):
                summary += f"{i}. {memory.content[:100]}... (Score: {memory.importance_score:.2f})\n"
        
        # Summary memories
        if self.summary_memories:
            summary += "\n📊 MEMORY SUMMARIES:\n"
            for i, memory in enumerate(self.summary_memories[-3:], 1):
                summary += f"{i}. {memory.content[:200]}...\n"
        
        return summary
    
    def _enforce_buffer_size(self):
        """Enforce the buffer size limit."""
        if len(self.buffer_memories) > self.buffer_window_size:
            # Keep only the most recent memories
            self.buffer_memories = self.buffer_memories[-self.buffer_window_size:]
            # Update database
            self._clear_old_buffer_memories()
    
    def compress_old_memories(self, days_old: int = 30, min_importance: float = 0.3):
        """Compress old, low-importance memories to save space."""
        with sqlite3.connect(self.memory_db_path) as conn:
            cursor = conn.cursor()
            
            # Find memories to compress
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cursor.execute("""
                SELECT id, content FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ? 
                AND timestamp < ? AND importance_score < ? 
                AND is_compressed = FALSE
            """, (self.user_id, self.character_id, cutoff_date, min_importance))
            
            memories_to_compress = cursor.fetchall()
            
            compressed_count = 0
            for memory_id, content in memories_to_compress:
                # Simple compression: keep first 100 chars + summary
                if len(content) > 200:
                    compressed_content = content[:100] + "... [COMPRESSED] ..." + content[-50:]
                    
                    cursor.execute("""
                        UPDATE enhanced_memory 
                        SET compressed_content = ?, is_compressed = TRUE 
                        WHERE id = ?
                    """, (compressed_content, memory_id))
                    
                    compressed_count += 1
            
            conn.commit()
        
        return compressed_count
    
    def optimize_database(self):
        """Optimize database performance."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Analyze table statistics
                cursor.execute("ANALYZE")
                
                # Check if enhanced_memory table exists first
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enhanced_memory'")
                if not cursor.fetchone():
                    print("Enhanced memory system: enhanced_memory table missing, triggering migration...")
                    self._migrate_database_schema(cursor)
                    conn.commit()
                    return
                
                # Update statistics - safely handle last_accessed column
                cursor.execute("PRAGMA table_info(enhanced_memory)")
                memory_cols = {row[1] for row in cursor.fetchall()}

                if "last_accessed" in memory_cols:
                    try:
                        cursor.execute("UPDATE enhanced_memory SET last_accessed = CURRENT_TIMESTAMP WHERE last_accessed IS NULL")
                        print("Enhanced memory system: Updated null last_accessed timestamps")
                    except Exception as e:
                        # Skip warning - this is normal for some database setups
                        pass
                else:
                    # Column genuinely missing – trigger on-the-fly migration once
                    print("Enhanced memory system: last_accessed column missing, triggering migration...")
                    self._migrate_database_schema(cursor)
                
                # Create performance indexes
                self._create_indexes_safely(cursor)
                
                # Vacuum to optimize file size
                cursor.execute("VACUUM")
                
                conn.commit()
                print("Enhanced memory system: Database optimization completed")
                
        except Exception as e:
            # Silently handle errors to avoid cluttering logs during normal operation
            pass
    
    def get_memory_statistics(self):
        """Get memory system statistics for monitoring."""
        with sqlite3.connect(self.memory_db_path) as conn:
            cursor = conn.cursor()
            
            # Total memories
            cursor.execute("""
                SELECT COUNT(*) FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ?
            """, (self.user_id, self.character_id))
            total_memories = cursor.fetchone()[0]
            
            # Compressed memories
            cursor.execute("""
                SELECT COUNT(*) FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ? AND is_compressed = TRUE
            """, (self.user_id, self.character_id))
            compressed_memories = cursor.fetchone()[0]
            
            # Average importance
            cursor.execute("""
                SELECT AVG(importance_score) FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ?
            """, (self.user_id, self.character_id))
            avg_importance = cursor.fetchone()[0] or 0
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            cursor.execute("""
                SELECT COUNT(*) FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ? AND timestamp > ?
            """, (self.user_id, self.character_id, recent_cutoff))
            recent_memories = cursor.fetchone()[0]
        
        return {
            'total_memories': total_memories,
            'compressed_memories': compressed_memories,
            'average_importance': avg_importance,
            'recent_memories_24h': recent_memories,
            'compression_ratio': compressed_memories / total_memories if total_memories > 0 else 0
        }
    
    def get_entity_relationships(self, user_id: str = None) -> List[Dict]:
        """Get entity relationships for memory summary."""
        entities = []
        
        # Use the specified user_id or fall back to the instance user_id
        target_user_id = user_id if user_id else self.user_id
        
        try:
            # Get entities from entity memory system
            if hasattr(self, 'entity_system') and self.entity_system:
                # Get all entities for this user
                all_entities = self.entity_system.get_all_entities(target_user_id)
                
                for entity in all_entities:
                    # Determine relationship type based on entity type and attributes
                    relationship = self._determine_relationship_type(entity)
                    emotional_tone = self._determine_emotional_tone(entity)
                    significance = self._calculate_entity_significance(entity)
                    
                    entities.append({
                        'name': entity.name,
                        'type': entity.entity_type.value,
                        'relationship': relationship,
                        'emotional_tone': emotional_tone,
                        'significance': significance,
                        'attributes': entity.attributes,
                        'mention_count': entity.mention_count
                    })
            
            # Also check entity_memory table for additional entities
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT DISTINCT entity_name, entity_type, attributes, confidence_score
                    FROM entity_memory 
                    WHERE memory_id IN (
                        SELECT id FROM enhanced_memory 
                        WHERE user_id = ? AND character_id = ?
                    )
                """, (target_user_id, self.character_id))
                
                for row in cursor.fetchall():
                    entity_name, entity_type, attributes_json, confidence = row
                    
                    # Skip if we already have this entity
                    if any(e['name'] == entity_name for e in entities):
                        continue
                    
                    try:
                        attributes = json.loads(attributes_json) if attributes_json else {}
                    except:
                        attributes = {}
                    
                    relationship = self._determine_relationship_from_attributes(attributes, entity_type)
                    emotional_tone = self._determine_emotional_tone_from_attributes(attributes)
                    significance = confidence if confidence else 0.5
                    
                    entities.append({
                        'name': entity_name,
                        'type': entity_type,
                        'relationship': relationship,
                        'emotional_tone': emotional_tone,
                        'significance': significance,
                        'attributes': attributes,
                        'mention_count': 1
                    })
            
        except Exception as e:
            print(f"Error getting entity relationships: {e}")
        
        # Sort by significance and mention count
        entities.sort(key=lambda x: (x['significance'], x.get('mention_count', 0)), reverse=True)
        
        return entities
    
    def _determine_relationship_type(self, entity) -> str:
        """Determine the relationship type based on entity attributes."""
        if entity.entity_type.value == 'person':
            if 'family' in entity.attributes.get('relationship', '').lower():
                return 'family'
            elif 'friend' in entity.attributes.get('relationship', '').lower():
                return 'friend'
            elif 'colleague' in entity.attributes.get('relationship', '').lower():
                return 'colleague'
            else:
                return 'acquaintance'
        elif entity.entity_type.value == 'location':
            if entity.attributes.get('visited', False):
                return 'visited'
            elif entity.attributes.get('lives_in', False):
                return 'lives_in'
            else:
                return 'known'
        elif entity.entity_type.value == 'object':
            if entity.attributes.get('owns', False):
                return 'owns'
            elif entity.attributes.get('wants', False):
                return 'wants'
            else:
                return 'knows_about'
        else:
            return 'associated'
    
    def _determine_relationship_from_attributes(self, attributes: Dict, entity_type: str) -> str:
        """Determine relationship from entity attributes."""
        if entity_type == 'person':
            relationship = attributes.get('relationship', '')
            if 'family' in relationship.lower():
                return 'family'
            elif 'friend' in relationship.lower():
                return 'friend'
            elif 'colleague' in relationship.lower():
                return 'colleague'
            else:
                return 'acquaintance'
        elif entity_type == 'location':
            if attributes.get('visited', False):
                return 'visited'
            elif attributes.get('lives_in', False):
                return 'lives_in'
            else:
                return 'known'
        else:
            return 'associated'
    
    def _determine_emotional_tone(self, entity) -> str:
        """Determine emotional tone towards an entity."""
        emotional_indicators = entity.attributes.get('emotional_tone', 'neutral')
        
        if isinstance(emotional_indicators, str):
            if any(word in emotional_indicators.lower() for word in ['love', 'adore', 'happy', 'excited']):
                return 'positive'
            elif any(word in emotional_indicators.lower() for word in ['hate', 'angry', 'fear', 'dislike']):
                return 'negative'
            else:
                return 'neutral'
        
        return 'neutral'
    
    def _determine_emotional_tone_from_attributes(self, attributes: Dict) -> str:
        """Determine emotional tone from attributes."""
        emotional_tone = attributes.get('emotional_tone', 'neutral')
        
        if isinstance(emotional_tone, str):
            if any(word in emotional_tone.lower() for word in ['love', 'adore', 'happy', 'excited']):
                return 'positive'
            elif any(word in emotional_tone.lower() for word in ['hate', 'angry', 'fear', 'dislike']):
                return 'negative'
        
        return 'neutral'
    
    def _calculate_entity_significance(self, entity) -> float:
        """Calculate the significance of an entity based on various factors."""
        significance = 0.5  # Base significance
        
        # Increase based on mention count
        significance += min(0.3, entity.mention_count * 0.05)
        
        # Increase based on confidence score
        significance += entity.confidence_score * 0.2
        
        # Increase based on relationship type
        if entity.entity_type.value == 'person':
            significance += 0.1
        elif entity.entity_type.value == 'location':
            significance += 0.05
        
        # Increase based on emotional attachment
        if self._determine_emotional_tone(entity) == 'positive':
            significance += 0.1
        elif self._determine_emotional_tone(entity) == 'negative':
            significance += 0.05
        
        return min(1.0, significance)
    
    def _save_memory_optimized(self, memory_entry: MemoryEntry):
        """Optimized memory saving with batch operations."""
        print('[DEBUG] Entering _save_memory_optimized')
        with sqlite3.connect(self.memory_db_path) as conn:
            print('[DEBUG] Opened connection in _save_memory_optimized')
            cursor = conn.cursor()
            
            # Check which columns exist in the table
            cursor.execute("PRAGMA table_info(enhanced_memory)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Build insert query based on available columns
            base_columns = ["id", "character_id", "user_id", "content", "memory_type", 
                           "importance_score", "emotional_context", "conversation_id", "timestamp"]
            values = [
                memory_entry.id,
                self.character_id,
                self.user_id,
                memory_entry.content,
                memory_entry.memory_type.value,
                memory_entry.importance_score,
                memory_entry.emotional_context,
                memory_entry.conversation_id,
                memory_entry.timestamp
            ]
            
            # Add optional columns if they exist
            if "last_accessed" in columns:
                base_columns.append("last_accessed")
                values.append(datetime.now().isoformat())
            if "access_count" in columns:
                base_columns.append("access_count")
                values.append(1)
            if "related_entities" in columns:
                base_columns.append("related_entities")
                values.append(json.dumps(memory_entry.related_entities))
            if "conversation_context" in columns:
                base_columns.append("conversation_context")
                values.append(memory_entry.conversation_context)
            if "metadata" in columns:
                base_columns.append("metadata")
                values.append(json.dumps(memory_entry.metadata))
            
            # Ensure created_at is set if the column exists (older DBs may lack DEFAULT)
            if "created_at" in columns:
                base_columns.append("created_at")
                values.append(datetime.now().isoformat())
            
            # Use parameterized query for better performance
            placeholders = ", ".join(["?" for _ in values])
            columns_str = ", ".join(base_columns)
            
            cursor.execute(f"""
                INSERT OR REPLACE INTO enhanced_memory 
                ({columns_str})
                VALUES ({placeholders})
            """, values)
            
            # Save entity associations in batch (only if entity_memory table exists)
            if memory_entry.related_entities:
                try:
                    cursor.execute("PRAGMA table_info(entity_memory)")
                    entity_columns = [row[1] for row in cursor.fetchall()]
                    
                    if entity_columns:  # Table exists
                        for entity_id in memory_entry.related_entities:
                            # Get entity details from entity system
                            entity = self.entity_system.get_entity_by_id(entity_id)
                            if entity:
                                cursor.execute("""
                                    INSERT OR REPLACE INTO entity_memory 
                                    (id, memory_id, entity_name, entity_type, attributes, confidence_score, timestamp)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    f"{memory_entry.id}_{entity.name}",
                                    memory_entry.id,
                                    entity.name,
                                    entity.entity_type.value,
                                    json.dumps(entity.attributes),
                                    entity.confidence_score,
                                    datetime.now()
                                ))
                except Exception as e:
                    print(f"Warning: Could not save entity associations: {e}")
            
            conn.commit()
            print('[DEBUG] Closing connection in _save_memory_optimized')
        print('[DEBUG] Exiting _save_memory_optimized')
    
    def _load_memories_optimized(self, limit: int = None):
        """Optimized memory loading with pagination."""
        print('[DEBUG] Entering _load_memories_optimized')
        with sqlite3.connect(self.memory_db_path) as conn:
            print('[DEBUG] Opened connection in _load_memories_optimized')
            cursor = conn.cursor()
            
            # Check which columns exist in the table
            cursor.execute("PRAGMA table_info(enhanced_memory)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Build query based on available columns
            base_columns = ["id", "content", "memory_type", "user_id", "character_id", "timestamp"]
            optional_columns = []
            
            if "importance_score" in columns:
                optional_columns.append("importance_score")
            else:
                optional_columns.append("0.5 as importance_score")
            
            if "emotional_context" in columns:
                optional_columns.append("emotional_context")
            else:
                optional_columns.append("'' as emotional_context")
            
            if "conversation_id" in columns:
                optional_columns.append("conversation_id")
            else:
                optional_columns.append("NULL as conversation_id")
            
            if "related_entities" in columns:
                optional_columns.append("related_entities")
            else:
                optional_columns.append("'[]' as related_entities")
            
            if "conversation_context" in columns:
                optional_columns.append("conversation_context")
            else:
                optional_columns.append("'' as conversation_context")
            
            if "metadata" in columns:
                optional_columns.append("metadata")
            else:
                optional_columns.append("'{}' as metadata")
            
            select_columns = base_columns + optional_columns
            
            query = f"""
                SELECT {', '.join(select_columns)}
                FROM enhanced_memory 
                WHERE user_id = ? AND character_id = ?
                ORDER BY timestamp DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (self.user_id, self.character_id))
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                try:
                    # Map row data to columns
                    row_data = dict(zip(select_columns, row))
                    
                    memory_entry = MemoryEntry(
                        id=row_data["id"],
                        content=row_data["content"],
                        memory_type=MemoryType(row_data["memory_type"]),
                        user_id=row_data["user_id"],
                        character_id=row_data["character_id"],
                        timestamp=datetime.fromisoformat(row_data["timestamp"]) if isinstance(row_data["timestamp"], str) else row_data["timestamp"],
                        importance_score=row_data["importance_score"],
                        emotional_context=row_data["emotional_context"] or "",
                        related_entities=json.loads(row_data["related_entities"]) if row_data["related_entities"] else [],
                        conversation_context=row_data["conversation_context"] or "",
                        metadata=json.loads(row_data["metadata"]) if row_data["metadata"] else {},
                        conversation_id=row_data["conversation_id"]
                    )
                    memories.append(memory_entry)
                except Exception as e:
                    print(f"Error parsing memory row in optimized load: {e}")
                    continue
            print('[DEBUG] Closing connection in _load_memories_optimized')
        print('[DEBUG] Exiting _load_memories_optimized')
        return memories

    def _create_database(self):
        """Create the enhanced memory database with optimized schema and indexes."""
        print('[DEBUG] Entering _create_database')
        with sqlite3.connect(self.memory_db_path) as conn:
            print('[DEBUG] Opened connection in _create_database')
            cursor = conn.cursor()
            
            # Create enhanced memory table with optimized schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_memory (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.5,
                    emotional_context TEXT,
                    conversation_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    compressed_content TEXT,
                    is_compressed BOOLEAN DEFAULT FALSE,
                    related_entities TEXT,
                    conversation_context TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create entity memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_memory (
                    id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    entity_name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    attributes TEXT,
                    confidence_score REAL DEFAULT 1.0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create conversation context table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    conversation_id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    context_window TEXT,
                    emotional_state TEXT,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create memory summary table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_summary (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    summary_content TEXT NOT NULL,
                    memory_count INTEGER DEFAULT 0,
                    start_timestamp DATETIME,
                    end_timestamp DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes safely
            self._create_indexes_safely(cursor)
            
            conn.commit()
            print('[DEBUG] Closing connection in _create_database')
        print('[DEBUG] Exiting _create_database')

    def get_expanded_memory_context(self, conversation_id: str = None, max_memories: int = None) -> Dict[str, Any]:
        """Get expanded memory context optimized for response generation with more comprehensive context."""
        if max_memories is None:
            max_memories = self.context_window_size
            
        context = {
            "recent_memories": [],
            "important_memories": [],
            "entity_context": {},
            "summary_context": "",
            "emotional_context": "",
            "conversation_topic": "",
            "memory_stats": {},
            "user_profile": {}
        }
        
        # Get recent buffer memories (more than before)
        recent_memories = self.buffer_memories[-max_memories:] if self.buffer_memories else []
        context["recent_memories"] = [
            {
                "content": memory.content,
                "timestamp": memory.timestamp.isoformat(),
                "importance": memory.importance_score,
                "entities": memory.related_entities,
                "emotional_context": memory.emotional_context,
                "conversation_id": memory.conversation_id
            }
            for memory in recent_memories
        ]
        
        # Get high-importance memories from summary
        important_memories = [m for m in self.summary_memories if m.importance_score >= 0.7][-10:]
        context["important_memories"] = [
            {
                "content": memory.content,
                "timestamp": memory.timestamp.isoformat(),
                "importance": memory.importance_score,
                "summary_type": "high_importance"
            }
            for memory in important_memories
        ]
        
        # Enhanced entity context with relationship data
        if self.entity_system.entities:
            context["entity_context"] = {}
            for entity in list(self.entity_system.entities.values())[:20]:  # Top 20 entities
                context["entity_context"][entity.name] = {
                    "type": entity.entity_type.value,
                    "attributes": entity.attributes,
                    "mention_count": entity.mention_count,
                    "last_mentioned": entity.last_mentioned.isoformat(),
                    "confidence": getattr(entity, 'confidence_score', 1.0),
                    "relationship_type": self._get_entity_relationship_type(entity)
                }
        
        # Get multiple summary contexts for richer background
        if self.summary_memories:
            recent_summaries = self.summary_memories[-3:]  # Last 3 summaries instead of 1
            context["summary_context"] = {
                "recent_summary": recent_summaries[-1].content if recent_summaries else "",
                "historical_summaries": [
                    {
                        "content": summary.content[:200] + "..." if len(summary.content) > 200 else summary.content,
                        "timestamp": summary.timestamp.isoformat(),
                        "memory_count": summary.metadata.get("summarized_memories", 0)
                    }
                    for summary in recent_summaries[:-1]
                ]
            }
        
        # Enhanced emotional context tracking
        emotional_memories = [m for m in self.buffer_memories[-20:] if m.emotional_context]
        if emotional_memories:
            context["emotional_context"] = {
                "current_emotion": emotional_memories[-1].emotional_context,
                "emotion_history": [
                    {
                        "emotion": m.emotional_context,
                        "timestamp": m.timestamp.isoformat(),
                        "content_preview": m.content[:100] + "..." if len(m.content) > 100 else m.content
                    }
                    for m in emotional_memories[-5:]
                ]
            }
        
        # Enhanced conversation topic analysis
        if self.buffer_memories:
            recent_topics = {}
            for memory in self.buffer_memories[-10:]:
                topic = self._extract_topic_from_memory(memory)
                if topic not in recent_topics:
                    recent_topics[topic] = []
                recent_topics[topic].append(memory.content[:100])
            
            context["conversation_topic"] = {
                "primary_topic": max(recent_topics.keys(), key=lambda t: len(recent_topics[t])) if recent_topics else "general",
                "topic_distribution": {topic: len(contents) for topic, contents in recent_topics.items()},
                "recent_topics": list(recent_topics.keys())
            }
        
        # Memory statistics for context awareness
        context["memory_stats"] = {
            "buffer_count": len(self.buffer_memories),
            "summary_count": len(self.summary_memories),
            "entity_count": len(self.entity_system.entities),
            "total_interactions": len(self.buffer_memories) + len(self.summary_memories),
            "avg_importance": sum(m.importance_score for m in self.buffer_memories) / len(self.buffer_memories) if self.buffer_memories else 0.5
        }
        
        # User profile insights from memory patterns
        context["user_profile"] = self._generate_user_profile_insights()
        
        return context
    
    def _get_entity_relationship_type(self, entity) -> str:
        """Determine relationship type for an entity."""
        if hasattr(entity, 'attributes') and entity.attributes:
            if 'family' in entity.attributes or 'relationship' in entity.attributes:
                return 'family_friend'
            elif 'work' in entity.attributes or 'colleague' in entity.attributes:
                return 'professional'
            elif 'pet' in entity.attributes or entity.entity_type.value == 'PET':
                return 'pet'
            elif 'location' in entity.attributes or entity.entity_type.value == 'PLACE':
                return 'location'
        return 'general'
    
    def _generate_user_profile_insights(self) -> Dict[str, Any]:
        """Generate user profile insights from memory patterns."""
        if not self.buffer_memories:
            return {}
        
        insights = {
            "communication_style": "unknown",
            "interests": [],
            "activity_patterns": {},
            "relationship_indicators": []
        }
        
        # Analyze communication style from recent messages
        recent_messages = [m.content.lower() for m in self.buffer_memories[-20:]]
        
        question_count = sum(1 for msg in recent_messages if '?' in msg)
        if question_count > len(recent_messages) * 0.3:
            insights["communication_style"] = "inquisitive"
        elif any(word in ' '.join(recent_messages) for word in ['feel', 'emotion', 'happy', 'sad', 'excited']):
            insights["communication_style"] = "emotional"
        elif any(word in ' '.join(recent_messages) for word in ['work', 'project', 'analyze', 'think']):
            insights["communication_style"] = "analytical"
        else:
            insights["communication_style"] = "conversational"
        
        # Extract interests from entity mentions
        entity_mentions = {}
        for memory in self.buffer_memories[-30:]:
            for entity_id in memory.related_entities:
                if entity_id in self.entity_system.entities:
                    entity = self.entity_system.entities[entity_id]
                    entity_mentions[entity.name] = entity_mentions.get(entity.name, 0) + 1
        
        # Top mentioned entities as interests
        insights["interests"] = sorted(entity_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Activity patterns (simplified)
        hours = [m.timestamp.hour for m in self.buffer_memories[-50:]]
        insights["activity_patterns"] = {
            "most_active_hour": max(set(hours), key=hours.count) if hours else 12,
            "total_interactions": len(hours)
        }
        
        return insights

    def get_cached_context(self, conversation_id: str = None) -> Dict[str, Any]:
        """Get memory context with caching for improved performance."""
        cache_key = f"context_{self.user_id}_{self.character_id}_{conversation_id or 'main'}"
        
        if self.cache_enabled and cache_key in self._memory_cache:
            cached_data = self._memory_cache[cache_key]
            # Check if cache is still fresh (5 minutes)
            if (datetime.now() - cached_data['timestamp']).seconds < 300:
                return cached_data['context']
        
        # Generate fresh context
        context = self.get_expanded_memory_context(conversation_id)
        
        # Cache the result
        if self.cache_enabled:
            self._memory_cache[cache_key] = {
                'context': context,
                'timestamp': datetime.now()
            }
            
            # Limit cache size
            if len(self._memory_cache) > 50:
                # Remove oldest entries
                oldest_key = min(self._memory_cache.keys(), 
                               key=lambda k: self._memory_cache[k]['timestamp'])
                del self._memory_cache[oldest_key]
        
        return context
    
    def batch_process_memories(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process multiple messages in batch for improved performance."""
        results = []
        
        # Process in batches
        for i in range(0, len(messages), self.batch_size):
            batch = messages[i:i + self.batch_size]
            batch_results = []
            
            for msg_data in batch:
                try:
                    result = self.process_message(
                        msg_data['message'],
                        msg_data.get('conversation_id', 'main'),
                        msg_data.get('emotional_context', '')
                    )
                    batch_results.append(result)
                except Exception as e:
                    print(f"Error processing message in batch: {e}")
                    batch_results.append({
                        "error": str(e),
                        "message": msg_data['message']
                    })
            
            results.extend(batch_results)
        
        return results
    
    def optimize_memory_access(self):
        """Optimize memory access patterns for better performance."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Create memory access optimization
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_access_optimization 
                    ON enhanced_memory (user_id, character_id, timestamp DESC, importance_score DESC)
                """)
                
                # Create entity optimization index
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_entity_optimization 
                    ON entity_memory (entity_name, timestamp DESC)
                """)
                
                # Update statistics for query optimizer
                cursor.execute("ANALYZE")
                
                conn.commit()
                print("Memory access optimization completed")
                
        except Exception as e:
            print(f"Memory access optimization error: {e}")
    
    def preload_memory_cache(self):
        """Preload frequently accessed memories into cache."""
        if not self.cache_enabled:
            return
        
        try:
            # Load recent high-importance memories
            important_memories = [m for m in self.buffer_memories 
                                if m.importance_score >= 0.7][-20:]
            
            # Cache recent conversation contexts
            recent_conversations = set()
            for memory in self.buffer_memories[-50:]:
                if memory.conversation_id:
                    recent_conversations.add(memory.conversation_id)
            
            # Preload contexts for recent conversations
            for conv_id in list(recent_conversations)[:10]:  # Limit to 10 conversations
                self.get_cached_context(conv_id)
            
            print(f"Preloaded {len(important_memories)} important memories and {len(recent_conversations)} conversation contexts")
            
        except Exception as e:
            print(f"Cache preloading error: {e}")
    
    def get_memory_context_fast(self, conversation_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """Fast memory context retrieval with minimal database queries."""
        context = {
            "recent_memories": [],
            "key_entities": {},
            "emotional_state": "",
            "conversation_summary": ""
        }
        
        # Use in-memory buffer for recent memories
        recent_memories = self.buffer_memories[-limit:] if self.buffer_memories else []
        context["recent_memories"] = [
            {
                "content": memory.content,
                "importance": memory.importance_score,
                "entities": memory.related_entities[:3],  # Limit entities for speed
                "emotional_context": memory.emotional_context
            }
            for memory in recent_memories
        ]
        
        # Get key entities from recent memories only
        entity_counts = {}
        for memory in recent_memories:
            for entity_id in memory.related_entities:
                if entity_id in self.entity_system.entities:
                    entity = self.entity_system.entities[entity_id]
                    entity_counts[entity.name] = entity_counts.get(entity.name, 0) + 1
        
        # Top 5 entities for speed
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for entity_name, count in top_entities:
            if entity_name in [e.name for e in self.entity_system.entities.values()]:
                entity = next(e for e in self.entity_system.entities.values() if e.name == entity_name)
                context["key_entities"][entity_name] = {
                    "type": entity.entity_type.value,
                    "mentions": count,
                    "attributes": list(entity.attributes.keys())[:3]  # Limit attributes for speed
                }
        
        # Get latest emotional state
        emotional_memories = [m for m in recent_memories if m.emotional_context]
        if emotional_memories:
            context["emotional_state"] = emotional_memories[-1].emotional_context
        
        # Generate quick conversation summary
        if recent_memories:
            topics = [self._extract_topic_from_memory(m) for m in recent_memories]
            main_topic = max(set(topics), key=topics.count) if topics else "general"
            context["conversation_summary"] = f"Recent conversation focused on {main_topic} with {len(recent_memories)} exchanges"
        
        return context

    def update_access_info(self, memory_id: str):
        """Update access information for a memory."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Try to update access info, but handle gracefully if columns don't exist
                try:
                    cursor.execute("""
                        UPDATE enhanced_memory 
                        SET last_accessed = ?, access_count = access_count + 1 
                        WHERE id = ?
                    """, (datetime.now().isoformat(), memory_id))
                except sqlite3.OperationalError:
                    # If columns don't exist, just continue without updating access info
                    pass
                    
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not update access info: {e}")
