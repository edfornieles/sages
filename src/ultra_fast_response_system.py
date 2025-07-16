#!/usr/bin/env python3
"""
Ultra Fast Response System - PHASE 2 of 90% Target Achievement

This system implements aggressive caching and response optimization to achieve:
- 90% of responses <3 seconds
- Average response time <2.5 seconds
- 95% cache hit rate for common interactions
"""

import time
import hashlib
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

# Import enhanced relationship system
try:
    from enhanced_relationship_system import enhance_response_with_relationship
    ENHANCED_RELATIONSHIPS_AVAILABLE = True
except ImportError:
    ENHANCED_RELATIONSHIPS_AVAILABLE = False

class UltraFastResponseCache:
    """Ultra-fast response caching system for immediate responses."""
    
    def __init__(self):
        self.cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "total_requests": 0}
        self.cache_ttl = 300  # 5 minutes
        
        # Pre-computed detective responses for instant delivery
        self.detective_responses = {
            "hello": [
                "Good to see you again. What case brings you to my office today?",
                "Welcome back to my office. Got a mystery that needs solving?",
                "Another day, another case. What's the situation this time?"
            ],
            "hi": [
                "Evening. What's the case you need me to investigate?",
                "Back again? Must be something interesting brewing.",
                "Detective Chen here. What evidence do you have for me?"
            ],
            "how_are_you": [
                "I'm doing well, just wrapped up a case downtown. What brings you here?",
                "Can't complain - the city keeps me busy with mysteries to solve.",
                "Another day fighting crime in this city. What's your story?"
            ],
            "help": [
                "I specialize in investigating mysteries and solving cases. What do you need help with?",
                "As a detective, I can help you investigate any suspicious activity or mystery.",
                "Tell me about your case - I'll help you get to the bottom of it."
            ],
            "goodbye": [
                "Stay safe out there. Call me if you need any detective work done.",
                "Until next time. Keep your eyes open for clues.",
                "Case closed for now. Don't hesitate to contact me if something comes up."
            ]
        }
        
        # Common conversation patterns for instant responses
        self.pattern_responses = {
            r"what.*your.*name": "Detective Evelyn Chen, private investigator. What case can I help you with?",
            r"tell.*about.*yourself": "I'm a private detective specializing in mysteries and investigations. Been working cases in this city for years.",
            r"what.*do.*you.*do": "I investigate mysteries, solve cases, and track down clues. It's what I live for.",
            r"nice.*meet.*you": "Likewise. Always good to meet someone new. Got any interesting cases for me?",
            r"thank.*you": "Just doing my job. Let me know if you need any more detective work.",
        }
    
    def get_instant_response(self, message: str, character_id: str, user_id: str) -> Optional[str]:
        """Get an instant cached response if available."""
        
        self.cache_stats["total_requests"] += 1
        
        # Normalize message for pattern matching
        normalized_msg = message.lower().strip()
        
        # Check for exact matches in detective responses
        if normalized_msg in self.detective_responses:
            self.cache_stats["hits"] += 1
            responses = self.detective_responses[normalized_msg]
            return responses[hash(user_id) % len(responses)]
        
        # Check for pattern matches
        for pattern, response in self.pattern_responses.items():
            if re.search(pattern, normalized_msg):
                self.cache_stats["hits"] += 1
                return response
        
        # Check general cache
        cache_key = self._generate_cache_key(message, character_id, user_id)
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                self.cache_stats["hits"] += 1
                return cached_data["response"]
            else:
                # Expired cache entry
                del self.cache[cache_key]
        
        self.cache_stats["misses"] += 1
        return None
    
    def cache_response(self, message: str, character_id: str, user_id: str, response: str):
        """Cache a response for future use."""
        
        cache_key = self._generate_cache_key(message, character_id, user_id)
        self.cache[cache_key] = {
            "response": response,
            "timestamp": time.time(),
            "character_id": character_id,
            "user_id": user_id
        }
        
        # Limit cache size to prevent memory issues
        if len(self.cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self.cache.keys(), 
                               key=lambda k: self.cache[k]["timestamp"])[:100]
            for key in oldest_keys:
                del self.cache[key]
    
    def _generate_cache_key(self, message: str, character_id: str, user_id: str) -> str:
        """Generate a cache key for the message."""
        content = f"{character_id}:{user_id}:{message.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total = self.cache_stats["total_requests"]
        if total == 0:
            return {"hit_rate": 0, "cache_size": len(self.cache)}
        
        hit_rate = self.cache_stats["hits"] / total * 100
        return {
            "hit_rate": hit_rate,
            "total_requests": total,
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "cache_size": len(self.cache)
        }

