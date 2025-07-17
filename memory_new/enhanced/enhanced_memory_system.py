"""
Enhanced Memory System for Dynamic Character Playground

This module provides advanced memory management capabilities including:
- Temporal memory storage and retrieval
- Relationship tracking and progression
- Personal details extraction and storage
- Memory context generation for conversations
- Memory optimization and cleanup
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import re
from dataclasses import dataclass, asdict
import os
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    character_id: str
    user_id: str
    content: str
    memory_type: str
    importance: float
    timestamp: datetime
    context: Dict[str, Any]
    tags: List[str]
    emotional_valence: float
    relationship_impact: float

@dataclass
class PersonalDetail:
    """Represents a personal detail about a user"""
    id: str
    character_id: str
    user_id: str
    detail_type: str
    content: str
    confidence: float
    timestamp: datetime
    source: str

@dataclass
class RelationshipStage:
    """Represents the relationship stage between a character and user"""
    character_id: str
    user_id: str
    stage: str
    trust_level: float
    familiarity: float
    last_interaction: datetime
    interaction_count: int
    positive_interactions: int
    negative_interactions: int

class EnhancedMemorySystem:
    """
    Advanced memory system for character interactions
    """
    
    def __init__(self, character_id: str, user_id: str):
        self.character_id = character_id
        self.user_id = user_id
        self.memory_key = f"{character_id}_{user_id}"
        self.db_path = f"memory_databases/enhanced_{self.memory_key}.db"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize subsystems
        self._init_subsystems()
        
        self.relationship_context_assembler = RelationshipContextAssembler()
        self.emotional_intelligence = EmotionalIntelligence()
        
        logger.info(f"✅ Enhanced memory system initialized for {self.memory_key}")
    
    def _init_database(self):
        """Initialize the enhanced memory database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create enhanced_memory table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS enhanced_memory (
                        id TEXT PRIMARY KEY,
                        character_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        importance REAL DEFAULT 0.5,
                        timestamp TEXT NOT NULL,
                        context TEXT,
                        tags TEXT,
                        emotional_valence REAL DEFAULT 0.0,
                        relationship_impact REAL DEFAULT 0.0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create personal_details table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS personal_details (
                        id TEXT PRIMARY KEY,
                        character_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        detail_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        confidence REAL DEFAULT 0.5,
                        timestamp TEXT NOT NULL,
                        source TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create relationship_stages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS relationship_stages (
                        character_id TEXT,
                        user_id TEXT,
                        stage TEXT DEFAULT 'stranger',
                        trust_level REAL DEFAULT 0.0,
                        familiarity REAL DEFAULT 0.0,
                        last_interaction TEXT,
                        interaction_count INTEGER DEFAULT 0,
                        positive_interactions INTEGER DEFAULT 0,
                        negative_interactions INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (character_id, user_id)
                    )
                """)
                
                # Create memory_metadata table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info(f"✅ Enhanced memory database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced memory database: {e}")
            raise
    
    def _init_subsystems(self):
        """Initialize memory subsystems"""
        self.personal_details_extractor = PersonalDetailsExtractor()
        self.relationship_tracker = RelationshipTracker(self.character_id, self.user_id)
        self.memory_optimizer = MemoryOptimizer()
        self.context_generator = ContextGenerator()
        self.summarizer = AISummarizer()
        
        logger.info(f"✅ Enhanced memory subsystems initialized for {self.memory_key}")
    
    def store_memory(self, content: str, memory_type: str = "conversation", 
                    importance: float = 0.5, context: Dict[str, Any] = None,
                    tags: List[str] = None, emotional_valence: float = 0.0,
                    relationship_impact: float = 0.0) -> str:
        """
        Store a new memory entry with enhanced emotional analysis
        
        Args:
            content: The memory content
            memory_type: Type of memory (conversation, fact, emotion, etc.)
            importance: Importance score (0.0 to 1.0)
            context: Additional context information
            tags: Memory tags for categorization
            emotional_valence: Emotional valence (-1.0 to 1.0)
            relationship_impact: Impact on relationship (-1.0 to 1.0)
            
        Returns:
            Memory ID
        """
        try:
            memory_id = self._generate_memory_id(content)
            
            # Enhanced emotional analysis
            if emotional_valence == 0.0:  # Only analyze if not provided
                emotional_valence = self._analyze_emotional_content(content)
            
            # Enhanced relationship impact analysis
            if relationship_impact == 0.0:  # Only analyze if not provided
                relationship_impact = self._analyze_relationship_impact(content, memory_type)
            
            # Enhanced importance calculation
            if importance == 0.5:  # Only recalculate if using default
                importance = self._calculate_enhanced_importance(content, emotional_valence, relationship_impact)
            
            # CRITICAL: Auto-boost importance for personal details
            content_lower = content.lower()
            personal_boost_applied = False
            
            # Name-related patterns (highest priority)
            name_patterns = [
                r"\b(ed|edward|edwin|eddie)\b",
                r"my name is",
                r"i am \w+",
                r"i'm \w+",
                r"call me",
                r"you can call me",
                r"my name's"
            ]
            
            for pattern in name_patterns:
                if re.search(pattern, content_lower):
                    importance = max(importance, 1.0)  # Maximum importance for names
                    personal_boost_applied = True
                    memory_type = "personal_identity"  # Mark as identity memory
                    break
            
            # Other personal detail patterns
            if not personal_boost_applied:
                personal_patterns = [
                    r"i live in", r"i work", r"my family", r"my parents", 
                    r"my sister", r"my brother", r"my job", r"i'm from"
                ]
                
                for pattern in personal_patterns:
                    if re.search(pattern, content_lower):
                        importance = max(importance, 0.9)  # High importance for personal details
                        personal_boost_applied = True
                        memory_type = "personal_detail"
                        break
            
            # Enhanced tags generation
            if not tags:
                tags = self._generate_enhanced_tags(content, memory_type, emotional_valence)
            
            # Add personal detail tags if applicable
            if personal_boost_applied:
                if "personal_info" not in tags:
                    tags.append("personal_info")
                if memory_type == "personal_identity":
                    tags.append("identity")
                    tags.append("name")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO enhanced_memory 
                    (id, character_id, user_id, content, memory_type, importance, 
                     timestamp, context, tags, emotional_valence, relationship_impact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id,
                    self.character_id,
                    self.user_id,
                    content,
                    memory_type,
                    importance,
                    datetime.now().isoformat(),
                    json.dumps(context or {}),
                    json.dumps(tags or []),
                    emotional_valence,
                    relationship_impact
                ))
                
                conn.commit()
                
                # Extract and store personal details
                self._extract_and_store_personal_details(content)
                
                # Log if personal boost was applied
                if personal_boost_applied:
                    logger.info(f"✅ Stored CRITICAL personal memory (importance: {importance:.2f}): {content[:50]}...")
                else:
                    logger.info(f"✅ Stored enhanced memory: {content[:50]}...")
                
                return memory_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store memory: {e}")
            raise
    
    def _analyze_emotional_content(self, content: str) -> float:
        """Analyze emotional content and return valence score (-1.0 to 1.0)"""
        content_lower = content.lower()
        
        # Emotional keywords with valence scores
        emotional_keywords = {
            # Positive emotions
            "happy": 0.8, "excited": 0.9, "thrilled": 0.9, "delighted": 0.8,
            "joy": 0.8, "pleased": 0.7, "wonderful": 0.8, "amazing": 0.8,
            "fantastic": 0.8, "great": 0.6, "good": 0.5, "nice": 0.5,
            "love": 0.9, "adore": 0.9, "cherish": 0.8, "care": 0.6,
            "thankful": 0.7, "grateful": 0.7, "appreciate": 0.6,
            "hope": 0.6, "wish": 0.4, "dream": 0.5, "aspire": 0.6,
            
            # Negative emotions
            "sad": -0.7, "depressed": -0.8, "melancholy": -0.6, "down": -0.5,
            "blue": -0.5, "unhappy": -0.6, "disappointed": -0.6, "heartbroken": -0.9,
            "lonely": -0.7, "angry": -0.8, "mad": -0.7, "furious": -0.9,
            "irritated": -0.6, "annoyed": -0.5, "frustrated": -0.6, "rage": -0.9,
            "hate": -0.9, "disgusted": -0.8, "afraid": -0.7, "scared": -0.7,
            "terrified": -0.9, "anxious": -0.6, "worried": -0.5, "nervous": -0.5,
            "fearful": -0.7, "panicked": -0.8, "stressed": -0.6,
            
            # Neutral/contextual emotions
            "surprised": 0.2, "shocked": 0.1, "amazed": 0.6, "astonished": 0.5,
            "stunned": 0.0, "bewildered": -0.2, "confused": -0.3,
            "understand": 0.3, "feel": 0.2, "relate": 0.4, "sympathize": 0.5,
            "compassion": 0.6, "care about": 0.5
        }
        
        # Calculate emotional valence
        total_score = 0.0
        keyword_count = 0
        
        for keyword, score in emotional_keywords.items():
            if keyword in content_lower:
                total_score += score
                keyword_count += 1
        
        # Return average valence, or 0.0 if no emotional keywords found
        if keyword_count > 0:
            return max(-1.0, min(1.0, total_score / keyword_count))
        else:
            return 0.0
    
    def _analyze_relationship_impact(self, content: str, memory_type: str) -> float:
        """Analyze relationship impact of the memory content"""
        content_lower = content.lower()
        
        # Relationship-relevant keywords
        relationship_keywords = {
            # High impact
            "family": 0.8, "parents": 0.8, "sister": 0.7, "brother": 0.7,
            "daughter": 0.8, "son": 0.8, "wife": 0.9, "husband": 0.9,
            "partner": 0.8, "friend": 0.6, "best friend": 0.8,
            "love": 0.9, "care": 0.7, "trust": 0.8, "believe": 0.6,
            "miss": 0.6, "remember": 0.5, "think about": 0.5,
            
            # Medium impact
            "work": 0.4, "job": 0.4, "career": 0.5, "profession": 0.4,
            "hobby": 0.3, "interest": 0.3, "passion": 0.6, "dream": 0.5,
            "goal": 0.4, "achievement": 0.5, "success": 0.5,
            
            # Low impact
            "weather": 0.1, "food": 0.2, "movie": 0.2, "music": 0.3,
            "book": 0.2, "game": 0.2, "sport": 0.3
        }
        
        # Calculate relationship impact
        total_impact = 0.0
        keyword_count = 0
        
        for keyword, impact in relationship_keywords.items():
            if keyword in content_lower:
                total_impact += impact
                keyword_count += 1
        
        # Base impact from memory type
        type_impact = {
            "conversation": 0.3,
            "fact": 0.4,
            "emotion": 0.7,
            "relationship": 0.8,
            "personal": 0.6,
            "memory": 0.5
        }.get(memory_type, 0.3)
        
        # Combine keyword impact with type impact
        if keyword_count > 0:
            keyword_impact = total_impact / keyword_count
            return max(0.0, min(1.0, (keyword_impact + type_impact) / 2))
        else:
            return type_impact
    
    def _calculate_enhanced_importance(self, content: str, emotional_valence: float, relationship_impact: float) -> float:
        """Calculate enhanced importance based on content analysis"""
        # Base importance factors
        length_factor = min(1.0, len(content) / 200)  # Longer content = more important
        emotional_factor = abs(emotional_valence)  # Strong emotions = more important
        relationship_factor = relationship_impact  # High relationship impact = more important
        
        # Personal detail detection with enhanced priority
        personal_keywords = {
            "critical": ["my name", "i am", "i'm", "call me", "you can call me", "ed", "edward", "edwin", "eddie"],
            "high": ["i live", "i work", "my family", "my parents", "my sister", "my brother", "my job"],
            "medium": ["i like", "i love", "i hate", "my favorite", "my hobby", "my interest"]
        }
        
        personal_factor = 0.0
        content_lower = content.lower()
        
        # Check for critical personal info (names, identity)
        for keyword in personal_keywords["critical"]:
            if keyword in content_lower:
                personal_factor = 1.0  # Maximum importance for name/identity
                break
        
        # Check for high priority personal info
        if personal_factor == 0.0:
            for keyword in personal_keywords["high"]:
                if keyword in content_lower:
                    personal_factor = 0.9
                    break
        
        # Check for medium priority personal info
        if personal_factor == 0.0:
            for keyword in personal_keywords["medium"]:
                if keyword in content_lower:
                    personal_factor = 0.7
                    break
        
        # Special boost for name-related content
        name_patterns = [
            r"\b(ed|edward|edwin|eddie)\b",
            r"my name is",
            r"i am \w+",
            r"i'm \w+",
            r"call me",
            r"you can call me"
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, content_lower):
                personal_factor = max(personal_factor, 1.0)  # Ensure maximum importance
                break
        
        # Calculate weighted importance with enhanced personal factor
        importance = (
            length_factor * 0.15 +
            emotional_factor * 0.25 +
            relationship_factor * 0.25 +
            personal_factor * 0.35  # Increased weight for personal details
        )
        
        return max(0.1, min(1.0, importance))
    
    def _generate_enhanced_tags(self, content: str, memory_type: str, emotional_valence: float) -> List[str]:
        """Generate enhanced tags for memory categorization"""
        tags = [memory_type]
        
        # Emotional tags
        if emotional_valence > 0.5:
            tags.append("positive_emotion")
        elif emotional_valence < -0.5:
            tags.append("negative_emotion")
        else:
            tags.append("neutral_emotion")
        
        # Content-based tags
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["family", "parents", "sister", "brother"]):
            tags.append("family")
        
        if any(word in content_lower for word in ["work", "job", "career", "profession"]):
            tags.append("work")
        
        if any(word in content_lower for word in ["love", "care", "trust", "relationship"]):
            tags.append("relationship")
        
        if any(word in content_lower for word in ["hobby", "interest", "passion", "dream"]):
            tags.append("personal_interest")
        
        if any(word in content_lower for word in ["i am", "i'm", "my name", "i live"]):
            tags.append("personal_info")
        
        return tags
    
    def get_memory_context(self, character_id: str, user_id: str, max_memories: int = 10, 
                          min_importance: float = 0.3, include_emotional: bool = True,
                          semantic_query: str = None) -> dict:
        """
        Enhanced memory context retrieval with semantic search and importance ranking
        Returns a dict with keys: 'memories', 'important_memories', 'recent_memories', 'emotional_context', 'relationship_context', 'context_summary'.
        """
        try:
            memories = self._get_semantic_memories(
                character_id, user_id, max_memories, min_importance, semantic_query
            )
            if not memories:
                return {
                    'memories': [],
                    'important_memories': [],
                    'recent_memories': [],
                    'emotional_context': None,
                    'relationship_context': None,
                    'context_summary': 'No relevant memories found.'
                }
            
            # CRITICAL: Prioritize personal details, especially names
            personal_memories = []
            identity_memories = []
            other_memories = []
            
            for memory in memories:
                content = memory.get('content', '').lower()
                tags = memory.get('tags', [])
                
                # Check for identity/name memories (highest priority)
                if any(tag in tags for tag in ['identity', 'name']) or any(pattern in content for pattern in ['my name', 'i am', 'i\'m', 'call me', 'ed', 'edward']):
                    identity_memories.append(memory)
                # Check for other personal details
                elif any(tag in tags for tag in ['personal_info', 'personal_detail']) or any(pattern in content for pattern in ['i live', 'i work', 'my family', 'my job']):
                    personal_memories.append(memory)
                else:
                    other_memories.append(memory)
            
            # Reorder memories with personal details first
            prioritized_memories = identity_memories + personal_memories + other_memories
            
            important_memories = [m for m in prioritized_memories if m.get('importance', 0) > 0.7][:3]
            recent_memories = sorted(prioritized_memories, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            emotional_context = self._get_emotional_context(prioritized_memories) if include_emotional else None
            relationship_context = self._get_relationship_context(prioritized_memories)
            
            # Build context summary with personal details prominently featured
            context_parts = []
            
            # CRITICAL: Always show identity/name information first
            if identity_memories:
                context_parts.append("**CRITICAL - User Identity:**")
                for memory in identity_memories[:2]:  # Show up to 2 identity memories
                    content = memory.get('content', '')[:200]
                    if content:
                        context_parts.append(f"- {content}...")
            
            # Show other important memories
            if important_memories:
                context_parts.append("\n**Important Memories:**")
                for memory in important_memories:
                    content = memory.get('content', '')[:200]
                    if content:
                        context_parts.append(f"- {content}...")
            
            # Show recent context
            if recent_memories:
                context_parts.append("\n**Recent Context:**")
                for memory in recent_memories[:3]:  # Limit to 3 recent memories
                    content = memory.get('content', '')[:150]
                    if content:
                        context_parts.append(f"- {content}...")
            
            if emotional_context:
                context_parts.append(f"\n**Emotional Context:** {emotional_context}")
            if relationship_context:
                context_parts.append(f"\n**Relationship Context:** {relationship_context}")
            
            context_summary = "\n".join(context_parts) if context_parts else "No relevant memories found."
            
            return {
                'memories': prioritized_memories,
                'important_memories': important_memories,
                'recent_memories': recent_memories,
                'emotional_context': emotional_context,
                'relationship_context': relationship_context,
                'context_summary': context_summary,
                'identity_memories': identity_memories,  # New field for identity memories
                'personal_memories': personal_memories   # New field for personal memories
            }
        except Exception as e:
            logger.error(f"❌ Error getting enhanced memory context: {e}")
            return {
                'memories': [],
                'important_memories': [],
                'recent_memories': [],
                'emotional_context': None,
                'relationship_context': None,
                'context_summary': 'Memory context unavailable.',
                'identity_memories': [],
                'personal_memories': []
            }

    def _get_semantic_memories(self, character_id: str, user_id: str, max_memories: int,
                              min_importance: float, semantic_query: str = None) -> List[Dict[str, Any]]:
        """
        Get memories using semantic search and importance ranking
        """
        try:
            db_path = f"memory_databases/enhanced_{character_id}_{user_id}.db"
            
            if not os.path.exists(db_path):
                logger.warning(f"⚠️ Memory database not found: {db_path}")
                return []
            
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Build query with semantic relevance if provided
                if semantic_query:
                    # Use semantic similarity for relevance
                    query = """
                        SELECT *, 
                               CASE 
                                   WHEN content LIKE ? THEN 1.0
                                   WHEN content LIKE ? THEN 0.8
                                   WHEN content LIKE ? THEN 0.6
                                   ELSE 0.3
                               END as relevance_score
                    FROM enhanced_memory 
                        WHERE importance >= ?
                        ORDER BY relevance_score DESC, importance DESC, timestamp DESC
                        LIMIT ?
                    """
                    
                    # Create semantic variations for better matching
                    query_words = semantic_query.lower().split()
                    primary_match = f"%{semantic_query}%"
                    secondary_match = f"%{'%'.join(query_words[:2])}%" if len(query_words) >= 2 else primary_match
                    tertiary_match = f"%{query_words[0]}%" if query_words else primary_match
                    
                    cursor = conn.execute(query, (primary_match, secondary_match, tertiary_match, min_importance, max_memories))
                else:
                    # Standard importance-based retrieval
                    query = """
                        SELECT * FROM enhanced_memory 
                        WHERE importance >= ?
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    """
                    cursor = conn.execute(query, (min_importance, max_memories))
                
                memories = []
                for row in cursor.fetchall():
                    memory = dict(row)
                    
                    # Enhance memory with additional context
                    memory['emotional_context'] = self._extract_emotional_context(memory.get('content', ''))
                    memory['relationship_impact'] = self._calculate_relationship_impact(memory.get('content', ''))
                    memory['topic_category'] = self._categorize_topic(memory.get('content', ''))
                    
                    memories.append(memory)
                
                logger.info(f"✅ Retrieved {len(memories)} semantic memories for {character_id}_{user_id}")
                return memories
                
        except Exception as e:
            logger.error(f"❌ Error in semantic memory retrieval: {e}")
            return []

    def _extract_emotional_context(self, content: str) -> Dict[str, Any]:
        """
        Extract emotional context from memory content
        """
        try:
            # Simple emotional analysis
            content_lower = content.lower()
            
            # Positive indicators
            positive_words = ['happy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'care', 'support']
            positive_count = sum(1 for word in positive_words if word in content_lower)
            
            # Negative indicators  
            negative_words = ['sad', 'angry', 'worried', 'scared', 'frustrated', 'hate', 'dislike', 'stress']
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            # Intensity indicators
            intensity_words = ['very', 'really', 'extremely', 'incredibly', 'so']
            intensity = sum(1 for word in intensity_words if word in content_lower) * 0.2
            
            # Determine emotional valence
            if positive_count > negative_count:
                valence = "positive"
                intensity += positive_count * 0.1
            elif negative_count > positive_count:
                valence = "negative"
                intensity += negative_count * 0.1
            else:
                valence = "neutral"
                intensity = 0.3
            
            return {
                "valence": valence,
                "intensity": min(1.0, intensity),
                "positive_indicators": positive_count,
                "negative_indicators": negative_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting emotional context: {e}")
            return {"valence": "neutral", "intensity": 0.3, "positive_indicators": 0, "negative_indicators": 0}

    def _calculate_relationship_impact(self, content: str) -> float:
        """
        Calculate relationship impact score for memory content
        """
        try:
            content_lower = content.lower()
            
            # Relationship indicators
            positive_indicators = ['love', 'care', 'trust', 'appreciate', 'miss', 'support', 'understand']
            negative_indicators = ['hate', 'dislike', 'distrust', 'ignore', 'blame', 'criticize']
            
            positive_score = sum(0.2 for word in positive_indicators if word in content_lower)
            negative_score = sum(-0.2 for word in negative_indicators if word in content_lower)
            
            return max(-1.0, min(1.0, positive_score + negative_score))
                
        except Exception as e:
            logger.error(f"❌ Error calculating relationship impact: {e}")
            return 0.0

    def _categorize_topic(self, content: str) -> str:
        """
        Categorize memory topic
        """
        try:
            content_lower = content.lower()
            
            # Topic patterns
            topics = {
                "family": ["family", "parents", "mom", "dad", "kids", "children", "sister", "brother"],
                "work": ["work", "job", "career", "boss", "colleague", "office", "project"],
                "health": ["health", "sick", "illness", "doctor", "hospital", "pain", "medicine"],
                "relationships": ["relationship", "partner", "boyfriend", "girlfriend", "spouse", "marriage"],
                "hobbies": ["hobby", "music", "art", "sport", "game", "reading", "writing"],
                "travel": ["travel", "trip", "vacation", "holiday", "visit", "place", "country"],
                "emotions": ["feel", "emotion", "mood", "happy", "sad", "angry", "excited"]
            }
            
            for topic, keywords in topics.items():
                if any(keyword in content_lower for keyword in keywords):
                    return topic
            
            return "general"
            
        except Exception as e:
            logger.error(f"❌ Error categorizing topic: {e}")
            return "general"

    def _get_emotional_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Generate emotional context summary from memories
        """
        try:
            if not memories:
                return ""
            
            # Analyze emotional patterns
            emotional_contexts = [m.get('emotional_context', {}) for m in memories if m.get('emotional_context')]
            
            if not emotional_contexts:
                return ""
            
            # Calculate emotional summary
            valence_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_intensity = 0
            
            for context in emotional_contexts:
                valence = context.get('valence', 'neutral')
                valence_counts[valence] += 1
                total_intensity += context.get('intensity', 0)
            
            avg_intensity = total_intensity / len(emotional_contexts)
            dominant_valence = max(valence_counts, key=valence_counts.get)
            
            # Generate emotional summary
            if dominant_valence == "positive" and avg_intensity > 0.6:
                return "User shows positive emotional engagement with high intensity"
            elif dominant_valence == "positive":
                return "User shows positive emotional engagement"
            elif dominant_valence == "negative" and avg_intensity > 0.6:
                return "User shows negative emotional engagement with high intensity"
            elif dominant_valence == "negative":
                return "User shows negative emotional engagement"
            else:
                return "User shows neutral emotional engagement"
                
        except Exception as e:
            logger.error(f"❌ Error generating emotional context: {e}")
            return ""

    def _get_relationship_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Generate relationship context summary from memories
        """
        try:
            if not memories:
                return ""
            
            # Analyze relationship impact
            relationship_impacts = [m.get('relationship_impact', 0) for m in memories]
            avg_impact = sum(relationship_impacts) / len(relationship_impacts)
            
            if avg_impact > 0.3:
                return "Positive relationship indicators present"
            elif avg_impact < -0.3:
                return "Negative relationship indicators present"
            else:
                return "Neutral relationship context"
                
        except Exception as e:
            logger.error(f"❌ Error generating relationship context: {e}")
            return ""
    
    def search_memories(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search memories by content
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT content, memory_type, importance, timestamp, 
                           emotional_valence, relationship_impact
                    FROM enhanced_memory 
                    WHERE character_id = ? AND user_id = ? 
                    AND content LIKE ?
                    ORDER BY importance DESC, timestamp DESC 
                    LIMIT ?
                """, (self.character_id, self.user_id, f"%{query}%", max_results))
                
                memories = cursor.fetchall()
                
                return [
                    {
                        "content": memory[0],
                        "type": memory[1],
                        "importance": memory[2],
                        "timestamp": memory[3],
                        "emotional_valence": memory[4],
                        "relationship_impact": memory[5]
                    }
                    for memory in memories
                ]
                
        except Exception as e:
            logger.error(f"❌ Failed to search enhanced memories: {e}")
            return []
    
    def update_memory_importance(self, memory_id: str, new_importance: float):
        """Update the importance of a memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE enhanced_memory 
                    SET importance = ? 
                    WHERE id = ? AND character_id = ? AND user_id = ?
                """, (new_importance, memory_id, self.character_id, self.user_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Failed to update memory importance: {e}")
    
    def delete_memory(self, memory_id: str):
        """Delete a memory entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM enhanced_memory 
                    WHERE id = ? AND character_id = ? AND user_id = ?
                """, (memory_id, self.character_id, self.user_id))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Failed to delete enhanced memory: {e}")
            return False

    def update_memory(self, memory_id: str, content: str, memory_type: str = "conversation", 
                     importance: float = 0.5, confidence: float = 0.8):
        """Update an existing memory"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE enhanced_memory 
                    SET content = ?, memory_type = ?, importance = ?
                    WHERE id = ? AND character_id = ? AND user_id = ?
                """, (content, memory_type, importance, memory_id, self.character_id, self.user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Failed to update memory {memory_id}: {e}")
            return False

    def get_all_memories(self):
        """Get all memories for memory management interface"""
        return self.get_all_memories_for_summary()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total memories
                cursor.execute("""
                    SELECT COUNT(*) FROM enhanced_memory 
                    WHERE character_id = ? AND user_id = ?
                """, (self.character_id, self.user_id))
                total_memories = cursor.fetchone()[0]
                
                # Memory types distribution
                cursor.execute("""
                    SELECT memory_type, COUNT(*) 
                    FROM enhanced_memory 
                    WHERE character_id = ? AND user_id = ?
                    GROUP BY memory_type
                """, (self.character_id, self.user_id))
                type_distribution = dict(cursor.fetchall())
                
                # Average importance
                cursor.execute("""
                    SELECT AVG(importance) FROM enhanced_memory 
                    WHERE character_id = ? AND user_id = ?
                """, (self.character_id, self.user_id))
                avg_importance = cursor.fetchone()[0] or 0.0
                
                return {
                    "total_memories": total_memories,
                    "type_distribution": type_distribution,
                    "average_importance": avg_importance,
                    "relationship_stage": self.relationship_tracker.get_relationship_stage()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get enhanced memory stats: {e}")
            return {"error": str(e)}
    
    def _generate_memory_id(self, content: str) -> str:
        """Generate a unique memory ID"""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{self.memory_key}_{timestamp}_{content_hash}"
    
    def _extract_and_store_personal_details(self, content: str):
        """Extract and store personal details from content"""
        try:
            details = self.personal_details_extractor.extract_details(content)
            
            for detail in details:
                detail_id = f"{self.memory_key}_{detail['type']}_{hashlib.md5(detail['content'].encode()).hexdigest()[:8]}"
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO personal_details 
                        (id, character_id, user_id, detail_type, content, confidence, timestamp, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        detail_id,
                        self.character_id,
                        self.user_id,
                        detail['type'],
                        detail['content'],
                        detail['confidence'],
                        datetime.now().isoformat(),
                        'extraction'
                    ))
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"❌ Failed to extract personal details: {e}")
    
    def _get_personal_details(self) -> List[Dict[str, Any]]:
        """Get stored personal details"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT detail_type, content, confidence, timestamp
                    FROM personal_details 
                    WHERE character_id = ? AND user_id = ?
                    ORDER BY confidence DESC, timestamp DESC
                """, (self.character_id, self.user_id))
                
                details = cursor.fetchall()
                
                return [
                    {
                        "type": detail[0],
                        "content": detail[1],
                        "confidence": detail[2],
                        "timestamp": detail[3]
                    }
                    for detail in details
                ]
                
        except Exception as e:
            logger.error(f"❌ Failed to get personal details: {e}")
            return []

    def get_personal_details(self) -> List[Dict[str, Any]]:
        """Public method to get stored personal details"""
        return self._get_personal_details()

    def process_message(self, *args, **kwargs):
        """Stub for process_message to avoid attribute errors. Implement as needed."""
        return None

    def get_recent_memories(self, *args, **kwargs):
        """Stub for get_recent_memories to avoid attribute errors. Implement as needed."""
        return []

    def get_all_memories_for_summary(self) -> List[Dict[str, Any]]:
        """
        Retrieve all memories for summary extraction (no limit).
        Returns:
            List of memory dictionaries, ordered by timestamp ascending.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content, memory_type, importance, timestamp, 
                           emotional_valence, relationship_impact, tags
                    FROM enhanced_memory 
                    WHERE character_id = ? AND user_id = ?
                    ORDER BY timestamp ASC
                """, (self.character_id, self.user_id))
                memories = cursor.fetchall()
                return [
                    {
                        "content": memory[0],
                        "type": memory[1],
                        "importance": memory[2],
                        "timestamp": memory[3],
                        "emotional_valence": memory[4],
                        "relationship_impact": memory[5],
                        "tags": json.loads(memory[6]) if memory[6] else []
                    }
                    for memory in memories
                ]
        except Exception as e:
            logger.error(f"❌ Failed to get all memories for summary: {e}")
        return []

    def summarize_recent_session(self, n: int = 10) -> str:
        """Summarize the most recent n memories as a session."""
        memories = self.get_recent_memories(n)
        return self.summarizer.summarize_session(memories)

    def consolidate_summaries(self, summaries: List[str]) -> str:
        return self.summarizer.consolidate_period(summaries)

    def get_relationship_aware_context(self, max_memories: int = 10) -> str:
        """Get context assembled with relationship awareness."""
        memories = self.get_recent_memories(max_memories)
        relationship_stage = self.relationship_tracker.get_relationship_stage()
        return self.relationship_context_assembler.assemble_context(memories, relationship_stage)

    def analyze_and_store_emotion(self, text: str):
        emotion = self.emotional_intelligence.analyze_emotion(text)
        # Store as a special memory type
        self.store_memory(content=text, memory_type="emotion", importance=0.7, context=emotion, emotional_valence=emotion["intensity"])
        return emotion

    def generate_emotionally_aware_response(self, context: str, text: str) -> str:
        emotion = self.emotional_intelligence.analyze_emotion(text)
        return self.emotional_intelligence.generate_emotional_response(context, emotion)


