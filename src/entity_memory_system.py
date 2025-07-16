#!/usr/bin/env python3
"""
Enhanced Entity Memory System

This system provides entity disambiguation, role tagging, and context tracking
to prevent confusion between different entities (people, pets, places, etc.)
in conversational AI memory systems.
"""

import json
import sqlite3
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Configure logging for entity memory system
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntityType(Enum):
    PERSON = "person"
    PET = "pet"
    PLACE = "place"
    OBJECT = "object"
    CONCEPT = "concept"
    PROJECT = "project"
    EVENT = "event"

class RelationshipType(Enum):
    FAMILY = "family"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    PET_OWNER = "pet_owner"
    LOCATION = "location"
    ASSOCIATION = "association"

@dataclass
class Entity:
    """Represents a unique entity in the user's world."""
    id: str
    name: str
    entity_type: EntityType
    aliases: List[str]
    attributes: Dict[str, Any]
    relationships: Dict[str, List[str]]  # relationship_type -> [entity_ids]
    first_mentioned: datetime
    last_mentioned: datetime
    mention_count: int
    confidence_score: float
    user_id: str

@dataclass
class ContextWindow:
    """Represents the current conversation context window."""
    conversation_id: str
    user_id: str
    character_id: str
    recent_entities: List[str]  # Entity IDs in order of mention
    current_topic: str
    emotional_context: str
    timestamp: datetime

