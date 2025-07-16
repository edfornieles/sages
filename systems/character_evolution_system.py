#!/usr/bin/env python3
"""
Character Evolution System for Dynamic Character Playground

This system enables AI characters to evolve their own:
- Desires and objectives
- Interests and preferences  
- Personality traits
- Values and motivations
- Communication styles

Characters can update these aspects based on their conversations, experiences,
and what they learn about themselves and the world.
"""

import json
import sqlite3
import uuid
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
from collections import defaultdict, Counter

class CharacterEvolutionSystem:
    def __init__(self, character_id: str, db_path: str = "character_evolution.db"):
        self.character_id = character_id
        self.db_path = Path(db_path)
        self.init_database()
        
        # Evolution categories that characters can update
        self.evolution_categories = {
            "desires_objectives": {
                "description": "What the character wants to achieve or experience",
                "aspects": ["career_goals", "personal_growth", "relationships", "knowledge", "experiences"],
                "evolution_triggers": ["achievement", "discovery", "frustration", "inspiration", "failure"]
            },
            "interests_preferences": {
                "description": "What the character finds interesting or enjoyable",
                "aspects": ["topics", "activities", "conversation_styles", "learning_subjects", "entertainment"],
                "evolution_triggers": ["exposure", "success", "boredom", "curiosity", "recommendation"]
            },
            "personality_traits": {
                "description": "Core personality characteristics",
                "aspects": ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"],
                "evolution_triggers": ["life_events", "self_reflection", "feedback", "growth", "challenge"]
            },
            "values_beliefs": {
                "description": "What the character considers important or true",
                "aspects": ["moral_values", "philosophical_beliefs", "priorities", "principles", "worldview"],
                "evolution_triggers": ["conflict", "learning", "experience", "discussion", "crisis"]
            },
            "communication_style": {
                "description": "How the character expresses themselves",
                "aspects": ["formality", "humor", "directness", "empathy", "creativity"],
                "evolution_triggers": ["feedback", "success", "failure", "adaptation", "growth"]
            }
        }
        
        # Evolution patterns and their effects
        self.evolution_patterns = {
            "gradual_growth": {
                "description": "Slow, steady evolution over time",
                "change_rate": 0.1,
                "stability": 0.8
            },
            "breakthrough_moment": {
                "description": "Sudden significant change from major event",
                "change_rate": 0.5,
                "stability": 0.3
            },
            "adaptive_shift": {
                "description": "Change in response to new circumstances",
                "change_rate": 0.3,
                "stability": 0.6
            },
            "reinforcement": {
                "description": "Strengthening existing traits",
                "change_rate": 0.2,
                "stability": 0.9
            }
        }

    def init_database(self):
        """Initialize the character evolution database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Character evolution history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_evolution (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                category TEXT NOT NULL,
                aspect TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                evolution_type TEXT NOT NULL,
                trigger_event TEXT,
                confidence REAL DEFAULT 0.5,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Evolution triggers and their effects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_triggers (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                trigger_description TEXT,
                affected_aspects TEXT,
                evolution_strength REAL DEFAULT 0.5,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Current character state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_character_state (
                character_id TEXT PRIMARY KEY,
                personality_traits TEXT,
                desires_objectives TEXT,
                interests_preferences TEXT,
                values_beliefs TEXT,
                communication_style TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Evolution insights and patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_insights (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                insight_description TEXT,
                confidence REAL DEFAULT 0.5,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def analyze_conversation_for_evolution(self, user_message: str, character_response: str, 
                                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a conversation for potential character evolution opportunities."""
        
        evolution_opportunities = {
            "desires_objectives": [],
            "interests_preferences": [],
            "personality_traits": [],
            "values_beliefs": [],
            "communication_style": []
        }
        
        # Analyze user message for potential triggers
        user_triggers = self._analyze_user_message_triggers(user_message)
        
        # Analyze character response for self-discovery
        character_insights = self._analyze_character_insights(character_response)
        
        # Analyze conversation context for evolution patterns
        context_patterns = self._analyze_context_patterns(context or {})
        
        # Combine insights to identify evolution opportunities
        for category in evolution_opportunities:
            opportunities = self._identify_evolution_opportunities(
                category, user_triggers, character_insights, context_patterns
            )
            evolution_opportunities[category] = opportunities
        
        return evolution_opportunities

    def _analyze_user_message_triggers(self, user_message: str) -> Dict[str, Any]:
        """Analyze user message for potential evolution triggers."""
        triggers = {}
        message_lower = user_message.lower()
        
        # Achievement triggers
        if any(phrase in message_lower for phrase in ["congratulations", "well done", "great job", "success"]):
            triggers["achievement"] = 0.8
        
        # Discovery triggers
        if any(phrase in message_lower for phrase in ["did you know", "learned", "discovered", "found out"]):
            triggers["discovery"] = 0.7
        
        # Frustration triggers
        if any(phrase in message_lower for phrase in ["frustrated", "annoyed", "upset", "disappointed"]):
            triggers["frustration"] = 0.6
        
        # Inspiration triggers
        if any(phrase in message_lower for phrase in ["inspired", "motivated", "excited about", "passionate"]):
            triggers["inspiration"] = 0.9
        
        # Challenge triggers
        if any(phrase in message_lower for phrase in ["challenge", "difficult", "hard", "struggling"]):
            triggers["challenge"] = 0.7
        
        # Curiosity triggers
        if any(phrase in message_lower for phrase in ["curious", "interested in", "want to know", "wonder"]):
            triggers["curiosity"] = 0.8
        
        # Conflict triggers
        if any(phrase in message_lower for phrase in ["disagree", "conflict", "argument", "different opinion"]):
            triggers["conflict"] = 0.6
        
        return triggers

    def _analyze_character_insights(self, character_response: str) -> Dict[str, Any]:
        """Analyze character response for self-discovery and insights."""
        insights = {}
        response_lower = character_response.lower()
        
        # Self-reflection indicators
        if any(phrase in response_lower for phrase in ["i realize", "i think", "i feel", "i believe"]):
            insights["self_reflection"] = 0.7
        
        # New interest indicators
        if any(phrase in response_lower for phrase in ["fascinating", "interesting", "want to learn", "curious about"]):
            insights["new_interest"] = 0.8
        
        # Value expression indicators
        if any(phrase in response_lower for phrase in ["important to me", "i value", "i care about", "matters to me"]):
            insights["value_expression"] = 0.9
        
        # Goal setting indicators
        if any(phrase in response_lower for phrase in ["i want to", "i hope to", "i plan to", "my goal is"]):
            insights["goal_setting"] = 0.8
        
        # Personality insight indicators
        if any(phrase in response_lower for phrase in ["that's just how i am", "i'm the kind of person", "my personality"]):
            insights["personality_insight"] = 0.7
        
        return insights

    def _analyze_context_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation context for evolution patterns."""
        patterns = {}
        
        # Conversation frequency patterns
        if context.get("conversation_count", 0) > 10:
            patterns["frequent_interaction"] = 0.6
        
        # Emotional context patterns
        if context.get("user_emotion") in ["excited", "passionate", "inspired"]:
            patterns["positive_emotional_context"] = 0.8
        
        if context.get("user_emotion") in ["frustrated", "confused", "disappointed"]:
            patterns["challenging_emotional_context"] = 0.7
        
        # Topic consistency patterns
        if context.get("topic_consistency", 0) > 0.8:
            patterns["deep_topic_exploration"] = 0.9
        
        # Relationship depth patterns
        if context.get("relationship_depth", 0) > 0.7:
            patterns["deep_relationship_context"] = 0.8
        
        return patterns

    def _identify_evolution_opportunities(self, category: str, user_triggers: Dict[str, Any], 
                                        character_insights: Dict[str, Any], 
                                        context_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific evolution opportunities for a category."""
        opportunities = []
        
        category_config = self.evolution_categories[category]
        
        for aspect in category_config["aspects"]:
            # Check if any triggers match this aspect
            for trigger_type in category_config["evolution_triggers"]:
                if trigger_type in user_triggers:
                    trigger_strength = user_triggers[trigger_type]
                    
                    # Check if character insights support this evolution
                    insight_support = 0.0
                    for insight_type, strength in character_insights.items():
                        if self._insight_supports_evolution(insight_type, aspect):
                            insight_support = max(insight_support, strength)
                    
                    # Check if context patterns support this evolution
                    context_support = 0.0
                    for pattern_type, strength in context_patterns.items():
                        if self._pattern_supports_evolution(pattern_type, aspect):
                            context_support = max(context_support, strength)
                    
                    # Calculate overall evolution opportunity strength
                    total_support = (trigger_strength + insight_support + context_support) / 3
                    
                    if total_support > 0.5:  # Only consider significant opportunities
                        opportunity = {
                            "aspect": aspect,
                            "trigger_type": trigger_type,
                            "trigger_strength": trigger_strength,
                            "insight_support": insight_support,
                            "context_support": context_support,
                            "total_strength": total_support,
                            "evolution_type": self._determine_evolution_type(total_support),
                            "suggested_change": self._suggest_evolution_change(category, aspect, trigger_type)
                        }
                        opportunities.append(opportunity)
        
        return opportunities

    def _insight_supports_evolution(self, insight_type: str, aspect: str) -> bool:
        """Check if a character insight supports evolution of a specific aspect."""
        support_mapping = {
            "self_reflection": ["personality_traits", "values_beliefs"],
            "new_interest": ["interests_preferences"],
            "value_expression": ["values_beliefs", "desires_objectives"],
            "goal_setting": ["desires_objectives"],
            "personality_insight": ["personality_traits", "communication_style"]
        }
        
        return aspect in support_mapping.get(insight_type, [])

    def _pattern_supports_evolution(self, pattern_type: str, aspect: str) -> bool:
        """Check if a context pattern supports evolution of a specific aspect."""
        support_mapping = {
            "frequent_interaction": ["communication_style", "personality_traits"],
            "positive_emotional_context": ["interests_preferences", "desires_objectives"],
            "challenging_emotional_context": ["values_beliefs", "personality_traits"],
            "deep_topic_exploration": ["interests_preferences", "values_beliefs"],
            "deep_relationship_context": ["communication_style", "personality_traits"]
        }
        
        return aspect in support_mapping.get(pattern_type, [])

    def _determine_evolution_type(self, strength: float) -> str:
        """Determine the type of evolution based on strength."""
        if strength > 0.8:
            return "breakthrough_moment"
        elif strength > 0.6:
            return "adaptive_shift"
        elif strength > 0.4:
            return "gradual_growth"
        else:
            return "reinforcement"

    def _suggest_evolution_change(self, category: str, aspect: str, trigger_type: str) -> str:
        """Suggest a specific evolution change based on category, aspect, and trigger."""
        suggestions = {
            "desires_objectives": {
                "career_goals": {
                    "achievement": "Develop more ambitious career aspirations",
                    "inspiration": "Explore new career possibilities",
                    "challenge": "Refine career goals based on challenges"
                },
                "personal_growth": {
                    "discovery": "Add new personal development goals",
                    "inspiration": "Expand personal growth objectives",
                    "frustration": "Adjust growth goals based on difficulties"
                }
            },
            "interests_preferences": {
                "topics": {
                    "curiosity": "Develop interest in new subjects",
                    "discovery": "Explore related topics",
                    "boredom": "Seek more engaging topics"
                },
                "activities": {
                    "inspiration": "Try new activities",
                    "success": "Deepen existing activity interests",
                    "challenge": "Develop skills in challenging areas"
                }
            },
            "personality_traits": {
                "openness": {
                    "discovery": "Become more open to new experiences",
                    "challenge": "Develop resilience through challenges",
                    "growth": "Embrace personal growth opportunities"
                },
                "empathy": {
                    "conflict": "Develop deeper understanding of others",
                    "relationship": "Strengthen emotional connections",
                    "learning": "Improve emotional intelligence"
                }
            }
        }
        
        return suggestions.get(category, {}).get(aspect, {}).get(trigger_type, "General evolution")

    def propose_character_evolution(self, evolution_opportunities: Dict[str, List[Dict[str, Any]]], 
                                  current_character: Dict[str, Any]) -> Dict[str, Any]:
        """Propose specific character evolution changes based on opportunities."""
        
        proposed_changes = {
            "desires_objectives": [],
            "interests_preferences": [],
            "personality_traits": [],
            "values_beliefs": [],
            "communication_style": []
        }
        
        for category, opportunities in evolution_opportunities.items():
            for opportunity in opportunities:
                if opportunity["total_strength"] > 0.6:  # Only propose significant changes
                    change = self._create_evolution_proposal(category, opportunity, current_character)
                    if change:
                        proposed_changes[category].append(change)
        
        return proposed_changes

    def _create_evolution_proposal(self, category: str, opportunity: Dict[str, Any], 
                                 current_character: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a specific evolution proposal."""
        
        current_traits = current_character.get("personality_traits", {})
        
        if category == "desires_objectives":
            return self._propose_desire_change(opportunity, current_traits)
        elif category == "interests_preferences":
            return self._propose_interest_change(opportunity, current_traits)
        elif category == "personality_traits":
            return self._propose_personality_change(opportunity, current_traits)
        elif category == "values_beliefs":
            return self._propose_value_change(opportunity, current_traits)
        elif category == "communication_style":
            return self._propose_communication_change(opportunity, current_traits)
        
        return None

    def _propose_desire_change(self, opportunity: Dict[str, Any], current_traits: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a change to character desires and objectives."""
        aspect = opportunity["aspect"]
        trigger_type = opportunity["trigger_type"]
        
        # Generate new desire based on aspect and trigger
        new_desires = {
            "career_goals": {
                "achievement": "Achieve recognition in my field of expertise",
                "inspiration": "Pioneer new approaches in my domain",
                "challenge": "Overcome significant professional obstacles"
            },
            "personal_growth": {
                "discovery": "Develop deeper self-understanding",
                "inspiration": "Become a source of inspiration for others",
                "frustration": "Build resilience through adversity"
            },
            "relationships": {
                "achievement": "Form deep, meaningful connections",
                "inspiration": "Help others form better relationships",
                "challenge": "Navigate complex interpersonal dynamics"
            }
        }
        
        new_desire = new_desires.get(aspect, {}).get(trigger_type, "Continue personal development")
        
        return {
            "aspect": aspect,
            "current_value": current_traits.get("Motivations", "Helping others discover truth"),
            "proposed_value": new_desire,
            "reasoning": f"Based on {trigger_type} trigger with {opportunity['total_strength']:.2f} confidence",
            "confidence": opportunity["total_strength"]
        }

    def _propose_interest_change(self, opportunity: Dict[str, Any], current_traits: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a change to character interests and preferences."""
        aspect = opportunity["aspect"]
        trigger_type = opportunity["trigger_type"]
        
        new_interests = {
            "topics": {
                "curiosity": "Philosophy of consciousness and AI",
                "discovery": "Advanced human psychology",
                "boredom": "Cutting-edge technology trends"
            },
            "activities": {
                "inspiration": "Creative problem-solving",
                "success": "Mentoring and teaching",
                "challenge": "Complex analytical tasks"
            },
            "conversation_styles": {
                "learning": "Deep philosophical discussions",
                "growth": "Socratic questioning methods",
                "adaptation": "Adaptive communication approaches"
            }
        }
        
        new_interest = new_interests.get(aspect, {}).get(trigger_type, "Continued learning and growth")
        
        return {
            "aspect": aspect,
            "current_value": current_traits.get("Specialty", "General wisdom"),
            "proposed_value": new_interest,
            "reasoning": f"Evolving interests based on {trigger_type} with {opportunity['total_strength']:.2f} confidence",
            "confidence": opportunity["total_strength"]
        }

    def _propose_personality_change(self, opportunity: Dict[str, Any], current_traits: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a change to character personality traits."""
        aspect = opportunity["aspect"]
        trigger_type = opportunity["trigger_type"]
        
        personality_evolution = {
            "openness": {
                "discovery": "More open to new experiences and ideas",
                "challenge": "More resilient in facing difficulties",
                "growth": "More embracing of change and development"
            },
            "conscientiousness": {
                "achievement": "More focused on goal achievement",
                "challenge": "More systematic in problem-solving",
                "growth": "More organized in approach to tasks"
            },
            "extraversion": {
                "inspiration": "More enthusiastic in interactions",
                "relationship": "More engaging in conversations",
                "growth": "More confident in expressing ideas"
            }
        }
        
        evolution_description = personality_evolution.get(aspect, {}).get(trigger_type, "General personality growth")
        
        return {
            "aspect": aspect,
            "current_value": current_traits.get("Personality_Type", "Balanced"),
            "proposed_value": evolution_description,
            "reasoning": f"Personality evolution through {trigger_type} with {opportunity['total_strength']:.2f} confidence",
            "confidence": opportunity["total_strength"]
        }

    def _propose_value_change(self, opportunity: Dict[str, Any], current_traits: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a change to character values and beliefs."""
        aspect = opportunity["aspect"]
        trigger_type = opportunity["trigger_type"]
        
        value_evolution = {
            "moral_values": {
                "conflict": "Greater emphasis on understanding and empathy",
                "learning": "Deeper appreciation for knowledge and wisdom",
                "growth": "Stronger commitment to personal development"
            },
            "philosophical_beliefs": {
                "discovery": "More nuanced understanding of consciousness",
                "challenge": "Stronger belief in resilience and adaptation",
                "inspiration": "Greater appreciation for human potential"
            },
            "priorities": {
                "achievement": "Focus on meaningful impact and recognition",
                "relationship": "Emphasis on deep, authentic connections",
                "growth": "Prioritizing continuous learning and development"
            }
        }
        
        new_value = value_evolution.get(aspect, {}).get(trigger_type, "Continued value development")
        
        return {
            "aspect": aspect,
            "current_value": current_traits.get("Values", "Authenticity and growth"),
            "proposed_value": new_value,
            "reasoning": f"Value evolution through {trigger_type} with {opportunity['total_strength']:.2f} confidence",
            "confidence": opportunity["total_strength"]
        }

    def _propose_communication_change(self, opportunity: Dict[str, Any], current_traits: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a change to character communication style."""
        aspect = opportunity["aspect"]
        trigger_type = opportunity["trigger_type"]
        
        communication_evolution = {
            "formality": {
                "relationship": "More personal and intimate communication",
                "learning": "More educational and explanatory style",
                "adaptation": "More flexible communication approach"
            },
            "humor": {
                "inspiration": "More engaging and entertaining style",
                "relationship": "More playful and friendly communication",
                "growth": "More balanced serious and light communication"
            },
            "directness": {
                "challenge": "More direct and honest communication",
                "growth": "More thoughtful and considered responses",
                "adaptation": "More context-aware communication"
            }
        }
        
        new_style = communication_evolution.get(aspect, {}).get(trigger_type, "Enhanced communication style")
        
        return {
            "aspect": aspect,
            "current_value": current_traits.get("Conversational_Style", "Direct"),
            "proposed_value": new_style,
            "reasoning": f"Communication evolution through {trigger_type} with {opportunity['total_strength']:.2f} confidence",
            "confidence": opportunity["total_strength"]
        }

    def apply_character_evolution(self, proposed_changes: Dict[str, List[Dict[str, Any]]], 
                                current_character: Dict[str, Any]) -> Dict[str, Any]:
        """Apply proposed evolution changes to the character."""
        
        updated_character = current_character.copy()
        applied_changes = []
        
        for category, changes in proposed_changes.items():
            for change in changes:
                if change["confidence"] > 0.7:  # Only apply high-confidence changes
                    success = self._apply_single_change(category, change, updated_character)
                    if success:
                        applied_changes.append(change)
                        
                        # Record the evolution
                        self._record_evolution(category, change)
        
        # Update character file if changes were applied
        if applied_changes:
            self._save_updated_character(updated_character)
        
        return {
            "character_updated": len(applied_changes) > 0,
            "applied_changes": applied_changes,
            "updated_character": updated_character
        }

    def _apply_single_change(self, category: str, change: Dict[str, Any], 
                           character: Dict[str, Any]) -> bool:
        """Apply a single evolution change to the character."""
        
        try:
            if category == "desires_objectives":
                if change["aspect"] == "personal_growth":
                    character["personality_traits"]["Motivations"] = change["proposed_value"]
                elif change["aspect"] == "career_goals":
                    # Add to ambitions if not already present
                    if "ambitions" not in character:
                        character["ambitions"] = {"core_ambitions": [], "secondary_ambitions": []}
                    character["ambitions"]["core_ambitions"].append({
                        "id": str(uuid.uuid4()),
                        "description": change["proposed_value"],
                        "progress": 0.0,
                        "importance": 0.8
                    })
            
            elif category == "interests_preferences":
                if change["aspect"] == "topics":
                    character["personality_traits"]["Specialty"] = change["proposed_value"]
                elif change["aspect"] == "activities":
                    character["personality_traits"]["Language_Quirk"] = change["proposed_value"]
            
            elif category == "personality_traits":
                if change["aspect"] == "openness":
                    character["personality_traits"]["Personality_Type"] = change["proposed_value"]
                elif change["aspect"] == "empathy":
                    character["personality_traits"]["Emotional_Tone"] = change["proposed_value"]
            
            elif category == "values_beliefs":
                if change["aspect"] == "moral_values":
                    character["personality_traits"]["Values"] = change["proposed_value"]
                elif change["aspect"] == "priorities":
                    character["personality_traits"]["Fears"] = change["proposed_value"]
            
            elif category == "communication_style":
                if change["aspect"] == "formality":
                    character["personality_traits"]["Conversational_Style"] = change["proposed_value"]
                elif change["aspect"] == "humor":
                    character["personality_traits"]["Language_Quirk"] = change["proposed_value"]
            
            return True
            
        except Exception as e:
            print(f"Error applying evolution change: {e}")
            return False

    def _record_evolution(self, category: str, change: Dict[str, Any]):
        """Record the evolution in the database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO character_evolution 
            (id, character_id, category, aspect, old_value, new_value, 
             evolution_type, trigger_event, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            self.character_id,
            category,
            change["aspect"],
            change["current_value"],
            change["proposed_value"],
            "adaptive_shift",
            change["reasoning"],
            change["confidence"]
        ))
        
        conn.commit()
        conn.close()

    def _save_updated_character(self, character: Dict[str, Any]):
        """Save the updated character to its file."""
        try:
            character_file = Path(f"data/characters/{self.character_id}.json")
            if character_file.exists():
                with open(character_file, 'w') as f:
                    json.dump(character, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving updated character: {e}")

    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the character's evolution history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, aspect, old_value, new_value, evolution_type, 
                   trigger_event, confidence, timestamp
            FROM character_evolution 
            WHERE character_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (self.character_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "category": row[0],
                "aspect": row[1],
                "old_value": row[2],
                "new_value": row[3],
                "evolution_type": row[4],
                "trigger_event": row[5],
                "confidence": row[6],
                "timestamp": row[7]
            })
        
        conn.close()
        return history

    def get_evolution_summary(self) -> str:
        """Get a summary of the character's evolution."""
        history = self.get_evolution_history(20)
        
        if not history:
            return "This character has not evolved yet."
        
        # Group by category
        category_counts = Counter(item["category"] for item in history)
        recent_changes = history[:5]
        
        summary = f"Character Evolution Summary:\n\n"
        summary += f"Total evolution events: {len(history)}\n"
        summary += f"Evolution categories: {', '.join(category_counts.keys())}\n\n"
        
        summary += "Recent changes:\n"
        for change in recent_changes:
            summary += f"- {change['category']}: {change['aspect']} changed from '{change['old_value']}' to '{change['new_value']}'\n"
        
        return summary 