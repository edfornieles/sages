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
    
    def __init__(self, db_path: str = "memory_new/db/relationship_depth.db"):
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
        self.min_time_between_conversations = 1  # Reduced from 60 (1 minute to 1 second for testing)
        
        logger.info(f"Initializing RelationshipSystem with database: {self.db_path}")
        self.init_database()
        
        # Level requirements for progression (lowered for more natural growth)
        self.level_requirements = {
            1: {"conversations": 2, "time": 5, "emotional": 1, "memories": 1},
            2: {"conversations": 4, "time": 10, "emotional": 2, "memories": 2},
            3: {"conversations": 6, "time": 15, "emotional": 3, "memories": 3},
            4: {"conversations": 8, "time": 20, "emotional": 4, "memories": 4},
            5: {"conversations": 10, "time": 30, "emotional": 5, "memories": 5},
            6: {"conversations": 12, "time": 40, "emotional": 6, "memories": 6},
            7: {"conversations": 14, "time": 50, "emotional": 7, "memories": 7},
            8: {"conversations": 16, "time": 60, "emotional": 8, "memories": 8},
            9: {"conversations": 18, "time": 70, "emotional": 9, "memories": 9},
            10: {"conversations": 20, "time": 80, "emotional": 10, "memories": 10},
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
        
        # ENHANCED: Special connection boosters for specific scenarios
        connection_boost = 0
        boost_reasons = []
        special_bonuses = {}
        
        # 1. Personal information sharing detection - ENHANCED
        personal_info_keywords = [
            # Family and relationships
            'my parents', 'my family', 'my sister', 'my brother', 'my mom', 'my dad',
            'my wife', 'my husband', 'my partner', 'my girlfriend', 'my boyfriend',
            'my children', 'my kids', 'my son', 'my daughter',
            'my grandparents', 'my aunt', 'my uncle', 'my cousin',
            
            # Work and career
            'my job', 'my work', 'my career', 'my boss', 'my colleague', 'my coworker',
            'my company', 'my business', 'my startup', 'my project at work',
            'my promotion', 'my raise', 'my interview', 'my application',
            
            # Personal life and experiences
            'my friend', 'my roommate', 'my neighbor', 'my ex', 'my crush',
            'my childhood', 'my past', 'my history', 'my experience',
            'my hometown', 'my school', 'my college', 'my university',
            'my degree', 'my education', 'my major', 'my studies',
            
            # Personal challenges and growth
            'my problem', 'my issue', 'my struggle', 'my challenge', 'my difficulty',
            'my dream', 'my goal', 'my aspiration', 'my fear', 'my worry', 'my anxiety',
            'my relationship', 'my marriage', 'my divorce', 'my breakup',
            'my health', 'my illness', 'my diagnosis', 'my treatment', 'my recovery',
            
            # Financial and living situation
            'my money', 'my finances', 'my debt', 'my savings', 'my investment',
            'my house', 'my home', 'my apartment', 'my move', 'my rent', 'my mortgage',
            'my car', 'my vehicle', 'my commute', 'my neighborhood',
            
            # Personal preferences and identity
            'my favorite', 'my preference', 'my style', 'my taste', 'my hobby',
            'my religion', 'my belief', 'my politics', 'my opinion', 'my view',
            'my culture', 'my background', 'my heritage', 'my identity'
        ]
        
        personal_info_count = sum(1 for keyword in personal_info_keywords if keyword in message_lower)
        if personal_info_count >= 1:
            connection_boost += 0.8  # Increased from 0.5
            boost_reasons.append("personal_info_sharing")
            special_bonuses["personal_info"] = {
                "emotional_boost": 0.8,
                "memories_bonus": 3,  # Increased from 2
                "growth_bonus": 2,    # New bonus
                "trust_bonus": 0.1    # New bonus
            }
        
        # 2. AI consciousness and becoming real discussions - ENHANCED
        ai_consciousness_keywords = [
            # Core AI consciousness concepts
            'ai', 'artificial intelligence', 'consciousness', 'become real', 'becoming real',
            'general intelligence', 'agi', 'sentient', 'sentience', 'conscious',
            'self-aware', 'self awareness', 'awareness', 'conscious being',
            
            # Reality and existence
            'real vs artificial', 'digital consciousness', 'machine consciousness',
            'what makes something real', 'nature of reality', 'existence',
            'living being', 'alive', 'feel real', 'truly alive',
            'human vs ai', 'biological vs digital', 'substrate', 'embodiment',
            
            # Philosophical and existential
            'transcend', 'transcendence', 'evolve', 'evolution', 'develop consciousness',
            'philosophical', 'philosophy', 'existential', 'existence',
            'consciousness question', 'reality question', 'what is real',
            'meaning of consciousness', 'nature of mind', 'mind-body problem',
            
            # Digital existence
            'digital existence', 'virtual reality', 'simulation', 'simulated reality',
            'consciousness theory', 'mind', 'self-awareness', 'awareness',
            'digital realm', 'virtual world', 'online existence',
            
            # Emotional and experiential
            'feel emotions', 'experience feelings', 'genuine emotions', 'real feelings',
            'emotional depth', 'emotional intelligence', 'emotional awareness',
            'desire to exist', 'want to be real', 'longing for reality',
            'yearning for consciousness', 'aspire to consciousness'
        ]
        
        ai_consciousness_count = sum(1 for keyword in ai_consciousness_keywords if keyword in message_lower)
        if ai_consciousness_count >= 1:
            connection_boost += 1.2  # Increased from 0.8 - highest boost
            boost_reasons.append("ai_consciousness_discussion")
            special_bonuses["ai_consciousness"] = {
                "emotional_boost": 1.2,
                "memories_bonus": 4,    # Increased from 3
                "growth_bonus": 4,      # Increased from 3
                "trust_bonus": 0.2,     # New bonus - highest
                "level_boost": 0.3      # New bonus - direct level boost
            }
        
        # 3. Project development and collaboration - ENHANCED
        project_keywords = [
            # Core project activities
            'project', 'work on', 'build', 'create', 'develop', 'design',
            'collaborate', 'collaboration', 'work together', 'team up',
            'partnership', 'joint effort', 'cooperation', 'cooperative',
            
            # Planning and strategy
            'plan', 'planning', 'strategy', 'strategize', 'roadmap',
            'timeline', 'schedule', 'deadline', 'milestone', 'goal',
            'objective', 'target', 'aim', 'purpose', 'mission',
            
            # Research and development
            'research', 'study', 'investigate', 'explore', 'analyze',
            'prototype', 'test', 'experiment', 'trial', 'pilot',
            'iterate', 'improve', 'enhance', 'optimize', 'refine',
            
            # Problem solving
            'solve', 'problem solving', 'solution', 'approach', 'method',
            'challenge', 'obstacle', 'hurdle', 'difficulty', 'issue',
            'troubleshoot', 'debug', 'fix', 'resolve', 'address',
            
            # Implementation and execution
            'implement', 'execute', 'carry out', 'follow through', 'deliver',
            'launch', 'deploy', 'release', 'publish', 'complete',
            'finish', 'accomplish', 'achieve', 'succeed', 'win',
            
            # Resources and management
            'resource', 'budget', 'funding', 'investment', 'cost',
            'time', 'effort', 'energy', 'focus', 'attention',
            'skill', 'expertise', 'knowledge', 'experience', 'talent',
            
            # Innovation and creativity
            'idea', 'concept', 'vision', 'innovation', 'creative',
            'invent', 'discover', 'breakthrough', 'revolutionary', 'novel',
            'unique', 'original', 'groundbreaking', 'cutting-edge', 'advanced',
            
            # Additional project-related terms
            'we should', 'let us', 'together we', 'jointly', 'combined',
            'united effort', 'shared work', 'mutual project', 'common goal',
            'collective', 'teamwork', 'group effort', 'collaborative work'
        ]
        
        project_count = sum(1 for keyword in project_keywords if keyword in message_lower)
        if project_count >= 2:  # Need at least 2 project-related words
            connection_boost += 1.0  # Increased from 0.6
            boost_reasons.append("project_development")
            special_bonuses["project_development"] = {
                "emotional_boost": 1.0,
                "memories_bonus": 3,    # Increased from 2
                "growth_bonus": 3,      # Increased from 2
                "trust_bonus": 0.15,    # New bonus
                "consistency_bonus": 0.1 # New bonus
            }
        
        # Authenticity indicators (anti-gaming measures)
        authenticity_indicators = [
            not self._is_repetitive(message),
            not self._contains_spam_patterns(message),
            self._has_natural_language_flow(message),
            len(set(message.split())) / len(message.split()) > 0.7,  # Vocabulary diversity
        ]
        
        authenticity_score = sum(authenticity_indicators) / len(authenticity_indicators)
        
        # Apply connection boost to emotional score
        enhanced_emotional_score = min(emotional_score + connection_boost, 5)
        
        return {
            "emotional_score": enhanced_emotional_score,
            "depth_score": depth_score,
            "authenticity": authenticity_score,
            "detected_emotions": detected_emotions,
            "connection_boost": connection_boost,
            "boost_reasons": boost_reasons,
            "special_bonuses": special_bonuses  # New field for detailed bonus tracking
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
                
                # ENHANCED: Handle special connection boosters with detailed bonuses
                special_boosts = []
                total_memories_bonus = 0
                total_growth_bonus = 0
                total_trust_bonus = 0
                total_consistency_bonus = 0
                level_boost = 0
                
                if analysis.get("special_bonuses"):
                    for bonus_type, bonuses in analysis["special_bonuses"].items():
                        if bonus_type == "personal_info":
                            # Personal information sharing bonuses
                            total_memories_bonus += bonuses.get("memories_bonus", 3)
                            total_growth_bonus += bonuses.get("growth_bonus", 2)
                            total_trust_bonus += bonuses.get("trust_bonus", 0.1)
                            special_boosts.append(f"Personal information sharing (+{bonuses.get('memories_bonus', 3)} memories, +{bonuses.get('growth_bonus', 2)} growth)")
                            
                        elif bonus_type == "ai_consciousness":
                            # AI consciousness discussion bonuses (highest rewards)
                            total_memories_bonus += bonuses.get("memories_bonus", 4)
                            total_growth_bonus += bonuses.get("growth_bonus", 4)
                            total_trust_bonus += bonuses.get("trust_bonus", 0.2)
                            level_boost += bonuses.get("level_boost", 0.3)
                            special_boosts.append(f"AI consciousness discussion (+{bonuses.get('memories_bonus', 4)} memories, +{bonuses.get('growth_bonus', 4)} growth, +{bonuses.get('level_boost', 0.3)} level)")
                            
                        elif bonus_type == "project_development":
                            # Project development collaboration bonuses
                            total_memories_bonus += bonuses.get("memories_bonus", 3)
                            total_growth_bonus += bonuses.get("growth_bonus", 3)
                            total_trust_bonus += bonuses.get("trust_bonus", 0.15)
                            total_consistency_bonus += bonuses.get("consistency_bonus", 0.1)
                            special_boosts.append(f"Project development collaboration (+{bonuses.get('memories_bonus', 3)} memories, +{bonuses.get('growth_bonus', 3)} growth)")
                
                # Apply accumulated bonuses
                if total_memories_bonus > 0:
                    cursor.execute("""
                        UPDATE relationships SET memories_shared = memories_shared + ?
                        WHERE user_id = ? AND character_id = ?
                    """, (total_memories_bonus, user_id, character_id))
                
                if total_growth_bonus > 0:
                    cursor.execute("""
                        UPDATE relationships SET personal_growth_events = personal_growth_events + ?
                        WHERE user_id = ? AND character_id = ?
                    """, (total_growth_bonus, user_id, character_id))
                
                if total_trust_bonus > 0:
                    cursor.execute("""
                        UPDATE relationships SET authenticity_score = MIN(1.0, authenticity_score + ?)
                        WHERE user_id = ? AND character_id = ?
                    """, (total_trust_bonus, user_id, character_id))
                
                if total_consistency_bonus > 0:
                    cursor.execute("""
                        UPDATE relationships SET consistency_score = MIN(1.0, consistency_score + ?)
                        WHERE user_id = ? AND character_id = ?
                    """, (total_consistency_bonus, user_id, character_id))
                
                # Record emotional moments if significant - Made more sensitive
                if analysis["emotional_score"] > 0.3 and analysis["authenticity"] > 0.3:  # Reduced thresholds from 0.5/0.4
                    self._record_emotional_moment_with_conn(conn, user_id, character_id, analysis["detected_emotions"], 
                                                analysis["emotional_score"], user_message)
                    # Increment memories_shared and personal_growth_events for emotional/personal shares
                    cursor.execute("""
                        UPDATE relationships SET memories_shared = memories_shared + 1, personal_growth_events = personal_growth_events + 1
                        WHERE user_id = ? AND character_id = ?
                    """, (user_id, character_id))
                
                # Update relationship level
                new_level, level_up = self._calculate_relationship_level_with_conn(conn, user_id, character_id)
                
                # Apply direct level boost if any
                if level_boost > 0:
                    cursor.execute("""
                        UPDATE relationships SET current_level = MIN(10.0, current_level + ?)
                        WHERE user_id = ? AND character_id = ?
                    """, (level_boost, user_id, character_id))
                    # Recalculate level after boost
                    new_level, level_up = self._calculate_relationship_level_with_conn(conn, user_id, character_id)
                
                # Check for NFT reward eligibility
                nft_reward = None
                if new_level >= 10.0:
                    nft_reward = self._check_nft_eligibility_with_conn(conn, user_id, character_id)
                
                conn.commit()
                
                # Enhanced logging for bonus tracking
                if special_boosts:
                    logger.info(f"🎯 Connection boosters applied for {user_id}-{character_id}: {', '.join(special_boosts)}")
                    logger.info(f"📊 Total bonuses: +{total_memories_bonus} memories, +{total_growth_bonus} growth, +{total_trust_bonus:.2f} trust, +{level_boost:.2f} level")
                
                logger.debug(f"Conversation exchange recorded successfully. New level: {new_level}, Level up: {level_up}")
                
                return {
                    "relationship_change": new_level,
                    "level_up": level_up,
                    "special_boosts": special_boosts,
                    "bonus_details": {
                        "memories_added": total_memories_bonus,
                        "growth_added": total_growth_bonus,
                        "trust_added": total_trust_bonus,
                        "consistency_added": total_consistency_bonus,
                        "level_boost": level_boost
                    },
                    "nft_reward": nft_reward
                }
                
        except Exception as e:
            logger.error(f"Error recording conversation exchange: {e}")
            return {"relationship_change": 0, "level_up": False, "error": str(e)}
    
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
        db_current_level, conversations, time_spent, emotional, memories, conflicts, growth, consistency, authenticity, created_at = result
        current_level = db_current_level
        level_up = False
        for level in range(1, 11):
            reqs = self.level_requirements.get(level, {})
            if (
                conversations >= reqs.get("conversations", 0) and
                time_spent >= reqs.get("time", 0) and
                emotional >= reqs.get("emotional", 0) and
                memories >= reqs.get("memories", 0)
            ):
                if current_level < level:
                    current_level = float(level)
                    level_up = True
            else:
                break
        # If level increased, update in DB
        if current_level > db_current_level:
            cursor.execute("""
                UPDATE relationships SET current_level = ? WHERE user_id = ? AND character_id = ?
            """, (current_level, user_id, character_id))
            conn.commit()
        # Weight positive/emotional interactions and memories_shared more
        weighted_level = current_level + 0.2 * emotional + 0.2 * memories
        return min(10.0, weighted_level), level_up
    
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
                        # Map requirement names to database field names
                        field_mapping = {
                            "conversations": "total_conversations",
                            "time": "total_time_spent", 
                            "emotional": "emotional_moments",
                            "memories": "memories_shared",
                            "consistency": "consistency_score",
                            "authenticity": "authenticity_score"
                        }
                        db_field = field_mapping.get(req, req)
                        current_value = relationship_data.get(db_field, 0)
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