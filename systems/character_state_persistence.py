"""
Character State Persistence System
Maintains character emotional states, conversation context, and personality evolution
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CharacterState:
    """Character state data structure"""
    character_id: str
    user_id: str
    current_mood: str
    mood_intensity: float
    conversation_context: str
    personality_evolution: Dict[str, Any]
    last_interaction: str
    emotional_trajectory: List[Dict[str, Any]]
    relationship_context: Dict[str, Any]
    created_at: str
    updated_at: str

class CharacterStatePersistence:
    """Manages character state persistence across sessions"""
    
    def __init__(self, db_path: str = "memory_new/db/character_states.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the character state database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS character_states (
                        character_id TEXT,
                        user_id TEXT,
                        current_mood TEXT,
                        mood_intensity REAL,
                        conversation_context TEXT,
                        personality_evolution TEXT,
                        last_interaction TEXT,
                        emotional_trajectory TEXT,
                        relationship_context TEXT,
                        created_at TEXT,
                        updated_at TEXT,
                        PRIMARY KEY (character_id, user_id)
                    )
                """)
                conn.commit()
            logger.info(f"✅ Character state database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize character state database: {e}")
    
    def save_state(self, character_id: str, user_id: str, state: CharacterState) -> bool:
        """Save character state to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO character_states 
                    (character_id, user_id, current_mood, mood_intensity, conversation_context,
                     personality_evolution, last_interaction, emotional_trajectory, 
                     relationship_context, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_id, user_id, state.current_mood, state.mood_intensity,
                    state.conversation_context, json.dumps(state.personality_evolution),
                    state.last_interaction, json.dumps(state.emotional_trajectory),
                    json.dumps(state.relationship_context), state.created_at, state.updated_at
                ))
                conn.commit()
            logger.info(f"✅ Character state saved for {character_id}_{user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save character state: {e}")
            return False
    
    def load_state(self, character_id: str, user_id: str) -> Optional[CharacterState]:
        """Load character state from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM character_states 
                    WHERE character_id = ? AND user_id = ?
                """, (character_id, user_id))
                row = cursor.fetchone()
                
                if row:
                    return CharacterState(
                        character_id=row[0],
                        user_id=row[1],
                        current_mood=row[2],
                        mood_intensity=row[3],
                        conversation_context=row[4],
                        personality_evolution=json.loads(row[5]),
                        last_interaction=row[6],
                        emotional_trajectory=json.loads(row[7]),
                        relationship_context=json.loads(row[8]),
                        created_at=row[9],
                        updated_at=row[10]
                    )
                return None
        except Exception as e:
            logger.error(f"❌ Failed to load character state: {e}")
            return None
    
    def update_mood(self, character_id: str, user_id: str, mood: str, intensity: float) -> bool:
        """Update character mood"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE character_states 
                    SET current_mood = ?, mood_intensity = ?, updated_at = ?
                    WHERE character_id = ? AND user_id = ?
                """, (mood, intensity, datetime.now().isoformat(), character_id, user_id))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update mood: {e}")
            return False
    
    def add_emotional_event(self, character_id: str, user_id: str, event: Dict[str, Any]) -> bool:
        """Add emotional event to trajectory"""
        try:
            state = self.load_state(character_id, user_id)
            if state:
                state.emotional_trajectory.append(event)
                state.updated_at = datetime.now().isoformat()
                return self.save_state(character_id, user_id, state)
            return False
        except Exception as e:
            logger.error(f"❌ Failed to add emotional event: {e}")
            return False
    
    def get_emotional_trajectory(self, character_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get emotional trajectory for character"""
        state = self.load_state(character_id, user_id)
        return state.emotional_trajectory if state else []
    
    def create_default_state(self, character_id: str, user_id: str) -> CharacterState:
        """Create default character state"""
        now = datetime.now().isoformat()
        return CharacterState(
            character_id=character_id,
            user_id=user_id,
            current_mood="neutral",
            mood_intensity=0.5,
            conversation_context="",
            personality_evolution={},
            last_interaction=now,
            emotional_trajectory=[],
            relationship_context={},
            created_at=now,
            updated_at=now
        ) 