class EntityMemorySystem:
    def __init__(self, character_id: str, user_id: str, memory_db_path: Path):
        """Initialize the entity memory system."""
        self.character_id = character_id
        self.user_id = user_id
        self.memory_db_path = memory_db_path
        self.context_window_size = 10
        self.entity_confidence_threshold = 0.7
        
        logger.info(f"Initializing EntityMemorySystem for character_id={character_id}, user_id={user_id}")
        
        # Initialize database tables
        self._init_database()
        
        # Load existing entities
        self.entities: Dict[str, Entity] = self._load_entities()
        self.context_windows: List[ContextWindow] = self._load_context_windows()
        
        logger.info(f"EntityMemorySystem initialized with {len(self.entities)} entities and {len(self.context_windows)} context windows")
        
    def _init_database(self):
        """Initialize database tables for entity memory."""
        logger.debug(f"Initializing database tables at {self.memory_db_path}")
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Entity table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entity_memory (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        aliases TEXT NOT NULL,
                        attributes TEXT NOT NULL,
                        relationships TEXT NOT NULL,
                        first_mentioned TEXT NOT NULL,
                        last_mentioned TEXT NOT NULL,
                        mention_count INTEGER DEFAULT 1,
                        confidence_score REAL DEFAULT 1.0,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL
                    )
                """)
                
                # Context window table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS context_windows (
                        conversation_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        recent_entities TEXT NOT NULL,
                        current_topic TEXT,
                        emotional_context TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                # Entity mention tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entity_mentions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_id TEXT NOT NULL,
                        conversation_id TEXT NOT NULL,
                        mention_text TEXT NOT NULL,
                        context_before TEXT,
                        context_after TEXT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        FOREIGN KEY (entity_id) REFERENCES entity_memory (id)
                    )
                """)
                
                conn.commit()
                logger.debug("Database tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _load_entities(self) -> Dict[str, Entity]:
        """Load existing entities from database."""
        entities = {}
        logger.debug(f"Loading entities for user_id={self.user_id}, character_id={self.character_id}")
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, entity_type, aliases, attributes, relationships,
                           first_mentioned, last_mentioned, mention_count, confidence_score
                    FROM entity_memory 
                    WHERE user_id = ? AND character_id = ?
                """, (self.user_id, self.character_id))
                
                for row in cursor.fetchall():
                    entity = Entity(
                        id=row[0],
                        name=row[1],
                        entity_type=EntityType(row[2]),
                        aliases=json.loads(row[3]),
                        attributes=json.loads(row[4]),
                        relationships=json.loads(row[5]),
                        first_mentioned=datetime.fromisoformat(row[6]),
                        last_mentioned=datetime.fromisoformat(row[7]),
                        mention_count=row[8],
                        confidence_score=row[9],
                        user_id=self.user_id
                    )
                    entities[entity.id] = entity
                
                logger.debug(f"Loaded {len(entities)} entities from database")
                
        except Exception as e:
            logger.error(f"Error loading entities: {e}")
        
        return entities
    
    def _load_context_windows(self) -> List[ContextWindow]:
        """Load recent context windows from database."""
        windows = []
        logger.debug(f"Loading context windows for user_id={self.user_id}, character_id={self.character_id}")
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conversation_id, user_id, character_id, recent_entities,
                           current_topic, emotional_context, timestamp
                    FROM context_windows 
                    WHERE user_id = ? AND character_id = ?
                    ORDER BY timestamp DESC LIMIT 5
                """, (self.user_id, self.character_id))
                
                for row in cursor.fetchall():
                    window = ContextWindow(
                        conversation_id=row[0],
                        user_id=row[1],
                        character_id=row[2],
                        recent_entities=json.loads(row[3]),
                        current_topic=row[4] or "",
                        emotional_context=row[5] or "",
                        timestamp=datetime.fromisoformat(row[6])
                    )
                    windows.append(window)
                
                logger.debug(f"Loaded {len(windows)} context windows from database")
                
        except Exception as e:
            logger.error(f"Error loading context windows: {e}")
        
        return windows
    
    def _save_entity(self, entity: Entity):
        """Save entity to database."""
        logger.debug(f"Saving entity: {entity.name} (id: {entity.id})")
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO entity_memory 
                    (id, name, entity_type, aliases, attributes, relationships, 
                     first_mentioned, last_mentioned, mention_count, confidence_score, 
                     user_id, character_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.id, entity.name, entity.entity_type.value,
                    json.dumps(entity.aliases), json.dumps(entity.attributes),
                    json.dumps(entity.relationships), entity.first_mentioned.isoformat(),
                    entity.last_mentioned.isoformat(), entity.mention_count,
                    entity.confidence_score, entity.user_id, self.character_id
                ))
                
                conn.commit()
                logger.debug(f"Successfully saved entity: {entity.name}")
                
        except Exception as e:
            logger.error(f"Error saving entity {entity.name}: {e}")
            raise
    
    def _save_context_window(self, window: ContextWindow):
        """Save context window to database."""
        logger.debug(f"Saving context window for conversation: {window.conversation_id}")
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO context_windows 
                    (conversation_id, user_id, character_id, recent_entities,
                     current_topic, emotional_context, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    window.conversation_id, window.user_id, window.character_id,
                    json.dumps(window.recent_entities), window.current_topic,
                    window.emotional_context, window.timestamp.isoformat()
                ))
                
                conn.commit()
                logger.debug(f"Successfully saved context window for conversation: {window.conversation_id}")
                
        except Exception as e:
            logger.error(f"Error saving context window: {e}")
            raise
    
    def extract_entities(self, message: str, conversation_id: str) -> List[Tuple[Entity, float]]:
        """Extract and disambiguate entities from a message."""
        extracted_entities = []
        logger.debug(f"Extracting entities from message: '{message[:100]}...' for conversation_id={conversation_id}")
        
        # Common entity patterns
        patterns = {
            EntityType.PERSON: [
                # General name introduction patterns
                r'\b(I|i)\s+(am|m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b(Hello|Hi|Hey),?\s+(I|i)\s+(am|m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b(My|my)\s+name\s+(is|s)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b(I|i)\s+(am|m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+I\b',
                # Relationship patterns
                r'\b(my|the)\s+(mom|mother|mum|dad|father|sister|brother|wife|husband|partner|friend|colleague|boss)\b',
                r'\b(I|i)\s+(have|got)\s+(a\s+)?(cat|dog|pet|child|son|daughter)\s+(named|called)\s+(\w+)',
                r'\b(\w+)\s+(is|was)\s+(my|the)\s+(mom|mother|mum|dad|father|sister|brother|wife|husband|partner|friend|colleague|boss)\b',
                r'\b(my|the)\s+(cat|dog|pet|child|son|daughter)\s+(\w+)\b',
                r'\b(\w+)\s+(is|was)\s+(my|the)\s+(cat|dog|pet|child|son|daughter)\b',
                # Occupation patterns
                r'\b(\w+)\s+(works?\s+as|is\s+a|is\s+an)\s+(\w+(?:\s+\w+)*)\b',
                r'\b(\w+)\s+(is|was)\s+(\d+)\s+years?\s+old\b'
            ],
            EntityType.PET: [
                r'\b(my|the)\s+(cat|dog|pet)\s+(named|called)\s+(\w+)',
                r'\b(\w+)\s+(is|was)\s+(my|the)\s+(cat|dog|pet)\b',
                r'\b(I|i)\s+(have|got)\s+(a\s+)?(cat|dog|pet)\s+(named|called)\s+(\w+)'
            ],
            EntityType.PLACE: [
                r'\b(I|i)\s+(live|work|study)\s+(in|at)\s+(\w+)',
                r'\b(\w+)\s+(is|was)\s+(where|the\s+place)\s+(I|i)\s+(live|work|study)\b'
            ],
            EntityType.PROJECT: [
                r'\b(my|the)\s+(project|work|job|assignment)\s+(is|was)\s+(\w+)',
                r'\b(I|i)\s+(am|was)\s+(working\s+on|doing)\s+(a\s+)?(\w+)'
            ]
        }
        
        # Extract potential entities
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    # Extract the entity name and context
                    entity_name = self._extract_entity_name(match, message)
                    if entity_name:
                        logger.debug(f"Found potential entity: '{entity_name}' of type {entity_type.value}")
                        
                        # Check if this entity already exists
                        existing_entity = self._find_existing_entity(entity_name, entity_type)
                        
                        if existing_entity:
                            # Update existing entity
                            logger.debug(f"Updating existing entity: {existing_entity.name}")
                            existing_entity.last_mentioned = datetime.now()
                            existing_entity.mention_count += 1
                            self._save_entity(existing_entity)
                            extracted_entities.append((existing_entity, 1.0))
                        else:
                            # Create new entity
                            logger.debug(f"Creating new entity: {entity_name}")
                            new_entity = self._create_new_entity(entity_name, entity_type, match, message)
                            if new_entity:
                                self.entities[new_entity.id] = new_entity
                                self._save_entity(new_entity)
                                extracted_entities.append((new_entity, 0.8))
        
        logger.debug(f"Extracted {len(extracted_entities)} entities from message")
        return extracted_entities
    
    def _extract_entity_name(self, match, message: str) -> Optional[str]:
        """Extract the actual entity name from a regex match."""
        groups = match.groups()
        
        # Common words to exclude from entity names
        exclude_words = {
            'my', 'the', 'is', 'was', 'have', 'got', 'a', 'named', 'called',
            'i', 'am', 'm', 'hello', 'hi', 'hey', 'and', 'in', 'at', 'on',
            'with', 'to', 'for', 'of', 'from', 'by', 'as', 'like', 'this',
            'that', 'these', 'those', 'here', 'there', 'where', 'when', 'why',
            'how', 'what', 'who', 'which', 'whose', 'whom'
        }
        
        # For name introduction patterns, the name is typically in the last group
        # Look for the actual name in the groups, prioritizing later groups
        for i, group in enumerate(reversed(groups)):
            if group and group.lower() not in exclude_words:
                # Check if this looks like a proper name (starts with capital letter)
                if group[0].isupper() and len(group) > 1:
                    return group.strip()
        
        # If no clear name found, try to extract from context
        start, end = match.span()
        context_before = message[max(0, start-50):start]
        context_after = message[end:min(len(message), end+50)]
        
        # Look for names in context (proper names starting with capital letters)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        names_before = re.findall(name_pattern, context_before)
        names_after = re.findall(name_pattern, context_after)
        
        if names_before:
            return names_before[-1]
        elif names_after:
            return names_after[0]
        
        return None
    
    def _find_existing_entity(self, name: str, entity_type: EntityType) -> Optional[Entity]:
        """Find an existing entity by name and type."""
        name_lower = name.lower()
        
        for entity in self.entities.values():
            if entity.entity_type == entity_type:
                if (name_lower == entity.name.lower() or 
                    name_lower in [alias.lower() for alias in entity.aliases]):
                    return entity
        
        return None
    
    def _create_new_entity(self, name: str, entity_type: EntityType, match, message: str) -> Optional[Entity]:
        """Create a new entity from extracted information."""
        entity_id = self._generate_entity_id(name, entity_type)
        
        # Extract attributes from context
        attributes = self._extract_attributes(match, message, entity_type)
        
        # Determine relationships
        relationships = self._determine_relationships(match, message, entity_type)
        
        entity = Entity(
            id=entity_id,
            name=name,
            entity_type=entity_type,
            aliases=[name],
            attributes=attributes,
            relationships=relationships,
            first_mentioned=datetime.now(),
            last_mentioned=datetime.now(),
            mention_count=1,
            confidence_score=0.8,
            user_id=self.user_id
        )
        
        return entity
    
    def _generate_entity_id(self, name: str, entity_type: EntityType) -> str:
        """Generate a unique entity ID."""
        base = f"{self.user_id}_{entity_type.value}_{name.lower()}"
        return hashlib.md5(base.encode()).hexdigest()[:12]
    
    def _extract_attributes(self, match, message: str, entity_type: EntityType) -> Dict[str, Any]:
        """Extract attributes from the context."""
        attributes = {}
        
        if entity_type == EntityType.PERSON:
            # Extract relationship type
            if 'mom' in match.group().lower() or 'mother' in match.group().lower():
                attributes['relationship'] = 'mother'
            elif 'dad' in match.group().lower() or 'father' in match.group().lower():
                attributes['relationship'] = 'father'
            elif 'sister' in match.group().lower():
                attributes['relationship'] = 'sister'
            elif 'brother' in match.group().lower():
                attributes['relationship'] = 'brother'
            elif 'wife' in match.group().lower():
                attributes['relationship'] = 'wife'
            elif 'husband' in match.group().lower():
                attributes['relationship'] = 'husband'
            elif 'friend' in match.group().lower():
                attributes['relationship'] = 'friend'
            elif 'colleague' in match.group().lower():
                attributes['relationship'] = 'colleague'
            
            # Extract occupation
            occupation_match = re.search(r'works?\s+as\s+(\w+(?:\s+\w+)*)\b', message, re.IGNORECASE)
            if occupation_match:
                attributes['occupation'] = occupation_match.group(1).strip()
            else:
                occupation_match = re.search(r'is\s+(?:a|an)\s+(\w+(?:\s+\w+)*)', message, re.IGNORECASE)
                if occupation_match:
                    attributes['occupation'] = occupation_match.group(1).strip()
            
            # Extract age
            age_match = re.search(r'(\d+)\s+years?\s+old', message, re.IGNORECASE)
            if age_match:
                attributes['age'] = age_match.group(1)
        
        elif entity_type == EntityType.PET:
            # Extract pet type
            if 'cat' in match.group().lower():
                attributes['species'] = 'cat'
            elif 'dog' in match.group().lower():
                attributes['species'] = 'dog'
            else:
                attributes['species'] = 'pet'
        
        return attributes
    
    def _determine_relationships(self, match, message: str, entity_type: EntityType) -> Dict[str, List[str]]:
        """Determine relationships with other entities."""
        relationships = {}
        
        # For now, just track the user as the primary relationship
        if entity_type in [EntityType.PERSON, EntityType.PET]:
            relationships['associated_with'] = [self.user_id]
        
        return relationships
    
    def resolve_ambiguous_reference(self, reference: str, conversation_context: str) -> Optional[Entity]:
        """Resolve ambiguous references like 'she', 'he', 'it', 'they'."""
        # Get recent entities from context
        recent_entities = self._get_recent_entities_from_context(conversation_context)
        
        if not recent_entities:
            return None
        
        # Determine the most likely referent based on:
        # 1. Recency in conversation
        # 2. Grammatical gender/type matching
        # 3. Contextual relevance
        
        for entity in recent_entities:
            if self._matches_reference(entity, reference, conversation_context):
                return entity
        
        return None
    
    def _get_recent_entities_from_context(self, context: str) -> List[Entity]:
        """Get entities mentioned in recent context."""
        # This is a simplified version - in practice, you'd want more sophisticated
        # context analysis
        recent_entities = []
        
        for entity in self.entities.values():
            # Check if entity was mentioned in recent context
            if entity.name.lower() in context.lower():
                recent_entities.append(entity)
        
        # Sort by last mentioned time
        recent_entities.sort(key=lambda e: e.last_mentioned, reverse=True)
        
        return recent_entities[:5]  # Return top 5 most recent
    
    def _matches_reference(self, entity: Entity, reference: str, context: str) -> bool:
        """Check if an entity matches a reference."""
        reference_lower = reference.lower()
        
        # Direct name matching gets highest priority
        if entity.name.lower() in context.lower()[-200:]:  # Check recent context
            entity_position = context.lower().rfind(entity.name.lower())
            reference_position = context.lower().rfind(reference_lower)
            
            # If reference appears after entity mention, likely referring to it
            if reference_position > entity_position:
                return True
        
        # Gender matching for pronouns
        if reference_lower in ['she', 'her', 'hers']:
            # Check if entity is likely female
            if entity.entity_type == EntityType.PERSON:
                # Female indicators
                female_indicators = ['mother', 'mom', 'sister', 'wife', 'daughter', 'girlfriend', 'aunt', 'grandmother', 'grandma']
                relationship = entity.attributes.get('relationship', '').lower()
                if any(indicator in relationship for indicator in female_indicators):
                    return True
                
                # Check name patterns (common female names)
                female_names = ['sarah', 'emily', 'jessica', 'amanda', 'jennifer', 'michelle', 'lisa', 'karen', 'nancy', 'betty', 'helen', 'donna', 'carol', 'ruth', 'sharon', 'maria', 'mary', 'patricia', 'linda', 'barbara', 'elizabeth', 'susan', 'anna', 'evelyn']
                if any(name in entity.name.lower() for name in female_names):
                    return True
        
        elif reference_lower in ['he', 'his', 'him']:
            # Check if entity is likely male
            if entity.entity_type == EntityType.PERSON:
                # Male indicators
                male_indicators = ['father', 'dad', 'brother', 'husband', 'son', 'boyfriend', 'uncle', 'grandfather', 'grandpa']
                relationship = entity.attributes.get('relationship', '').lower()
                if any(indicator in relationship for indicator in male_indicators):
                    return True
                
                # Check name patterns (common male names)
                male_names = ['john', 'michael', 'david', 'william', 'richard', 'charles', 'joseph', 'thomas', 'christopher', 'daniel', 'paul', 'mark', 'donald', 'george', 'kenneth', 'steven', 'edward', 'brian', 'ronald', 'anthony', 'kevin', 'jason', 'matthew', 'gary', 'timothy', 'jose', 'alex', 'max', 'james', 'robert']
                if any(name in entity.name.lower() for name in male_names):
                    return True
        
        elif reference_lower in ['it', 'its']:
            # Check if entity is an object, pet, or inanimate
            if entity.entity_type in [EntityType.PET, EntityType.OBJECT, EntityType.PLACE, EntityType.CONCEPT]:
                return True
            # Animals generally referred to as "it" unless explicitly gendered
            if entity.entity_type == EntityType.PET:
                species = entity.attributes.get('species', '').lower()
                if species in ['cat', 'dog', 'bird', 'fish', 'rabbit', 'hamster']:
                    return True
        
        elif reference_lower in ['they', 'them', 'their']:
            # "They" can refer to groups, organizations, or gender-neutral individuals
            if entity.entity_type in [EntityType.PERSON, EntityType.CONCEPT]:
                # Check for group indicators
                group_indicators = ['team', 'company', 'organization', 'family', 'group', 'people']
                if any(indicator in entity.name.lower() for indicator in group_indicators):
                    return True
                # Also accept as fallback for any person if no other matches
                return True
        
        # Context-based matching - if entity was mentioned recently
        recent_context = context.lower()[-300:]  # Look at last 300 characters
        if entity.name.lower() in recent_context:
            # Calculate distance between entity mention and pronoun
            entity_pos = recent_context.rfind(entity.name.lower())
            ref_pos = recent_context.rfind(reference_lower)
            
            # If pronoun appears within reasonable distance after entity mention
            if ref_pos > entity_pos and (ref_pos - entity_pos) < 100:
                return True
        
        # Alias matching
        for alias in entity.aliases:
            if alias.lower() in recent_context:
                return True
        
        # Special case: pets with common pet names
        if entity.entity_type == EntityType.PET and reference_lower in ['he', 'she', 'it']:
            pet_male_names = ['max', 'buddy', 'charlie', 'jack', 'cooper', 'rocky', 'bear', 'duke', 'tucker', 'oliver']
            pet_female_names = ['bella', 'lucy', 'molly', 'daisy', 'maggie', 'sophie', 'sadie', 'chloe', 'bailey', 'luna']
            
            if reference_lower in ['he', 'him'] and any(name in entity.name.lower() for name in pet_male_names):
                return True
            elif reference_lower in ['she', 'her'] and any(name in entity.name.lower() for name in pet_female_names):
                return True
            elif reference_lower == 'it':  # Default for pets when gender unclear
                return True
        
        return False
    
    def update_context_window(self, conversation_id: str, message: str, 
                            extracted_entities: List[Entity], emotional_context: str = ""):
        """Update the current context window."""
        logger.debug(f"Updating context window for conversation_id={conversation_id} with {len(extracted_entities)} entities")
        
        # Get entity IDs
        entity_ids = [entity.id for entity in extracted_entities]
        
        # Create or update context window
        window = ContextWindow(
            conversation_id=conversation_id,
            user_id=self.user_id,
            character_id=self.character_id,
            recent_entities=entity_ids,
            current_topic=self._extract_topic(message),
            emotional_context=emotional_context,
            timestamp=datetime.now()
        )
        
        # Save to database
        self._save_context_window(window)
        
        # Update in-memory list
        self.context_windows.append(window)
        if len(self.context_windows) > 5:
            self.context_windows.pop(0)
        
        logger.debug(f"Context window updated successfully for conversation_id={conversation_id}")
    
    def _extract_topic(self, message: str) -> str:
        """Extract the main topic from a message."""
        # Simple topic extraction - in practice, you'd want more sophisticated NLP
        topics = []
        
        if any(word in message.lower() for word in ['work', 'job', 'career']):
            topics.append('work')
        if any(word in message.lower() for word in ['family', 'mom', 'dad', 'parents']):
            topics.append('family')
        if any(word in message.lower() for word in ['pet', 'cat', 'dog']):
            topics.append('pets')
        if any(word in message.lower() for word in ['health', 'sick', 'doctor']):
            topics.append('health')
        if any(word in message.lower() for word in ['project', 'hobby', 'interest']):
            topics.append('projects')
        
        topic = ', '.join(topics) if topics else 'general'
        logger.debug(f"Extracted topic '{topic}' from message: '{message[:50]}...'")
        return topic
    
    def get_entity_summary(self) -> str:
        """Generate a summary of all entities for this user."""
        if not self.entities:
            return f"No entities stored for user {self.user_id}"
        
        summary = f"🎭 ENTITY MEMORY SUMMARY\n"
        summary += f"User: {self.user_id}\n"
        summary += f"Character: {self.character_id}\n"
        summary += f"Total Entities: {len(self.entities)}\n\n"
        
        # Group by entity type
        by_type = {}
        for entity in self.entities.values():
            if entity.entity_type not in by_type:
                by_type[entity.entity_type] = []
            by_type[entity.entity_type].append(entity)
        
        for entity_type, entities in by_type.items():
            summary += f"📋 {entity_type.value.upper()}S ({len(entities)}):\n"
            for entity in entities:
                summary += f"  • {entity.name}"
                if entity.attributes:
                    attrs = []
                    for key, value in entity.attributes.items():
                        attrs.append(f"{key}: {value}")
                    summary += f" ({', '.join(attrs)})"
                summary += f" (mentioned {entity.mention_count} times)\n"
            summary += "\n"
        
        return summary
    
    def get_clarification_prompt(self, ambiguous_reference: str, context: str) -> str:
        """Generate a clarification prompt for ambiguous references."""
        recent_entities = self._get_recent_entities_from_context(context)
        
        if not recent_entities:
            return ""
        
        prompt = f"I want to make sure I understand correctly. When you say '{ambiguous_reference}', are you referring to:\n"
        
        for i, entity in enumerate(recent_entities[:3], 1):
            relationship = entity.attributes.get('relationship', '')
            entity_type = entity.entity_type.value
            
            if relationship:
                prompt += f"{i}. {entity.name} (your {relationship})\n"
            elif entity_type == 'pet':
                species = entity.attributes.get('species', 'pet')
                prompt += f"{i}. {entity.name} (your {species})\n"
            else:
                prompt += f"{i}. {entity.name} ({entity_type})\n"
        
        prompt += "4. Someone/something else (please clarify)\n\n"
        prompt += "Please let me know which one you mean so I can respond appropriately."
        
        return prompt
    
    def get_all_entities(self, user_id: str = None) -> List[Entity]:
        """Get all entities for a specific user."""
        target_user_id = user_id if user_id else self.user_id
        logger.debug(f"Getting all entities for user_id={target_user_id}")
        
        entities = []
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, entity_type, aliases, attributes, relationships,
                           first_mentioned, last_mentioned, mention_count, confidence_score
                    FROM entity_memory 
                    WHERE user_id = ?
                """, (target_user_id,))
                
                for row in cursor.fetchall():
                    entity = Entity(
                        id=row[0],
                        name=row[1],
                        entity_type=EntityType(row[2]),
                        aliases=json.loads(row[3]),
                        attributes=json.loads(row[4]),
                        relationships=json.loads(row[5]),
                        first_mentioned=datetime.fromisoformat(row[6]),
                        last_mentioned=datetime.fromisoformat(row[7]),
                        mention_count=row[8],
                        confidence_score=row[9],
                        user_id=target_user_id
                    )
                    entities.append(entity)
                
                logger.debug(f"Retrieved {len(entities)} entities for user_id={target_user_id}")
                
        except Exception as e:
            logger.error(f"Error getting entities for user_id={target_user_id}: {e}")
        
        return entities
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID."""
        logger.debug(f"Getting entity by ID: {entity_id}")
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, entity_type, aliases, attributes, relationships,
                           first_mentioned, last_mentioned, mention_count, confidence_score, user_id
                    FROM entity_memory 
                    WHERE id = ?
                """, (entity_id,))
                
                row = cursor.fetchone()
                if row:
                    entity = Entity(
                        id=row[0],
                        name=row[1],
                        entity_type=EntityType(row[2]),
                        aliases=json.loads(row[3]),
                        attributes=json.loads(row[4]),
                        relationships=json.loads(row[5]),
                        first_mentioned=datetime.fromisoformat(row[6]),
                        last_mentioned=datetime.fromisoformat(row[7]),
                        mention_count=row[8],
                        confidence_score=row[9],
                        user_id=row[10]
                    )
                    logger.debug(f"Found entity: {entity.name}")
                    return entity
                else:
                    logger.debug(f"Entity not found with ID: {entity_id}")
                    return None
                
        except Exception as e:
            logger.error(f"Error getting entity by ID {entity_id}: {e}")
            return None