class PersonalDetailsExtractor:
    """Extracts personal details from text content"""
    
    def __init__(self):
        self.detail_patterns = {
            "name": [
                # Direct name introductions
                r"my name is (\w+)",
                r"i am (\w+)",
                r"call me (\w+)",
                r"i'm (\w+)",
                r"you can call me (\w+)",
                r"my name's (\w+)",
                r"i'm called (\w+)",
                # More casual introductions
                r"hey,? i'm (\w+)",
                r"hi,? i'm (\w+)",
                r"hello,? i'm (\w+)",
                r"i'm (\w+),? nice to meet you",
                r"(\w+) here",
                r"the name's (\w+)",
                # Contextual name mentions
                r"(\w+) is my name",
                r"people call me (\w+)",
                r"everyone calls me (\w+)",
                # Direct statements
                r"i am (\w+) fornieles",
                r"my name is (\w+) fornieles",
                r"i'm (\w+) fornieles",
                # Ed-specific patterns (since we know the user is Ed)
                r"\b(ed|edward|edwin|eddie)\b(?!\s+(is|was|will|can|should|would))",
                r"(\b(ed|edward|edwin|eddie)\b).*?(name|called|call)",
                r"(name|called|call).*?(\b(ed|edward|edwin|eddie)\b)"
            ],
            "age": [
                r"i am (\d+) years? old",
                r"i'm (\d+) years? old",
                r"age (\d+)",
                r"(\d+) years? old",
                r"i'm (\d+)",
                r"(\d+) years"
            ],
            "location": [
                r"i live in ([^,\.]+)",
                r"from ([^,\.]+)",
                r"in ([^,\.]+)",
                r"residing in ([^,\.]+)",
                r"i'm from ([^,\.]+)",
                r"i live at ([^,\.]+)",
                r"my home is ([^,\.]+)"
            ],
            "occupation": [
                r"i work as ([^,\.]+)",
                r"i'm a ([^,\.]+)",
                r"i am a ([^,\.]+)",
                r"my job is ([^,\.]+)",
                r"i work at ([^,\.]+)",
                r"i work for ([^,\.]+)",
                r"my profession is ([^,\.]+)"
            ],
            "family": [
                r"my (mother|father|mom|dad|sister|brother) is ([^,\.]+)",
                r"i have a (sister|brother) named ([^,\.]+)",
                r"my (wife|husband) is ([^,\.]+)",
                r"my (daughter|son) is ([^,\.]+)",
                r"i have a (daughter|son) named ([^,\.]+)"
            ]
        }
    
    def extract_details(self, content: str) -> List[Dict[str, Any]]:
        """Extract personal details from content"""
        details = []
        content_lower = content.lower()
        
        for detail_type, patterns in self.detail_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower)
                for match in matches:
                    detail_content = match.group(1)
                    
                    # Special handling for name patterns that might have multiple groups
                    if detail_type == "name" and len(match.groups()) > 1:
                        # For patterns like "name is ed" or "ed is name"
                        if match.group(1) in ['name', 'called', 'call'] and match.group(2) in ['ed', 'edward', 'edwin', 'eddie']:
                            detail_content = match.group(2)
                        elif match.group(2) in ['name', 'called', 'call'] and match.group(1) in ['ed', 'edward', 'edwin', 'eddie']:
                            detail_content = match.group(1)
                    
                    if detail_type == "family":
                        # Handle family members with names
                        if len(match.groups()) > 1:
                            detail_content = f"{match.group(1)}: {match.group(2)}"
                    
                    # Clean up the extracted content
                    detail_content = detail_content.strip()
                    if detail_content:
                        # Capitalize names properly
                        if detail_type == "name":
                            detail_content = detail_content.title()
                            # Handle "Ed" specifically
                            if detail_content.lower() in ['ed', 'edward', 'edwin', 'eddie']:
                                detail_content = "Ed"
                        
                        details.append({
                            "type": detail_type,
                            "content": detail_content,
                            "confidence": 0.8,
                            "source": "pattern_matching"
                        })
        
        return details


