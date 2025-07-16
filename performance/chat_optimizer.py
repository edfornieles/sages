
# API Call Optimization System
import time
from typing import Dict, Any, Optional
import hashlib

class ChatOptimizer:
    def __init__(self):
        self.recent_responses = {}
        self.call_count = 0
        self.cache_duration = 300  # 5 minutes
    
    def get_cache_key(self, message: str, character_id: str, user_id: str) -> str:
        """Generate cache key for similar requests"""
        combined = f"{message.lower().strip()}:{character_id}:{user_id}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def should_use_cache(self, message: str, character_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Check if we can use a cached response"""
        cache_key = self.get_cache_key(message, character_id, user_id)
        
        if cache_key in self.recent_responses:
            cached_data = self.recent_responses[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                # Simple similarity check for short messages
                if len(message) < 100:
                    return cached_data['response']
        
        return None
    
    def cache_response(self, message: str, character_id: str, user_id: str, response: Dict[str, Any]):
        """Cache a response for future use"""
        cache_key = self.get_cache_key(message, character_id, user_id)
        self.recent_responses[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        # Clean old cache entries
        if len(self.recent_responses) > 100:
            current_time = time.time()
            expired_keys = [k for k, v in self.recent_responses.items() 
                          if current_time - v['timestamp'] > self.cache_duration]
            for key in expired_keys:
                del self.recent_responses[key]
    
    def track_api_call(self):
        """Track API call count"""
        self.call_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            'total_api_calls': self.call_count,
            'cached_responses': len(self.recent_responses)
        }

# Global optimizer instance
chat_optimizer = ChatOptimizer()
