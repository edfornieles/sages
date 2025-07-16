#!/usr/bin/env python3
"""
Memory System Critical Fixes Patch

This patch addresses the critical memory system failures:
1. DISABLES destructive compression that destroys content
2. Implements proper memory correction when users provide updates  
3. Fixes character state persistence across sessions
4. Adds relationship context loading at session start
5. Creates memory importance ranking to preserve key details
6. Maintains mood and character consistency

Apply this patch by importing and calling apply_memory_fixes()
"""

import os
import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

def apply_memory_fixes():
    """Apply critical fixes to the memory system."""
    print("🔧 Applying memory system critical fixes...")
    
    # Import the memory system
    try:
        from enhanced_memory_system import EnhancedMemorySystem
    except ImportError:
        print("❌ Could not import EnhancedMemorySystem")
        return False
    
    # Patch the destructive methods
    _patch_destructive_methods(EnhancedMemorySystem)
    
    # Add new methods for corrections and character state
    _add_correction_methods(EnhancedMemorySystem)
    
    # Add character state persistence
    _add_character_state_methods(EnhancedMemorySystem)
    
    # Add relationship context methods
    _add_relationship_context_methods(EnhancedMemorySystem)
    
    # Fix importance calculation
    _fix_importance_calculation(EnhancedMemorySystem)
    
    print("✅ Memory system fixes applied successfully!")
    return True

def _patch_destructive_methods(cls):
    """Disable destructive compression and deletion methods."""
    
    def safe_compress_old_memories(self, *args, **kwargs):
        """PATCHED: No destructive compression - preserves all content."""
        print("🛡️ Memory compression disabled to prevent content loss")
        # Instead of compressing, move low-importance old memories to summary
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Move very old, low-importance memories to summary (not compressed)
                cutoff_date = datetime.now() - timedelta(days=90)  # Much longer retention
                
                cursor.execute("""
                    UPDATE enhanced_memory 
                    SET memory_type = 'summary'
                    WHERE user_id = ? AND character_id = ? 
                    AND timestamp < ? AND importance_score < 0.2
                    AND memory_type = 'buffer'
                    AND is_compressed = FALSE
                """, (self.user_id, self.character_id, cutoff_date))
                
                moved_count = cursor.rowcount
                conn.commit()
                
                if moved_count > 0:
                    print(f"📁 Moved {moved_count} old memories to summary (no data loss)")
                
                return moved_count
        except Exception as e:
            print(f"Error in safe memory archiving: {e}")
            return 0
    
    def safe_delete_memories(self, *args, **kwargs):
        """PATCHED: No memory deletion to prevent data loss."""
        print("🛡️ Memory deletion disabled to prevent data loss")
        return 0
    
    # Apply patches
    cls.compress_old_memories = safe_compress_old_memories
    cls.delete_old_memories = safe_delete_memories
    
    print("🔒 Destructive memory operations disabled")

