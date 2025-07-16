#!/usr/bin/env python3
"""
Relationship Depth System

Tracks genuine connection between users and characters on a 0-10 scale.
The first 100 users to reach level 10 with any character will receive an NFT reward.

Relationship factors:
- Conversation depth and emotional resonance
- Time spent together (consistency over time)
- Memory sharing and recall
- Emotional support exchanges
- Personal growth moments
- Conflict resolution
- Shared experiences and inside jokes
- Character development influence
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass
import hashlib
import logging

# Configure logging for relationship system
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RelationshipMetrics:
    user_id: str
    character_id: str
    current_level: float
    total_conversations: int
    total_time_spent: int  # minutes
    emotional_moments: int
    memories_shared: int
    conflicts_resolved: int
    personal_growth_events: int
    consistency_score: float
    authenticity_score: float
    last_interaction: datetime
    created_at: datetime

class RelationshipSystem:
    """Advanced relationship tracking system with anti-gaming measures and NFT rewards."""
    
    def __init__(self, db_path: str = "relationship_depth.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Enhanced emotional keywords for better detection
        self.emotional_keywords = {
            "joy": ["happy", "excited", "thrilled", "delighted", "joy", "pleased", "wonderful", "amazing", "fantastic", "great"],
            "sadness": ["sad", "depressed", "melancholy", "down", "blue", "unhappy", "disappointed", "heartbroken", "lonely"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "rage", "hate", "disgusted"],
            "fear": ["afraid", "scared", "terrified", "anxious", "worried", "nervous", "fearful", "panicked", "stressed"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "stunned", "bewildered", "confused"],
            "love": ["love", "adore", "cherish", "care", "affection", "romantic", "passionate", "devoted"],
            "trust": ["trust", "believe", "rely", "depend", "confident", "secure", "faithful"],
            "gratitude": ["thankful", "grateful", "appreciate", "blessed", "fortunate", "thank you"],
            "hope": ["hope", "wish", "dream", "aspire", "believe", "optimistic", "positive"],
            "empathy": ["understand", "feel", "relate", "sympathize", "compassion", "care about"]
        }
        
        # Anti-gaming measures - Made more sensitive
        self.min_message_length = 5  # Reduced from 10
        self.max_daily_emotional_events = 10  # Increased from 5
        self.min_time_between_conversations = 60  # Reduced from 300 (5 minutes to 1 minute)
        
        logger.info(f"Initializing RelationshipSystem with database: {self.db_path}")
        self.init_database()
        
        # Relationship level thresholds and requirements - Made more sensitive
        self.level_requirements = {
            1: {"conversations": 2, "time": 10, "emotional": 1},
            2: {"conversations": 5, "time": 30, "emotional": 2, "memories": 1},
            3: {"conversations": 10, "time": 60, "emotional": 3, "memories": 2, "consistency": 0.2},
            4: {"conversations": 15, "time": 120, "emotional": 5, "memories": 3, "consistency": 0.3},
            5: {"conversations": 25, "time": 240, "emotional": 8, "memories": 5, "consistency": 0.4, "growth": 1},
            6: {"conversations": 35, "time": 400, "emotional": 12, "memories": 8, "consistency": 0.5, "growth": 2, "conflicts": 1},
            7: {"conversations": 50, "time": 600, "emotional": 18, "memories": 12, "consistency": 0.6, "growth": 3, "conflicts": 2},
            8: {"conversations": 70, "time": 900, "emotional": 25, "memories": 18, "consistency": 0.7, "growth": 5, "conflicts": 3, "authenticity": 0.6},
            9: {"conversations": 100, "time": 1500, "emotional": 35, "memories": 25, "consistency": 0.8, "growth": 8, "conflicts": 5, "authenticity": 0.7},
            10: {"conversations": 150, "time": 2400, "emotional": 50, "memories": 35, "consistency": 0.85, "growth": 12, "conflicts": 8, "authenticity": 0.8}
        }
        
    def init_database(self):
        """Initialize the relationship tracking database."""
        logger.debug(f"Initializing relationship database at {self.db_path}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Main relationships table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        current_level REAL DEFAULT 0.0,
                        total_conversations INTEGER DEFAULT 0,
                        total_time_spent INTEGER DEFAULT 0,
                        emotional_moments INTEGER DEFAULT 0,
                        memories_shared INTEGER DEFAULT 0,
                        conflicts_resolved INTEGER DEFAULT 0,
                        personal_growth_events INTEGER DEFAULT 0,
                        consistency_score REAL DEFAULT 0.0,
                        authenticity_score REAL DEFAULT 0.0,
                        last_interaction TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, character_id)
                    )
                """)
                
                # Conversation sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        message_count INTEGER DEFAULT 0,
                        emotional_score REAL DEFAULT 0.0,
                        depth_score REAL DEFAULT 0.0,
                        authenticity_indicators TEXT
                    )
                """)
                
                # Emotional moments table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS emotional_moments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        moment_type TEXT NOT NULL,
                        intensity REAL NOT NULL,
                        context TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # NFT rewards table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS nft_rewards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        wallet_address TEXT,
                        reward_rank INTEGER NOT NULL,
                        achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        nft_minted BOOLEAN DEFAULT FALSE,
                        nft_transaction_hash TEXT
                    )
                """)
                
                # Memory significance table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS significant_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        character_id TEXT NOT NULL,
                        memory_content TEXT NOT NULL,
                        significance_score REAL NOT NULL,
                        emotional_weight REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.debug("Relationship database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing relationship database: {e}")
            raise
    
    def start_conversation_session(self, user_id: str, character_id: str) -> str:
        """Start a new conversation session."""
        logger.debug(f"Starting conversation session for user_id={user_id}, character_id={character_id}")
        
        session_id = hashlib.md5(f"{user_id}_{character_id}_{time.time()}".encode()).hexdigest()
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conversation_sessions (user_id, character_id, start_time)
                    VALUES (?, ?, ?)
                """, (user_id, character_id, datetime.now()))
                
                conn.commit()
                logger.debug(f"Conversation session started: {session_id}")
                
        except Exception as e:
            logger.error(f"Error starting conversation session: {e}")
            raise
        
        return session_id
    
    def analyze_message_depth(self, message: str, response: str) -> Dict:
        """Analyze the emotional and intellectual depth of a conversation exchange."""
        if len(message) < self.min_message_length:
            return {"emotional_score": 0, "depth_score": 0, "authenticity": 0}
        
        # Emotional analysis
        emotional_score = 0
        detected_emotions = []
        
        message_lower = message.lower()
        response_lower = response.lower()
        
        for emotion_type, keywords in self.emotional_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    emotional_score += 1
                    detected_emotions.append(emotion_type)
                if keyword in response_lower:
                    emotional_score += 0.5
        
        # Depth indicators - Made more sensitive
        depth_indicators = [
            len(message.split()) > 10,  # Reduced from 20 to 10
            '?' in message,  # Questions show engagement
            any(word in message_lower for word in ['feel', 'think', 'believe', 'remember', 'experience', 'like', 'want', 'need', 'hope', 'wish']),  # Added more common words
            any(word in message_lower for word in ['why', 'how', 'what if', 'imagine', 'maybe', 'could', 'would']),  # Added more common words
            '"' in message or "'" in message,  # Quotes suggest storytelling
            any(word in message_lower for word in ['good', 'bad', 'happy', 'sad', 'excited', 'worried', 'love', 'hate']),  # Added emotional words
        ]
        
        depth_score = sum(depth_indicators) / len(depth_indicators)
        
        # Authenticity indicators (anti-gaming measures)
        authenticity_indicators = [
            not self._is_repetitive(message),
            not self._contains_spam_patterns(message),
            self._has_natural_language_flow(message),
            len(set(message.split())) / len(message.split()) > 0.7,  # Vocabulary diversity
        ]
        
        authenticity_score = sum(authenticity_indicators) / len(authenticity_indicators)
        
        return {
            "emotional_score": min(emotional_score, 5),  # Increased cap from 3 to 5
            "depth_score": depth_score,
            "authenticity": authenticity_score,
            "detected_emotions": detected_emotions
        }
    
    def record_conversation_exchange(self, user_id: str, character_id: str, 
                                   user_message: str, character_response: str,
                                   conversation_duration: int = 0) -> Dict:
        """Record a conversation exchange and update relationship metrics."""
        logger.debug(f"Recording conversation exchange for user_id={user_id}, character_id={character_id}")
        
        # Analyze the exchange
        analysis = self.analyze_message_depth(user_message, character_response)
        
        # Check for anti-gaming violations
        if not self._is_valid_interaction(user_id, character_id):
            logger.warning(f"Invalid interaction detected for user_id={user_id}, character_id={character_id}")
            return {"relationship_change": 0, "level_up": False, "warning": "Too frequent interactions"}

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Get or create relationship record
                cursor.execute("""
                    INSERT OR IGNORE INTO relationships (user_id, character_id, last_interaction)
                    VALUES (?, ?, ?)
                """, (user_id, character_id, datetime.now()))
                
                # Update conversation metrics
                cursor.execute("""
                    UPDATE relationships SET
                        total_conversations = total_conversations + 1,
                        total_time_spent = total_time_spent + ?,
                        last_interaction = ?
                    WHERE user_id = ? AND character_id = ?
                """, (conversation_duration, datetime.now(), user_id, character_id))
                
                # Record emotional moments if significant - Made more sensitive
                if analysis["emotional_score"] > 0.5 and analysis["authenticity"] > 0.4:  # Reduced thresholds
                    self._record_emotional_moment_with_conn(conn, user_id, character_id, analysis["detected_emotions"], 
                                                analysis["emotional_score"], user_message)
                
                # Update relationship level
                new_level, level_up = self._calculate_relationship_level_with_conn(conn, user_id, character_id)
                
                # Check for NFT reward eligibility
                nft_reward = None
                if new_level >= 10.0:
                    nft_reward = self._check_nft_eligibility_with_conn(conn, user_id, character_id)
                
                conn.commit()
                
                logger.debug(f"Conversation exchange recorded successfully. New level: {new_level}, Level up: {level_up}")
                
                return {
                    "relationship_change": analysis["emotional_score"] * analysis["authenticity"],
                    "current_level": new_level,
                    "level_up": level_up,
                    "analysis": analysis,
                    "nft_reward": nft_reward
                }
                
        except Exception as e:
            logger.error(f"Error recording conversation exchange: {e}")
            raise
    
    def _record_emotional_moment_with_conn(self, conn, user_id: str, character_id: str, 
                                emotions: List[str], intensity: float, context: str):
        """Record a significant emotional moment using existing connection."""
        cursor = conn.cursor()
        
        # Check daily limit to prevent gaming
        today = datetime.now().date()
        cursor.execute("""
            SELECT COUNT(*) FROM emotional_moments 
            WHERE user_id = ? AND character_id = ? AND DATE(timestamp) = ?
        """, (user_id, character_id, today))
        
        daily_count = cursor.fetchone()[0]
        if daily_count >= self.max_daily_emotional_events:
            return
        
        # Record the moment
        cursor.execute("""
            INSERT INTO emotional_moments (user_id, character_id, moment_type, intensity, context)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, character_id, ','.join(emotions), intensity, context[:500]))
        
        # Update relationship emotional moments count
        cursor.execute("""
            UPDATE relationships SET emotional_moments = emotional_moments + 1
            WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
    
    def _calculate_relationship_level_with_conn(self, conn, user_id: str, character_id: str) -> Tuple[float, bool]:
        """Calculate the current relationship level using existing connection."""
        cursor = conn.cursor()
        
        # Get current metrics
        cursor.execute("""
            SELECT current_level, total_conversations, total_time_spent, emotional_moments,
                   memories_shared, conflicts_resolved, personal_growth_events,
                   consistency_score, authenticity_score, created_at
            FROM relationships WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
        
        result = cursor.fetchone()
        if not result:
            return 0.0, False
        
        current_level, conversations, time_spent, emotional, memories, conflicts, growth, consistency, authenticity, created_at = result
        
        # Calculate consistency score (regular interactions over time)
        relationship_age_days = (datetime.now() - datetime.fromisoformat(created_at)).days
        if relationship_age_days > 0:
            consistency = min(conversations / max(relationship_age_days, 1), 1.0)
        
        # Calculate authenticity score based on interaction patterns
        authenticity = self._calculate_authenticity_score_with_conn(conn, user_id, character_id)
        
        # Update calculated scores
        cursor.execute("""
            UPDATE relationships SET consistency_score = ?, authenticity_score = ?
            WHERE user_id = ? AND character_id = ?
        """, (consistency, authenticity, user_id, character_id))
        
        # Determine highest achievable level
        new_level = 0
        for level, requirements in self.level_requirements.items():
            meets_requirements = True
            
            if conversations < requirements.get("conversations", 0):
                meets_requirements = False
            if time_spent < requirements.get("time", 0):
                meets_requirements = False
            if emotional < requirements.get("emotional", 0):
                meets_requirements = False
            if memories < requirements.get("memories", 0):
                meets_requirements = False
            if conflicts < requirements.get("conflicts", 0):
                meets_requirements = False
            if growth < requirements.get("growth", 0):
                meets_requirements = False
            if consistency < requirements.get("consistency", 0):
                meets_requirements = False
            if authenticity < requirements.get("authenticity", 0):
                meets_requirements = False
            
            if meets_requirements:
                new_level = level
            else:
                break
        
        # Update level in database
        level_up = new_level > current_level
        cursor.execute("""
            UPDATE relationships SET current_level = ?
            WHERE user_id = ? AND character_id = ?
        """, (new_level, user_id, character_id))
        
        return new_level, level_up
    
    def _calculate_authenticity_score_with_conn(self, conn, user_id: str, character_id: str) -> float:
        """Calculate authenticity score using existing connection."""
        cursor = conn.cursor()
        
        # Check for suspicious patterns
        cursor.execute("""
            SELECT COUNT(*) as total,
                   AVG(intensity) as avg_emotional,
                   COUNT(DISTINCT DATE(timestamp)) as unique_days
            FROM emotional_moments 
            WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
        
        result = cursor.fetchone()
        if not result or result[0] == 0:
            return 0.5
        
        total_moments, avg_emotional, unique_days = result
        
        # Authenticity indicators
        authenticity_factors = []
        
        # Spread over time (not all in one day)
        if unique_days > 0:
            time_spread = min(unique_days / max(total_moments / 3, 1), 1.0)
            authenticity_factors.append(time_spread)
        
        # Reasonable emotional intensity (not always max)
        if avg_emotional:
            emotional_variance = 1.0 - abs(avg_emotional - 1.5) / 1.5
            authenticity_factors.append(max(emotional_variance, 0))
        
        # Conversation length variety
        cursor.execute("""
            SELECT AVG(message_count), COUNT(DISTINCT message_count)
            FROM conversation_sessions 
            WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
        
        session_result = cursor.fetchone()
        if session_result and session_result[0]:
            variety_score = min(session_result[1] / max(session_result[0] / 5, 1), 1.0)
            authenticity_factors.append(variety_score)
        
        return sum(authenticity_factors) / len(authenticity_factors) if authenticity_factors else 0.5
    
    def _check_nft_eligibility_with_conn(self, conn, user_id: str, character_id: str) -> Optional[Dict]:
        """Check if user is eligible for NFT reward using existing connection."""
        cursor = conn.cursor()
        
        # Check if already rewarded
        cursor.execute("""
            SELECT id FROM nft_rewards WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
        
        if cursor.fetchone():
            return None
        
        # Count existing rewards
        cursor.execute("SELECT COUNT(*) FROM nft_rewards")
        reward_count = cursor.fetchone()[0]
        
        if reward_count >= 100:
            return None
        
        # Award NFT
        rank = reward_count + 1
        cursor.execute("""
            INSERT INTO nft_rewards (user_id, character_id, reward_rank)
            VALUES (?, ?, ?)
        """, (user_id, character_id, rank))
        
        return {
            "eligible": True,
            "rank": rank,
            "message": f"Congratulations! You've achieved a level 10 relationship and earned NFT reward #{rank}!"
        }
    
    def _is_valid_interaction(self, user_id: str, character_id: str) -> bool:
        """Check if interaction is valid (anti-gaming)."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Check time since last interaction
        cursor.execute("""
            SELECT last_interaction FROM relationships 
            WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
        
        result = cursor.fetchone()
        if result and result[0]:
            last_interaction = datetime.fromisoformat(result[0])
            time_diff = (datetime.now() - last_interaction).total_seconds()
            if time_diff < self.min_time_between_conversations:
                conn.close()
                return False
        
        conn.close()
        return True
    
    def _is_repetitive(self, message: str) -> bool:
        """Check if message is repetitive."""
        words = message.lower().split()
        if len(words) < 3:
            return True
        
        # Check for repeated words
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        max_repetition = max(word_counts.values())
        return max_repetition > len(words) * 0.4
    
    def _contains_spam_patterns(self, message: str) -> bool:
        """Check for spam patterns."""
        spam_patterns = [
            r'(.)\1{4,}',  # Repeated characters
            r'\b(\w+)\s+\1\b',  # Repeated words
            r'^[^a-zA-Z]*$',  # No letters
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, message):
                return True
        return False
    
    def _has_natural_language_flow(self, message: str) -> bool:
        """Check if message has natural language flow."""
        # Simple heuristics for natural language
        words = message.split()
        if len(words) < 2:
            return False
        
        # Check for basic sentence structure
        has_verbs = any(word.lower() in ['am', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could', 'should'] for word in words)
        has_pronouns = any(word.lower() in ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'] for word in words)
        
        return has_verbs or has_pronouns
    
    def get_relationship_status(self, user_id: str, character_id: str) -> Dict:
        """Get detailed relationship status."""
        logger.debug(f"Getting relationship status for user_id={user_id}, character_id={character_id}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM relationships WHERE user_id = ? AND character_id = ?
                """, (user_id, character_id))
                
                result = cursor.fetchone()
                if not result:
                    logger.debug(f"No relationship found for user_id={user_id}, character_id={character_id}")
                    return {"level": 0, "exists": False}
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                relationship_data = dict(zip(columns, result))
                
                # Get next level requirements
                current_level = int(relationship_data["current_level"])
                next_level = current_level + 1
                next_requirements = self.level_requirements.get(next_level, {})
                
                # Calculate progress to next level
                progress = {}
                if next_requirements:
                    for req, target in next_requirements.items():
                        current_value = relationship_data.get(req.replace("consistency", "consistency_score").replace("authenticity", "authenticity_score"), 0)
                        progress[req] = {
                            "current": current_value,
                            "required": target,
                            "progress": min(current_value / target, 1.0) if target > 0 else 1.0
                        }
                
                logger.debug(f"Retrieved relationship status: level={relationship_data['current_level']}")
                
                return {
                    "exists": True,
                    "level": relationship_data["current_level"],
                    "metrics": relationship_data,
                    "next_level_progress": progress,
                    "nft_eligible": relationship_data["current_level"] >= 10
                }
                
        except Exception as e:
            logger.error(f"Error getting relationship status: {e}")
            return {"level": 0, "exists": False}
    
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get relationship leaderboard."""
        logger.debug(f"Getting leaderboard with limit={limit}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT user_id, character_id, current_level, total_conversations, 
                           total_time_spent, created_at
                    FROM relationships 
                    ORDER BY current_level DESC, total_conversations DESC
                    LIMIT ?
                """, (limit,))
                
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                leaderboard = []
                for result in results:
                    entry = dict(zip(columns, result))
                    entry["rank"] = len(leaderboard) + 1
                    leaderboard.append(entry)
                
                logger.debug(f"Retrieved leaderboard with {len(leaderboard)} entries")
                return leaderboard
                
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def get_nft_rewards_status(self) -> Dict:
        """Get NFT rewards status."""
        logger.debug("Getting NFT rewards status")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM nft_rewards")
                total_awarded = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT user_id, character_id, reward_rank, achieved_at
                    FROM nft_rewards 
                    ORDER BY reward_rank
                """)
                
                rewards = cursor.fetchall()
                
                logger.debug(f"Retrieved NFT rewards status: {total_awarded} awarded")
                
                return {
                    "total_awarded": total_awarded,
                    "remaining_slots": max(0, 100 - total_awarded),
                    "rewards": [
                        {
                            "user_id": r[0],
                            "character_id": r[1], 
                            "rank": r[2],
                            "achieved_at": r[3]
                        } for r in rewards
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting NFT rewards status: {e}")
            return {"total_awarded": 0, "remaining_slots": 100, "rewards": []}

    # Original methods for backward compatibility
    def _record_emotional_moment(self, user_id: str, character_id: str, 
                                emotions: List[str], intensity: float, context: str):
        """Record a significant emotional moment."""
        logger.debug(f"Recording emotional moment for user_id={user_id}, character_id={character_id}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                self._record_emotional_moment_with_conn(conn, user_id, character_id, emotions, intensity, context)
                conn.commit()
                logger.debug("Emotional moment recorded successfully")
                
        except Exception as e:
            logger.error(f"Error recording emotional moment: {e}")
            raise
    
    def _calculate_relationship_level(self, user_id: str, character_id: str) -> Tuple[float, bool]:
        """Calculate the current relationship level based on all metrics."""
        logger.debug(f"Calculating relationship level for user_id={user_id}, character_id={character_id}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                result = self._calculate_relationship_level_with_conn(conn, user_id, character_id)
                logger.debug(f"Relationship level calculated: {result[0]}, level up: {result[1]}")
                return result
                
        except Exception as e:
            logger.error(f"Error calculating relationship level: {e}")
            return 0.0, False
    
    def _calculate_authenticity_score(self, user_id: str, character_id: str) -> float:
        """Calculate authenticity score to prevent gaming."""
        logger.debug(f"Calculating authenticity score for user_id={user_id}, character_id={character_id}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                score = self._calculate_authenticity_score_with_conn(conn, user_id, character_id)
                logger.debug(f"Authenticity score calculated: {score}")
                return score
                
        except Exception as e:
            logger.error(f"Error calculating authenticity score: {e}")
            return 0.5
    
    def _check_nft_eligibility(self, user_id: str, character_id: str) -> Optional[Dict]:
        """Check if user is eligible for NFT reward (top 100)."""
        logger.debug(f"Checking NFT eligibility for user_id={user_id}, character_id={character_id}")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                result = self._check_nft_eligibility_with_conn(conn, user_id, character_id)
                if result:
                    conn.commit()
                    logger.info(f"NFT reward granted to user_id={user_id}, character_id={character_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error checking NFT eligibility: {e}")
            return None

# Test the system
if __name__ == "__main__":
    rs = RelationshipSystem()
    
    # Test conversation
    result = rs.record_conversation_exchange(
        "test_user", 
        "test_character",
        "I've been feeling really anxious about my job interview tomorrow. I keep thinking about all the things that could go wrong.",
        "I understand how nerve-wracking interviews can be. What specifically worries you most about it?",
        5
    )
    
    print("Conversation result:", result)
    
    # Check status
    status = rs.get_relationship_status("test_user", "test_character")
    print("Relationship status:", status) 