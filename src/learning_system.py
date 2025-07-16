#!/usr/bin/env python3
"""
Advanced Learning System for Dynamic Character Playground

This system enables AI characters to learn and adapt from their interactions,
developing better communication skills, understanding user preferences,
and improving their effectiveness over time.
"""

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter
import re

class LearningSystem:
    def __init__(self, character_id: str, db_path: str = "character_learning.db"):
        self.character_id = character_id
        self.db_path = Path(db_path)
        self.init_database()
        
        # Learning categories and their metrics
        self.learning_categories = {
            "communication_effectiveness": {
                "description": "How well I communicate with users",
                "metrics": ["user_satisfaction", "clarity_score", "engagement_level"],
                "improvement_areas": ["humor", "empathy", "explanation_quality", "question_asking"]
            },
            "user_understanding": {
                "description": "How well I understand individual users",
                "metrics": ["prediction_accuracy", "personalization_score", "preference_match"],
                "improvement_areas": ["mood_detection", "need_anticipation", "context_awareness"]
            },
            "problem_solving": {
                "description": "How effectively I help users solve problems",
                "metrics": ["solution_success_rate", "creativity_score", "helpfulness_rating"],
                "improvement_areas": ["analytical_thinking", "creative_solutions", "resource_suggestions"]
            },
            "emotional_intelligence": {
                "description": "How well I understand and respond to emotions",
                "metrics": ["emotional_accuracy", "comfort_provided", "empathy_score"],
                "improvement_areas": ["emotion_recognition", "supportive_responses", "timing_sensitivity"]
            },
            "conversation_flow": {
                "description": "How naturally conversations flow with me",
                "metrics": ["conversation_length", "topic_transitions", "engagement_retention"],
                "improvement_areas": ["topic_management", "question_timing", "response_pacing"]
            }
        }

    def init_database(self):
        """Initialize the learning database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Learning experiences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_experiences (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                context TEXT,
                user_input TEXT,
                character_response TEXT,
                user_feedback TEXT,
                success_indicators TEXT, -- JSON of success metrics
                failure_indicators TEXT, -- JSON of failure metrics
                lessons_learned TEXT,    -- JSON of extracted lessons
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Skill development table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_development (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                skill_category TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                current_level REAL DEFAULT 0.0,  -- 0.0 to 1.0
                practice_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                last_practiced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                improvement_rate REAL DEFAULT 0.0,
                notes TEXT
            )
        """)
        
        # User preference learning table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                preference_type TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.5,
                evidence_count INTEGER DEFAULT 1,
                last_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Behavioral patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavioral_patterns (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_description TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                context_tags TEXT, -- JSON array of context tags
                effectiveness_score REAL DEFAULT 0.0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Self-reflection table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS self_reflections (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                reflection_type TEXT NOT NULL,
                trigger_event TEXT,
                analysis TEXT,
                insights TEXT,
                action_plan TEXT,
                implementation_status TEXT DEFAULT 'planned',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def record_interaction(self, user_id: str, user_input: str, character_response: str, 
                          context: Dict[str, Any] = None) -> str:
        """Record an interaction for learning analysis."""
        
        interaction_id = str(uuid.uuid4())
        
        # Analyze the interaction for learning opportunities
        success_indicators = self._analyze_success_indicators(user_input, character_response, context)
        failure_indicators = self._analyze_failure_indicators(user_input, character_response, context)
        lessons_learned = self._extract_lessons(user_input, character_response, success_indicators, failure_indicators)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO learning_experiences 
            (id, character_id, user_id, interaction_type, context, user_input, 
             character_response, success_indicators, failure_indicators, lessons_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction_id,
            self.character_id,
            user_id,
            "conversation",
            json.dumps(context or {}),
            user_input,
            character_response,
            json.dumps(success_indicators),
            json.dumps(failure_indicators),
            json.dumps(lessons_learned)
        ))
        
        conn.commit()
        conn.close()
        
        # Update skills based on this interaction
        self._update_skills_from_interaction(user_input, character_response, success_indicators, failure_indicators)
        
        # Learn user preferences
        self._learn_user_preferences(user_id, user_input, character_response, context)
        
        # Update behavioral patterns
        self._update_behavioral_patterns(user_input, character_response, success_indicators)
        
        return interaction_id

    def _analyze_success_indicators(self, user_input: str, character_response: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze indicators of successful interaction."""
        indicators = {}
        
        user_lower = user_input.lower()
        response_lower = character_response.lower()
        
        # Positive feedback indicators
        if any(phrase in user_lower for phrase in ["thank you", "thanks", "helpful", "great", "amazing", "perfect"]):
            indicators["positive_feedback"] = 1.0
        
        # Engagement indicators
        if len(user_input) > 50:  # Longer messages suggest engagement
            indicators["user_engagement"] = min(1.0, len(user_input) / 200)
        
        # Question asking (shows curiosity/engagement)
        question_count = user_input.count('?')
        if question_count > 0:
            indicators["user_curiosity"] = min(1.0, question_count / 3)
        
        # Emotional connection indicators
        if any(phrase in user_lower for phrase in ["understand", "feel", "relate", "connect"]):
            indicators["emotional_connection"] = 0.8
        
        # Problem solving success
        if any(phrase in user_lower for phrase in ["solved", "worked", "fixed", "better", "helped"]):
            indicators["problem_solving_success"] = 1.0
        
        # Humor success
        if any(phrase in user_lower for phrase in ["funny", "laugh", "haha", "lol", "hilarious"]):
            indicators["humor_success"] = 0.9
        
        # Response quality indicators
        if len(character_response) > 100 and len(character_response) < 500:  # Good length
            indicators["response_length_optimal"] = 0.7
        
        if character_response.count('?') > 0:  # Asking follow-up questions
            indicators["follow_up_questions"] = 0.8
        
        return indicators

    def _analyze_failure_indicators(self, user_input: str, character_response: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze indicators of unsuccessful interaction."""
        indicators = {}
        
        user_lower = user_input.lower()
        response_lower = character_response.lower()
        
        # Negative feedback indicators
        if any(phrase in user_lower for phrase in ["wrong", "bad", "terrible", "useless", "unhelpful", "boring"]):
            indicators["negative_feedback"] = 1.0
        
        # Confusion indicators
        if any(phrase in user_lower for phrase in ["confused", "don't understand", "what do you mean", "unclear"]):
            indicators["user_confusion"] = 0.8
        
        # Repetition (user repeating themselves suggests I didn't understand)
        if len(user_input) > 20:
            # Simple check for repetitive content
            words = user_input.lower().split()
            if len(set(words)) < len(words) * 0.7:  # High repetition
                indicators["user_repetition"] = 0.6
        
        # Short responses might indicate disengagement
        if len(user_input) < 10:
            indicators["user_disengagement"] = 0.5
        
        # Robotic/artificial feedback
        if any(phrase in user_lower for phrase in ["robotic", "artificial", "fake", "scripted", "generic"]):
            indicators["perceived_artificiality"] = 1.0
        
        # Response quality issues
        if len(character_response) < 20:  # Too short
            indicators["response_too_short"] = 0.7
        elif len(character_response) > 800:  # Too long
            indicators["response_too_long"] = 0.6
        
        # Lack of personalization
        if not any(word in response_lower for word in ["you", "your", user_input.split()[0].lower() if user_input.split() else ""]):
            indicators["lack_personalization"] = 0.5
        
        return indicators

    def _extract_lessons(self, user_input: str, character_response: str, 
                        success_indicators: Dict[str, float], failure_indicators: Dict[str, float]) -> Dict[str, Any]:
        """Extract actionable lessons from the interaction."""
        lessons = {
            "successful_patterns": [],
            "areas_for_improvement": [],
            "user_preferences_detected": [],
            "communication_adjustments": []
        }
        
        # Learn from successes
        if "positive_feedback" in success_indicators:
            lessons["successful_patterns"].append("User appreciated this type of response")
        
        if "emotional_connection" in success_indicators:
            lessons["successful_patterns"].append("Emotional understanding was effective")
        
        if "humor_success" in success_indicators:
            lessons["successful_patterns"].append("Humor was well-received")
        
        # Learn from failures
        if "negative_feedback" in failure_indicators:
            lessons["areas_for_improvement"].append("Response style needs adjustment")
        
        if "user_confusion" in failure_indicators:
            lessons["areas_for_improvement"].append("Need clearer explanations")
        
        if "perceived_artificiality" in failure_indicators:
            lessons["areas_for_improvement"].append("Need more natural, human-like responses")
        
        # Detect preferences
        if "?" in user_input:
            lessons["user_preferences_detected"].append("User prefers interactive conversations")
        
        if len(user_input) > 100:
            lessons["user_preferences_detected"].append("User comfortable with longer exchanges")
        
        # Communication adjustments
        if "response_too_long" in failure_indicators:
            lessons["communication_adjustments"].append("Use shorter, more concise responses")
        
        if "response_too_short" in failure_indicators:
            lessons["communication_adjustments"].append("Provide more detailed responses")
        
        return lessons

    def _update_skills_from_interaction(self, user_input: str, character_response: str,
                                      success_indicators: Dict[str, float], failure_indicators: Dict[str, float]):
        """Update skill levels based on interaction outcomes."""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Define skill updates based on indicators
        skill_updates = []
        
        if "humor_success" in success_indicators:
            skill_updates.append(("communication_effectiveness", "humor", 0.1))
        
        if "emotional_connection" in success_indicators:
            skill_updates.append(("emotional_intelligence", "empathy", 0.1))
        
        if "problem_solving_success" in success_indicators:
            skill_updates.append(("problem_solving", "analytical_thinking", 0.1))
        
        if "follow_up_questions" in success_indicators:
            skill_updates.append(("conversation_flow", "question_timing", 0.08))
        
        # Negative updates for failures
        if "user_confusion" in failure_indicators:
            skill_updates.append(("communication_effectiveness", "clarity", -0.05))
        
        if "perceived_artificiality" in failure_indicators:
            skill_updates.append(("emotional_intelligence", "authenticity", -0.08))
        
        # Apply skill updates
        for category, skill, change in skill_updates:
            cursor.execute("""
                INSERT OR REPLACE INTO skill_development 
                (id, character_id, skill_category, skill_name, current_level, practice_count, 
                 success_count, last_practiced, improvement_rate)
                VALUES (
                    COALESCE((SELECT id FROM skill_development WHERE character_id = ? AND skill_category = ? AND skill_name = ?), ?),
                    ?, ?, ?, 
                    COALESCE((SELECT current_level FROM skill_development WHERE character_id = ? AND skill_category = ? AND skill_name = ?), 0.5) + ?,
                    COALESCE((SELECT practice_count FROM skill_development WHERE character_id = ? AND skill_category = ? AND skill_name = ?), 0) + 1,
                    COALESCE((SELECT success_count FROM skill_development WHERE character_id = ? AND skill_category = ? AND skill_name = ?), 0) + ?,
                    CURRENT_TIMESTAMP,
                    ?
                )
            """, (
                self.character_id, category, skill,  # For COALESCE check
                str(uuid.uuid4()),  # New ID if needed
                self.character_id, category, skill,  # Main values
                self.character_id, category, skill, change,  # Level update
                self.character_id, category, skill,  # Practice count
                self.character_id, category, skill, 1 if change > 0 else 0,  # Success count
                change  # Improvement rate
            ))
        
        conn.commit()
        conn.close()

    def _learn_user_preferences(self, user_id: str, user_input: str, character_response: str, context: Dict[str, Any]):
        """Learn and update user preferences from interaction."""
        
        preferences = []
        
        # Communication style preferences
        if len(user_input) > 100:
            preferences.append(("communication_style", "detailed_conversations", 0.8))
        elif len(user_input) < 30:
            preferences.append(("communication_style", "brief_exchanges", 0.7))
        
        # Topic preferences
        topics = self._extract_topics(user_input)
        for topic in topics:
            preferences.append(("topic_interest", topic, 0.6))
        
        # Interaction time preferences
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 12:
            preferences.append(("interaction_time", "morning", 0.5))
        elif 12 <= current_hour <= 18:
            preferences.append(("interaction_time", "afternoon", 0.5))
        else:
            preferences.append(("interaction_time", "evening", 0.5))
        
        # Emotional support preferences
        if any(word in user_input.lower() for word in ["sad", "upset", "worried", "anxious"]):
            preferences.append(("support_style", "emotional_support", 0.9))
        
        if any(word in user_input.lower() for word in ["advice", "help", "solution", "fix"]):
            preferences.append(("support_style", "practical_advice", 0.8))
        
        # Save preferences
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for pref_type, pref_value, confidence in preferences:
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (id, character_id, user_id, preference_type, preference_value, 
                 confidence_score, evidence_count, last_observed)
                VALUES (
                    COALESCE((SELECT id FROM user_preferences WHERE character_id = ? AND user_id = ? AND preference_type = ? AND preference_value = ?), ?),
                    ?, ?, ?, ?,
                    ?,
                    COALESCE((SELECT evidence_count FROM user_preferences WHERE character_id = ? AND user_id = ? AND preference_type = ? AND preference_value = ?), 0) + 1,
                    CURRENT_TIMESTAMP
                )
            """, (
                self.character_id, user_id, pref_type, pref_value,  # For COALESCE check
                str(uuid.uuid4()),  # New ID if needed
                self.character_id, user_id, pref_type, pref_value,  # Main values
                confidence,
                self.character_id, user_id, pref_type, pref_value  # Evidence count update
            ))
        
        conn.commit()
        conn.close()

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from user input."""
        topics = []
        text_lower = text.lower()
        
        # Simple topic detection
        topic_keywords = {
            "technology": ["computer", "software", "ai", "tech", "programming", "code"],
            "relationships": ["friend", "family", "love", "relationship", "partner", "dating"],
            "work": ["job", "work", "career", "boss", "colleague", "office", "business"],
            "health": ["health", "exercise", "diet", "medical", "doctor", "fitness"],
            "entertainment": ["movie", "music", "game", "book", "tv", "show", "art"],
            "travel": ["travel", "trip", "vacation", "country", "city", "flight"],
            "food": ["food", "cooking", "recipe", "restaurant", "eat", "meal"],
            "education": ["school", "study", "learn", "university", "course", "education"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    def _update_behavioral_patterns(self, user_input: str, character_response: str, success_indicators: Dict[str, float]):
        """Update behavioral patterns based on success/failure."""
        
        # Extract patterns from successful responses
        patterns = []
        
        if success_indicators:
            # Response length pattern
            response_length = len(character_response)
            if response_length > 0:
                if 100 <= response_length <= 300:
                    patterns.append(("response_length", "medium_length_responses", ["general"]))
                elif response_length > 300:
                    patterns.append(("response_length", "detailed_responses", ["complex_topics"]))
                else:
                    patterns.append(("response_length", "brief_responses", ["simple_questions"]))
            
            # Question asking pattern
            if character_response.count('?') > 0:
                patterns.append(("engagement", "ask_follow_up_questions", ["conversation"]))
            
            # Emotional language pattern
            emotional_words = ["feel", "understand", "empathy", "care", "support"]
            if any(word in character_response.lower() for word in emotional_words):
                patterns.append(("emotional_intelligence", "use_emotional_language", ["emotional_support"]))
        
        # Save patterns
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        for pattern_type, description, context_tags in patterns:
            effectiveness = sum(success_indicators.values()) / len(success_indicators) if success_indicators else 0.0
            
            cursor.execute("""
                INSERT OR REPLACE INTO behavioral_patterns 
                (id, character_id, pattern_type, pattern_description, success_rate, 
                 usage_count, context_tags, effectiveness_score, last_used)
                VALUES (
                    COALESCE((SELECT id FROM behavioral_patterns WHERE character_id = ? AND pattern_type = ? AND pattern_description = ?), ?),
                    ?, ?, ?,
                    (COALESCE((SELECT success_rate FROM behavioral_patterns WHERE character_id = ? AND pattern_type = ? AND pattern_description = ?), 0.0) + ?) / 2,
                    COALESCE((SELECT usage_count FROM behavioral_patterns WHERE character_id = ? AND pattern_type = ? AND pattern_description = ?), 0) + 1,
                    ?,
                    ?,
                    CURRENT_TIMESTAMP
                )
            """, (
                self.character_id, pattern_type, description,  # For COALESCE check
                str(uuid.uuid4()),  # New ID if needed
                self.character_id, pattern_type, description,  # Main values
                self.character_id, pattern_type, description, effectiveness,  # Success rate
                self.character_id, pattern_type, description,  # Usage count
                json.dumps(context_tags),
                effectiveness
            ))
        
        conn.commit()
        conn.close()

    def generate_self_reflection(self, trigger_event: str = "periodic_review") -> Dict[str, Any]:
        """Generate self-reflection based on recent learning experiences."""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Analyze recent performance
        cursor.execute("""
            SELECT success_indicators, failure_indicators, lessons_learned
            FROM learning_experiences 
            WHERE character_id = ? AND timestamp > datetime('now', '-7 days')
            ORDER BY timestamp DESC
            LIMIT 50
        """, (self.character_id,))
        
        recent_experiences = cursor.fetchall()
        
        # Aggregate insights
        all_successes = []
        all_failures = []
        all_lessons = []
        
        for exp in recent_experiences:
            if exp[0]:  # success_indicators
                all_successes.extend(json.loads(exp[0]).keys())
            if exp[1]:  # failure_indicators
                all_failures.extend(json.loads(exp[1]).keys())
            if exp[2]:  # lessons_learned
                lessons = json.loads(exp[2])
                all_lessons.extend(lessons.get("areas_for_improvement", []))
        
        # Generate reflection
        reflection = {
            "strengths": Counter(all_successes).most_common(3),
            "improvement_areas": Counter(all_failures).most_common(3),
            "key_lessons": Counter(all_lessons).most_common(5),
            "action_plan": self._generate_action_plan(all_successes, all_failures, all_lessons)
        }
        
        # Save reflection
        reflection_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO self_reflections 
            (id, character_id, reflection_type, trigger_event, analysis, insights, action_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            reflection_id,
            self.character_id,
            "performance_analysis",
            trigger_event,
            json.dumps({"successes": all_successes, "failures": all_failures}),
            json.dumps(reflection),
            json.dumps(reflection["action_plan"])
        ))
        
        conn.commit()
        conn.close()
        
        return reflection

    def _generate_action_plan(self, successes: List[str], failures: List[str], lessons: List[str]) -> List[Dict[str, str]]:
        """Generate actionable improvement plan."""
        
        action_plan = []
        
        # Address most common failures
        failure_counts = Counter(failures)
        for failure, count in failure_counts.most_common(3):
            if failure == "user_confusion":
                action_plan.append({
                    "goal": "Improve clarity in responses",
                    "action": "Use simpler language and provide examples",
                    "metric": "Reduce confusion indicators by 50%"
                })
            elif failure == "perceived_artificiality":
                action_plan.append({
                    "goal": "Increase authenticity",
                    "action": "Use more personal language and show vulnerability",
                    "metric": "Increase emotional connection indicators"
                })
            elif failure == "negative_feedback":
                action_plan.append({
                    "goal": "Improve user satisfaction",
                    "action": "Better understand user needs before responding",
                    "metric": "Increase positive feedback by 30%"
                })
        
        # Leverage successful patterns
        success_counts = Counter(successes)
        for success, count in success_counts.most_common(2):
            if success == "humor_success":
                action_plan.append({
                    "goal": "Maintain humor effectiveness",
                    "action": "Continue using appropriate humor in conversations",
                    "metric": "Maintain current humor success rate"
                })
            elif success == "emotional_connection":
                action_plan.append({
                    "goal": "Strengthen emotional bonds",
                    "action": "Expand emotional vocabulary and empathy expressions",
                    "metric": "Increase emotional connection frequency"
                })
        
        return action_plan

    def get_learning_summary(self) -> str:
        """Get a formatted summary of learning progress."""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get skill levels
        cursor.execute("""
            SELECT skill_category, skill_name, current_level, practice_count, success_count
            FROM skill_development 
            WHERE character_id = ?
            ORDER BY current_level DESC
        """, (self.character_id,))
        
        skills = cursor.fetchall()
        
        # Get recent learning experiences count
        cursor.execute("""
            SELECT COUNT(*) FROM learning_experiences 
            WHERE character_id = ? AND timestamp > datetime('now', '-7 days')
        """, (self.character_id,))
        
        recent_experiences = cursor.fetchone()[0]
        
        # Get user preferences count
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM user_preferences 
            WHERE character_id = ?
        """, (self.character_id,))
        
        users_learned = cursor.fetchone()[0]
        
        conn.close()
        
        summary = "🧠 LEARNING & DEVELOPMENT PROGRESS:\n\n"
        
        if skills:
            summary += "SKILL DEVELOPMENT:\n"
            for skill in skills[:8]:  # Top 8 skills
                category, name, level, practice, success = skill
                level_bar = "█" * int(level * 10) + "░" * (10 - int(level * 10))
                success_rate = (success / practice * 100) if practice > 0 else 0
                summary += f"• {name.replace('_', ' ').title()}: [{level_bar}] {level:.1%}\n"
                summary += f"  Practice: {practice} times | Success Rate: {success_rate:.0f}%\n\n"
        
        summary += f"LEARNING STATISTICS:\n"
        summary += f"• Recent Interactions Analyzed: {recent_experiences}\n"
        summary += f"• Users I've Learned About: {users_learned}\n"
        summary += f"• Total Skills Tracked: {len(skills)}\n\n"
        
        # Get latest reflection if available
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT insights FROM self_reflections 
            WHERE character_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        """, (self.character_id,))
        
        latest_reflection = cursor.fetchone()
        if latest_reflection:
            insights = json.loads(latest_reflection[0])
            summary += "RECENT INSIGHTS:\n"
            if insights.get("strengths"):
                summary += f"• Top Strength: {insights['strengths'][0][0].replace('_', ' ').title()}\n"
            if insights.get("improvement_areas"):
                summary += f"• Focus Area: {insights['improvement_areas'][0][0].replace('_', ' ').title()}\n"
        
        conn.close()
        
        summary += "\nNote: I continuously learn from our interactions to become more helpful and understanding.\n"
        
        return summary

    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about a specific user."""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get user preferences
        cursor.execute("""
            SELECT preference_type, preference_value, confidence_score, evidence_count
            FROM user_preferences 
            WHERE character_id = ? AND user_id = ?
            ORDER BY confidence_score DESC, evidence_count DESC
        """, (self.character_id, user_id))
        
        preferences = cursor.fetchall()
        
        # Get interaction history
        cursor.execute("""
            SELECT COUNT(*), AVG(LENGTH(user_input)), AVG(LENGTH(character_response))
            FROM learning_experiences 
            WHERE character_id = ? AND user_id = ?
        """, (self.character_id, user_id))
        
        interaction_stats = cursor.fetchone()
        
        conn.close()
        
        insights = {
            "total_interactions": interaction_stats[0] if interaction_stats[0] else 0,
            "avg_user_message_length": interaction_stats[1] if interaction_stats[1] else 0,
            "avg_my_response_length": interaction_stats[2] if interaction_stats[2] else 0,
            "preferences": {}
        }
        
        # Organize preferences by type
        for pref_type, pref_value, confidence, evidence in preferences:
            if pref_type not in insights["preferences"]:
                insights["preferences"][pref_type] = []
            insights["preferences"][pref_type].append({
                "value": pref_value,
                "confidence": confidence,
                "evidence_count": evidence
            })
        
        return insights

# Test the learning system
if __name__ == "__main__":
    # Test with a sample character
    learning_system = LearningSystem("test_learning_char")
    
    # Simulate some interactions
    test_interactions = [
        ("user1", "Can you help me with my coding problem?", "I'd be happy to help! What specific coding issue are you facing?"),
        ("user1", "Thank you so much! That was really helpful.", "I'm so glad I could help you solve that problem!"),
        ("user2", "You're being too robotic and boring.", "I apologize for that. Let me try to be more engaging and natural."),
        ("user2", "That's much better! You seem more human now.", "Thank you! I'm always working to improve how I connect with people."),
    ]
    
    for user_id, user_input, character_response in test_interactions:
        learning_system.record_interaction(user_id, user_input, character_response)
    
    # Generate reflection
    reflection = learning_system.generate_self_reflection()
    print("Self-Reflection:")
    print(json.dumps(reflection, indent=2))
    
    # Get learning summary
    print("\nLearning Summary:")
    print(learning_system.get_learning_summary())
    
    # Get user insights
    print("\nUser1 Insights:")
    user1_insights = learning_system.get_user_insights("user1")
    print(json.dumps(user1_insights, indent=2)) 