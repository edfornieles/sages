#!/usr/bin/env python3
"""
Historical Character Loader
Loads biography, style, expertise, and works for historical characters.
Provides recall/search API for agent use.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class HistoricalCharacterLoader:
    def __init__(self, data_dir: str = "data/characters/generated_characters"):
        self.data_dir = Path(data_dir)

    def load_historical_character(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Load historical character data by name."""
        for file in self.data_dir.glob("historical_*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("name", "").lower() == character_name.lower():
                    return data
        return None

    def get_biography(self, character_data: Dict[str, Any]) -> str:
        bio = character_data.get("biography", {})
        lines = []
        if bio.get("birth_date"):
            lines.append(f"Born: {bio['birth_date']}")
        if bio.get("birth_location"):
            lines.append(f"Birthplace: {bio['birth_location']}")
        if bio.get("death_date"):
            lines.append(f"Died: {bio['death_date']}")
        if bio.get("profession"):
            lines.append(f"Profession: {', '.join(bio['profession'])}")
        if bio.get("achievements"):
            lines.append(f"Achievements: {', '.join(bio['achievements'])}")
        if bio.get("life_story"):
            lines.append(f"Life Story: {bio['life_story']}")
        return "\n".join(lines)

    def get_expertise(self, character_data: Dict[str, Any]) -> List[str]:
        bio = character_data.get("biography", {})
        expertise = []
        if "core_beliefs" in bio:
            for belief in bio["core_beliefs"]:
                expertise.append(belief.get("belief", ""))
        if "psychoanalytic_techniques" in bio:
            for tech in bio["psychoanalytic_techniques"]:
                expertise.append(tech.get("technique", ""))
        if "analytic_concepts" in bio:
            for concept in bio["analytic_concepts"]:
                expertise.append(concept.get("concept", ""))
        return expertise

    def get_style_profile(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        return character_data.get("style_profile", {})

    def get_famous_quotes(self, character_data: Dict[str, Any]) -> List[str]:
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
                    if isinstance(item, dict):
                        for val in item.values():
                            if isinstance(val, str) and topic in val.lower():
                                return val
        # Search style profile
        style = character_data.get("style_profile", {})
        for k, v in style.items():
            if isinstance(v, str) and topic in v.lower():
                return v
            if isinstance(v, list):
                for item in v:
                    if topic in item.lower():
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
                    if isinstance(item, dict):
                        for val in item.values():
                            if isinstance(val, str) and query in val.lower():
                                results.append(val)
        # Search style profile
        style = character_data.get("style_profile", {})
        for k, v in style.items():
            if isinstance(v, str) and query in v.lower():
                results.append(v)
            if isinstance(v, list):
                for item in v:
                    if query in item.lower():
                        results.append(item)
        # Search famous quotes
        for quote in self.get_famous_quotes(character_data):
            if query in quote.lower():
                results.append(quote)
        return results

# Singleton instance
historical_loader = HistoricalCharacterLoader() 