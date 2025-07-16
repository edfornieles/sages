"""
Enhanced Emotional Context Tracking System
Analyzes emotional valence, intensity, and relationship impact in real-time
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class EmotionalContext:
    """Emotional context data structure"""
    valence: str  # positive, negative, neutral
    intensity: float  # 0.0 to 1.0
    primary_emotion: str
    secondary_emotions: List[str]
    relationship_impact: float  # -1.0 to 1.0
    emotional_triggers: List[str]
    context_notes: str
    timestamp: str

class EmotionalContextTracker:
    """Tracks and analyzes emotional context in conversations"""
    
    def __init__(self):
        self.emotional_lexicon = self._load_emotional_lexicon()
        self.intensity_indicators = self._load_intensity_indicators()
        self.relationship_indicators = self._load_relationship_indicators()
    
    def _load_emotional_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """Load emotional lexicon with valence and intensity scores"""
        return {
            # Positive emotions
            "happy": {"valence": "positive", "intensity": 0.7, "category": "joy"},
            "excited": {"valence": "positive", "intensity": 0.8, "category": "joy"},
            "thrilled": {"valence": "positive", "intensity": 0.9, "category": "joy"},
            "content": {"valence": "positive", "intensity": 0.5, "category": "satisfaction"},
            "grateful": {"valence": "positive", "intensity": 0.6, "category": "appreciation"},
            "hopeful": {"valence": "positive", "intensity": 0.6, "category": "optimism"},
            "proud": {"valence": "positive", "intensity": 0.7, "category": "achievement"},
            "loved": {"valence": "positive", "intensity": 0.8, "category": "affection"},
            "inspired": {"valence": "positive", "intensity": 0.7, "category": "motivation"},
            
            # Negative emotions
            "sad": {"valence": "negative", "intensity": 0.6, "category": "sorrow"},
            "angry": {"valence": "negative", "intensity": 0.8, "category": "anger"},
            "frustrated": {"valence": "negative", "intensity": 0.7, "category": "irritation"},
            "worried": {"valence": "negative", "intensity": 0.6, "category": "anxiety"},
            "scared": {"valence": "negative", "intensity": 0.8, "category": "fear"},
            "disappointed": {"valence": "negative", "intensity": 0.6, "category": "disappointment"},
            "lonely": {"valence": "negative", "intensity": 0.7, "category": "isolation"},
            "stressed": {"valence": "negative", "intensity": 0.7, "category": "pressure"},
            "confused": {"valence": "negative", "intensity": 0.5, "category": "uncertainty"},
            
            # Neutral emotions
            "curious": {"valence": "neutral", "intensity": 0.4, "category": "interest"},
            "thoughtful": {"valence": "neutral", "intensity": 0.3, "category": "reflection"},
            "calm": {"valence": "neutral", "intensity": 0.2, "category": "serenity"},
            "focused": {"valence": "neutral", "intensity": 0.4, "category": "concentration"}
        }
    
    def _load_intensity_indicators(self) -> Dict[str, float]:
        """Load intensity indicators"""
        return {
            "very": 1.5, "really": 1.4, "extremely": 1.6, "incredibly": 1.5,
            "so": 1.3, "quite": 1.2, "pretty": 1.1, "kinda": 0.8, "sorta": 0.8,
            "slightly": 0.7, "barely": 0.6, "hardly": 0.5
        }
    
    def _load_relationship_indicators(self) -> Dict[str, float]:
        """Load relationship impact indicators"""
        return {
            # Positive relationship indicators
            "love": 0.8, "care": 0.7, "trust": 0.6, "appreciate": 0.6,
            "miss": 0.5, "support": 0.6, "understand": 0.5, "respect": 0.5,
            
            # Negative relationship indicators
            "hate": -0.8, "dislike": -0.6, "distrust": -0.7, "ignore": -0.5,
            "blame": -0.6, "criticize": -0.5, "judge": -0.4, "reject": -0.7
        }
    
    def analyze_emotional_context(self, text: str, speaker: str = "user") -> EmotionalContext:
        """Analyze emotional context of text"""
        try:
            # Convert to lowercase for analysis
            text_lower = text.lower()
            
            # Detect emotions and calculate valence
            detected_emotions = self._detect_emotions(text_lower)
            valence, intensity = self._calculate_valence_intensity(detected_emotions, text_lower)
            
            # Determine primary and secondary emotions
            primary_emotion = self._get_primary_emotion(detected_emotions)
            secondary_emotions = self._get_secondary_emotions(detected_emotions)
            
            # Calculate relationship impact
            relationship_impact = self._calculate_relationship_impact(text_lower)
            
            # Identify emotional triggers
            emotional_triggers = self._identify_emotional_triggers(text_lower)
            
            # Generate context notes
            context_notes = self._generate_context_notes(
                valence, intensity, primary_emotion, relationship_impact, speaker
            )
            
            return EmotionalContext(
                valence=valence,
                intensity=intensity,
                primary_emotion=primary_emotion,
                secondary_emotions=secondary_emotions,
                relationship_impact=relationship_impact,
                emotional_triggers=emotional_triggers,
                context_notes=context_notes,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing emotional context: {e}")
            return self._create_default_context()
    
    def _detect_emotions(self, text: str) -> List[Dict[str, Any]]:
        """Detect emotions in text"""
        detected_emotions = []
        
        for emotion, data in self.emotional_lexicon.items():
            if emotion in text:
                # Check for intensity modifiers
                intensity_modifier = self._find_intensity_modifier(text, emotion)
                adjusted_intensity = data["intensity"] * intensity_modifier
                
                detected_emotions.append({
                    "emotion": emotion,
                    "valence": data["valence"],
                    "intensity": adjusted_intensity,
                    "category": data["category"]
                })
        
        return detected_emotions
    
    def _find_intensity_modifier(self, text: str, emotion: str) -> float:
        """Find intensity modifier for emotion"""
        # Look for intensity words before the emotion
        words = text.split()
        try:
            emotion_index = words.index(emotion)
            if emotion_index > 0:
                modifier = words[emotion_index - 1]
                return self.intensity_indicators.get(modifier, 1.0)
        except ValueError:
            pass
        return 1.0
    
    def _calculate_valence_intensity(self, emotions: List[Dict[str, Any]], text: str) -> Tuple[str, float]:
        """Calculate overall valence and intensity"""
        if not emotions:
            return "neutral", 0.3
        
        # Calculate weighted average
        total_intensity = 0
        valence_scores = {"positive": 0, "negative": 0, "neutral": 0}
        
        for emotion in emotions:
            intensity = emotion["intensity"]
            valence = emotion["valence"]
            total_intensity += intensity
            valence_scores[valence] += intensity
        
        # Determine dominant valence
        dominant_valence = max(valence_scores, key=valence_scores.get)
        
        # Calculate average intensity
        avg_intensity = total_intensity / len(emotions)
        
        # Check for exclamation marks and caps for intensity boost
        if "!" in text or text.isupper():
            avg_intensity = min(1.0, avg_intensity * 1.2)
        
        return dominant_valence, avg_intensity
    
    def _get_primary_emotion(self, emotions: List[Dict[str, Any]]) -> str:
        """Get primary emotion (highest intensity)"""
        if not emotions:
            return "neutral"
        
        primary = max(emotions, key=lambda x: x["intensity"])
        return primary["emotion"]
    
    def _get_secondary_emotions(self, emotions: List[Dict[str, Any]]) -> List[str]:
        """Get secondary emotions"""
        if len(emotions) <= 1:
            return []
        
        # Sort by intensity and take second highest
        sorted_emotions = sorted(emotions, key=lambda x: x["intensity"], reverse=True)
        return [emotion["emotion"] for emotion in sorted_emotions[1:3]]  # Top 2-3 secondary
    
    def _calculate_relationship_impact(self, text: str) -> float:
        """Calculate relationship impact score"""
        impact_score = 0.0
        impact_count = 0
        
        for indicator, score in self.relationship_indicators.items():
            if indicator in text:
                impact_score += score
                impact_count += 1
        
        if impact_count > 0:
            return impact_score / impact_count
        return 0.0
    
    def _identify_emotional_triggers(self, text: str) -> List[str]:
        """Identify potential emotional triggers"""
        triggers = []
        
        # Personal topics
        personal_patterns = [
            r"my (mom|dad|parents|family|kids|children)",
            r"my (job|work|career|boss)",
            r"my (health|illness|sickness)",
            r"my (relationship|partner|spouse|boyfriend|girlfriend)",
            r"my (money|finances|bills|debt)"
        ]
        
        for pattern in personal_patterns:
            if re.search(pattern, text):
                triggers.append("personal_topic")
        
        # Future concerns
        if any(word in text for word in ["future", "tomorrow", "next", "plan", "worry"]):
            triggers.append("future_concern")
        
        # Past events
        if any(word in text for word in ["remember", "yesterday", "last", "used to", "miss"]):
            triggers.append("past_event")
        
        return triggers
    
    def _generate_context_notes(self, valence: str, intensity: float, 
                               primary_emotion: str, relationship_impact: float, 
                               speaker: str) -> str:
        """Generate context notes for the emotional analysis"""
        notes = []
        
        # Valence description
        if valence == "positive":
            notes.append(f"{speaker} expressing positive emotions")
        elif valence == "negative":
            notes.append(f"{speaker} expressing negative emotions")
        else:
            notes.append(f"{speaker} in neutral emotional state")
        
        # Intensity description
        if intensity > 0.7:
            notes.append("high emotional intensity")
        elif intensity > 0.4:
            notes.append("moderate emotional intensity")
        else:
            notes.append("low emotional intensity")
        
        # Relationship impact
        if abs(relationship_impact) > 0.3:
            if relationship_impact > 0:
                notes.append("positive relationship indicators present")
            else:
                notes.append("negative relationship indicators present")
        
        return "; ".join(notes)
    
    def _create_default_context(self) -> EmotionalContext:
        """Create default emotional context"""
        return EmotionalContext(
            valence="neutral",
            intensity=0.3,
            primary_emotion="neutral",
            secondary_emotions=[],
            relationship_impact=0.0,
            emotional_triggers=[],
            context_notes="default emotional context",
            timestamp=datetime.now().isoformat()
        )
    
    def get_emotional_summary(self, contexts: List[EmotionalContext]) -> Dict[str, Any]:
        """Generate emotional summary from multiple contexts"""
        if not contexts:
            return {"summary": "No emotional data available"}
        
        # Calculate averages
        avg_intensity = sum(c.intensity for c in contexts) / len(contexts)
        avg_relationship_impact = sum(c.relationship_impact for c in contexts) / len(contexts)
        
        # Count valences
        valence_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for context in contexts:
            valence_counts[context.valence] += 1
        
        # Most common emotions
        emotion_counts = {}
        for context in contexts:
            emotion_counts[context.primary_emotion] = emotion_counts.get(context.primary_emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
        
        return {
            "total_interactions": len(contexts),
            "average_intensity": avg_intensity,
            "average_relationship_impact": avg_relationship_impact,
            "valence_distribution": valence_counts,
            "dominant_emotion": dominant_emotion,
            "emotional_trajectory": "improving" if avg_relationship_impact > 0 else "declining" if avg_relationship_impact < 0 else "stable"
        } 