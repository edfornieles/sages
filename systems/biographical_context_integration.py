#!/usr/bin/env python3
"""
[DEPRECATED] Biographical Context Integration
This module is deprecated. Historical character context is now loaded at agent creation
and included in the system prompt. Use the recall/search API from historical_character_loader instead.
"""
# This file is now deprecated and kept only for backward compatibility.
# All on-demand context injection logic has been removed.

import re
from typing import Dict, List, Any, Optional, Tuple
from systems.biographical_data_system import biographical_system
import logging

logger = logging.getLogger(__name__)

class BiographicalContextIntegration:
    """Integrates biographical data into chat context on-demand."""
    
    def __init__(self):
        self.bio_system = biographical_system
        
        # Patterns to detect when biographical context might be needed
        self.bio_triggers = {
            'life_events': [
                r'\b(birth|born|death|died|life|lived|childhood|youth|adulthood)\b',
                r'\b(marriage|married|divorce|family|children|parents)\b',
                r'\b(education|studied|university|school|degree)\b',
                r'\b(career|job|work|profession|occupation)\b'
            ],
            'achievements': [
                r'\b(achievement|accomplishment|success|award|prize|recognition)\b',
                r'\b(discovery|invention|creation|work|book|theory)\b',
                r'\b(contribution|impact|influence|legacy)\b'
            ],
            'beliefs_philosophy': [
                r'\b(belief|beliefs|philosophy|philosophical|theory|theories)\b',
                r'\b(opinion|view|views|perspective|thinking)\b',
                r'\b(principle|principles|values|morals|ethics)\b'
            ],
            'relationships': [
                r'\b(friend|friends|colleague|colleagues|student|students)\b',
                r'\b(teacher|mentor|influence|influenced|relationship)\b',
                r'\b(wife|husband|spouse|partner|family)\b'
            ],
            'historical_context': [
                r'\b(history|historical|period|era|time|century)\b',
                r'\b(culture|cultural|society|social|political)\b',
                r'\b(war|conflict|revolution|movement|change)\b'
            ],
            'specific_questions': [
                r'\b(who|what|when|where|why|how)\b.*\b(was|did|said|thought|believed)\b',
                r'\b(tell me about|what do you know about|explain)\b',
                r'\b(describe|discuss|analyze|examine)\b'
            ]
        }
        
        # Historical character names that might be mentioned
        self.historical_characters = self.bio_system.list_available_historical_characters()
        
    def should_include_biographical_context(self, message: str, character_name: str = None) -> Tuple[bool, List[str]]:
        """Determine if biographical context should be included based on the message."""
        message_lower = message.lower()
        triggers_found = []
        
        # Check if the message mentions a historical character
        mentioned_character = self._detect_mentioned_character(message_lower)
        if mentioned_character:
            triggers_found.append(f"mentions_historical_character:{mentioned_character}")
        
        # Check for biographical trigger patterns
        for category, patterns in self.bio_triggers.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    triggers_found.append(category)
                    break
        
        # Check if the current character is historical
        is_historical_character = character_name and self.bio_system.is_historical_character(character_name)
        if is_historical_character:
            triggers_found.append("current_character_historical")
        
        # Determine if context should be included
        # For historical characters, only include context if there are specific triggers beyond just being historical
        if is_historical_character:
            # Remove the "current_character_historical" trigger for the decision
            decision_triggers = [t for t in triggers_found if t != "current_character_historical"]
            should_include = len(decision_triggers) > 0
        else:
            should_include = len(triggers_found) > 0
        
        return should_include, triggers_found
    
    def _detect_mentioned_character(self, message: str) -> Optional[str]:
        """Detect if a historical character is mentioned in the message."""
        for character in self.historical_characters:
            # Check for exact name matches
            if character.lower() in message:
                return character
            
            # Check for common variations
            name_parts = character.lower().split()
            if len(name_parts) > 1:
                # Check for first name only
                if name_parts[0] in message and len(name_parts[0]) > 3:
                    return character
                # Check for last name only
                if name_parts[-1] in message and len(name_parts[-1]) > 3:
                    return character
        
        return None
    
    def get_relevant_biographical_context(self, message: str, character_name: str = None) -> Optional[str]:
        """Get relevant biographical context for the message."""
        should_include, triggers = self.should_include_biographical_context(message, character_name)
        
        if not should_include:
            return None
        
        context_parts = []
        
        # Handle mentioned historical character
        mentioned_character = self._detect_mentioned_character(message.lower())
        if mentioned_character:
            context_parts.append(self._get_character_context(mentioned_character, message))
        
        # Handle current character if historical
        if character_name and self.bio_system.is_historical_character(character_name):
            context_parts.append(self._get_character_context(character_name, message))
        
        return "\n\n".join([part for part in context_parts if part])
    
    def _get_character_context(self, character_name: str, message: str) -> str:
        """Get context for a specific character based on the message."""
        context_parts = []
        
        # Get character summary
        summary = self.bio_system.get_character_summary(character_name)
        if summary:
            context_parts.append(f"📚 {character_name} Summary:\n{summary}")
        
        # Search for relevant content
        search_results = self.bio_system.search_biographical_content(character_name, message)
        if search_results:
            relevant_info = []
            for result in search_results[:3]:  # Limit to top 3 results
                if result["type"] == "core_belief":
                    relevant_info.append(f"💭 Belief: {result['content']}")
                elif result["type"] == "key_event":
                    relevant_info.append(f"📅 Event: {result['content']}")
                elif result["type"] == "relationship":
                    relevant_info.append(f"👥 Relationship: {result['content']}")
                elif result["type"] == "achievement":
                    relevant_info.append(f"🏆 Achievement: {result['content']}")
            
            if relevant_info:
                context_parts.append(f"🔍 Relevant Information:\n" + "\n".join(relevant_info))
        
        # Get historical context if relevant
        historical_context = self.bio_system.get_historical_context(character_name, message)
        if historical_context:
            context_parts.append(f"🌍 Historical Context:\n{historical_context}")
        
        return "\n\n".join(context_parts)
    
    def enhance_agent_instructions_with_biographical_access(self, base_instructions: str) -> str:
        """Add instructions for accessing biographical data to agent instructions."""
        bio_instructions = """

📚 BIOGRAPHICAL DATA ACCESS:
You have access to rich biographical data for historical figures. When users ask about:
- Historical figures' lives, beliefs, or achievements
- Historical events or contexts
- Philosophical or theoretical discussions
- Personal relationships or influences

You can reference this data to provide accurate, detailed responses. The system will automatically provide relevant biographical context when needed.

When discussing historical figures, you can:
- Reference their actual beliefs and writings
- Mention key life events and achievements
- Discuss their historical context and influence
- Quote from their original works (when available)
- Explain their relationships and connections

This helps you provide authentic, historically accurate responses while maintaining your character's personality.
"""
        
        return base_instructions + bio_instructions
    
    def get_biographical_context_for_agent(self, message: str, character_name: str = None) -> Dict[str, Any]:
        """Get structured biographical context for agent use."""
        context = {
            "should_include": False,
            "triggers": [],
            "mentioned_characters": [],
            "relevant_data": {},
            "context_text": ""
        }
        
        should_include, triggers = self.should_include_biographical_context(message, character_name)
        context["should_include"] = should_include
        context["triggers"] = triggers
        
        if should_include:
            # Get mentioned characters
            mentioned_character = self._detect_mentioned_character(message.lower())
            if mentioned_character:
                context["mentioned_characters"].append(mentioned_character)
                context["relevant_data"][mentioned_character] = {
                    "summary": self.bio_system.get_character_summary(mentioned_character),
                    "search_results": self.bio_system.search_biographical_content(mentioned_character, message),
                    "speaking_style": self.bio_system.get_speaking_style(mentioned_character)
                }
            
            # Get context for current character if historical
            if character_name and self.bio_system.is_historical_character(character_name):
                context["relevant_data"][character_name] = {
                    "summary": self.bio_system.get_character_summary(character_name),
                    "search_results": self.bio_system.search_biographical_content(character_name, message),
                    "speaking_style": self.bio_system.get_speaking_style(character_name)
                }
            
            # Generate context text
            context["context_text"] = self.get_relevant_biographical_context(message, character_name)
        
        return context


# Global instance for easy access
bio_context_integration = BiographicalContextIntegration() 