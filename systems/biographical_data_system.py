#!/usr/bin/env python3
"""
Biographical Data System - On-Demand Historical Character Data Access

This system provides access to biographical data, original texts, and style profiles
for historical characters without forcing them into context all the time.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BiographicalDataSystem:
    """Provides on-demand access to biographical data for historical characters."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.biographies_dir = self.data_dir / "biographies"
        self.original_texts_dir = self.data_dir / "original_texts"
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
    def get_biographical_data(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Get biographical data for a character by name."""
        cache_key = f"bio_{character_name.lower()}"
        
        # Check cache first
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return cached_data
        
        # Load from file
        bio_file = self.biographies_dir / f"{character_name.lower().replace(' ', '_')}.json"
        if not bio_file.exists():
            return None
            
        try:
            with open(bio_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Cache the result
            self._cache[cache_key] = (data, datetime.now())
            return data
            
        except Exception as e:
            logger.error(f"Error loading biographical data for {character_name}: {e}")
            return None
    
    def get_original_texts(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Get original texts and style profiles for a character."""
        cache_key = f"texts_{character_name.lower()}"
        
        # Check cache first
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return cached_data
        
        try:
            # Load processed passages
            passages_file = self.original_texts_dir / "processed" / f"{character_name.lower().replace(' ', '_')}_passages.json"
            passages = []
            if passages_file.exists():
                with open(passages_file, 'r', encoding='utf-8') as f:
                    passages = json.load(f)
            
            # Load style profile
            style_file = self.original_texts_dir / "style_profiles" / f"{character_name.lower().replace(' ', '_')}_style.json"
            style_profile = {}
            if style_file.exists():
                with open(style_file, 'r', encoding='utf-8') as f:
                    style_profile = json.load(f)
            
            # Load raw texts
            raw_texts_file = self.original_texts_dir / "raw_texts" / f"{character_name.lower().replace(' ', '_')}_selected_works.txt"
            raw_texts = ""
            if raw_texts_file.exists():
                with open(raw_texts_file, 'r', encoding='utf-8') as f:
                    raw_texts = f.read()
            
            data = {
                "passages": passages,
                "style_profile": style_profile,
                "raw_texts": raw_texts
            }
            
            # Cache the result
            self._cache[cache_key] = (data, datetime.now())
            return data
            
        except Exception as e:
            logger.error(f"Error loading original texts for {character_name}: {e}")
            return None
    
    def get_historical_context(self, character_name: str, topic: str = None) -> Optional[str]:
        """Get relevant historical context for a character and optional topic."""
        bio_data = self.get_biographical_data(character_name)
        if not bio_data:
            return None
        
        context_parts = []
        
        # Add basic biographical info
        if bio_data.get("historical_context"):
            context_parts.append(f"Historical Context: {bio_data['historical_context']}")
        
        if bio_data.get("cultural_background"):
            context_parts.append(f"Cultural Background: {bio_data['cultural_background']}")
        
        # Add topic-specific information
        if topic:
            topic_lower = topic.lower()
            
            # Check core beliefs for relevance
            if bio_data.get("core_beliefs"):
                relevant_beliefs = []
                for belief in bio_data["core_beliefs"]:
                    if topic_lower in belief.get("belief", "").lower() or topic_lower in belief.get("explanation", "").lower():
                        relevant_beliefs.append(belief["belief"])
                
                if relevant_beliefs:
                    context_parts.append(f"Relevant Beliefs: {'; '.join(relevant_beliefs)}")
            
            # Check key events for relevance
            if bio_data.get("key_events"):
                relevant_events = []
                for event in bio_data["key_events"]:
                    if topic_lower in event.get("event", "").lower() or topic_lower in event.get("significance", "").lower():
                        relevant_events.append(f"{event.get('date', 'Unknown date')}: {event['event']}")
                
                if relevant_events:
                    context_parts.append(f"Relevant Events: {'; '.join(relevant_events)}")
        
        return "\n".join(context_parts) if context_parts else None
    
    def get_speaking_style(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Get speaking style and mannerisms for a character."""
        bio_data = self.get_biographical_data(character_name)
        if not bio_data:
            return None
        
        style_data = {
            "speaking_style": bio_data.get("speaking_style", ""),
            "mannerisms": bio_data.get("mannerisms", []),
            "personality_traits": bio_data.get("personality_traits", []),
            "famous_quotes": bio_data.get("famous_quotes", [])
        }
        
        # Add style profile if available
        texts_data = self.get_original_texts(character_name)
        if texts_data and texts_data.get("style_profile"):
            style_data.update(texts_data["style_profile"])
        
        return style_data
    
    def search_biographical_content(self, character_name: str, query: str) -> List[Dict[str, Any]]:
        """Search biographical content for relevant information."""
        bio_data = self.get_biographical_data(character_name)
        if not bio_data:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Search in core beliefs
        if bio_data.get("core_beliefs"):
            for belief in bio_data["core_beliefs"]:
                if query_lower in belief.get("belief", "").lower() or query_lower in belief.get("explanation", "").lower():
                    results.append({
                        "type": "core_belief",
                        "content": belief["belief"],
                        "explanation": belief.get("explanation", ""),
                        "source": belief.get("source", ""),
                        "relevance": "high"
                    })
        
        # Search in key events
        if bio_data.get("key_events"):
            for event in bio_data["key_events"]:
                if query_lower in event.get("event", "").lower() or query_lower in event.get("significance", "").lower():
                    results.append({
                        "type": "key_event",
                        "content": event["event"],
                        "date": event.get("date", ""),
                        "significance": event.get("significance", ""),
                        "relevance": "high"
                    })
        
        # Search in relationships
        if bio_data.get("relationships"):
            for relationship in bio_data["relationships"]:
                if query_lower in relationship.get("name", "").lower() or query_lower in relationship.get("description", "").lower():
                    results.append({
                        "type": "relationship",
                        "content": f"{relationship['name']}: {relationship['description']}",
                        "relationship_type": relationship.get("relationship_type", ""),
                        "time_period": relationship.get("time_period", ""),
                        "relevance": "medium"
                    })
        
        # Search in achievements
        if bio_data.get("achievements"):
            for achievement in bio_data["achievements"]:
                if query_lower in achievement.lower():
                    results.append({
                        "type": "achievement",
                        "content": achievement,
                        "relevance": "medium"
                    })
        
        return results
    
    def get_character_summary(self, character_name: str) -> Optional[str]:
        """Get a concise summary of a character's life and work."""
        bio_data = self.get_biographical_data(character_name)
        if not bio_data:
            return None
        
        summary_parts = []
        
        # Basic info
        if bio_data.get("name"):
            summary_parts.append(f"Name: {bio_data['name']}")
        
        if bio_data.get("birth_date") and bio_data.get("death_date"):
            summary_parts.append(f"Lifespan: {bio_data['birth_date']} - {bio_data['death_date']}")
        
        if bio_data.get("profession"):
            summary_parts.append(f"Profession: {', '.join(bio_data['profession'])}")
        
        # Key achievements
        if bio_data.get("achievements"):
            summary_parts.append(f"Key Achievements: {bio_data['achievements'][0] if bio_data['achievements'] else 'None'}")
        
        # Core beliefs
        if bio_data.get("core_beliefs"):
            summary_parts.append(f"Core Belief: {bio_data['core_beliefs'][0]['belief'] if bio_data['core_beliefs'] else 'None'}")
        
        # Legacy
        if bio_data.get("legacy"):
            summary_parts.append(f"Legacy: {bio_data['legacy']}")
        
        return "\n".join(summary_parts)
    
    def is_historical_character(self, character_name: str) -> bool:
        """Check if a character has biographical data available."""
        bio_file = self.biographies_dir / f"{character_name.lower().replace(' ', '_')}.json"
        return bio_file.exists()
    
    def list_available_historical_characters(self) -> List[str]:
        """List all available historical characters."""
        characters = []
        for bio_file in self.biographies_dir.glob("*.json"):
            character_name = bio_file.stem.replace('_', ' ').title()
            characters.append(character_name)
        return characters
    
    def clear_cache(self):
        """Clear the biographical data cache."""
        self._cache.clear()
        logger.info("Biographical data cache cleared")


# Global instance for easy access
biographical_system = BiographicalDataSystem() 