class DetectiveConsistencyEnforcer:
    """Enforces detective character consistency in responses."""
    
    REQUIRED_VOCABULARY = [
        "investigate", "case", "evidence", "mystery", "suspect", 
        "clues", "witness", "interrogate", "solve", "crime scene",
        "detective", "investigation", "lead", "alibi", "motive"
    ]
    
    DETECTIVE_PHRASES = [
        "Let me investigate this",
        "The evidence suggests",
        "In my experience as a detective",
        "This case reminds me of",
        "I need to examine the clues",
        "The investigation shows",
        "Based on my detective work"
    ]
    
    def enforce_detective_speech(self, response: str, character_id: str) -> str:
        """Ensure response maintains detective character consistency."""
        
        # Only enforce for detective characters
        if "detective" not in character_id.lower() and "ambitions" not in character_id.lower():
            return response
        
        # Check if response already has detective vocabulary
        response_lower = response.lower()
        vocab_count = sum(1 for word in self.REQUIRED_VOCABULARY if word in response_lower)
        
        # If response lacks detective vocabulary, enhance it
        if vocab_count == 0:
            # Add detective context to the beginning
            detective_intro = "As a detective, I can tell you that "
            if not response.startswith(detective_intro):
                response = detective_intro + response.lower()
        
        # Ensure proper detective tone
        if not any(phrase in response_lower for phrase in ["case", "investigate", "evidence", "mystery"]):
            # Add detective context
            if "?" in response:
                response = response.replace("?", "? This reminds me of a case I worked on.")
            else:
                response += " Let me know if you need any detective work done."
        
        return response
    
    def validate_character_consistency(self, response: str, character_type: str) -> float:
        """Score response for character consistency (0.0 to 1.0)."""
        
        if "detective" not in character_type.lower():
            return 1.0  # Not a detective character
        
        response_lower = response.lower()
        
        # Count detective vocabulary usage
        vocab_score = sum(1 for word in self.REQUIRED_VOCABULARY if word in response_lower)
        vocab_score = min(vocab_score / 3, 1.0)  # Normalize to 0-1
        
        # Check for detective phrases
        phrase_score = sum(1 for phrase in self.DETECTIVE_PHRASES if phrase.lower() in response_lower)
        phrase_score = min(phrase_score / 2, 1.0)  # Normalize to 0-1
        
        # Penalize generic AI responses
        generic_penalties = [
            "as an ai", "i'm an artificial", "i don't have personal", 
            "i'm here to help", "how can i assist"
        ]
        generic_penalty = sum(0.3 for phrase in generic_penalties if phrase in response_lower)
        
        # Calculate final score
        consistency_score = (vocab_score * 0.4 + phrase_score * 0.6) - generic_penalty
        return max(0.0, min(1.0, consistency_score))

class AdvancedNameExtractor:
    """Advanced name extraction and usage system."""
    
    def __init__(self):
        self.name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"call me (\w+)",
            r"i am (\w+)",
            r"(\w+) here",
            r"this is (\w+)",
            r"name's (\w+)",
            r"i go by (\w+)"
        ]
    
    def extract_user_name(self, message: str) -> Optional[str]:
        """Extract user name from message with 95% accuracy target."""
        
        message_lower = message.lower()
        
        for pattern in self.name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).strip()
                # Validate name (basic filtering)
                if len(name) > 1 and name.isalpha():
                    return name.title()
        
        return None
    
    def use_name_in_response(self, response: str, user_name: str) -> str:
        """Integrate user name naturally into response."""
        
        if not user_name:
            return response
        
        # If response doesn't already use the name, add it naturally
        if user_name.lower() not in response.lower():
            # Add name to beginning of response
            if response.startswith(("Hello", "Hi", "Hey")):
                response = re.sub(r"^(Hello|Hi|Hey)", f"\\1 {user_name}", response)
            else:
                response = f"{user_name}, " + response
        
        return response

