#!/usr/bin/env python3
"""
OpenAI Compatibility Fix
Handles compatibility issues between different OpenAI API versions
"""
import sys
from types import ModuleType

# Create mock classes for missing OpenAI components
class ParsedChatCompletion:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ParsedChoice:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ParsedMessage:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ParsedToolCall:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ParsedToolCallDelta:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ParsedMessageDelta:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

class ParsedChatCompletionMessage:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

# Fix for missing ParsedChatCompletion and related classes
if 'openai.types.chat.parsed_chat_completion' not in sys.modules:
    module = ModuleType('openai.types.chat.parsed_chat_completion')
    module.ParsedChatCompletion = ParsedChatCompletion
    module.ParsedChoice = ParsedChoice
    module.ParsedMessage = ParsedMessage
    module.ParsedToolCall = ParsedToolCall
    module.ParsedToolCallDelta = ParsedToolCallDelta
    module.ParsedMessageDelta = ParsedMessageDelta
    module.ParsedChatCompletionMessage = ParsedChatCompletionMessage
    sys.modules['openai.types.chat.parsed_chat_completion'] = module

# Fix for TypeAlias compatibility issue
try:
    from typing import TypeAlias
except ImportError:
    # For Python < 3.10, create a simple TypeAlias
    class TypeAlias:
        def __init__(self, target):
            self.target = target
        def __getitem__(self, key):
            return self.target

# Fix for the specific TypeAlias issue in OpenAI
try:
    import openai.lib.streaming.chat._types as chat_types
    if not hasattr(chat_types, 'ParsedChatCompletionSnapshot'):
        chat_types.ParsedChatCompletionSnapshot = ParsedChatCompletion
    print("✅ Fixed TypeAlias compatibility issue")
except Exception as e:
    print(f"⚠️ TypeAlias fix failed: {e}")

# Fix for ChatCompletionMessage audio attribute error
try:
    import openai
    from openai.types.chat import ChatCompletionMessage
    
    # Monkey patch the class to handle missing audio attribute
    original_getattribute = ChatCompletionMessage.__getattribute__
    
    def patched_getattribute(self, name):
        if name == 'audio':
            return getattr(self, '_audio', None)
        return original_getattribute(self, name)
    
    def patched_setattr(self, name, value):
        if name == 'audio':
            object.__setattr__(self, '_audio', value)
        else:
            object.__setattr__(self, name, value)
    
    # Apply the patches
    ChatCompletionMessage.__getattribute__ = patched_getattribute
    ChatCompletionMessage.__setattr__ = patched_setattr
    
    print("✅ OpenAI ChatCompletionMessage patched for audio attribute")
    
except Exception as e:
    print(f"⚠️ OpenAI compatibility patch failed: {e}")

# Additional fix for response content access
try:
    def safe_get_content(response):
        """Safely get content from OpenAI response"""
        if hasattr(response, 'content'):
            return response.content
        elif hasattr(response, 'message') and hasattr(response.message, 'content'):
            return response.message.content
        return str(response)
    
    # Make this function available globally
    import builtins
    builtins.safe_get_content = safe_get_content
    
    print("✅ Safe content extraction function added")
    
except Exception as e:
    print(f"⚠️ Safe content extraction patch failed: {e}")

# Fix for OpenAI client initialization
try:
    def safe_openai_client():
        """Safely create OpenAI client with fallback"""
        try:
            from openai import OpenAI
            return OpenAI()
        except ImportError:
            print("⚠️ OpenAI package not installed, using fallback")
            return None
    
    import builtins
    builtins.safe_openai_client = safe_openai_client
    
    print("✅ Safe OpenAI client function added")
    
except Exception as e:
    print(f"⚠️ Safe OpenAI client patch failed: {e}")

print("✅ OpenAI compatibility fixes applied")
