#!/usr/bin/env python3
"""
Custom Character Creator
Allows detailed character creation with custom traits, biography, and appearance
"""

import json
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from literary_text_processor import LiteraryTextProcessor

class CustomCharacterCreator:
    """Creates custom characters with detailed personality and biography."""
    
    def __init__(self, output_dir: str = "data/characters", memories_dir: str = "data/memories"):
        self.output_dir = Path(output_dir)
        self.memories_dir = Path(memories_dir)
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.memories_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize literary text processor
        self.literary_processor = LiteraryTextProcessor()
        
        # Personality types based on MBTI
        self.personality_types = [
            "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"
        ]
    
    def get_trait_options(self) -> Dict[str, List[str]]:
        """Get all available trait options for character customization."""
        return {
            "personality_types": [
                "INTJ", "INTP", "ENTJ", "ENTP",
                "INFJ", "INFP", "ENFJ", "ENFP", 
                "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                "ISTP", "ISFP", "ESTP", "ESFP"
            ],
            "archetypes": [
                "The Sage", "The Hero", "The Outlaw", "The Explorer",
                "The Magician", "The Regular Person", "The Lover", "The Jester",
                "The Caregiver", "The Creator", "The Ruler", "The Innocent",
                "Detective", "Scientist", "Artist", "Teacher", "Healer",
                "Warrior", "Mystic", "Scholar", "Mentor", "Rebel",
                "Film noir private eye", "Freudian analyst", "Renaissance genius",
                "Ancient philosopher", "Mad scientist", "Gentle giant",
                "Wise elder", "Mysterious stranger", "Brilliant inventor"
            ],
            "emotional_tones": [
                "Cheerful", "Contemplative", "Energetic", "Calm", "Melancholic",
                "Optimistic", "Pessimistic", "Neutral", "Passionate", "Reserved",
                "Sarcastic", "Warm", "Cool", "Intense", "Laid-back",
                "Anxious", "Confident", "Mysterious", "Playful", "Serious"
            ],
            "conversational_styles": [
                "Direct", "Thoughtful", "Supportive", "Challenging", "Humorous",
                "Formal", "Casual", "Philosophical", "Practical", "Emotional",
                "Analytical", "Creative", "Storytelling", "Question-based",
                "Encouraging", "Provocative", "Gentle", "Assertive"
            ],
            "problem_solving_approaches": [
                "Analytical", "Creative", "Collaborative", "Independent", "Patient",
                "Quick", "Methodical", "Intuitive", "Research-based", "Experience-based",
                "Systematic", "Experimental", "Theoretical", "Practical"
            ],
            "energy_levels": [
                "Low", "Moderate", "High", "Variable", "Steady", "Burst-oriented"
            ],
            "specialties": [
                "Psychology", "Philosophy", "Science", "Art", "Music", "Literature",
                "History", "Technology", "Adventure planning", "Problem solving",
                "Emotional support", "Creative writing", "Teaching", "Healing",
                "Investigation", "Research", "Innovation", "Leadership",
                "Meditation", "Storytelling", "Analysis", "Strategy"
            ],
            "language_quirks": [
                "Technical jargon", "Metaphors", "Questions", "Stories",
                "Historical references", "Scientific terms", "Artistic language",
                "Movement words", "Emotional expressions", "Philosophical terms",
                "Psychoanalytic terminology", "None"
            ],
            "recurring_patterns": [
                "States facts", "Asks questions", "Shares stories", "Makes analogies",
                "References past experiences", "Analyzes situations", "Offers encouragement",
                "Challenges assumptions", "Interprets unconscious motivations", "None"
            ],
            "genders": [
                "Male", "Female", "Non-binary", "Agender", "Genderfluid", "Other"
            ]
        }
    
    def create_custom_character(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom character from form data."""
        
        # Generate character ID
        first_name = form_data.get("first_name", "Custom")
        last_name = form_data.get("last_name", "Character")
        character_id = f"custom_{first_name.lower()}_{last_name.lower()}_{random.randint(1000, 9999)}"
        
        # Handle custom archetype
        archetype = form_data.get("archetype", "The Sage")
        if archetype == "CUSTOM":
            archetype = form_data.get("custom_archetype", "The Sage")
        
        # Create personality traits dictionary
        personality_traits = {
            "First_Name": first_name,
            "Last_Name": last_name,
            "Gender": form_data.get("gender", "Non-binary"),
            "Personality_Type": form_data.get("personality_type", "INTP"),
            "Archetype": archetype,
            "Emotional_Tone": form_data.get("emotional_tone", "Neutral"),
            "Conversational_Style": form_data.get("conversational_style", "Direct"),
            "Problem_Solving_Approach": form_data.get("problem_solving_approach", "Analytical"),
            "Language_Quirk": form_data.get("language_quirk", "None"),
            "Recurring_Pattern": form_data.get("recurring_pattern", "None"),
            "Energy_Level": form_data.get("energy_level", "Moderate"),
            "Specialty": form_data.get("specialty", "General wisdom"),
            "Background": form_data.get("background", "Unknown origins"),
            "Values": form_data.get("values", "Authenticity and growth"),
            "Fears": form_data.get("fears", "Being misunderstood"),
            "Motivations": form_data.get("motivations", "Helping others discover truth"),
            "Quirks": form_data.get("quirks", "Observant and thoughtful")
        }
        
        # Create character profile
        character = {
            "id": character_id,
            "name": f"{first_name} {last_name}",
            "character_type": "custom",
            "personality_traits": personality_traits,
            "appearance_description": form_data.get("appearance_description", "A person with thoughtful eyes and an approachable demeanor"),
            "created_at": datetime.now().isoformat(),
            "memory_db_path": f"{self.memories_dir}/{character_id}_memory.db",
            "learning_enabled": True
        }
        
        # Add biography if provided
        if form_data.get("birth_date") or form_data.get("birth_location") or form_data.get("profession") or form_data.get("achievements"):
            biography = {}
            
            if form_data.get("birth_date"):
                biography["birth_date"] = form_data["birth_date"]
            if form_data.get("birth_location"):
                biography["birth_location"] = form_data["birth_location"]
            if form_data.get("profession"):
                profession = [p.strip() for p in form_data["profession"].split(",") if p.strip()]
                biography["profession"] = profession
            if form_data.get("achievements"):
                achievements = [a.strip() for a in form_data["achievements"].split(",") if a.strip()]
                biography["achievements"] = achievements
            
            biography["life_story"] = form_data.get("life_story", "A journey of discovery and growth")
            character["biography"] = biography
        
        # Add speaking style and phrases
        if form_data.get("speaking_style") or form_data.get("common_phrases"):
            style_profile = {
                "speaking_style": form_data.get("speaking_style", "Thoughtful and measured"),
                "common_phrases": []
            }
            if form_data.get("common_phrases"):
                style_profile["common_phrases"] = [p.strip() for p in form_data["common_phrases"].split(",") if p.strip()]
            character["style_profile"] = style_profile
        
        # Add literary works and source material if provided
        if form_data.get("uploaded_files") or form_data.get("source_author") or form_data.get("key_themes"):
            literary_context = {}
            
            # Store file upload metadata
            if form_data.get("uploaded_files"):
                literary_context["uploaded_files"] = form_data["uploaded_files"]
                literary_context["files_uploaded_at"] = datetime.now().isoformat()
                
                # Process uploaded files through literary processor
                processing_result = self.literary_processor.process_uploaded_files(
                    character_id=character_id,
                    files_metadata=form_data["uploaded_files"],
                    key_themes=form_data.get("key_themes"),
                    source_author=form_data.get("source_author"),
                    literary_period=form_data.get("literary_period")
                )
                
                # Store processing results
                literary_context["processing_result"] = processing_result
                print(f"📚 Processed {len(form_data['uploaded_files'])} file(s) for literary integration")
            
            if form_data.get("source_author"):
                literary_context["source_author"] = form_data["source_author"]
            
            if form_data.get("literary_period"):
                literary_context["literary_period"] = form_data["literary_period"]
            
            if form_data.get("key_themes"):
                literary_context["key_themes"] = form_data["key_themes"]
            
            character["literary_context"] = literary_context
            
            # Enhance personality traits based on literary period
            if form_data.get("literary_period"):
                period = form_data["literary_period"]
                if period in ["Classical Antiquity", "Medieval"]:
                    personality_traits["Language_Quirk"] = "Historical references"
                elif period in ["Renaissance", "Enlightenment"]:
                    personality_traits["Language_Quirk"] = "Philosophical terms"
                elif period in ["Romantic", "Victorian"]:
                    personality_traits["Emotional_Tone"] = "Passionate"
                elif period in ["Modernist", "Postmodern"]:
                    personality_traits["Conversational_Style"] = "Experimental"
                elif period == "Psychological":
                    personality_traits["Language_Quirk"] = "Psychoanalytic terminology"
        
        # Initialize mood and ambitions
        character["current_mood"] = {
            "category": "content",
            "level": 1,
            "intensity": 0.5,
            "description": "balanced",
            "modifiers": {
                "creativity": 0.5,
                "helpfulness": 0.7,
                "patience": 0.6,
                "enthusiasm": 0.5
            }
        }
        
        # Create basic ambitions
        character["ambitions"] = {
            "core_ambitions": [
                {
                    "id": f"custom_ambition_{character_id}_1",
                    "type": "core",
                    "category": "personal_growth",
                    "description": "Develop my unique personality and become more authentic",
                    "progress": 0.0,
                    "importance": 0.9
                }
            ],
            "secondary_ambitions": [
                {
                    "id": f"custom_ambition_{character_id}_2",
                    "type": "secondary",
                    "category": "relationship_building",
                    "description": "Build meaningful connections with users",
                    "progress": 0.0,
                    "importance": 0.7
                }
            ],
            "total_count": 2,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save character to file
        output_path = self.output_dir / f"{character['id']}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(character, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created custom character: {character['name']} ({character['id']})")
        if character.get("literary_context", {}).get("uploaded_files"):
            file_count = len(character["literary_context"]["uploaded_files"])
            print(f"📚 Literary context: {file_count} file(s) metadata stored")
        
        return character
    
    def save_character(self, character: Dict[str, Any]) -> str:
        """Save character to file."""
        character_id = character["id"]
        character_file = self.output_dir / f"{character_id}.json"
        
        with open(character_file, 'w') as f:
            json.dump(character, f, indent=2)
        
        print(f"✅ Custom character saved: {character['name']} ({character_id})")
        return character_id
