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
from systems.historical_character_loader import historical_loader
import re

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
    
    def validate_character_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate character creation form data."""
        errors = []
        warnings = []
        
        # Required field validation
        required_fields = ["first_name", "last_name"]
        for field in required_fields:
            if not form_data.get(field) or not form_data[field].strip():
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Name validation
        if form_data.get("first_name"):
            if len(form_data["first_name"]) < 2:
                errors.append("First name must be at least 2 characters long")
            if len(form_data["first_name"]) > 50:
                errors.append("First name must be less than 50 characters")
            if not re.match(r'^[a-zA-Z\s\-\.]+$', form_data["first_name"]):
                warnings.append("First name contains unusual characters")
        
        if form_data.get("last_name"):
            if len(form_data["last_name"]) < 2:
                errors.append("Last name must be at least 2 characters long")
            if len(form_data["last_name"]) > 50:
                errors.append("Last name must be less than 50 characters")
            if not re.match(r'^[a-zA-Z\s\-\.]+$', form_data["last_name"]):
                warnings.append("Last name contains unusual characters")
        
        # Personality type validation
        valid_personality_types = [
            "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"
        ]
        if form_data.get("personality_type") and form_data["personality_type"] not in valid_personality_types:
            errors.append("Invalid personality type selected")
        
        # Archetype validation
        if form_data.get("archetype") == "CUSTOM":
            if not form_data.get("custom_archetype") or not form_data["custom_archetype"].strip():
                errors.append("Custom archetype is required when 'Write Custom Archetype' is selected")
            elif len(form_data["custom_archetype"]) > 100:
                errors.append("Custom archetype must be less than 100 characters")
        
        # File upload validation
        if form_data.get("uploaded_files"):
            total_size = sum(file.get("size", 0) for file in form_data["uploaded_files"])
            if total_size > 50 * 1024 * 1024:  # 50MB total limit
                errors.append("Total file size exceeds 50MB limit")
            
            for file in form_data["uploaded_files"]:
                if file.get("size", 0) > 10 * 1024 * 1024:  # 10MB per file
                    errors.append(f"File '{file.get('name', 'Unknown')}' exceeds 10MB limit")
                
                # Check file type
                file_type = file.get("type", "").lower()
                allowed_types = ["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
                if file_type and not any(allowed in file_type for allowed in allowed_types):
                    warnings.append(f"File '{file.get('name', 'Unknown')}' may not be supported")
        
        # Date validation for historical characters
        if form_data.get("birth_date"):
            try:
                datetime.strptime(form_data["birth_date"], "%Y-%m-%d")
            except ValueError:
                errors.append("Birth date must be in YYYY-MM-DD format")
        
        # Content length validation
        text_fields = ["background", "life_story", "achievements", "famous_quotes"]
        for field in text_fields:
            if form_data.get(field) and len(form_data[field]) > 2000:
                warnings.append(f"{field.replace('_', ' ').title()} is quite long - consider shortening")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def create_custom_character(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom character from form data."""
        
        # Validate form data first
        validation_result = self.validate_character_data(form_data)
        if not validation_result["valid"]:
            raise ValueError(f"Character validation failed: {'; '.join(validation_result['errors'])}")
        
        # Show warnings if any
        if validation_result["warnings"]:
            print(f"Warnings during character creation: {'; '.join(validation_result['warnings'])}")
        
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
            "learning_enabled": True,
            "validation_status": "validated"
        }
        
        # If this is a historical character (biography provided), inject expertise, style, and works
        is_historical = form_data.get("character_type") == "historical" or form_data.get("biography") or form_data.get("birth_date")
        if is_historical:
            # Try to load from historical loader if name matches
            name = f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip()
            loaded = historical_loader.load_historical_character(name)
            if loaded:
                character.update(loaded)
            # Otherwise, inject from form_data
            if not character.get("biography"):
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
            # Style profile
            if not character.get("style_profile"):
                style_profile = {
                    "argumentation_style": form_data.get("argumentation_style", "Analytical"),
                    "common_phrases": [p.strip() for p in form_data.get("common_phrases", "").split(",") if p.strip()],
                    "rhetorical_devices": [d.strip() for d in form_data.get("rhetorical_devices", "").split(",") if d.strip()]
                }
                character["style_profile"] = style_profile
            # Famous quotes
            if not character.get("famous_quotes") and form_data.get("famous_quotes"):
                character["famous_quotes"] = [q.strip() for q in form_data["famous_quotes"].split("\n") if q.strip()]
        
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
                literary_context["processing_result"] = processing_result
            
            # Add other literary context
            if form_data.get("source_author"):
                literary_context["source_author"] = form_data["source_author"]
            if form_data.get("literary_period"):
                literary_context["literary_period"] = form_data["literary_period"]
            if form_data.get("key_themes"):
                literary_context["key_themes"] = form_data["key_themes"]
            
            character["literary_context"] = literary_context
        
        return character
    
    def save_character(self, character: Dict[str, Any]) -> str:
        """Save character to file."""
        character_id = character["id"]
        character_file = self.output_dir / f"{character_id}.json"
        
        with open(character_file, 'w') as f:
            json.dump(character, f, indent=2)
        
        print(f"✅ Custom character saved: {character['name']} ({character_id})")
        return character_id