class RelationshipTracker:
    """Tracks and manages relationship progression"""
    
    def __init__(self, character_id: str, user_id: str):
        self.character_id = character_id
        self.user_id = user_id
        self.db_path = f"memory_databases/enhanced_{character_id}_{user_id}.db"
    
    def update_relationship(self, interaction_impact: float):
        """Update relationship based on interaction impact"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current relationship
                cursor.execute("""
                    SELECT stage, trust_level, familiarity, interaction_count,
                           positive_interactions, negative_interactions
                    FROM relationship_stages 
                    WHERE character_id = ? AND user_id = ?
                """, (self.character_id, self.user_id))
                
                result = cursor.fetchone()
                
                if result:
                    stage, trust_level, familiarity, count, pos_count, neg_count = result
                else:
                    # Initialize new relationship
                    stage = "stranger"
                    trust_level = 0.0
                    familiarity = 0.0
                    count = 0
                    pos_count = 0
                    neg_count = 0
                
                # Update counts
                count += 1
                if interaction_impact > 0:
                    pos_count += 1
                elif interaction_impact < 0:
                    neg_count += 1
                
                # Update trust and familiarity
                trust_level = max(0.0, min(1.0, trust_level + interaction_impact * 0.1))
                familiarity = max(0.0, min(1.0, familiarity + 0.05))
                
                # Determine stage
                if familiarity < 0.2:
                    stage = "stranger"
                elif familiarity < 0.5:
                    stage = "acquaintance"
                elif familiarity < 0.8:
                    stage = "friend"
                else:
                    stage = "close_friend"
                
                # Update database
                cursor.execute("""
                    INSERT OR REPLACE INTO relationship_stages 
                    (character_id, user_id, stage, trust_level, familiarity,
                     last_interaction, interaction_count, positive_interactions, negative_interactions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.character_id, self.user_id, stage, trust_level, familiarity,
                    datetime.now().isoformat(), count, pos_count, neg_count
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Failed to update relationship: {e}")
    
    def get_relationship_stage(self) -> Dict[str, Any]:
        """Get current relationship stage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT stage, trust_level, familiarity, interaction_count,
                           positive_interactions, negative_interactions, last_interaction
                    FROM relationship_stages 
                    WHERE character_id = ? AND user_id = ?
                """, (self.character_id, self.user_id))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        "stage": result[0],
                        "trust_level": result[1],
                        "familiarity": result[2],
                        "interaction_count": result[3],
                        "positive_interactions": result[4],
                        "negative_interactions": result[5],
                        "last_interaction": result[6]
                    }
                else:
                    return {
                        "stage": "stranger",
                        "trust_level": 0.0,
                        "familiarity": 0.0,
                        "interaction_count": 0,
                        "positive_interactions": 0,
                        "negative_interactions": 0,
                        "last_interaction": None
                    }
                    
        except Exception as e:
            logger.error(f"❌ Failed to get relationship stage: {e}")
            return {"stage": "stranger", "trust_level": 0.0}


