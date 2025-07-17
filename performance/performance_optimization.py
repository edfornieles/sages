#!/usr/bin/env python3
"""
Performance Optimization Module

This module provides various optimizations to speed up character responses
including prompt optimization, response caching, and efficient context preparation.
"""

import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

class PerformanceOptimizer:
    """Handles various performance optimizations for the character system."""
    
    def __init__(self, character_id: str, user_id: str):
        self.character_id = character_id
        self.user_id = user_id
        self.response_cache = {}
        self.context_cache = {}
        self.prompt_templates = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        
    def optimize_prompt_for_speed(self, base_prompt: str, memory_context: Dict[str, Any]) -> str:
        """Optimize the prompt for faster LLM processing while maintaining quality."""
        
        # Use cached prompt template if available
        template_key = f"prompt_{self.character_id}_{self.user_id}"
        if template_key in self.prompt_templates:
            template = self.prompt_templates[template_key]
        else:
            template = self._create_optimized_prompt_template(base_prompt)
            self.prompt_templates[template_key] = template
        
        # Prepare condensed context
        condensed_context = self._condense_memory_context(memory_context)
        
        # Fill template with context
        optimized_prompt = template.format(**condensed_context)
        
        return optimized_prompt
    
    def _create_optimized_prompt_template(self, base_prompt: str) -> str:
        """Create an optimized prompt template for faster processing."""
        
        # Extract key elements from base prompt
        optimized_template = """You are {character_name}, a {personality_summary}.

RECENT CONTEXT (last {recent_count} exchanges):
{recent_memories}

KEY RELATIONSHIPS:
{key_entities}

CURRENT MOOD: {current_emotion}
CONVERSATION TOPIC: {main_topic}

USER PROFILE: {user_style} communicator interested in {user_interests}

Respond as {character_name} in character. Keep responses natural and engaging while referencing relevant context."""
        
        return optimized_template
    
    def _condense_memory_context(self, memory_context: Dict[str, Any]) -> Dict[str, str]:
        """Condense memory context into a compact format for faster processing."""
        
        condensed = {
            "character_name": "Character",
            "personality_summary": "unique personality",
            "recent_count": "0",
            "recent_memories": "No recent memories",
            "key_entities": "None mentioned",
            "current_emotion": "neutral",
            "main_topic": "general conversation",
            "user_style": "conversational",
            "user_interests": "various topics"
        }
        
        # Process recent memories (limit to 3 most important)
        if "recent_memories" in memory_context and memory_context["recent_memories"]:
            recent = memory_context["recent_memories"][-3:]  # Last 3 only
            condensed["recent_count"] = str(len(recent))
            condensed["recent_memories"] = "\n".join([
                f"- {mem['content'][:100]}..." if len(mem['content']) > 100 else f"- {mem['content']}"
                for mem in recent
            ])
        
        # Process key entities (top 3)
        if "entity_context" in memory_context and memory_context["entity_context"]:
            entities = list(memory_context["entity_context"].items())[:3]
            condensed["key_entities"] = ", ".join([
                f"{name} ({data['type']})" for name, data in entities
            ])
        
        # Process emotional context
        if "emotional_context" in memory_context:
            if isinstance(memory_context["emotional_context"], dict):
                condensed["current_emotion"] = memory_context["emotional_context"].get("current_emotion", "neutral")
            else:
                condensed["current_emotion"] = str(memory_context["emotional_context"])
        
        # Process conversation topic
        if "conversation_topic" in memory_context:
            if isinstance(memory_context["conversation_topic"], dict):
                condensed["main_topic"] = memory_context["conversation_topic"].get("primary_topic", "general")
            else:
                condensed["main_topic"] = str(memory_context["conversation_topic"])
        
        # Process user profile
        if "user_profile" in memory_context and memory_context["user_profile"]:
            profile = memory_context["user_profile"]
            condensed["user_style"] = profile.get("communication_style", "conversational")
            
            interests = profile.get("interests", [])
            if interests:
                condensed["user_interests"] = ", ".join([interest[0] for interest in interests[:3]])
        
        return condensed
    
    def get_cached_response(self, message: str, context_hash: str) -> Optional[str]:
        """Get cached response if available and fresh."""
        cache_key = self._generate_cache_key(message, context_hash)
        
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            
            # Check if cache is still fresh
            if (datetime.now() - cached_data['timestamp']).seconds < self.cache_ttl:
                return cached_data['response']
            else:
                # Remove stale cache
                del self.response_cache[cache_key]
        
        return None
    
    def cache_response(self, message: str, context_hash: str, response: str):
        """Cache a response for future use."""
        cache_key = self._generate_cache_key(message, context_hash)
        
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }
        
        # Limit cache size
        if len(self.response_cache) > 100:
            # Remove oldest entries
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]['timestamp'])
            del self.response_cache[oldest_key]
    
    def _generate_cache_key(self, message: str, context_hash: str) -> str:
        """Generate a cache key for message and context."""
        combined = f"{self.character_id}_{self.user_id}_{message}_{context_hash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _generate_context_hash(self, memory_context: Dict[str, Any]) -> str:
        """Generate a hash of the memory context for caching."""
        # Create a simplified hash based on key context elements
        context_str = json.dumps({
            "recent_count": len(memory_context.get("recent_memories", [])),
            "entity_count": len(memory_context.get("entity_context", {})),
            "emotion": memory_context.get("emotional_context", ""),
            "topic": memory_context.get("conversation_topic", "")
        }, sort_keys=True)
        
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def prepare_fast_context(self, enhanced_memory_system) -> Dict[str, Any]:
        """Prepare context optimized for fast response generation."""
        
        # Use fast context method instead of full expanded context
        if hasattr(enhanced_memory_system, 'get_memory_context_fast'):
            return enhanced_memory_system.get_memory_context_fast(limit=8)
        else:
            # Fallback to regular context with limit
            return enhanced_memory_system.get_memory_context()
    
    def optimize_agent_instructions(self, base_instructions: str, context: Dict[str, Any]) -> str:
        """Optimize agent instructions for faster processing while preserving character personality."""
        
        # Keep the original character instructions but add optimized context
        if not base_instructions or len(base_instructions) < 50:
            # Fallback if no base instructions
            optimized_instructions = f"""You are responding as a character in a conversation.

Key Context:
- Recent conversation: {len(context.get('recent_memories', []))} recent exchanges
- Main entities: {', '.join(list(context.get('key_entities', {}).keys())[:3])}
- Current emotion: {context.get('emotional_state', 'neutral')}
- Topic focus: {context.get('conversation_summary', 'general discussion')}

Respond naturally and in character. Reference context when relevant but don't overexplain."""
        else:
            # Preserve original character instructions and add context efficiently
            context_summary = []
            if context.get('recent_memories'):
                context_summary.append(f"Recent conversation: {len(context['recent_memories'])} exchanges")
            if context.get('emotional_state') and context['emotional_state'] != 'neutral':
                context_summary.append(f"Current mood: {context['emotional_state']}")
            if context.get('key_entities'):
                entities = list(context['key_entities'].keys())[:2]  # Limit to 2 for brevity
                if entities:
                    context_summary.append(f"Key topics: {', '.join(entities)}")
            
            # Add minimal context to original instructions
            if context_summary:
                context_line = f"\n\nContext: {'; '.join(context_summary)}"
                optimized_instructions = base_instructions + context_line
            else:
                optimized_instructions = base_instructions
        
        return optimized_instructions
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "cache_size": len(self.response_cache),
            "template_cache_size": len(self.prompt_templates),
            "context_cache_size": len(self.context_cache),
            "cache_ttl_seconds": self.cache_ttl
        }

