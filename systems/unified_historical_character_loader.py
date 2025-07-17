#!/usr/bin/env python3
"""
Unified Historical Character Loader
Loads biography, style, expertise, and works for historical characters from the correct directories.
Provides recall/search API for agent use.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class UnifiedHistoricalCharacterLoader:
    def __init__(self):
        """Initialize the unified historical character loader."""
        self.biographies_dir = Path("data/biographies")
        self.style_profiles_dir = Path("data/original_texts/style_profiles")
        self._cache = {}
        
    def get_available_historical_characters(self) -> List[str]:
        """Get list of available historical character IDs."""
        characters = []
        
        # Scan biographies directory
        for bio_file in self.biographies_dir.glob("*.json"):
            character_name = bio_file.stem
            characters.append(f"historical_{character_name}")
            
        return characters
    
    def load_historical_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Load historical character data by ID (e.g., 'historical_isaac_newton')."""
        # Extract character name from ID
        if character_id.startswith("historical_"):
            character_name = character_id[len("historical_"):]  # Remove "historical_" prefix
        else:
            character_name = character_id
            
        # Check cache first
        if character_name in self._cache:
            return self._cache[character_name]
        
        # Load biography
        bio_file = self.biographies_dir / f"{character_name}.json"
        if not bio_file.exists():
            logger.warning(f"Biography file not found: {bio_file}")
            return None
            
        try:
            with open(bio_file, 'r', encoding='utf-8') as f:
                bio_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading biography for {character_name}: {e}")
            return None
        
        # Load style profile
        style_file = self.style_profiles_dir / f"{character_name}_style.json"
        style_data = {}
        if style_file.exists():
            try:
                with open(style_file, 'r', encoding='utf-8') as f:
                    style_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading style profile for {character_name}: {e}")
        
        # Combine data
        character_data = {
            "id": character_id,
            "name": bio_data.get("name", character_name.replace("_", " ").title()),
            "character_type": "historical",
            "biography": bio_data,
            "style_profile": style_data,
            "era": bio_data.get("era", ""),
            "field": bio_data.get("field", ""),
            "birth_year": bio_data.get("birth_year", ""),
            "death_year": bio_data.get("death_year", ""),
            "nationality": bio_data.get("nationality", ""),
            "key_achievements": bio_data.get("key_achievements", []),
            "personality_traits": {
                "traits": bio_data.get("personality_traits", []),
                "Emotional_Tone": "Analytical",
                "Communication_Style": "Formal and precise",
                "Social_Behavior": "Reserved and methodical",
                "Decision_Making": "Logical and systematic"
            },
            "communication_style": bio_data.get("communication_style", ""),
            "expertise_areas": bio_data.get("expertise_areas", []),
            "famous_quotes": bio_data.get("famous_quotes", []),
            "historical_context": bio_data.get("historical_context", ""),
            "learning_enabled": True,
            "memory_db_path": f"memories/{character_id}_memory.db",
            "appearance_description": f"A distinguished figure from the {bio_data.get('era', 'historical')} era, with an air of {bio_data.get('personality_traits', ['thoughtful'])[0].lower()} wisdom and {bio_data.get('communication_style', 'formal').lower()} bearing."
        }
        
        # Cache the result
        self._cache[character_name] = character_data
        
        return character_data
    
    def get_biography(self, character_data: Dict[str, Any]) -> str:
        """Get formatted biography text."""
        bio = character_data.get("biography", {})
        lines = []
        
        if bio.get("name"):
            lines.append(f"Name: {bio['name']}")
        if bio.get("era"):
            lines.append(f"Era: {bio['era']}")
        if bio.get("field"):
            lines.append(f"Field: {bio['field']}")
        if bio.get("birth_year") and bio.get("death_year"):
            lines.append(f"Lifespan: {bio['birth_year']} - {bio['death_year']}")
        if bio.get("nationality"):
            lines.append(f"Nationality: {bio['nationality']}")
        if bio.get("biography"):
            lines.append(f"Biography: {bio['biography']}")
        if bio.get("key_achievements"):
            lines.append(f"Key Achievements: {', '.join(bio['key_achievements'])}")
        if bio.get("expertise_areas"):
            lines.append(f"Areas of Expertise: {', '.join(bio['expertise_areas'])}")
        if bio.get("personality_traits"):
            lines.append(f"Personality Traits: {', '.join(bio['personality_traits'])}")
        if bio.get("communication_style"):
            lines.append(f"Communication Style: {bio['communication_style']}")
        if bio.get("historical_context"):
            lines.append(f"Historical Context: {bio['historical_context']}")
            
        return "\n".join(lines)
    
    def get_expertise(self, character_data: Dict[str, Any]) -> List[str]:
        """Get list of expertise areas."""
        bio = character_data.get("biography", {})
        return bio.get("expertise_areas", [])
    
    def get_style_profile(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get style profile data."""
        return character_data.get("style_profile", {})
    
    def get_famous_quotes(self, character_data: Dict[str, Any]) -> List[str]:
        """Get famous quotes."""
        bio = character_data.get("biography", {})
        return bio.get("famous_quotes", [])
    
    def recall(self, character_data: Dict[str, Any], topic: str) -> str:
        """Recall info about a topic from biography, expertise, or works."""
        topic = topic.lower()
        
        # Search biography
        bio = character_data.get("biography", {})
        for k, v in bio.items():
            if isinstance(v, str) and topic in v.lower():
                return v
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and topic in item.lower():
                        return item
        
        # Search style profile
        style = character_data.get("style_profile", {})
        for k, v in style.items():
            if isinstance(v, str) and topic in v.lower():
                return v
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and topic in item.lower():
                        return item
        
        # Search famous quotes
        for quote in self.get_famous_quotes(character_data):
            if topic in quote.lower():
                return quote
                
        return "No relevant information found."
    
    def search(self, character_data: Dict[str, Any], query: str) -> List[str]:
        """Search for all relevant info about a query."""
        query = query.lower()
        results = []
        
        # Search biography
        bio = character_data.get("biography", {})
        for k, v in bio.items():
            if isinstance(v, str) and query in v.lower():
                results.append(v)
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and query in item.lower():
                        results.append(item)
        
        # Search style profile
        style = character_data.get("style_profile", {})
        for k, v in style.items():
            if isinstance(v, str) and query in v.lower():
                results.append(v)
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and query in item.lower():
                        results.append(item)
        
        # Search famous quotes
        for quote in self.get_famous_quotes(character_data):
            if query in quote.lower():
                results.append(quote)
                
        return results

# Singleton instance
unified_historical_loader = UnifiedHistoricalCharacterLoader() 