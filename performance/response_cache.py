#!/usr/bin/env python3
"""
Response Cache
Provides caching for response generation
"""

import time
from typing import Dict, Any, Optional

class ResponseCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["response"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, response: str):
        """Cache response"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "response": response,
            "timestamp": time.time()
        }

# Global cache instance
response_cache = ResponseCache()