def _add_correction_methods(cls):
    """Add memory correction methods."""
    
    def detect_memory_correction(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect if user is correcting previous information."""
        correction_patterns = [
            r"(?:actually|no|wait),?\s*(?:my|the)?\s*(.+?)\s+(?:is|are|was|were)\s+(.+)",
            r"(?:that's wrong|that's incorrect|not true),?\s*(.+?)\s+(?:is|are)\s+(.+)",
            r"(?:correction|actually|let me correct that):?\s*(.+)",
            r"(?:my\s+)?(.+?)\s+(?:is|are)\s+(.+?),?\s+not\s+(.+)",
        ]
        
        for pattern in correction_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return {
                    "type": "correction",
                    "original_message": message,
                    "correction_match": match.groups()
                }
        return None
    
    def handle_memory_correction(self, correction_info: Dict, message: str, 
                               conversation_id: str, emotional_context: str = "") -> Dict[str, Any]:
        """Handle memory corrections properly without losing information."""
        
        # Find related memories to correct
        related_memories = self._find_memories_for_correction(correction_info)
        
        # Create correction entry with high importance
        correction_id = f"CORRECTION_{self._generate_memory_id(message, conversation_id)}"
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Insert correction memory
                cursor.execute("""
                    INSERT INTO enhanced_memory (
                        id, character_id, user_id, content, memory_type,
                        importance_score, emotional_context, conversation_id,
                        timestamp, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    correction_id, self.character_id, self.user_id, 
                    f"CORRECTION: {message}", "correction", 0.95,
                    emotional_context, conversation_id, datetime.now().isoformat(),
                    json.dumps({
                        "correction_type": correction_info["type"],
                        "original_message": message,
                        "corrected_memories": [m["id"] for m in related_memories]
                    }),
                    datetime.now().isoformat()
                ))
                
                # Mark related memories as corrected (don't delete)
                for memory in related_memories:
                    cursor.execute("""
                        UPDATE enhanced_memory 
                        SET metadata = json_set(
                            COALESCE(metadata, '{}'), 
                            '$.corrected_by', ?
                        )
                        WHERE id = ?
                    """, (correction_id, memory["id"]))
                
                conn.commit()
                
                print(f"✅ Applied correction: {len(related_memories)} memories corrected")
                
                return {
                    "memory_id": correction_id,
                    "importance_score": 0.95,
                    "is_correction": True,
                    "corrected_memories": len(related_memories)
                }
                
        except Exception as e:
            print(f"Error handling correction: {e}")
            return {"error": str(e)}
    
    def _find_memories_for_correction(self, correction_info: Dict) -> List[Dict]:
        """Find memories that should be corrected."""
        related_memories = []
        
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Search for recent memories that might be corrected
                cursor.execute("""
                    SELECT id, content, importance_score, timestamp FROM enhanced_memory 
                    WHERE user_id = ? AND character_id = ? 
                    AND memory_type = 'buffer'
                    AND timestamp > datetime('now', '-7 days')
                    ORDER BY timestamp DESC LIMIT 20
                """, (self.user_id, self.character_id))
                
                search_terms = correction_info.get("correction_match", [])
                
                for row in cursor.fetchall():
                    memory_id, content, importance, timestamp = row
                    content_lower = content.lower()
                    
                    # Check if any correction terms match this memory
                    for term in search_terms:
                        if term and len(term) > 2 and term.lower() in content_lower:
                            related_memories.append({
                                "id": memory_id,
                                "content": content,
                                "importance": importance,
                                "timestamp": timestamp
                            })
                            break
                
        except Exception as e:
            print(f"Error finding memories for correction: {e}")
        
        return related_memories
    
    # Add methods to class
    cls.detect_memory_correction = detect_memory_correction
    cls.handle_memory_correction = handle_memory_correction
    cls._find_memories_for_correction = _find_memories_for_correction
    
    print("🔧 Memory correction methods added")

def _add_character_state_methods(cls):
    """Add character state persistence methods."""
    
    def save_character_state(self, state_type: str, state_data: Dict):
        """Save character state for persistence across sessions."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Create character_state table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS character_state (
                        id TEXT PRIMARY KEY,
                        character_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        state_type TEXT NOT NULL,
                        state_data TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(character_id, user_id, state_type)
                    )
                """)
                
                state_id = f"{self.character_id}_{self.user_id}_{state_type}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO character_state 
                    (id, character_id, user_id, state_type, state_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    state_id, self.character_id, self.user_id, state_type,
                    json.dumps(state_data), datetime.now().isoformat()
                ))
                
                conn.commit()
                print(f"💾 Character state saved: {state_type}")
                
        except Exception as e:
            print(f"Error saving character state: {e}")
    
    def load_character_state(self, state_type: str = None) -> Dict[str, Any]:
        """Load character state for session persistence."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                if state_type:
                    cursor.execute("""
                        SELECT state_data FROM character_state 
                        WHERE character_id = ? AND user_id = ? AND state_type = ?
                        ORDER BY timestamp DESC LIMIT 1
                    """, (self.character_id, self.user_id, state_type))
                    
                    row = cursor.fetchone()
                    if row:
                        return json.loads(row[0])
                else:
                    cursor.execute("""
                        SELECT state_type, state_data FROM character_state 
                        WHERE character_id = ? AND user_id = ?
                        ORDER BY timestamp DESC
                    """, (self.character_id, self.user_id))
                    
                    states = {}
                    for state_type, state_data in cursor.fetchall():
                        try:
                            states[state_type] = json.loads(state_data)
                        except:
                            continue
                    return states
                    
        except Exception as e:
            print(f"Error loading character state: {e}")
        
        return {}
    
    # Add methods to class
    cls.save_character_state = save_character_state
    cls.load_character_state = load_character_state
    
    print("🎭 Character state persistence methods added")

def _add_relationship_context_methods(cls):
    """Add relationship context methods."""
    
    def save_relationship_context(self, context_type: str, context_data: Dict, importance: float = 0.5):
        """Save relationship context for session start loading."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Create relationship_context table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS relationship_context (
                        id TEXT PRIMARY KEY,
                        character_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        context_type TEXT NOT NULL,
                        context_data TEXT NOT NULL,
                        importance_score REAL DEFAULT 0.5,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                context_id = f"{self.character_id}_{self.user_id}_{context_type}"
                
                cursor.execute("""
                    INSERT OR REPLACE INTO relationship_context 
                    (id, character_id, user_id, context_type, context_data, importance_score, timestamp, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    context_id, self.character_id, self.user_id, context_type,
                    json.dumps(context_data), importance, 
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                
                conn.commit()
                print(f"💕 Relationship context saved: {context_type}")
                
        except Exception as e:
            print(f"Error saving relationship context: {e}")
    
    def load_relationship_context(self) -> Dict[str, Any]:
        """Load relationship context for session start."""
        try:
            with sqlite3.connect(self.memory_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT context_type, context_data, importance_score, last_updated 
                    FROM relationship_context 
                    WHERE character_id = ? AND user_id = ?
                    ORDER BY importance_score DESC, last_updated DESC
                """, (self.character_id, self.user_id))
                
                contexts = {}
                for context_type, context_data, importance, last_updated in cursor.fetchall():
                    try:
                        contexts[context_type] = {
                            'data': json.loads(context_data),
                            'importance': importance,
                            'last_updated': last_updated
                        }
                    except:
                        continue
                
                return contexts
                
        except Exception as e:
            print(f"Error loading relationship context: {e}")
        
        return {}
    
    # Add methods to class
    cls.save_relationship_context = save_relationship_context
    cls.load_relationship_context = load_relationship_context
    
    print("💕 Relationship context methods added")

