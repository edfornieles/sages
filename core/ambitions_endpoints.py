#!/usr/bin/env python3
"""
Ambitions endpoints for the Dynamic Character Playground
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import json
import sys
import os

# Add the systems directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'systems'))
from ambitions_system import AmbitionsSystem

# Add the core directory to the path for character generator
sys.path.append(os.path.dirname(__file__))
from character_generator import CharacterGenerator

# Initialize router
router = APIRouter(prefix="/characters", tags=["ambitions"])

# Initialize character generator
generator = CharacterGenerator()

class AmbitionsRequest(BaseModel):
    desires: str = ""
    ambitions: str = ""
    motivations: str = ""

@router.get("/{character_id}/ambitions")
async def get_character_ambitions(character_id: str):
    """Get character's desires, ambitions, and motivations."""
    try:
        character = generator.load_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get ambitions from the ambitions system
        ambitions_system = AmbitionsSystem(character_id)
        ambitions_summary = ambitions_system.get_ambitions_summary()
        
        # Extract desires, ambitions, and motivations from character data
        character_ambitions = character.get("ambitions", {})
        
        return {
            "character_id": character_id,
            "character_name": character.get("name", "Character"),
            "desires": character_ambitions.get("desires", ""),
            "ambitions": character_ambitions.get("ambitions", ""),
            "motivations": character_ambitions.get("motivations", ""),
            "ambitions_summary": ambitions_summary,
            "ambitions_system": {
                "enabled": True,
                "total_ambitions": len(ambitions_system.get_character_ambitions())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ambitions: {str(e)}")

@router.put("/{character_id}/ambitions")
async def update_character_ambitions(character_id: str, request: AmbitionsRequest):
    """Update character's desires, ambitions, and motivations."""
    try:
        character = generator.load_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Update character data with new ambitions
        if "ambitions" not in character:
            character["ambitions"] = {}
        
        character["ambitions"].update({
            "desires": request.desires,
            "ambitions": request.ambitions,
            "motivations": request.motivations,
            "last_updated": datetime.now().isoformat()
        })
        
        # Save updated character data
        character_file = Path(f"characters/{character_id}.json")
        with open(character_file, 'w', encoding='utf-8') as f:
            json.dump(character, f, indent=2, ensure_ascii=False)
        
        # Update ambitions system if needed
        ambitions_system = AmbitionsSystem(character_id)
        
        return {
            "character_id": character_id,
            "character_name": character.get("name", "Character"),
            "message": "Ambitions updated successfully",
            "updated_at": datetime.now().isoformat(),
            "ambitions": character["ambitions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ambitions: {str(e)}") 