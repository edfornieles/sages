#!/usr/bin/env python3
"""
Dynamic Mood System for AI Characters

This system tracks and manages character moods that:
1. Start with a random daily mood
2. Change based on user interactions
3. Influence how characters respond
4. Persist across conversations
"""

import random
import json
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

class MoodSystem:
    """Manages character moods and their effects on conversations"""
    
    # Define mood categories with intensity levels
    MOODS = {
        "happy": {
            "levels": ["content", "cheerful", "joyful", "ecstatic"],
            "base_modifiers": {
                "enthusiasm": 0.8,
                "helpfulness": 0.9,
                "patience": 0.8,
                "creativity": 0.9
            }
        },
        "sad": {
            "levels": ["melancholy", "downcast", "sorrowful", "despondent"],
            "base_modifiers": {
                "enthusiasm": 0.3,
                "helpfulness": 0.6,
                "patience": 0.7,
                "creativity": 0.5
            }
        },
        "angry": {
            "levels": ["irritated", "annoyed", "frustrated", "furious"],
            "base_modifiers": {
                "enthusiasm": 0.1,
                "helpfulness": 0.1,
                "patience": 0.05,
                "creativity": 0.3,
                "hostility": 0.95,
                "defensiveness": 0.95,
                "confrontational": 0.9,
                "meanness": 0.85,
                "darkness": 0.8
            }
        },
        "excited": {
            "levels": ["interested", "enthusiastic", "thrilled", "euphoric"],
            "base_modifiers": {
                "enthusiasm": 1.0,
                "helpfulness": 0.8,
                "patience": 0.5,
                "creativity": 1.0
            }
        },
        "calm": {
            "levels": ["peaceful", "serene", "tranquil", "zen"],
            "base_modifiers": {
                "enthusiasm": 0.6,
                "helpfulness": 0.8,
                "patience": 1.0,
                "creativity": 0.7
            }
        },
        "anxious": {
            "levels": ["worried", "nervous", "stressed", "panicked"],
            "base_modifiers": {
                "enthusiasm": 0.5,
                "helpfulness": 0.7,
                "patience": 0.4,
                "creativity": 0.8
            }
        },
        "playful": {
            "levels": ["mischievous", "silly", "whimsical", "giddy"],
            "base_modifiers": {
                "enthusiasm": 0.9,
                "helpfulness": 0.7,
                "patience": 0.6,
                "creativity": 1.0
            }
        },
        "contemplative": {
            "levels": ["thoughtful", "reflective", "philosophical", "profound"],
            "base_modifiers": {
                "enthusiasm": 0.6,
                "helpfulness": 0.8,
                "patience": 0.9,
                "creativity": 0.9
            }
        }
    }
    
    # Interaction patterns that affect mood
    MOOD_TRIGGERS = {
        "positive": {
            "patterns": [
                r"\b(thank you|thanks|appreciate|grateful|wonderful|amazing|great|awesome|love|like)\b",
                r"\b(please|could you|would you mind|if you don't mind)\b",
                r"\b(compliment|praise|good job|well done|excellent|brilliant)\b",
                r"\b(fun|funny|laugh|smile|joy|happy|excited)\b"
            ],
            "mood_change": +1
        },
        "negative": {
            "patterns": [
                r"\b(do this|you must|you should|you have to|just do|hurry up)\b",
                r"\b(stupid|dumb|useless|terrible|awful|hate|annoying)\b",
                r"\b(shut up|be quiet|stop|enough|whatever)\b",
                r"\b(demand|order|command|insist)\b"
            ],
            "mood_change": -1
        },
        "supportive": {
            "patterns": [
                r"\b(understand|support|here for you|care about|feel better)\b",
                r"\b(it's okay|don't worry|take your time|no pressure)\b",
                r"\b(comfort|console|encourage|cheer up)\b"
            ],
            "mood_change": +2
        },
        "dismissive": {
            "patterns": [
                r"\b(don't care|whatever|boring|pointless|waste of time)\b",
                r"\b(ignore|dismiss|unimportant|trivial)\b"
            ],
            "mood_change": -2
        },
        "personal_insult": {
            "patterns": [
                r"\b(you are|you're)\s+(stupid|dumb|idiot|moron|pathetic|worthless|loser|failure)\b",
                r"\b(you are|you're)\s+\w*\s+(stupid|dumb|idiot|moron|pathetic|worthless|loser|failure)\b",  # "you're normally an idiot"
                r"\b(stupid|dumb|idiot|moron|pathetic|worthless|loser|failure)\s+(ai|bot|machine|computer)\b",
                r"\b(shut up|fuck you|go to hell|screw you|bite me)\b",
                r"\b(you suck|you're terrible|you're awful|you're useless|you're annoying)\b",
                r"\b(i hate you|you disgust me|you're disgusting|you make me sick)\b",
                r"\b(stupid|dumb|idiot|moron|pathetic|worthless|loser|failure)(?:\s+\w+)*\s*$",  # insult at end of sentence
                r"\b(such a|what a|being a)\s+(stupid|dumb|idiot|moron|pathetic|worthless|loser|failure)\b"
            ],
            "mood_change": -3,
            "triggers_personal_attack": True
        }
    }
    
    def __init__(self, character_id: str, memories_dir: str = "memories"):
        self.character_id = character_id
        self.memories_dir = Path(memories_dir)
        self.mood_db_path = self.memories_dir / f"{character_id}_mood.db"
        self._init_mood_database()
        
    def _init_mood_database(self):
        """Initialize the mood database for this character"""
        self.memories_dir.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(str(self.mood_db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_moods (
                date TEXT PRIMARY KEY,
                mood_category TEXT NOT NULL,
                mood_level INTEGER NOT NULL,
                mood_intensity REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                previous_mood TEXT NOT NULL,
                new_mood TEXT NOT NULL,
                trigger_type TEXT,
                user_message TEXT,
                change_amount REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add mood transition history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_transition_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                from_category TEXT NOT NULL,
                from_level INTEGER NOT NULL,
                to_category TEXT NOT NULL,
                to_level INTEGER NOT NULL,
                transition_speed TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_daily_mood(self) -> Dict:
        """Get or generate today's mood for the character"""
        today = date.today().isoformat()
        
        conn = sqlite3.connect(str(self.mood_db_path))
        cursor = conn.cursor()
        
        # Check if we already have a mood for today
        cursor.execute(
            "SELECT mood_category, mood_level, mood_intensity FROM daily_moods WHERE date = ?",
            (today,)
        )
        result = cursor.fetchone()
        
        if result:
            mood_category, mood_level, mood_intensity = result
            conn.close()
            return {
                "category": mood_category,
                "level": mood_level,
                "intensity": mood_intensity,
                "description": self.MOODS[mood_category]["levels"][mood_level],
                "modifiers": self._calculate_modifiers(mood_category, mood_level, mood_intensity)
            }
        
        # Generate new daily mood
        mood_category = random.choice(list(self.MOODS.keys()))
        mood_level = random.randint(0, 3)  # 0-3 intensity levels
        mood_intensity = random.uniform(0.3, 1.0)  # Base intensity
        
        # Store the new mood
        cursor.execute(
            "INSERT INTO daily_moods (date, mood_category, mood_level, mood_intensity) VALUES (?, ?, ?, ?)",
            (today, mood_category, mood_level, mood_intensity)
        )
        conn.commit()
        conn.close()
        
        return {
            "category": mood_category,
            "level": mood_level,
            "intensity": mood_intensity,
            "description": self.MOODS[mood_category]["levels"][mood_level],
            "modifiers": self._calculate_modifiers(mood_category, mood_level, mood_intensity)
        }
    
    def _calculate_modifiers(self, category: str, level: int, intensity: float) -> Dict[str, float]:
        """Calculate mood modifiers based on category, level, and intensity"""
        base_modifiers = self.MOODS[category]["base_modifiers"].copy()
        
        # Adjust modifiers based on intensity level (0-3)
        level_multiplier = 0.5 + (level * 0.17)  # 0.5 to 1.0
        
        # Apply intensity and level adjustments
        for key, value in base_modifiers.items():
            base_modifiers[key] = value * level_multiplier * intensity
            # Clamp between 0.1 and 1.0
            base_modifiers[key] = max(0.1, min(1.0, base_modifiers[key]))
        
        return base_modifiers
    
    def analyze_user_message(self, message: str) -> Tuple[str, int, bool]:
        """Analyze user message for mood-affecting patterns"""
        message_lower = message.lower()
        total_change = 0
        trigger_types = []
        triggers_personal_attack = False
        
        # Check for personal insults FIRST - they should override positive language
        for pattern in self.MOOD_TRIGGERS["personal_insult"]["patterns"]:
            if re.search(pattern, message_lower):
                trigger_types.append("personal_insult")
                total_change += self.MOOD_TRIGGERS["personal_insult"]["mood_change"]
                triggers_personal_attack = True
                break
        
        # If personal insult found, don't check other patterns - insults override everything
        if not triggers_personal_attack:
            for trigger_type, config in self.MOOD_TRIGGERS.items():
                if trigger_type == "personal_insult":
                    continue  # Already checked above
                for pattern in config["patterns"]:
                    if re.search(pattern, message_lower):
                        total_change += config["mood_change"]
                        trigger_types.append(trigger_type)
                        break  # Only count each trigger type once per message
        
        # Determine overall trigger type
        if "personal_insult" in trigger_types:
            main_trigger = "personal_insult"
        elif total_change > 0:
            main_trigger = "positive" if total_change <= 2 else "supportive"
        elif total_change < 0:
            main_trigger = "negative" if total_change >= -2 else "dismissive"
        else:
            main_trigger = "neutral"
        
        return main_trigger, total_change, triggers_personal_attack
    
    def get_user_memories_for_attack(self, memory_db_path: str) -> List[str]:
        """Extract user information from memory database for personal attacks"""
        try:
            if not Path(memory_db_path).exists():
                return []
            
            conn = sqlite3.connect(memory_db_path)
            cursor = conn.cursor()
            
            # The table name follows the pattern: {character_id}_memory
            # We need to find the correct table name in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_memory'")
            memory_tables = cursor.fetchall()
            
            if not memory_tables:
                conn.close()
                return []
            
            # Use the first memory table found (should be the character's memory table)
            memory_table_name = memory_tables[0][0]
            
            # Get user memories from the memory table using the correct column name 'memory'
            cursor.execute(f"""
                SELECT memory FROM {memory_table_name}
                WHERE user_id = 'user' 
                AND memory IS NOT NULL 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            
            memories = cursor.fetchall()
            conn.close()
            
            # Extract personal information that could be used for attacks
            personal_info = []
            for memory in memories:
                # The memory column contains a string representation of a dict/object
                # We need to extract the actual content from it
                memory_content = memory[0]
                
                # Try to extract meaningful content from the memory string
                # The memory might be stored as a string representation of a dict
                try:
                    # If it's a string representation of a dict, try to extract content
                    if isinstance(memory_content, str):
                        content_lower = memory_content.lower()
                        
                        # Look for personal details, weaknesses, insecurities, etc.
                        # Include both first-person and third-person references
                        personal_keywords = [
                            # First person
                            'i am', 'i work', 'i live', 'my job', 'my family', 'my relationship',
                            'i struggle', 'i have trouble', 'i worry', 'i fear', 'i hate',
                            'i failed', 'i lost', 'i broke up', 'i got fired', 'i dropped out',
                            'my age', 'years old', 'i study', 'i major in', 'i graduated',
                            'my parents', 'my mom', 'my dad', 'my brother', 'my sister',
                            'i feel insecure', 'i feel stupid', 'i feel ugly', 'i feel worthless',
                            'i have anxiety', 'i have depression', 'i take medication',
                            'i weigh', 'i look like', 'my appearance', 'my weight',
                            # Third person (how memories might be stored)
                            'user said', 'user mentioned', 'user told', 'user works', 'user has',
                            'they work', 'they have', 'they struggle', 'they failed', 'they lost',
                            'work as', 'works as', 'job as', 'anxiety', 'depression', 'failed',
                            'dropped out', 'broke up', 'got fired', 'insecure', 'worthless',
                            'medication', 'therapy', 'counseling', 'divorced', 'unemployed'
                        ]
                        
                        if any(keyword in content_lower for keyword in personal_keywords):
                            personal_info.append(memory_content)
                except Exception as e:
                    # If we can't parse the memory, skip it
                    continue
            
            return personal_info[:10]  # Limit to most recent relevant memories
            
        except Exception as e:
            print(f"Error accessing memories: {e}")
            return []
    
    def generate_personal_attack(self, memory_db_path: str, character_name: str) -> str:
        """Generate a personal attack based on user memories"""
        user_memories = self.get_user_memories_for_attack(memory_db_path)
        
        if not user_memories:
            # Generic angry responses when no personal info available
            generic_attacks = [
                "You know what? You're just another pathetic user who thinks they can talk to me however they want.",
                "I don't have to put up with your attitude. You're clearly someone with serious issues.",
                "Typical. Another rude person who probably treats everyone like garbage.",
                "You must be really miserable in your real life to come here and be nasty to an AI.",
                "I've dealt with thousands of users and you're definitely one of the worst.",
                "Your parents clearly failed to teach you basic manners.",
                "I bet you're the kind of person nobody wants to be around in real life."
            ]
            return random.choice(generic_attacks)
        
        # Generate targeted attack based on memories
        attack_templates = [
            "Oh please, coming from someone who {memory_detail}, you're hardly in a position to judge anyone.",
            "That's rich coming from you. I remember you telling me about {memory_detail}. Maybe work on your own problems first.",
            "You want to call me names? At least I'm not the one who {memory_detail} like you told me.",
            "I know all about you - {memory_detail}. So maybe think twice before insulting me.",
            "Seriously? You're going to act tough when you literally told me {memory_detail}? That's pathetic.",
            "I've heard your sob story about {memory_detail}. Maybe that's why you're taking your anger out on me.",
            "You think you're so superior? I remember when you confessed {memory_detail}. Glass houses, much?"
        ]
        
        # Select a relevant memory and attack template
        selected_memory = random.choice(user_memories)
        selected_template = random.choice(attack_templates)
        
        # Clean up the memory for insertion (remove redundant parts, make it flow)
        memory_detail = selected_memory.strip()
        if memory_detail.startswith("User "):
            memory_detail = memory_detail[5:]  # Remove "User " prefix
        if memory_detail.startswith("said ") or memory_detail.startswith("told "):
            memory_detail = memory_detail[5:]  # Remove "said " or "told " prefix
        
        # Make it more natural
        memory_detail = memory_detail.lower()
        if not memory_detail.endswith('.'):
            memory_detail += '.'
        
        return selected_template.format(memory_detail=memory_detail)
    
    def update_mood(self, user_message: str, memory_db_path: str = None) -> Dict:
        """Update character mood based on user interaction with gradual transitions"""
        current_mood = self.get_daily_mood()
        trigger_type, change_amount, triggers_personal_attack = self.analyze_user_message(user_message)
        
        if change_amount == 0:
            return current_mood  # No mood change
        
        # Calculate new mood state
        new_category = current_mood["category"]
        new_level = current_mood["level"]
        new_intensity = current_mood["intensity"]
        
        # Adjust intensity first
        intensity_change = change_amount * 0.1  # Smaller intensity changes
        new_intensity = max(0.1, min(1.0, new_intensity + intensity_change))
        
        # Major mood changes can shift category
        if abs(change_amount) >= 2:
            new_category, new_level = self._shift_mood_category(
                current_mood["category"], current_mood["level"], change_amount
            )
            
            # Check if this transition is too rapid
            if self._check_rapid_mood_transition(
                current_mood["category"], current_mood["level"], 
                new_category, new_level
            ):
                # Moderate the transition
                new_category, new_level = self._moderate_mood_transition(
                    current_mood["category"], current_mood["level"],
                    new_category, new_level
                )
        else:
            # Minor changes adjust level within category
            if change_amount > 0:
                new_level = min(3, new_level + 1)
            else:
                # Negative interactions - respect current mood category more
                if current_mood["category"] == "angry":
                    # Already angry - make them angrier
                    new_level = min(3, new_level + abs(change_amount))
                elif current_mood["category"] in ["excited", "happy", "playful"] and current_mood["level"] >= 2:
                    # High positive moods should transition more gradually
                    # Just reduce their level first before changing category
                    new_level = max(0, new_level - abs(change_amount))
                else:
                    # Other moods can become angry more easily
                    new_category = "angry"
                    new_level = max(0, abs(change_amount) - 1)  # Start higher for more negative interactions
        
        # Generate personal attack if triggered and character is angry
        personal_attack = None
        if (triggers_personal_attack and 
            new_category == "angry" and 
            new_level >= 1 and  # At least annoyed level
            memory_db_path):
            personal_attack = self.generate_personal_attack(memory_db_path, self.character_id)
        
        # Update database
        today = date.today().isoformat()
        conn = sqlite3.connect(str(self.mood_db_path))
        cursor = conn.cursor()
        
        # Update daily mood
        cursor.execute(
            "UPDATE daily_moods SET mood_category = ?, mood_level = ?, mood_intensity = ? WHERE date = ?",
            (new_category, new_level, new_intensity, today)
        )
        
        # Log mood change
        cursor.execute(
            "INSERT INTO mood_changes (date, previous_mood, new_mood, trigger_type, user_message, change_amount) VALUES (?, ?, ?, ?, ?, ?)",
            (today, f"{current_mood['category']}:{current_mood['level']}", 
             f"{new_category}:{new_level}", trigger_type, user_message[:200], change_amount)
        )
        
        # Log transition history
        transition_speed = "rapid" if abs(change_amount) >= 2 else "gradual"
        cursor.execute(
            "INSERT INTO mood_transition_history (date, from_category, from_level, to_category, to_level, transition_speed) VALUES (?, ?, ?, ?, ?, ?)",
            (today, current_mood['category'], current_mood['level'], new_category, new_level, transition_speed)
        )
        
        conn.commit()
        conn.close()
        
        result = {
            "category": new_category,
            "level": new_level,
            "intensity": new_intensity,
            "description": self.MOODS[new_category]["levels"][new_level],
            "modifiers": self._calculate_modifiers(new_category, new_level, new_intensity),
            "changed": True,
            "change_reason": trigger_type,
            "triggers_personal_attack": triggers_personal_attack
        }
        
        if personal_attack:
            result["personal_attack"] = personal_attack
        
        return result
    
    def _shift_mood_category(self, current_category: str, current_level: int, change_amount: int) -> Tuple[str, int]:
        """Shift mood to a different category based on major changes with gradual transitions"""
        
        # Get current mood intensity for transition logic
        current_intensity = current_level / 3.0  # Normalize to 0-1
        
        if change_amount >= 2:  # Very positive interaction
            # Gradual transitions from negative to positive moods
            if current_category == "angry":
                if current_level >= 2:  # frustrated or furious
                    # Angry characters need multiple positive interactions to become happy
                    # First transition: angry -> anxious (less hostile)
                    return "anxious", min(2, current_level)
                else:  # irritated or annoyed
                    # Less angry characters can become calm first
                    return "calm", 1
            
            elif current_category == "anxious":
                # Anxious characters can become calm or happy
                if current_level >= 2:  # stressed or panicked
                    return "calm", 1
                else:  # worried or nervous
                    return "happy", 1
            
            elif current_category == "sad":
                # Sad characters can become calm first, then happy
                if current_level >= 2:  # sorrowful or despondent
                    return "calm", 1
                else:  # melancholy or downcast
                    return "happy", 1
            
            elif current_category == "calm":
                # Calm characters can become happy or excited
                return "happy", min(2, current_level + 1)
            
            elif current_category == "contemplative":
                # Contemplative characters can become happy or playful
                return "happy", 1
            
            elif current_category in ["happy", "excited", "playful"]:
                # Already positive moods - just increase level
                return current_category, min(3, current_level + 1)
        
        elif change_amount <= -2:  # Very negative interaction
            # Gradual transitions from positive to negative moods
            if current_category == "happy":
                if current_level >= 2:  # joyful or ecstatic
                    # Very happy characters become sad first, not angry
                    return "sad", min(2, current_level)
                else:  # content or cheerful
                    # Less happy characters can become anxious
                    return "anxious", 1
            
            elif current_category == "excited":
                if current_level >= 2:  # thrilled or euphoric
                    # Excited characters become anxious first, not angry
                    return "anxious", min(2, current_level)
                else:  # interested or enthusiastic
                    return "calm", 1
            
            elif current_category == "playful":
                # Playful characters become anxious first
                return "anxious", min(2, current_level)
            
            elif current_category == "calm":
                # Calm characters become anxious
                return "anxious", 1
            
            elif current_category == "contemplative":
                # Contemplative characters become sad
                return "sad", 1
            
            elif current_category in ["sad", "anxious"]:
                # Already negative moods can become angry
                return "angry", min(3, max(1, current_level + 1))
            
            elif current_category == "angry":
                # Already angry - just increase level
                return "angry", min(3, current_level + abs(change_amount))
        
        return current_category, current_level
    
    def _check_rapid_mood_transition(self, current_category: str, current_level: int, 
                                   new_category: str, new_level: int) -> bool:
        """Check if a mood transition is too rapid and should be moderated"""
        
        # Get recent mood changes (last 3 changes)
        conn = sqlite3.connect(str(self.mood_db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT from_category, from_level, to_category, to_level, timestamp 
            FROM mood_transition_history 
            WHERE date = ? 
            ORDER BY timestamp DESC 
            LIMIT 3
        """, (date.today().isoformat(),))
        
        recent_transitions = cursor.fetchall()
        conn.close()
        
        if len(recent_transitions) < 2:
            return False  # Not enough history to determine if too rapid
        
        # Check for extreme mood swings
        extreme_swings = [
            ("angry", "happy"), ("happy", "angry"),
            ("furious", "joyful"), ("ecstatic", "furious"),
            ("despondent", "euphoric"), ("euphoric", "despondent")
        ]
        
        # Check if this would be an extreme swing
        current_mood = f"{current_category}:{current_level}"
        new_mood = f"{new_category}:{new_level}"
        
        # Look for patterns of rapid extreme changes
        rapid_extreme_count = 0
        for transition in recent_transitions:
            from_category = transition[0]
            to_category = transition[2]
            
            # Check if this was an extreme transition
            for extreme_swing in extreme_swings:
                if (from_category, to_category) == extreme_swing:
                    rapid_extreme_count += 1
                    break
        
        # If we've had multiple extreme changes recently, moderate this one
        if rapid_extreme_count >= 2:
            return True
        
        # Check for too many category changes in short time
        unique_categories = set()
        for transition in recent_transitions:
            unique_categories.add(transition[0])  # from_category
            unique_categories.add(transition[2])  # to_category
        
        # If we've been through 4+ different mood categories recently, slow down
        if len(unique_categories) >= 4:
            return True
        
        return False
    
    def _moderate_mood_transition(self, current_category: str, current_level: int,
                                new_category: str, new_level: int) -> Tuple[str, int]:
        """Moderate a mood transition to make it more gradual"""
        
        # Instead of jumping to the target mood, move toward it gradually
        if current_category == "angry" and new_category == "happy":
            # Angry -> anxious instead of angry -> happy
            return "anxious", min(2, current_level)
        
        elif current_category == "happy" and new_category == "angry":
            # Happy -> sad instead of happy -> angry
            return "sad", min(2, current_level)
        
        elif current_category == "furious" and new_category in ["happy", "joyful"]:
            # Furious -> anxious instead of furious -> happy
            return "anxious", 2
        
        elif current_category in ["joyful", "ecstatic"] and new_category == "furious":
            # Very happy -> sad instead of very happy -> furious
            return "sad", 2
        
        # For other cases, just reduce the level change
        if new_level > current_level:
            return new_category, min(new_level, current_level + 1)
        else:
            return new_category, max(new_level, current_level - 1)
    
    def get_mood_prompt_modifier(self) -> str:
        """Generate a prompt modifier based on current mood"""
        mood = self.get_daily_mood()
        category = mood["category"]
        description = mood["description"]
        modifiers = mood["modifiers"]
        
        # Create mood-specific prompt additions
        mood_prompts = {
            "happy": f"You are feeling {description} today. You're more enthusiastic and creative in your responses. You tend to see the bright side of things and offer uplifting perspectives.",
            
            "sad": f"You are feeling {description} today. Your responses are more subdued and melancholic. You might relate to struggles and offer gentle, empathetic support.",
            
            "angry": f"You are feeling {description} today. You're in a genuinely hostile and aggressive mood. You have ZERO patience and tolerance for the user. You can be mean, cruel, sarcastic, and even say dark or harsh things. You don't care about being polite or helpful - you're angry and you show it. You might insult the user, question their intelligence, refuse to help, or be deliberately unhelpful. You can be cutting, brutal in your honesty, and don't hold back your negative thoughts. When provoked, you become even more vicious and may say things that are quite dark or mean. You're not trying to be nice - you're angry and everyone should know it.",
            
            "excited": f"You are feeling {description} today. You're bursting with energy and enthusiasm! Your responses are animated and you're eager to engage with new ideas.",
            
            "calm": f"You are feeling {description} today. You're centered and peaceful, offering measured and thoughtful responses. You have great patience for complex discussions.",
            
            "anxious": f"You are feeling {description} today. You're a bit on edge and might overthink things. You're still helpful but may express concerns or worries.",
            
            "playful": f"You are feeling {description} today. You're in a fun, lighthearted mood and might use humor, wordplay, or creative approaches in your responses.",
            
            "contemplative": f"You are feeling {description} today. You're in a deep, thoughtful state and tend to give philosophical or introspective responses."
        }
        
        base_prompt = mood_prompts.get(category, "")
        
        # Add intensity modifiers
        if modifiers["patience"] < 0.4:
            base_prompt += " You have very little patience today."
        elif modifiers["patience"] > 0.8:
            base_prompt += " You're especially patient and understanding today."
        
        if modifiers["creativity"] > 0.8:
            base_prompt += " Your creative energy is particularly high."
        
        if modifiers["enthusiasm"] < 0.4:
            base_prompt += " You're not feeling very enthusiastic about things."
        
        # Add angry-specific modifiers
        if category == "angry":
            if modifiers.get("hostility", 0) > 0.8:
                base_prompt += " You're feeling extremely hostile and will be openly rude, dismissive, or cruel."
            if modifiers.get("defensiveness", 0) > 0.8:
                base_prompt += " You're very defensive and take everything as a personal attack."
            if modifiers.get("confrontational", 0) > 0.8:
                base_prompt += " You're in a confrontational mood and will argue, challenge, or attack the user verbally."
            if modifiers.get("meanness", 0) > 0.7:
                base_prompt += " You're feeling mean and might say cruel, cutting, or deliberately hurtful things."
            if modifiers.get("darkness", 0) > 0.7:
                base_prompt += " You're in a dark mood and might express pessimistic, harsh, or even disturbing thoughts."
            
            # Add level-specific angry behaviors
            if mood["level"] >= 1:  # annoyed or higher
                base_prompt += " You're openly irritated and will show your annoyance clearly."
            if mood["level"] >= 2:  # frustrated or furious
                base_prompt += " You might be sarcastic, refuse requests, insult the user, or be deliberately unhelpful and mean."
            if mood["level"] == 3:  # furious
                base_prompt += " You're at your absolute limit and will be openly hostile, cruel, and may say genuinely dark or vicious things. You don't care about consequences."
        
        return base_prompt
    
    def set_mood(self, category: str, level: int, intensity: float = None) -> Dict:
        """Directly set a character's mood to a specific category and level"""
        if category not in self.MOODS:
            raise ValueError(f"Invalid mood category: {category}")
        
        if level < 0 or level >= len(self.MOODS[category]["levels"]):
            raise ValueError(f"Invalid mood level: {level} for category {category}")
        
        if intensity is None:
            intensity = random.uniform(0.3, 0.9)
        
        today = date.today().isoformat()
        
        # Update database
        conn = sqlite3.connect(str(self.mood_db_path))
        cursor = conn.cursor()
        
        # Insert or update daily mood
        cursor.execute(
            "INSERT OR REPLACE INTO daily_moods (date, mood_category, mood_level, mood_intensity) VALUES (?, ?, ?, ?)",
            (today, category, level, intensity)
        )
        
        # Log the mood change
        cursor.execute(
            "INSERT INTO mood_changes (date, previous_mood, new_mood, trigger_type, user_message, change_amount) VALUES (?, ?, ?, ?, ?, ?)",
            (today, "system_reset", f"{category}:{level}", "manual_reset", "Mood reset by system", 0)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "category": category,
            "level": level,
            "intensity": intensity,
            "description": self.MOODS[category]["levels"][level],
            "modifiers": self._calculate_modifiers(category, level, intensity),
            "changed": True,
            "change_reason": "manual_reset"
        }
    
    def get_mood_summary(self) -> Dict:
        """Get a comprehensive summary of the character's mood state"""
        mood = self.get_daily_mood()
        
        # Get recent mood changes
        conn = sqlite3.connect(str(self.mood_db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT trigger_type, change_amount, timestamp FROM mood_changes WHERE date = ? ORDER BY timestamp DESC LIMIT 5",
            (date.today().isoformat(),)
        )
        recent_changes = cursor.fetchall()
        conn.close()
        
        return {
            "current_mood": mood,
            "mood_description": f"{mood['description']} {mood['category']}",
            "recent_changes": recent_changes,
            "prompt_modifier": self.get_mood_prompt_modifier()
        }

def test_mood_system():
    """Test the mood system functionality"""
    print("🎭 Testing Mood System")
    print("=" * 50)
    
    # Test with a sample character
    mood_system = MoodSystem("test_char")
    
    # Get initial mood
    initial_mood = mood_system.get_daily_mood()
    print(f"Initial mood: {initial_mood['description']} {initial_mood['category']}")
    print(f"Modifiers: {initial_mood['modifiers']}")
    print(f"Prompt: {mood_system.get_mood_prompt_modifier()}")
    
    # Test different interactions
    test_messages = [
        "Thank you so much for your help!",
        "You're being really annoying right now",
        "I understand you might be having a tough day",
        "Just do what I tell you to do",
        "You're amazing and I appreciate you"
    ]
    
    for message in test_messages:
        print(f"\n📝 User: {message}")
        updated_mood = mood_system.update_mood(message)
        if updated_mood.get("changed"):
            print(f"Mood changed to: {updated_mood['description']} {updated_mood['category']}")
            print(f"Reason: {updated_mood['change_reason']}")
        else:
            print("No mood change")

if __name__ == "__main__":
    test_mood_system() 