def _fix_importance_calculation(cls):
    """Fix importance calculation to better preserve key details."""
    
    def calculate_importance_fixed(self, message: str, entities: List = None, 
                                 emotional_context: str = "") -> float:
        """Fixed importance calculation that better preserves key details."""
        base_importance = 0.5
        
        # Emotional context significantly increases importance
        if emotional_context:
            base_importance += 0.3
        
        # Personal information is critical
        personal_patterns = [
            r"my name is", r"i am", r"i have", r"my family", r"my sister", 
            r"my brother", r"my parents", r"i live", r"i work", r"i like",
            r"i don't like", r"i feel", r"i think"
        ]
        
        for pattern in personal_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                base_importance += 0.4
                break
        
        # Corrections are absolutely critical
        correction_indicators = ["actually", "correction", "no that's wrong", 
                               "let me correct", "that's not right"]
        for indicator in correction_indicators:
            if indicator in message.lower():
                base_importance += 0.5
                break
        
        # Questions are important for understanding user needs
        if "?" in message:
            base_importance += 0.2
        
        # Relationship information is very important
        relationship_patterns = [
            r"we are", r"our relationship", r"you make me", r"i trust",
            r"i don't trust", r"i love", r"i hate"
        ]
        
        for pattern in relationship_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                base_importance += 0.3
                break
        
        # Family information is critical
        if any(word in message.lower() for word in ["sister", "brother", "mother", "father", "family"]):
            base_importance += 0.4
        
        return min(1.0, base_importance)
    
    # Replace the importance calculation method
    cls._calculate_importance = calculate_importance_fixed
    
    print("📊 Importance calculation fixed")

def patch_enhanced_memory_process_message(cls):
    """Patch the process_message method to handle corrections."""
    
    original_process_message = cls.process_message
    
    def process_message_with_corrections(self, message: str, conversation_id: str, 
                                       emotional_context: str = "") -> Dict[str, Any]:
        """Enhanced process_message that handles corrections."""
        
        # Check for memory corrections first
        correction_info = self.detect_memory_correction(message)
        
        if correction_info:
            print(f"🔧 Detected memory correction: {message}")
            return self.handle_memory_correction(
                correction_info, message, conversation_id, emotional_context
            )
        
        # Process normally but with fixed importance calculation
        result = original_process_message(self, message, conversation_id, emotional_context)
        
        # Save any character mood state if available
        if hasattr(self, 'current_mood') and self.current_mood:
            self.save_character_state("current_mood", {
                "mood": self.current_mood,
                "context": message,
                "timestamp": datetime.now().isoformat()
            })
        
        return result
    
    cls.process_message = process_message_with_corrections
    
    print("🔄 Process message method patched for corrections")

# Apply all patches when this module is imported
if __name__ != "__main__":
    try:
        apply_memory_fixes()
        
        # Also patch the process_message method
        from enhanced_memory_system import EnhancedMemorySystem
        patch_enhanced_memory_process_message(EnhancedMemorySystem)
        
    except Exception as e:
        print(f"Error applying memory fixes: {e}")

def create_memory_with_fixes(character_id: str, user_id: str, memory_db_path: Path):
    """Create an EnhancedMemorySystem instance with all fixes applied."""
    from enhanced_memory_system import EnhancedMemorySystem
    
    # Apply fixes if not already applied
    apply_memory_fixes()
    patch_enhanced_memory_process_message(EnhancedMemorySystem)
    
    # Create instance
    memory_system = EnhancedMemorySystem(character_id, user_id, memory_db_path)
    
    # Load character state and relationship context
    character_state = memory_system.load_character_state()
    relationship_context = memory_system.load_relationship_context()
    
    print(f"🎭 Loaded character state: {len(character_state)} states")
    print(f"💕 Loaded relationship context: {len(relationship_context)} contexts")
    
    return memory_system 