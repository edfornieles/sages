#!/usr/bin/env python3
"""
Literary Text Processor
Handles processing of uploaded literary works to enhance character knowledge
"""

import os
import json
import hashlib
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import mimetypes

# Optional imports for enhanced processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class LiteraryTextProcessor:
    """Processes uploaded literary texts to enhance character knowledge."""
    
    def __init__(self, upload_dir: str = "data/uploaded_texts"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "raw").mkdir(exist_ok=True)
        (self.upload_dir / "processed").mkdir(exist_ok=True)
        (self.upload_dir / "metadata").mkdir(exist_ok=True)
        (self.upload_dir / "extracted").mkdir(exist_ok=True)
    
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
            "status": "processing_complete"
        }
        
        # Process each file
        for file_info in files_metadata:
            file_result = self._process_single_file(character_id, file_info)
            processing_result["files_processed"].append(file_result)
        
        # Analyze themes if provided
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
        processing_result["extracted_knowledge"] = self._create_knowledge_base(
            processing_result["files_processed"], 
            literary_period, 
            source_author, 
            key_themes
        )
        
        # Save processing metadata
        metadata_path = self.upload_dir / "metadata" / f"{character_id}_literary_processing.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(processing_result, f, indent=2, ensure_ascii=False)
        
        return processing_result
    
    def _process_single_file(self, character_id: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single uploaded file."""
        file_result = {
            "filename": file_info["name"],
            "size": file_info["size"],
            "type": file_info["type"],
            "status": "processed",
            "processing_notes": [],
            "extracted_content": "",
            "word_count": 0,
            "key_phrases": [],
            "vocabulary_analysis": {}
        }
        
        # Determine file type and processing method
        file_type = file_info["type"].lower()
        
        if "text/plain" in file_type or file_info["name"].endswith('.txt'):
            content = self._extract_text_content(file_info)
            file_result["extracted_content"] = content
            file_result["processing_notes"].append("Text file processed successfully")
            
        elif "pdf" in file_type or file_info["name"].endswith('.pdf'):
            if PDF_AVAILABLE:
                content = self._extract_pdf_content(file_info)
                file_result["extracted_content"] = content
                file_result["processing_notes"].append("PDF file processed successfully")
            else:
                file_result["status"] = "error"
                file_result["processing_notes"].append("PDF processing not available - PyPDF2 not installed")
                
        elif "word" in file_type or "document" in file_type or file_info["name"].endswith('.docx'):
            if DOCX_AVAILABLE:
                content = self._extract_docx_content(file_info)
                file_result["extracted_content"] = content
                file_result["processing_notes"].append("Word document processed successfully")
            else:
                file_result["status"] = "error"
                file_result["processing_notes"].append("Word document processing not available - python-docx not installed")
        else:
            file_result["status"] = "unsupported"
            file_result["processing_notes"].append(f"Unsupported file type: {file_type}")
        
        # Analyze extracted content
        if file_result["extracted_content"]:
            analysis = self._analyze_content(file_result["extracted_content"])
            file_result["word_count"] = analysis["word_count"]
            file_result["key_phrases"] = analysis["key_phrases"]
            file_result["vocabulary_analysis"] = analysis["vocabulary"]
            
            # Save extracted content
            content_path = self.upload_dir / "extracted" / f"{character_id}_{file_info['name']}.txt"
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(file_result["extracted_content"])
        
        return file_result
    
    def _extract_text_content(self, file_info: Dict[str, Any]) -> str:
        """Extract content from text files."""
        # For now, return a placeholder - in a real system, you'd read the actual file
        return f"Content extracted from {file_info['name']} - {file_info['size']} bytes"
    
    def _extract_pdf_content(self, file_info: Dict[str, Any]) -> str:
        """Extract content from PDF files."""
        # Placeholder for PDF extraction
        return f"PDF content extracted from {file_info['name']} - {file_info['size']} bytes"
    
    def _extract_docx_content(self, file_info: Dict[str, Any]) -> str:
        """Extract content from Word documents."""
        # Placeholder for Word document extraction
        return f"Word document content extracted from {file_info['name']} - {file_info['size']} bytes"
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze extracted content for key information."""
        words = content.split()
        word_count = len(words)
        
        # Extract key phrases (simple implementation)
        sentences = re.split(r'[.!?]+', content)
        key_phrases = []
        for sentence in sentences[:10]:  # First 10 sentences
            if len(sentence.strip()) > 20:
                key_phrases.append(sentence.strip())
        
        # Basic vocabulary analysis
        vocabulary = {
            "unique_words": len(set(words)),
            "avg_word_length": sum(len(word) for word in words) / word_count if word_count > 0 else 0,
            "complex_words": len([w for w in words if len(w) > 8]),
            "common_words": self._find_common_words(words)
        }
        
        return {
            "word_count": word_count,
            "key_phrases": key_phrases[:5],  # Top 5 phrases
            "vocabulary": vocabulary
        }
    
    def _find_common_words(self, words: List[str]) -> List[str]:
        """Find common words in the text."""
        word_freq = {}
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word.lower())
            if len(clean_word) > 3:  # Skip short words
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Return top 10 most common words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _create_knowledge_base(self, processed_files: List[Dict[str, Any]], 
                              period: Optional[str], 
                              author: Optional[str], 
                              themes: Optional[str]) -> Dict[str, Any]:
        """Create a knowledge base from processed files."""
        knowledge_base = {
            "vocabulary_enrichment": self._suggest_vocabulary_enrichment(period, author),
            "conversational_patterns": self._suggest_conversational_patterns(period, author),
            "knowledge_domains": self._identify_knowledge_domains(themes, author),
            "reference_material": "Processed content from uploaded files",
            "total_content_words": sum(f.get("word_count", 0) for f in processed_files),
            "extracted_phrases": []
        }
        
        # Collect key phrases from all processed files
        for file_result in processed_files:
            if file_result.get("key_phrases"):
                knowledge_base["extracted_phrases"].extend(file_result["key_phrases"])
        
        return knowledge_base
    
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