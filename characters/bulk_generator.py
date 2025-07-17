#!/usr/bin/env python3
"""
Bulk Character Generation System
Allows generating multiple characters at once with different configurations
"""

import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from character_generator import CharacterGenerator
from character_templates import character_templates
from character_preview import character_preview

class BulkCharacterGenerator:
    """Generates multiple characters with different configurations."""
    
    def __init__(self, output_dir: str = "data/characters"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.character_generator = CharacterGenerator(output_dir=str(self.output_dir))
    
    def generate_from_template_batch(self, template_name: str, 
                                   count: int = 5,
                                   variations: Dict[str, List[str]] = None) -> List[Dict[str, Any]]:
        """Generate multiple characters from a single template with variations."""
        
        template = character_templates.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        characters = []
        
        for i in range(count):
            # Apply template with variations
            custom_data = self._generate_variations(template, variations, i)
            character_data = character_templates.apply_template(template_name, custom_data)
            
            # Generate unique character ID and name
            character_id = f"bulk_{template_name}_{i+1}_{random.randint(1000, 9999)}"
            character_name = self._generate_unique_name(character_data, i)
            
            # Create full character
            character = self._create_character_from_template_data(character_data, character_id, character_name)
            characters.append(character)
        
        return characters
    
    def generate_diverse_batch(self, count: int = 10, 
                             archetype_distribution: Dict[str, int] = None) -> List[Dict[str, Any]]:
        """Generate a diverse batch of characters with different archetypes."""
        
        if archetype_distribution is None:
            # Default distribution
            archetype_distribution = {
                "The Sage": 2,
                "The Healer": 2,
                "The Creator": 2,
                "The Explorer": 1,
                "The Mentor": 1,
                "The Scholar": 1,
                "The Jester": 1
            }
        
        characters = []
        current_count = 0
        
        for archetype, target_count in archetype_distribution.items():
            for i in range(target_count):
                if current_count >= count:
                    break
                
                # Generate character with specific archetype
                character = self._generate_archetype_character(archetype, current_count)
                characters.append(character)
                current_count += 1
        
        # Fill remaining slots with random characters
        while current_count < count:
            character = self.character_generator.generate_character_profile()
            characters.append(character)
            current_count += 1
        
        return characters
    
    def generate_specialized_batch(self, specialty: str, 
                                 count: int = 5,
                                 personality_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate characters specialized in a particular domain."""
        
        if personality_types is None:
            personality_types = ["INTJ", "INTP", "INFJ", "INFP", "ENTJ", "ENTP", "ENFJ", "ENFP"]
        
        characters = []
        
        for i in range(count):
            # Generate character with specific specialty
            character = self._generate_specialized_character(specialty, personality_types[i % len(personality_types)], i)
            characters.append(character)
        
        return characters
    
    def generate_emotional_spectrum_batch(self, count: int = 8) -> List[Dict[str, Any]]:
        """Generate characters across the emotional spectrum."""
        
        emotional_tones = [
            "Cheerful", "Contemplative", "Energetic", "Calm", 
            "Melancholic", "Optimistic", "Pessimistic", "Passionate"
        ]
        
        characters = []
        
        for i in range(count):
            emotional_tone = emotional_tones[i % len(emotional_tones)]
            character = self._generate_emotional_character(emotional_tone, i)
            characters.append(character)
        
        return characters
    
    def generate_conversational_style_batch(self, count: int = 7) -> List[Dict[str, Any]]:
        """Generate characters with different conversational styles."""
        
        conversational_styles = [
            "Direct", "Thoughtful", "Supportive", "Challenging", 
            "Humorous", "Philosophical", "Analytical"
        ]
        
        characters = []
        
        for i in range(count):
            style = conversational_styles[i % len(conversational_styles)]
            character = self._generate_conversational_character(style, i)
            characters.append(character)
        
        return characters
    
    def save_bulk_characters(self, characters: List[Dict[str, Any]], 
                           batch_name: str = None) -> str:
        """Save a batch of characters to files."""
        
        if batch_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_name = f"bulk_batch_{timestamp}"
        
        batch_dir = self.output_dir / batch_name
        batch_dir.mkdir(exist_ok=True)
        
        # Save individual character files
        for character in characters:
            character_id = character["id"]
            character_file = batch_dir / f"{character_id}.json"
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character, f, indent=2, ensure_ascii=False)
        
        # Create batch manifest
        manifest = {
            "batch_name": batch_name,
            "created_at": datetime.now().isoformat(),
            "character_count": len(characters),
            "characters": [
                {
                    "id": char["id"],
                    "name": char["name"],
                    "archetype": char.get("personality_traits", {}).get("Archetype", "Unknown"),
                    "specialty": char.get("personality_traits", {}).get("Specialty", "Unknown"),
                    "emotional_tone": char.get("personality_traits", {}).get("Emotional_Tone", "Unknown")
                }
                for char in characters
            ]
        }
        
        manifest_file = batch_dir / "manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return str(batch_dir)
    
    def generate_bulk_preview(self, characters: List[Dict[str, Any]], 
                            previews_per_character: int = 2) -> Dict[str, Any]:
        """Generate previews for a batch of characters."""
        
        batch_preview = {
            "batch_created_at": datetime.now().isoformat(),
            "character_count": len(characters),
            "character_previews": []
        }
        
        for character in characters:
            character_preview_data = character_preview.generate_preview(
                character, num_scenarios=previews_per_character
            )
            batch_preview["character_previews"].append(character_preview_data)
        
        return batch_preview
    
    def _generate_variations(self, template: Dict[str, Any], 
                           variations: Dict[str, List[str]], 
                           index: int) -> Dict[str, Any]:
        """Generate variations for a template."""
        
        if not variations:
            return {}
        
        custom_data = {}
        
        for field, options in variations.items():
            if options:
                selected_option = options[index % len(options)]
                if field == "personality_traits":
                    custom_data.setdefault("personality_traits", {})
                    custom_data["personality_traits"][field] = selected_option
                else:
                    custom_data[field] = selected_option
        
        return custom_data
    
    def _generate_unique_name(self, character_data: Dict[str, Any], index: int) -> str:
        """Generate a unique name for a character."""
        
        # Use template name as base
        template_name = character_data.get("template_used", "Character")
        
        # Generate variations
        name_variations = [
            f"{template_name} {index + 1}",
            f"The {template_name}",
            f"{template_name} Prime",
            f"{template_name} Alpha",
            f"{template_name} Beta",
            f"{template_name} Gamma"
        ]
        
        return name_variations[index % len(name_variations)]
    
    def _create_character_from_template_data(self, template_data: Dict[str, Any], 
                                           character_id: str, 
                                           character_name: str) -> Dict[str, Any]:
        """Create a full character from template data."""
        
        character = {
            "id": character_id,
            "name": character_name,
            "character_type": "bulk_generated",
            "personality_traits": template_data["personality_traits"],
            "created_at": datetime.now().isoformat(),
            "template_used": template_data.get("template_used", "unknown"),
            "learning_enabled": True
        }
        
        # Add style profile if available
        if "common_phrases" in template_data:
            character["style_profile"] = {
                "speaking_style": template_data.get("speaking_style", "Thoughtful and measured"),
                "common_phrases": template_data["common_phrases"]
            }
        
        # Generate appearance description
        character["appearance_description"] = self._generate_appearance_from_traits(
            template_data["personality_traits"]
        )
        
        return character
    
    def _generate_archetype_character(self, archetype: str, index: int) -> Dict[str, Any]:
        """Generate a character with a specific archetype."""
        
        character = self.character_generator.generate_character_profile()
        
        # Override archetype
        character["personality_traits"]["Archetype"] = archetype
        
        # Adjust other traits based on archetype
        self._adjust_traits_for_archetype(character["personality_traits"], archetype)
        
        # Update character ID and name
        character["id"] = f"archetype_{archetype.lower().replace(' ', '_')}_{index+1}_{random.randint(1000, 9999)}"
        character["name"] = f"{archetype} {index + 1}"
        
        return character
    
    def _generate_specialized_character(self, specialty: str, 
                                      personality_type: str, 
                                      index: int) -> Dict[str, Any]:
        """Generate a character specialized in a particular domain."""
        
        character = self.character_generator.generate_character_profile()
        
        # Set specialty and personality type
        character["personality_traits"]["Specialty"] = specialty
        character["personality_traits"]["Personality_Type"] = personality_type
        
        # Adjust traits for specialty
        self._adjust_traits_for_specialty(character["personality_traits"], specialty)
        
        # Update character ID and name
        character["id"] = f"specialist_{specialty.lower().replace(' ', '_')}_{index+1}_{random.randint(1000, 9999)}"
        character["name"] = f"{specialty} Specialist {index + 1}"
        
        return character
    
    def _generate_emotional_character(self, emotional_tone: str, index: int) -> Dict[str, Any]:
        """Generate a character with a specific emotional tone."""
        
        character = self.character_generator.generate_character_profile()
        
        # Set emotional tone
        character["personality_traits"]["Emotional_Tone"] = emotional_tone
        
        # Adjust other traits based on emotional tone
        self._adjust_traits_for_emotion(character["personality_traits"], emotional_tone)
        
        # Update character ID and name
        character["id"] = f"emotional_{emotional_tone.lower().replace(' ', '_')}_{index+1}_{random.randint(1000, 9999)}"
        character["name"] = f"The {emotional_tone} One"
        
        return character
    
    def _generate_conversational_character(self, style: str, index: int) -> Dict[str, Any]:
        """Generate a character with a specific conversational style."""
        
        character = self.character_generator.generate_character_profile()
        
        # Set conversational style
        character["personality_traits"]["Conversational_Style"] = style
        
        # Adjust other traits based on conversational style
        self._adjust_traits_for_conversation(character["personality_traits"], style)
        
        # Update character ID and name
        character["id"] = f"conversational_{style.lower().replace(' ', '_')}_{index+1}_{random.randint(1000, 9999)}"
        character["name"] = f"The {style} Speaker"
        
        return character
    
    def _adjust_traits_for_archetype(self, traits: Dict[str, Any], archetype: str):
        """Adjust personality traits based on archetype."""
        
        archetype_adjustments = {
            "The Sage": {
                "Conversational_Style": "Philosophical",
                "Language_Quirk": "Philosophical terms",
                "Energy_Level": "Moderate"
            },
            "The Healer": {
                "Conversational_Style": "Supportive",
                "Language_Quirk": "Emotional expressions",
                "Energy_Level": "Steady"
            },
            "The Creator": {
                "Conversational_Style": "Creative",
                "Language_Quirk": "Artistic language",
                "Energy_Level": "Variable"
            },
            "The Explorer": {
                "Conversational_Style": "Question-based",
                "Language_Quirk": "Movement words",
                "Energy_Level": "High"
            }
        }
        
        if archetype in archetype_adjustments:
            traits.update(archetype_adjustments[archetype])
    
    def _adjust_traits_for_specialty(self, traits: Dict[str, Any], specialty: str):
        """Adjust personality traits based on specialty."""
        
        specialty_adjustments = {
            "Psychology": {
                "Language_Quirk": "Psychological terminology",
                "Problem_Solving_Approach": "Collaborative"
            },
            "Science": {
                "Language_Quirk": "Scientific terms",
                "Problem_Solving_Approach": "Research-based"
            },
            "Philosophy": {
                "Language_Quirk": "Philosophical terms",
                "Problem_Solving_Approach": "Analytical"
            },
            "Art": {
                "Language_Quirk": "Artistic language",
                "Problem_Solving_Approach": "Creative"
            }
        }
        
        if specialty in specialty_adjustments:
            traits.update(specialty_adjustments[specialty])
    
    def _adjust_traits_for_emotion(self, traits: Dict[str, Any], emotion: str):
        """Adjust personality traits based on emotional tone."""
        
        emotion_adjustments = {
            "Cheerful": {
                "Energy_Level": "High",
                "Conversational_Style": "Humorous"
            },
            "Contemplative": {
                "Energy_Level": "Low",
                "Conversational_Style": "Thoughtful"
            },
            "Passionate": {
                "Energy_Level": "High",
                "Conversational_Style": "Emotional"
            },
            "Calm": {
                "Energy_Level": "Steady",
                "Conversational_Style": "Gentle"
            }
        }
        
        if emotion in emotion_adjustments:
            traits.update(emotion_adjustments[emotion])
    
    def _adjust_traits_for_conversation(self, traits: Dict[str, Any], style: str):
        """Adjust personality traits based on conversational style."""
        
        conversation_adjustments = {
            "Direct": {
                "Energy_Level": "Moderate",
                "Language_Quirk": "None"
            },
            "Thoughtful": {
                "Energy_Level": "Low",
                "Language_Quirk": "Questions"
            },
            "Humorous": {
                "Energy_Level": "High",
                "Language_Quirk": "Puns and wordplay"
            },
            "Analytical": {
                "Energy_Level": "Moderate",
                "Language_Quirk": "Technical jargon"
            }
        }
        
        if style in conversation_adjustments:
            traits.update(conversation_adjustments[style])
    
    def _generate_appearance_from_traits(self, traits: Dict[str, Any]) -> str:
        """Generate appearance description from personality traits."""
        
        archetype = traits.get("Archetype", "The Sage")
        emotional_tone = traits.get("Emotional_Tone", "Neutral")
        energy_level = traits.get("Energy_Level", "Moderate")
        
        appearance_templates = {
            "The Sage": "A person with wise eyes and a thoughtful expression",
            "The Healer": "Someone with a warm, approachable presence and gentle demeanor",
            "The Creator": "A person with expressive features and an imaginative spark in their eyes",
            "The Explorer": "Someone with an alert, curious expression and an energetic presence"
        }
        
        base_appearance = appearance_templates.get(archetype, "A person with a distinctive presence")
        
        # Add emotional tone modifiers
        emotion_modifiers = {
            "Cheerful": "bright smile and animated gestures",
            "Contemplative": "thoughtful gaze and measured movements",
            "Passionate": "intense expression and expressive gestures",
            "Calm": "serene expression and graceful movements"
        }
        
        if emotional_tone in emotion_modifiers:
            base_appearance += f", with {emotion_modifiers[emotional_tone]}"
        
        return base_appearance

# Global instance
bulk_character_generator = BulkCharacterGenerator() 