class FastResponseManager:
    """Manages fast response generation with various optimizations."""
    
    def __init__(self):
        self.optimizers = {}  # character_id -> PerformanceOptimizer
        self.global_cache = {}
    
    def add_optimizer(self, character_id: str, user_id: str, optimizer: PerformanceOptimizer):
        """Register a PerformanceOptimizer for a character-user pair."""
        key = f"{character_id}_{user_id}"
        self.optimizers[key] = optimizer
        return optimizer
    
    def get_optimizer(self, character_id: str, user_id: str) -> PerformanceOptimizer:
        """Get or create a performance optimizer for a character-user pair."""
        key = f"{character_id}_{user_id}"
        
        if key not in self.optimizers:
            self.optimizers[key] = PerformanceOptimizer(character_id, user_id)
        
        return self.optimizers[key]
    
    def generate_fast_response(self, agent, message: str, character_id: str, user_id: str, 
                             enhanced_memory_system) -> tuple[str, Dict[str, Any]]:
        """Generate a response optimized for speed while preserving character authenticity."""
        
        start_time = time.time()
        optimizer = self.get_optimizer(character_id, user_id)
        
        # Prepare fast context
        context = optimizer.prepare_fast_context(enhanced_memory_system)
        context_hash = optimizer._generate_context_hash(context)
        
        # Check for cached response (but be more selective about caching character responses)
        cached_response = optimizer.get_cached_response(message, context_hash)
        if cached_response and len(message.split()) > 3:  # Only cache for longer messages
            return cached_response, {
                "cache_hit": True,
                "response_time": time.time() - start_time,
                "context_size": len(str(context))
            }
        
        # For character authenticity, use minimal optimization
        original_instructions = agent.instructions
        
        # Only add context if original instructions exist and are substantial
        if original_instructions and len(original_instructions) > 100:
            # Add minimal context without changing character personality
            optimized_instructions = optimizer.optimize_agent_instructions(
                original_instructions, context
            )
            agent.instructions = optimized_instructions
        
        try:
            # Generate response with preserved character instructions
            response = agent.run(message, user_id=user_id)
            response_content = response.content
            
            # Only cache longer conversations to preserve character nuance
            if len(message.split()) > 3 and len(response_content.split()) > 5:
                optimizer.cache_response(message, context_hash, response_content)
            
        finally:
            # Restore original instructions
            agent.instructions = original_instructions
        
        performance_stats = {
            "cache_hit": False,
            "response_time": time.time() - start_time,
            "context_size": len(str(context)),
            "optimization_applied": True,
            "character_preserved": True
        }
        
        return response_content, performance_stats

# Global instance
fast_response_manager = FastResponseManager() 

__all__ = [
    'PerformanceOptimizer',
    'FastResponseManager',
] 