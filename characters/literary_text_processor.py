#!/usr/bin/env python3
"""
Literary Text Processor
Handles processing of uploaded literary works to enhance character knowledge
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import re

class LiteraryTextProcessor:
    """Processes uploaded literary texts to enhance character knowledge."""
    
    def __init__(self, upload_dir: str = "data/uploaded_texts"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "raw").mkdir(exist_ok=True)
        (self.upload_dir / "processed").mkdir(exist_ok=True)
        (self.upload_dir / "metadata").mkdir(exist_ok=True)
    
    def process_uploaded_files(self, character_id: str, files_metadata: List[Dict[str, Any]], 
                              key_themes: Optional[str] = None, 
                              source_author: Optional[str] = None,
                              literary_period: Optional[str] = None) -> Dict[str, Any]:
        """Process uploaded files and extract literary knowledge."""
        
        processing_result = {
            "character_id": character_id,
            "processed_at": datetime.now().isoformat(),
            "files_processed": [],
            "extracted_knowledge": {},
            "style_analysis": {},
            "themes": {},
            "status": "ready_for_processing"
        }
        
        # For now, we'll create a placeholder processing result
        # In a full implementation, you'd process actual file content
        
        for file_info in files_metadata:
            file_result = {
                "filename": file_info["name"],
                "size": file_info["size"],
                "type": file_info["type"],
                "status": "metadata_stored",
                "processing_notes": []
            }
            
            # Analyze file type and suggest processing approach
            if file_info["type"] == "text/plain":
                file_result["processing_notes"].append("Text file - ready for direct analysis")
            elif "pdf" in file_info["type"]:
                file_result["processing_notes"].append("PDF file - requires text extraction")
            elif "word" in file_info["type"] or "document" in file_info["type"]:
                file_result["processing_notes"].append("Document file - requires format conversion")
            else:
                file_result["processing_notes"].append("Unknown format - may need manual processing")
            
            processing_result["files_processed"].append(file_result)
        
        # Add thematic analysis if provided
        if key_themes:
            processing_result["themes"] = self._analyze_themes(key_themes)
        
        # Add author style context
        if source_author:
            processing_result["style_analysis"]["source_author"] = source_author
            processing_result["style_analysis"]["author_context"] = self._get_author_context(source_author)
        
        # Add literary period context
        if literary_period:
            processing_result["style_analysis"]["literary_period"] = literary_period
            processing_result["style_analysis"]["period_characteristics"] = self._get_period_characteristics(literary_period)
        
        # Create knowledge base structure
        processing_result["extracted_knowledge"] = {
            "vocabulary_enrichment": self._suggest_vocabulary_enrichment(literary_period, source_author),
            "conversational_patterns": self._suggest_conversational_patterns(literary_period, source_author),
            "knowledge_domains": self._identify_knowledge_domains(key_themes, source_author),
            "reference_material": "File content will be processed to create character-specific knowledge base"
        }
        
        # Save processing metadata
        metadata_path = self.upload_dir / "metadata" / f"{character_id}_literary_processing.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(processing_result, f, indent=2, ensure_ascii=False)
        
        return processing_result
    
    def _analyze_themes(self, themes_text: str) -> Dict[str, Any]:
        """Analyze key themes from user input."""
        themes = [theme.strip() for theme in themes_text.split(',') if theme.strip()]
        
        return {
            "main_themes": themes,
            "theme_count": len(themes),
            "suggested_applications": [
                "Reference these themes in character responses",
                "Use thematic vocabulary in conversations",
                "Connect user questions to these core concepts"
            ]
        }
    
    def _get_author_context(self, author: str) -> Dict[str, Any]:
        """Get contextual information about an author."""
        # Basic author context - in a full system, this would be more comprehensive
        author_contexts = {
            "shakespeare": {
                "period": "Elizabethan/Jacobean",
                "style": "Iambic pentameter, metaphors, wordplay",
                "themes": ["love", "power", "fate", "human nature"],
                "language": "Early Modern English"
            },
            "hemingway": {
                "period": "Modern",
                "style": "Iceberg theory, understated prose, dialogue-heavy",
                "themes": ["war", "love", "death", "masculinity"],
                "language": "Simple, direct prose"
            },
            "freud": {
                "period": "Early 20th century",
                "style": "Analytical, case study format, psychological terminology",
                "themes": ["unconscious", "sexuality", "dreams", "repression"],
                "language": "Scientific German translated to formal English"
            }
        }
        
        author_key = author.lower().replace(" ", "")
        return author_contexts.get(author_key, {
            "period": "Unknown",
            "style": "To be analyzed from uploaded texts",
            "themes": [],
            "language": "To be determined"
        })
    
    def _get_period_characteristics(self, period: str) -> Dict[str, Any]:
        """Get characteristics of a literary period."""
        period_chars = {
            "Classical Antiquity": {
                "language_style": "Formal, rhetorical, philosophical",
                "common_themes": ["virtue", "honor", "wisdom", "fate"],
                "typical_forms": "Dialogue, epic, rhetoric"
            },
            "Renaissance": {
                "language_style": "Ornate, metaphorical, humanistic",
                "common_themes": ["rebirth", "humanism", "art", "discovery"],
                "typical_forms": "Sonnets, essays, scientific treatises"
            },
            "Enlightenment": {
                "language_style": "Rational, clear, argumentative",
                "common_themes": ["reason", "progress", "liberty", "science"],
                "typical_forms": "Essays, treatises, encyclopedias"
            },
            "Romantic": {
                "language_style": "Emotional, imaginative, nature-focused",
                "common_themes": ["emotion", "nature", "individualism", "sublime"],
                "typical_forms": "Poetry, novels, personal essays"
            },
            "Modernist": {
                "language_style": "Experimental, fragmented, stream-of-consciousness",
                "common_themes": ["alienation", "urban life", "psychology", "technology"],
                "typical_forms": "Free verse, experimental prose"
            },
            "Psychological": {
                "language_style": "Analytical, case-study format, technical terminology",
                "common_themes": ["unconscious", "behavior", "mental processes", "therapy"],
                "typical_forms": "Case studies, theoretical papers, analysis"
            }
        }
        
        return period_chars.get(period, {
            "language_style": "To be analyzed",
            "common_themes": [],
            "typical_forms": "Various"
        })
    
    def _suggest_vocabulary_enrichment(self, period: Optional[str], author: Optional[str]) -> List[str]:
        """Suggest vocabulary enrichment based on period and author."""
        suggestions = [
            "Analyze uploaded texts for characteristic vocabulary",
            "Extract key terms and phrases from source material",
            "Identify author-specific language patterns"
        ]
        
        if period:
            suggestions.append(f"Incorporate {period} period vocabulary and expressions")
        
        if author:
            suggestions.append(f"Study {author}'s characteristic word choices and sentence structures")
        
        return suggestions
    
    def _suggest_conversational_patterns(self, period: Optional[str], author: Optional[str]) -> List[str]:
        """Suggest conversational patterns based on literary context."""
        patterns = [
            "Reference themes from uploaded works naturally in conversation",
            "Use source material to provide authentic examples and quotes"
        ]
        
        if period == "Classical Antiquity":
            patterns.extend([
                "Use Socratic questioning methods",
                "Reference classical examples and parables"
            ])
        elif period == "Renaissance":
            patterns.extend([
                "Make connections between art, science, and philosophy",
                "Use metaphors from nature and human achievement"
            ])
        elif period == "Psychological":
            patterns.extend([
                "Analyze underlying motivations in conversations",
                "Use psychological frameworks and terminology appropriately"
            ])
        
        return patterns
    
    def _identify_knowledge_domains(self, themes: Optional[str], author: Optional[str]) -> List[str]:
        """Identify knowledge domains from themes and author."""
        domains = ["General knowledge from uploaded texts"]
        
        if themes:
            # Extract potential domains from themes
            theme_words = themes.lower().split()
            if any(word in theme_words for word in ["psychology", "mind", "behavior"]):
                domains.append("Psychology and mental processes")
            if any(word in theme_words for word in ["philosophy", "wisdom", "ethics"]):
                domains.append("Philosophy and ethics")
            if any(word in theme_words for word in ["art", "beauty", "creative"]):
                domains.append("Art and creativity")
            if any(word in theme_words for word in ["science", "nature", "discovery"]):
                domains.append("Science and natural philosophy")
        
        if author:
            author_lower = author.lower()
            if "freud" in author_lower:
                domains.append("Psychoanalytic theory and practice")
            elif "shakespeare" in author_lower:
                domains.append("Drama, human nature, and poetic expression")
            elif any(name in author_lower for name in ["plato", "aristotle", "socrates"]):
                domains.append("Ancient philosophy and dialectical reasoning")
        
        return domains
    
    def get_processing_status(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get the processing status for a character's literary materials."""
        metadata_path = self.upload_dir / "metadata" / f"{character_id}_literary_processing.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def integrate_with_character_prompt(self, character_data: Dict[str, Any]) -> str:
        """Generate additional prompt instructions based on literary context."""
        if "literary_context" not in character_data:
            return ""
        
        literary_context = character_data["literary_context"]
        prompt_additions = []
        
        # Add source material context
        if literary_context.get("source_author"):
            author = literary_context["source_author"]
            prompt_additions.append(f"You have deep knowledge of {author}'s works and can reference them naturally in conversation.")
        
        # Add period context
        if literary_context.get("literary_period"):
            period = literary_context["literary_period"]
            prompt_additions.append(f"Your knowledge and speaking style are influenced by the {period} period.")
        
        # Add thematic context
        if literary_context.get("key_themes"):
            themes = literary_context["key_themes"]
            prompt_additions.append(f"You often explore these themes in conversation: {themes}")
        
        # Add file processing context
        if literary_context.get("uploaded_files"):
            file_count = len(literary_context["uploaded_files"])
            prompt_additions.append(f"You have access to knowledge from {file_count} uploaded literary work(s) that inform your responses.")
        
        if prompt_additions:
            return "\n\nLiterary Context:\n" + "\n".join(f"- {addition}" for addition in prompt_additions)
        
        return "" 