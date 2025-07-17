#!/usr/bin/env python3
"""
Character Import/Export System
Allows saving and loading character configurations
"""

import json
import zipfile
import base64
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib

class CharacterIO:
    """Handles importing and exporting character configurations."""
    
    def __init__(self, export_dir: str = "data/character_exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_character(self, character_data: Dict[str, Any], 
                        include_memories: bool = False,
                        include_relationships: bool = False) -> str:
        """Export a character configuration to a file."""
        
        # Create export data
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "character": character_data.copy(),
            "metadata": {
                "character_id": character_data.get("id"),
                "character_name": character_data.get("name"),
                "character_type": character_data.get("character_type", "custom"),
                "export_options": {
                    "include_memories": include_memories,
                    "include_relationships": include_relationships
                }
            }
        }
        
        # Add memories if requested
        if include_memories and character_data.get("id"):
            memories = self._get_character_memories(character_data["id"])
            if memories:
                export_data["memories"] = memories
        
        # Add relationships if requested
        if include_relationships and character_data.get("id"):
            relationships = self._get_character_relationships(character_data["id"])
            if relationships:
                export_data["relationships"] = relationships
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        character_name = character_data.get("name", "character").replace(" ", "_").lower()
        filename = f"{character_name}_{timestamp}.json"
        filepath = self.export_dir / filename
        
        # Save export file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def export_character_package(self, character_data: Dict[str, Any],
                                include_memories: bool = True,
                                include_relationships: bool = True,
                                include_literary_files: bool = True) -> str:
        """Export a complete character package as a ZIP file."""
        
        # Create temporary directory for package
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        character_name = character_data.get("name", "character").replace(" ", "_").lower()
        package_name = f"{character_name}_package_{timestamp}"
        package_dir = self.export_dir / package_name
        package_dir.mkdir(exist_ok=True)
        
        try:
            # Export character data
            character_file = package_dir / "character.json"
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=2, ensure_ascii=False)
            
            # Export memories if requested
            if include_memories and character_data.get("id"):
                memories = self._get_character_memories(character_data["id"])
                if memories:
                    memories_file = package_dir / "memories.json"
                    with open(memories_file, 'w', encoding='utf-8') as f:
                        json.dump(memories, f, indent=2, ensure_ascii=False)
            
            # Export relationships if requested
            if include_relationships and character_data.get("id"):
                relationships = self._get_character_relationships(character_data["id"])
                if relationships:
                    relationships_file = package_dir / "relationships.json"
                    with open(relationships_file, 'w', encoding='utf-8') as f:
                        json.dump(relationships, f, indent=2, ensure_ascii=False)
            
            # Export literary files if requested
            if include_literary_files and character_data.get("literary_context"):
                literary_dir = package_dir / "literary_files"
                literary_dir.mkdir(exist_ok=True)
                self._export_literary_files(character_data["id"], literary_dir)
            
            # Create manifest
            manifest = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "character_name": character_data.get("name"),
                "character_id": character_data.get("id"),
                "files_included": [f.name for f in package_dir.iterdir() if f.is_file()],
                "directories_included": [f.name for f in package_dir.iterdir() if f.is_dir()]
            }
            
            manifest_file = package_dir / "manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Create ZIP file
            zip_filename = f"{package_name}.zip"
            zip_path = self.export_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in package_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(package_dir)
                        zipf.write(file_path, arcname)
            
            return str(zip_path)
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(package_dir, ignore_errors=True)
    
    def import_character(self, file_path: str) -> Dict[str, Any]:
        """Import a character configuration from a file."""
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Import file not found: {file_path}")
        
        if file_path.suffix.lower() == '.zip':
            return self._import_character_package(file_path)
        else:
            return self._import_character_file(file_path)
    
    def _import_character_file(self, file_path: Path) -> Dict[str, Any]:
        """Import from a single JSON file."""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Validate import data
        if "character" not in import_data:
            raise ValueError("Invalid character export file: missing character data")
        
        character_data = import_data["character"]
        
        # Import memories if present
        if "memories" in import_data and character_data.get("id"):
            self._import_character_memories(character_data["id"], import_data["memories"])
        
        # Import relationships if present
        if "relationships" in import_data and character_data.get("id"):
            self._import_character_relationships(character_data["id"], import_data["relationships"])
        
        return character_data
    
    def _import_character_package(self, zip_path: Path) -> Dict[str, Any]:
        """Import from a ZIP package."""
        
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_path)
            
            # Read manifest
            manifest_file = temp_path / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            
            # Read character data
            character_file = temp_path / "character.json"
            if not character_file.exists():
                raise ValueError("Invalid character package: missing character.json")
            
            with open(character_file, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Import memories if present
            memories_file = temp_path / "memories.json"
            if memories_file.exists() and character_data.get("id"):
                with open(memories_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                self._import_character_memories(character_data["id"], memories)
            
            # Import relationships if present
            relationships_file = temp_path / "relationships.json"
            if relationships_file.exists() and character_data.get("id"):
                with open(relationships_file, 'r', encoding='utf-8') as f:
                    relationships = json.load(f)
                self._import_character_relationships(character_data["id"], relationships)
            
            # Import literary files if present
            literary_dir = temp_path / "literary_files"
            if literary_dir.exists() and character_data.get("id"):
                self._import_literary_files(character_data["id"], literary_dir)
            
            return character_data
    
    def _get_character_memories(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get character memories from the memory system."""
        try:
            from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem
            
            # This would need to be implemented based on your memory system
            # For now, return None
            return None
        except ImportError:
            return None
    
    def _get_character_relationships(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get character relationships from the relationship system."""
        try:
            from systems.relationship_system import RelationshipSystem
            
            # This would need to be implemented based on your relationship system
            # For now, return None
            return None
        except ImportError:
            return None
    
    def _import_character_memories(self, character_id: str, memories_data: Dict[str, Any]):
        """Import character memories into the memory system."""
        # Implementation would depend on your memory system
        pass
    
    def _import_character_relationships(self, character_id: str, relationships_data: Dict[str, Any]):
        """Import character relationships into the relationship system."""
        # Implementation would depend on your relationship system
        pass
    
    def _export_literary_files(self, character_id: str, target_dir: Path):
        """Export literary files associated with a character."""
        literary_dir = Path("data/uploaded_texts/extracted")
        if literary_dir.exists():
            for file_path in literary_dir.glob(f"{character_id}_*"):
                if file_path.is_file():
                    shutil.copy2(file_path, target_dir / file_path.name)
    
    def _import_literary_files(self, character_id: str, source_dir: Path):
        """Import literary files for a character."""
        literary_dir = Path("data/uploaded_texts/extracted")
        literary_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in source_dir.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, literary_dir / file_path.name)
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """List all available character exports."""
        exports = []
        
        for file_path in self.export_dir.iterdir():
            if file_path.is_file():
                try:
                    if file_path.suffix.lower() == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            exports.append({
                                "filename": file_path.name,
                                "path": str(file_path),
                                "type": "json",
                                "character_name": data.get("character", {}).get("name", "Unknown"),
                                "exported_at": data.get("exported_at", "Unknown"),
                                "size": file_path.stat().st_size
                            })
                    elif file_path.suffix.lower() == '.zip':
                        exports.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "type": "package",
                            "character_name": file_path.stem.split('_package_')[0].replace('_', ' ').title(),
                            "exported_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "size": file_path.stat().st_size
                        })
                except Exception as e:
                    exports.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "type": "unknown",
                        "character_name": "Error reading file",
                        "exported_at": "Unknown",
                        "size": file_path.stat().st_size,
                        "error": str(e)
                    })
        
        return sorted(exports, key=lambda x: x["exported_at"], reverse=True)

# Global instance
character_io = CharacterIO() 