class MemoryOptimizer:
    """Optimizes memory storage and retrieval"""
    
    def __init__(self):
        self.optimization_rules = {
            "max_memories_per_type": 100,
            "min_importance_threshold": 0.1,
            "cleanup_interval_days": 30
        }
    
    def optimize_memory_access(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize memory access patterns"""
        # Sort by importance and recency
        sorted_memories = sorted(
            memories,
            key=lambda x: (x.get('importance', 0), x.get('timestamp', '')),
            reverse=True
        )
        
        # Apply importance threshold
        filtered_memories = [
            memory for memory in sorted_memories
            if memory.get('importance', 0) >= self.optimization_rules['min_importance_threshold']
        ]
        
        return filtered_memories


class ContextGenerator:
    """Generates context from memories and personal details"""
    
    def generate_context_summary(self, memories: List[Dict[str, Any]], 
                               personal_details: List[Dict[str, Any]],
                               relationship_stage: Dict[str, Any]) -> str:
        """Generate a context summary for conversation"""
        summary_parts = []
        
        # Add relationship context
        if relationship_stage:
            stage = relationship_stage.get('stage', 'stranger')
            trust = relationship_stage.get('trust_level', 0.0)
            familiarity = relationship_stage.get('familiarity', 0.0)
            
            summary_parts.append(f"Relationship: {stage} (trust: {trust:.2f}, familiarity: {familiarity:.2f})")
        
        # Add personal details
        if personal_details:
            details_summary = []
            for detail in personal_details[:5]:  # Limit to 5 most important details
                details_summary.append(f"{detail['type']}: {detail['content']}")
            
            if details_summary:
                summary_parts.append(f"Personal details: {', '.join(details_summary)}")
        
        # Add recent memories
        if memories:
            recent_memories = memories[:3]  # Limit to 3 most recent memories
            memory_summaries = []
            for memory in recent_memories:
                content = memory.get('content', '')[:100]  # Truncate long content
                memory_summaries.append(f"'{content}...'")
            
            if memory_summaries:
                summary_parts.append(f"Recent memories: {', '.join(memory_summaries)}")
        
        return " | ".join(summary_parts) if summary_parts else "No context available"


class AISummarizer:
    """Modular AI-powered summarizer for memory sessions and periods."""
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def summarize_session(self, memories: List[Dict[str, Any]]) -> str:
        """Summarize a session's memories using LLM."""
        if not memories:
            return "No memories to summarize."
        text = "\n".join([m["content"] for m in memories])
        prompt = f"Summarize the following conversation session in 2-3 sentences, focusing on key topics, emotions, and relationship changes.\n\n{text}"
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful AI memory summarizer."},
                          {"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.4
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            return f"[ERROR] LLM summarization failed: {e}"

    def consolidate_period(self, summaries: List[str]) -> str:
        """Consolidate multiple session summaries into a higher-level summary."""
        if not summaries:
            return "No summaries to consolidate."
        text = "\n".join(summaries)
        prompt = f"Consolidate the following session summaries into a weekly or monthly theme, highlighting relationship progression and emotional trends.\n\n{text}"
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful AI memory summarizer."},
                          {"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.4
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            return f"[ERROR] LLM consolidation failed: {e}"


class RelationshipContextAssembler:
    """Modular relationship-aware context assembler."""
    def __init__(self, tracker=None):
        self.tracker = tracker

    def assemble_context(self, memories: List[Dict[str, Any]], relationship_stage: Dict[str, Any]) -> str:
        # Filter and prioritize memories based on relationship stage
        if not memories:
            return "No memories available."
        stage = relationship_stage.get("stage", "acquaintance")
        trust = relationship_stage.get("trust_level", 0.0)
        # Example: prioritize personal, emotional, and shared memories as relationship deepens
        if stage in ["close", "intimate"] or trust > 0.7:
            relevant = [m for m in memories if m.get("memory_type") in ("personal", "emotion", "relationship")]
        else:
            relevant = [m for m in memories if m.get("memory_type") != "private"]
        # Sort by importance and recency
        relevant = sorted(relevant, key=lambda x: (x.get("importance", 0), x.get("timestamp", "")), reverse=True)
        return "\n".join([m["content"] for m in relevant[:10]])


class EmotionalIntelligence:
    """Modular emotional intelligence integration."""
    def __init__(self):
        pass

    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        # Simple sentiment/emotion analysis (placeholder)
        # In production, use a model or API
        text_lower = text.lower()
        if any(word in text_lower for word in ["happy", "love", "excited", "joy"]):
            return {"valence": "positive", "intensity": 0.8, "primary_emotion": "joy"}
        if any(word in text_lower for word in ["sad", "angry", "upset", "hate"]):
            return {"valence": "negative", "intensity": 0.8, "primary_emotion": "sadness"}
        return {"valence": "neutral", "intensity": 0.2, "primary_emotion": "neutral"}

    def generate_emotional_response(self, context: str, emotion: Dict[str, Any]) -> str:
        # Generate a response with emotional awareness (placeholder)
        if emotion["valence"] == "positive":
            return f"I'm really glad to hear that! {context}"
        if emotion["valence"] == "negative":
            return f"I'm sorry you're feeling that way. {context}"
        return f"Thank you for sharing. {context}"


# Factory function for creating enhanced memory systems
def create_enhanced_memory_system(character_id: str, user_id: str) -> EnhancedMemorySystem:
    """Create a new enhanced memory system instance"""
    return EnhancedMemorySystem(character_id, user_id)


# Global registry for memory systems
_memory_systems: Dict[str, EnhancedMemorySystem] = {}

def get_enhanced_memory_system(character_id: str, user_id: str) -> Optional[EnhancedMemorySystem]:
    """Get or create an enhanced memory system instance"""
    memory_key = f"{character_id}_{user_id}"
    
    if memory_key not in _memory_systems:
        try:
            _memory_systems[memory_key] = EnhancedMemorySystem(character_id, user_id)
        except Exception as e:
            logger.error(f"❌ Failed to create enhanced memory system: {e}")
            return None
    
    return _memory_systems[memory_key]


def cleanup_memory_systems():
    """Clean up memory system instances"""
    global _memory_systems
    _memory_systems.clear()
    logger.info("✅ Enhanced memory systems cleaned up")


# Export main classes and functions
__all__ = [
    'EnhancedMemorySystem',
    'PersonalDetailsExtractor',
    'RelationshipTracker',
    'MemoryOptimizer',
    'ContextGenerator',
    'create_enhanced_memory_system',
    'get_enhanced_memory_system',
    'cleanup_memory_systems'
] 