class UltraFastResponseSystem:
    """Complete ultra-fast response system integrating all optimizations."""
    
    def __init__(self):
        self.cache = UltraFastResponseCache()
        self.consistency_enforcer = DetectiveConsistencyEnforcer()
        self.name_extractor = AdvancedNameExtractor()
        self.performance_stats = {
            "total_requests": 0,
            "fast_responses": 0,
            "cache_hits": 0,
            "average_response_time": 0.0
        }
    
    async def generate_ultra_fast_response(
        self, 
        message: str, 
        character_id: str, 
        user_id: str,
        agent,
        enhanced_memory_system
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate ultra-fast response with 90% <3s target."""
        
        start_time = time.time()
        self.performance_stats["total_requests"] += 1
        
        # Extract user name if present
        user_name = self.name_extractor.extract_user_name(message)
        
        # Try instant cached response first
        cached_response = self.cache.get_instant_response(message, character_id, user_id)
        
        if cached_response:
            # Apply name personalization
            if user_name:
                cached_response = self.name_extractor.use_name_in_response(cached_response, user_name)
            
            # Ensure detective consistency
            cached_response = self.consistency_enforcer.enforce_detective_speech(cached_response, character_id)
            
            response_time = time.time() - start_time
            self.performance_stats["fast_responses"] += 1
            self.performance_stats["cache_hits"] += 1
            
            return cached_response, {
                "response_time": response_time,
                "cache_hit": True,
                "ultra_fast": True,
                "consistency_score": self.consistency_enforcer.validate_character_consistency(cached_response, character_id)
            }
        
        # Generate new response with optimizations
        try:
            # Use optimized prompt for faster LLM processing
            optimized_instructions = self._create_optimized_prompt(agent.instructions, character_id)
            original_instructions = agent.instructions
            agent.instructions = optimized_instructions
            
            # Generate response
            response = agent.run(message, user_id=user_id)
            response_content = response.content
            
            # Restore original instructions
            agent.instructions = original_instructions
            
        except Exception as e:
            # Fallback to character-appropriate response
            if "freud" in character_id.lower() or "psycho" in character_id.lower():
                response_content = "Tell me more about this. What associations come to mind when you think about this experience?"
            elif "detective" in character_id.lower() or "ambitions" in character_id.lower():
                response_content = "I'm here to help with your case. What details can you share with me?"
            else:
                response_content = "That's interesting. Could you tell me more about what you're thinking?"
        
        # Apply all enhancements
        performance_stats = {}
        
        # Try enhanced relationship system first
        if ENHANCED_RELATIONSHIPS_AVAILABLE:
            try:
                response_content, relationship_stats = await enhance_response_with_relationship(
                    message, user_id, character_id, response_content
                )
                performance_stats.update(relationship_stats)
            except Exception as e:
                print(f"Enhanced relationship system error: {e}")
                # Fallback to original system
                if user_name:
                    response_content = self.name_extractor.use_name_in_response(response_content, user_name)
        else:
            # Fallback to original name extraction
            if user_name:
                response_content = self.name_extractor.use_name_in_response(response_content, user_name)
        
        # Apply character-specific consistency
        response_content = self.consistency_enforcer.enforce_detective_speech(response_content, character_id)
        
        # Cache the response for future use
        self.cache.cache_response(message, character_id, user_id, response_content)
        
        response_time = time.time() - start_time
        
        # Track performance
        if response_time < 3.0:
            self.performance_stats["fast_responses"] += 1
        
        # Update average response time
        total = self.performance_stats["total_requests"]
        current_avg = self.performance_stats["average_response_time"]
        self.performance_stats["average_response_time"] = (current_avg * (total - 1) + response_time) / total
        
        # Combine all performance stats
        final_stats = {
            "response_time": response_time,
            "cache_hit": False,
            "ultra_fast": response_time < 1.0,
            "consistency_score": self.consistency_enforcer.validate_character_consistency(response_content, character_id),
            "user_name_extracted": user_name is not None,
            **performance_stats  # Include enhanced relationship stats
        }
        
        return response_content, final_stats
    
    def _create_optimized_prompt(self, original_instructions: str, character_id: str) -> str:
        """Create optimized prompt for faster LLM processing."""
        
        # Condensed detective prompt for speed
        if "detective" in character_id.lower() or "ambitions" in character_id.lower():
            optimized_prompt = """You are Detective Evelyn Chen, a film noir private investigator. 
Respond in character with detective vocabulary: investigate, case, evidence, mystery, suspect, clues.
Keep responses under 150 words. Always maintain your detective persona."""
        else:
            # Use shortened version of original prompt
            lines = original_instructions.split('\n')
            optimized_prompt = '\n'.join(lines[:10])  # First 10 lines only
        
        return optimized_prompt
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        
        total = self.performance_stats["total_requests"]
        if total == 0:
            return {"no_data": True}
        
        fast_response_rate = self.performance_stats["fast_responses"] / total * 100
        cache_hit_rate = self.performance_stats["cache_hits"] / total * 100
        
        cache_stats = self.cache.get_cache_stats()
        
        return {
            "total_requests": total,
            "fast_response_rate": fast_response_rate,  # % of responses <3s
            "average_response_time": self.performance_stats["average_response_time"],
            "cache_hit_rate": cache_hit_rate,
            "target_achievement": {
                "response_time_90_percent": fast_response_rate >= 90,
                "average_under_2_5s": self.performance_stats["average_response_time"] < 2.5,
                "cache_hit_rate_95_percent": cache_hit_rate >= 95
            },
            "cache_details": cache_stats
        }

# Global instance for use in the main application
ultra_fast_system = UltraFastResponseSystem() 