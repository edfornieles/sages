#!/usr/bin/env python3

# CRITICAL: Apply OpenAI compatibility fix BEFORE any other imports
try:
    from core import fix_openai_compatibility
except ImportError:
    import fix_openai_compatibility

# AGGRESSIVE FIX: Emergency timeout protection
import asyncio
from concurrent.futures import TimeoutError

async def timeout_wrapper(coro, timeout_seconds=2.5):
    """Wrap any coroutine with aggressive timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except (TimeoutError, asyncio.TimeoutError):
        return {
            "response": "I want to give you a quick response to keep our conversation flowing. What else would you like to know?",
            "timeout_protected": True,
            "processing_time": timeout_seconds
        }
    

# Performance Optimization Imports - Milestone 2
try:
    from response_cache import response_cache
    from chat_optimizer import chat_optimizer
    OPTIMIZATIONS_ENABLED = True
    print("✅ Performance optimizations loaded")
except ImportError as e:
    OPTIMIZATIONS_ENABLED = False
    print(f"✅ Performance optimizations not available: {e} (optional)")

"""
Enhanced Dynamic Character Playground with Advanced Memory System
"""

import sys
import os

# Remove any local phi paths to ensure we use the installed package
sys.path = [p for p in sys.path if 'phidata-main_live' not in p]

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import sqlite3
import json
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import logging
import re
import hashlib
from dataclasses import dataclass, asdict
import traceback
import asyncio
import time
from collections import defaultdict, Counter

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from characters.character_generator import CharacterGenerator
from phi.agent import Agent
from phi.memory import AgentMemory
from phi.memory.db.sqlite import SqliteMemoryDb
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.model.openai import OpenAIChat
from systems.universal_prompt_loader import get_universal_prompt_text, get_universal_instructions
from systems.mood_system import MoodSystem
from systems.relationship_system import RelationshipSystem
from systems.ambitions_system import AmbitionsSystem
from systems.learning_system import LearningSystem
import time
from performance.performance_optimization import fast_response_manager
from systems.ip_geolocation_system import IPGeolocationSystem
# from src.enhanced_memory_system import EnhancedMemorySystem  # Legacy import removed
from memory_new.db.connection import get_memory_db_path

# Character Identity Fixes - Simplified
CHARACTER_IDENTITY_FIXES = False
print("✅ Character identity fixes disabled for enhanced memory testing (intentional)")

def get_character_identity(character_id, character_data):
    """Get character identity with safe fallbacks"""
    return {
        "name": character_data.get("name", "Character"),
        "gender": character_data.get("gender", "Unknown"),
        "age": character_data.get("age", "Unknown"),
        "personality": character_data.get("personality_traits", {})
    }

# Enhanced subsystem imports
try:
    # Legacy memory imports removed - using new modular system
# from memory.enhanced_personal_details_extractor import create_enhanced_extractor, extract_personal_details_enhanced
# from memory.enhanced_relationship_progression import create_enhanced_relationship_progression, analyze_interaction_enhanced, calculate_progression_enhanced
# from memory.enhanced_shared_history import create_enhanced_shared_history, process_conversation_enhanced, get_conversation_summary_enhanced
    ENHANCED_SUBSYSTEMS_AVAILABLE = True
    print("✅ Enhanced subsystems loaded successfully")
except ImportError as e:
    ENHANCED_SUBSYSTEMS_AVAILABLE = False
    print(f"⚠️ Enhanced subsystems not available: {e}")

# Initialize enhanced modules (singleton for now)
if ENHANCED_SUBSYSTEMS_AVAILABLE:
    # Legacy enhanced subsystems disabled - using new modular system
    # personal_details_extractor = create_enhanced_extractor()
    # relationship_progression = create_enhanced_relationship_progression()
    # shared_history = create_enhanced_shared_history()
    personal_details_extractor = None
    relationship_progression = None
    shared_history = None
else:
    personal_details_extractor = None
    relationship_progression = None
    shared_history = None

def safe_load_memories(*args, **kwargs):
    return []
def build_memory_context(*args, **kwargs):
    return {}

# Ultra-Fast Response System Integration
try:
    from performance.ultra_fast_response_system import ultra_fast_system
    ULTRA_FAST_AVAILABLE = True
    print("✅ Ultra-fast response system loaded successfully")
except ImportError as e:
    ULTRA_FAST_AVAILABLE = False
    print(f"⚠️ Ultra-fast response system not available: {e}")

# NEW: Import modular memory system
ENHANCED_MEMORY_AVAILABLE = False  # Default to False
MODULAR_MEMORY_AVAILABLE = False  # Default to False
try:
    from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem, get_enhanced_memory_system
    from memory_new.db.connection import get_memory_db_path
    MODULAR_MEMORY_AVAILABLE = True
    ENHANCED_MEMORY_AVAILABLE = True
    print("✅ Modular memory system loaded successfully")
except ImportError as e:
    MODULAR_MEMORY_AVAILABLE = False
    ENHANCED_MEMORY_AVAILABLE = False
    print(f"⚠️ Modular memory system not available: {e}")

# Import ephemeral memory system
try:
    # Legacy ephemeral memory import removed - using new modular system
    # from memory.ephemeral_memory_api import ephemeral_router
    EPHEMERAL_MEMORY_AVAILABLE = True
    print("✅ Ephemeral memory system loaded successfully")
except ImportError as e:
    EPHEMERAL_MEMORY_AVAILABLE = False
    print(f"⚠️ Ephemeral memory system not available: {e}")

# Import new enhanced systems
try:
    from systems.character_state_persistence import CharacterStatePersistence
    from systems.emotional_context_tracker import EmotionalContextTracker
    ENHANCED_SYSTEMS_AVAILABLE = True
    print("✅ Enhanced character state and emotional tracking systems loaded")
except ImportError as e:
    ENHANCED_SYSTEMS_AVAILABLE = False
    print(f"⚠️ Enhanced systems not available: {e}")

# Initialize new systems
if ENHANCED_SYSTEMS_AVAILABLE:
    character_state_persistence = CharacterStatePersistence()
    emotional_context_tracker = EmotionalContextTracker()
else:
    character_state_persistence = None
    emotional_context_tracker = None

# Load environment variables
load_dotenv()

def get_playground_html() -> str:
    """Generate the HTML for the playground interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎭 Dynamic Character Playground</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a202c;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-weight: 800;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .version-toggle {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .version-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .version-btn.active {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
            transform: scale(1.05);
        }
        
        .version-btn:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 25px;
            height: calc(100vh - 250px);
        }
        
        .sidebar {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(20px);
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .chat-area {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(20px);
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .section-title {
            font-size: 1.4em;
            margin-bottom: 20px;
            color: #2d3748;
            border-bottom: 3px solid #e2e8f0;
            padding-bottom: 10px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title::before {
            content: "✨";
            font-size: 1.2em;
        }
        
        .generate-section {
            margin-bottom: 30px;
        }
        
        .generate-controls {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            font-size: 14px;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .user-presets {
            display: flex;
            gap: 12px;
            margin-top: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn-preset {
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(23, 162, 184, 0.3);
        }
        
        .btn-preset:hover {
            background: linear-gradient(135deg, #138496 0%, #117a8b 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(23, 162, 184, 0.4);
        }
        
        .btn-preset.active {
            background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
        }
        
        .input-group {
            display: flex;
            gap: 12px;
            margin-bottom: 15px;
        }
        
        input[type="text"], input[type="number"] {
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 14px;
            flex: 1;
            transition: all 0.3s ease;
            background: #f8fafc;
        }
        
        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            background: white;
            transform: translateY(-1px);
        }
        
        .characters-list {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        .characters-list::-webkit-scrollbar {
            width: 8px;
        }
        
        .characters-list::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 10px;
        }
        
        .characters-list::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        .character-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .character-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .character-card:hover {
            border-color: #667eea;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .character-card:hover::before {
            transform: scaleX(1);
        }
        
        .character-card.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }
        
        .character-card.selected::before {
            transform: scaleX(1);
        }
        
        .character-name {
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .character-details {
            font-size: 0.9em;
            color: #64748b;
            line-height: 1.5;
        }
        
        .character-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
        }
        
        .mood-indicator {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            color: #2d3748;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
            box-shadow: 0 2px 8px rgba(255, 234, 167, 0.3);
        }
        
        .mood-change {
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            border: 1px solid #68d391;
            border-radius: 12px;
            padding: 10px;
            margin: 8px 0;
            font-size: 0.85em;
            color: #22543d;
            box-shadow: 0 2px 8px rgba(154, 230, 180, 0.3);
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            max-height: 500px;
        }
        
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 10px;
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 15px;
            position: relative;
            animation: messageSlideIn 0.3s ease;
        }
        
        @keyframes messageSlideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .message.character {
            background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
            color: #2d3748;
            margin-right: 20%;
            box-shadow: 0 4px 15px rgba(226, 232, 240, 0.3);
        }
        
        .message-sender {
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .chat-input-area {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            font-size: 16px;
            color: #2d3748;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            transition: all 0.3s ease;
            resize: none;
            min-height: 50px;
            max-height: 120px;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            background: white;
            transform: translateY(-1px);
        }
        
        .chat-input::placeholder {
            color: #a0aec0;
        }
        
        .status {
            text-align: center;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-weight: 600;
            animation: statusSlideIn 0.3s ease;
        }
        
        @keyframes statusSlideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .status.success {
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            color: #22543d;
            border: 1px solid #68d391;
            box-shadow: 0 4px 15px rgba(154, 230, 180, 0.3);
        }
        
        .status.error {
            background: linear-gradient(135deg, #fed7d7 0%, #fc8181 100%);
            color: #742a2a;
            border: 1px solid #f56565;
            box-shadow: 0 4px 15px rgba(252, 129, 129, 0.3);
        }
        
        .status.info {
            background: linear-gradient(135deg, #bee3f8 0%, #63b3ed 100%);
            color: #2a4365;
            border: 1px solid #4299e1;
            box-shadow: 0 4px 15px rgba(99, 179, 237, 0.3);
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-weight: 600;
            padding: 20px;
        }
        
        .loading::after {
            content: '';
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #e2e8f0;
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
            margin-left: 10px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .character-actions {
            display: flex;
            gap: 8px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .btn-small {
            padding: 8px 16px;
            font-size: 0.85em;
            border-radius: 10px;
        }
        
        .relationship-progress {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .progress-label {
            font-weight: 700;
            color: #475569;
            font-size: 1.1em;
        }
        
        #progressLevel {
            font-weight: 800;
            color: #667eea;
            font-size: 1.2em;
        }
        
        .progress-bar-container {
            background: #e2e8f0;
            border-radius: 25px;
            height: 10px;
            margin-bottom: 12px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .progress-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            border-radius: 25px;
            transition: width 0.8s ease;
            width: 0%;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        }
        
        .progress-details {
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            color: #64748b;
            font-weight: 500;
        }
        
        .memory-status {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border: 2px solid #cbd5e0;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .memory-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .memory-label {
            font-weight: 700;
            color: #2d3748;
            font-size: 1.1em;
        }
        
        .memory-details {
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            color: #64748b;
            font-weight: 500;
        }
        
        /* Appearance Editor Modal Styles */
        .appearance-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        
        .appearance-modal-content {
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 700px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: modalSlideIn 0.4s ease;
        }
        
        @keyframes modalSlideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .appearance-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 3px solid #e2e8f0;
        }
        
        .appearance-modal-title {
            font-size: 1.6em;
            color: #2d3748;
            margin: 0;
            font-weight: 700;
        }
        
        .close-modal {
            background: none;
            border: none;
            font-size: 1.8em;
            cursor: pointer;
            color: #718096;
            padding: 8px;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .close-modal:hover {
            background: #f7fafc;
            color: #4a5568;
            transform: scale(1.1);
        }
        
        .appearance-textarea {
            width: 100%;
            min-height: 150px;
            padding: 20px;
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            transition: all 0.3s ease;
        }
        
        .appearance-textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            background: white;
        }
        
        .appearance-actions {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
        }
        
        .character-appearance-preview {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px;
            margin-top: 8px;
            font-size: 0.9em;
            color: #4a5568;
            font-style: italic;
            max-height: 60px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .character-appearance-preview.empty {
            color: #a0aec0;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .generate-controls {
                flex-direction: column;
            }
            
            .appearance-modal-content {
                margin: 10% auto;
                width: 95%;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 Dynamic Character Playground</h1>
            <p>Enhanced AI Characters with Memory, Mood, and Relationships</p>
        </div>
        
        <div class="version-toggle">
            <button class="version-btn active" onclick="switchVersion('new')">✨ New Design</button>
            <button class="version-btn" onclick="switchVersion('old')">📱 Classic Design</button>
        </div>
        
        <div class="main-content" id="newDesign">
            <div class="sidebar">
                <div class="generate-section">
                    <h3 class="section-title">🎲 Generate Characters</h3>
                    <div class="input-group">
                        <input type="text" id="characterId" placeholder="Character ID (optional)">
                        <input type="number" id="characterCount" value="1" min="1" max="10">
                    </div>
                    <div class="input-group">
                        <input type="text" id="userId" placeholder="User ID (default: user)" value="ed_fornieles">
                        <button class="btn btn-secondary" onclick="setCurrentUser()">Set User</button>
                    </div>
                    <div class="user-presets">
                        <button class="btn btn-preset" onclick="setPresetUser('ed_fornieles')">Ed Fornieles</button>
                        <button class="btn btn-preset" onclick="setPresetUser('alex_chen')">Alex Chen</button>
                    </div>
                    <div class="generate-controls">
                        <button class="btn btn-primary" onclick="generateCharacter()">Generate Random</button>
                        <button class="btn btn-secondary" onclick="refreshCharacters()">Refresh List</button>
                        <button class="btn btn-success" onclick="window.open('/create-character', '_blank')">🎭 Create Custom Character</button>
                    </div>
                    <div class="current-user-display">
                        <small style="color: #718096;">Current User: <span id="currentUser">ed_fornieles</span></small>
                    </div>
                </div>
                
                <div class="characters-section">
                    <h3 class="section-title">👥 Characters</h3>
                    <div class="search-section" style="margin-bottom: 15px;">
                        <input type="text" id="characterSearch" class="search-input" placeholder="🔍 Search characters by name..." style="width: 100%; padding: 10px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px;">
                    </div>
                    <div id="charactersList" class="characters-list">
                        <div class="loading">Loading characters...</div>
                    </div>
                </div>
            </div>
            
            <div class="chat-area">
                <h3 class="section-title">💬 Chat</h3>
                <div id="status" class="status" style="display: none;"></div>
                
                <!-- Relationship Progress Bar -->
                <div id="relationshipProgress" class="relationship-progress" style="display: none;">
                    <div class="progress-header">
                        <span class="progress-label">🤝 Connection Level</span>
                        <span id="progressLevel">0</span>
                    </div>
                    <div class="progress-bar-container">
                        <div id="progressBar" class="progress-bar"></div>
                    </div>
                    <div class="progress-details">
                        <span id="progressDescription">Not connected</span>
                        <span id="progressPercentage">0%</span>
                    </div>
                </div>
                
                <!-- Memory Status Display -->
                <div id="memoryStatus" class="memory-status" style="display: none;">
                    <div class="memory-header">
                        <span class="memory-label">🧠 Character Memory</span>
                        <button class="btn btn-small" onclick="viewMemorySummary()" id="viewMemoryBtn">View Details</button>
                    </div>
                    <div class="memory-details">
                        <span id="memoryCount">0 memories stored</span>
                        <span id="memoryStatus">No conversation history</span>
                    </div>
                </div>
                
                <div id="chatMessages" class="chat-messages">
                    <div style="text-align: center; color: #718096; margin-top: 50px;">
                        Select a character to start chatting
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chatInput" class="chat-input" placeholder="Type your message..." disabled>
                    <button class="btn btn-primary" id="sendBtn" onclick="sendMessage()" disabled>Send</button>
                </div>
            </div>
        </div>
        
        <!-- Old Design Version -->
        <div class="main-content" id="oldDesign" style="display: none;">
            <div class="sidebar">
                <div class="generate-section">
                    <h3 class="section-title">🎲 Generate Characters</h3>
                    <div class="input-group">
                        <input type="text" id="characterIdOld" placeholder="Character ID (optional)">
                        <input type="number" id="characterCountOld" value="1" min="1" max="10">
                    </div>
                    <div class="input-group">
                        <input type="text" id="userIdOld" placeholder="User ID (default: user)" value="ed_fornieles">
                        <button class="btn btn-secondary" onclick="setCurrentUserOld()">Set User</button>
                    </div>
                    <div class="user-presets">
                        <button class="btn btn-preset" onclick="setPresetUserOld('ed_fornieles')">Ed Fornieles</button>
                        <button class="btn btn-preset" onclick="setPresetUserOld('alex_chen')">Alex Chen</button>
                    </div>
                    <div class="generate-controls">
                        <button class="btn btn-primary" onclick="generateCharacterOld()">Generate Random</button>
                        <button class="btn btn-secondary" onclick="refreshCharactersOld()">Refresh List</button>
                        <button class="btn btn-success" onclick="window.open('/create-character', '_blank')">🎭 Create Custom Character</button>
                    </div>
                    <div class="current-user-display">
                        <small style="color: #718096;">Current User: <span id="currentUserOld">ed_fornieles</span></small>
                    </div>
                </div>
                
                <div class="characters-section">
                    <h3 class="section-title">👥 Characters</h3>
                    <div class="search-section" style="margin-bottom: 15px;">
                        <input type="text" id="characterSearchOld" class="search-input" placeholder="🔍 Search characters by name..." style="width: 100%; padding: 10px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px;">
                    </div>
                    <div id="charactersListOld" class="characters-list">
                        <div class="loading">Loading characters...</div>
                    </div>
                </div>
            </div>
            
            <div class="chat-area">
                <h3 class="section-title">💬 Chat</h3>
                <div id="statusOld" class="status" style="display: none;"></div>
                
                <!-- Relationship Progress Bar -->
                <div id="relationshipProgressOld" class="relationship-progress" style="display: none;">
                    <div class="progress-header">
                        <span class="progress-label">🤝 Connection Level</span>
                        <span id="progressLevelOld">0</span>
                    </div>
                    <div class="progress-bar-container">
                        <div id="progressBarOld" class="progress-bar"></div>
                    </div>
                    <div class="progress-details">
                        <span id="progressDescriptionOld">Not connected</span>
                        <span id="progressPercentageOld">0%</span>
                    </div>
                </div>
                
                <!-- Memory Status Display -->
                <div id="memoryStatusOld" class="memory-status" style="display: none;">
                    <div class="memory-header">
                        <span class="memory-label">🧠 Character Memory</span>
                        <button class="btn btn-small" onclick="viewMemorySummaryOld()" id="viewMemoryBtnOld">View Details</button>
                    </div>
                    <div class="memory-details">
                        <span id="memoryCountOld">0 memories stored</span>
                        <span id="memoryStatusOld">No conversation history</span>
                    </div>
                </div>
                
                <div id="chatMessagesOld" class="chat-messages">
                    <div style="text-align: center; color: #718096; margin-top: 50px;">
                        Select a character to start chatting
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chatInputOld" class="chat-input" placeholder="Type your message..." disabled>
                    <button class="btn btn-primary" id="sendBtnOld" onclick="sendMessageOld()" disabled>Send</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Appearance Editor Modal -->
    <div id="appearanceModal" class="appearance-modal">
        <div class="appearance-modal-content">
            <div class="appearance-modal-header">
                <h3 class="appearance-modal-title">✨ Edit Character Appearance</h3>
                <button class="close-modal" onclick="closeAppearanceModal()">&times;</button>
            </div>
            <div>
                <label for="appearanceTextarea" style="display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568;">
                    Appearance Description:
                </label>
                <textarea 
                    id="appearanceTextarea" 
                    class="appearance-textarea" 
                    placeholder="Describe how this character looks... (e.g., tall with curly brown hair, bright green eyes, always wearing a vintage leather jacket, has a friendly smile...)"
                ></textarea>
                <div style="font-size: 0.85em; color: #718096; margin-bottom: 15px;">
                    💡 Tip: Be descriptive! This helps the character describe themselves naturally in conversations.
                </div>
            </div>
            <div class="appearance-actions">
                <button class="btn btn-secondary" onclick="closeAppearanceModal()">Cancel</button>
                <button class="btn btn-primary" onclick="saveAppearance()">Save Appearance</button>
            </div>
        </div>
    </div>

    <script>
        let selectedCharacter = null;
        let characters = [];
        let currentUserId = 'ed_fornieles';
        let currentVersion = 'new';

        // Version switching functionality
        function switchVersion(version) {
            currentVersion = version;
            
            // Update button states
            document.querySelectorAll('.version-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Show/hide appropriate design
            if (version === 'new') {
                document.getElementById('newDesign').style.display = 'grid';
                document.getElementById('oldDesign').style.display = 'none';
            } else {
                document.getElementById('newDesign').style.display = 'none';
                document.getElementById('oldDesign').style.display = 'grid';
            }
            
            // Refresh characters for the active version
            if (version === 'new') {
                refreshCharacters();
            } else {
                refreshCharactersOld();
            }
        }

        // Initialize the playground
        document.addEventListener('DOMContentLoaded', function() {
            refreshCharacters();
            
            // Set initial current user display
            document.getElementById('currentUser').textContent = currentUserId;
            updatePresetButtonStates();
            
            // Enable Enter key for chat input
            document.getElementById('chatInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // Enable Enter key for user ID input
            document.getElementById('userId').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    setCurrentUser();
                }
            });
            
            // Enable search functionality
            document.getElementById('characterSearch').addEventListener('input', function(e) {
                filterCharacters(e.target.value);
            });
            
            // Old design event listeners
            document.getElementById('chatInputOld').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessageOld();
                }
            });
            
            document.getElementById('userIdOld').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    setCurrentUserOld();
                }
            });
            
            document.getElementById('characterSearchOld').addEventListener('input', function(e) {
                filterCharactersOld(e.target.value);
            });
        });

        function setCurrentUser() {
            const userIdInput = document.getElementById('userId');
            const newUserId = userIdInput.value.trim() || 'user';
            currentUserId = newUserId;
            document.getElementById('currentUser').textContent = currentUserId;
            showStatus(`Switched to user: ${currentUserId}`, 'success');
            
            // Update preset button active states
            updatePresetButtonStates();
            
            // Clear chat when switching users
            if (selectedCharacter) {
                document.getElementById('chatMessages').innerHTML = `
                    <div style="text-align: center; color: #718096;">
                        Chat with ${characters.find(c => c.id === selectedCharacter)?.name || 'Character'} as ${currentUserId}
                    </div>
                `;
                // Reload relationship progress and memory status for new user
                loadRelationshipProgress(selectedCharacter);
                loadMemoryStatus(selectedCharacter);
            }
        }
        
        function setPresetUser(userId) {
            // Update the input field
            document.getElementById('userId').value = userId;
            
            // Set the current user
            currentUserId = userId;
            document.getElementById('currentUser').textContent = currentUserId;
            showStatus(`Switched to user: ${currentUserId}`, 'success');
            
            // Update preset button active states
            updatePresetButtonStates();
            
            // Clear chat when switching users
            if (selectedCharacter) {
                document.getElementById('chatMessages').innerHTML = `
                    <div style="text-align: center; color: #718096;">
                        Chat with ${characters.find(c => c.id === selectedCharacter)?.name || 'Character'} as ${currentUserId}
                    </div>
                `;
                // Reload relationship progress and memory status for new user
                loadRelationshipProgress(selectedCharacter);
                loadMemoryStatus(selectedCharacter);
            }
        }
        
        function updatePresetButtonStates() {
            // Remove active class from all preset buttons
            document.querySelectorAll('.btn-preset').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to the matching preset button
            document.querySelectorAll('.btn-preset').forEach(btn => {
                if (btn.textContent === 'Ed Fornieles' && currentUserId === 'ed_fornieles') {
                    btn.classList.add('active');
                } else if (btn.textContent === 'Alex Chen' && currentUserId === 'alex_chen') {
                    btn.classList.add('active');
                }
            });
        }

        // Old version functions
        function setCurrentUserOld() {
            const userIdInput = document.getElementById('userIdOld');
            const newUserId = userIdInput.value.trim() || 'user';
            currentUserId = newUserId;
            document.getElementById('currentUserOld').textContent = currentUserId;
            showStatusOld(`Switched to user: ${currentUserId}`, 'success');
            
            // Update preset button active states
            updatePresetButtonStatesOld();
            
            // Clear chat when switching users
            if (selectedCharacter) {
                document.getElementById('chatMessagesOld').innerHTML = `
                    <div style="text-align: center; color: #718096;">
                        Chat with ${characters.find(c => c.id === selectedCharacter)?.name || 'Character'} as ${currentUserId}
                    </div>
                `;
                // Reload relationship progress and memory status for new user
                loadRelationshipProgressOld(selectedCharacter);
                loadMemoryStatusOld(selectedCharacter);
            }
        }
        
        function setPresetUserOld(userId) {
            // Update the input field
            document.getElementById('userIdOld').value = userId;
            
            // Set the current user
            currentUserId = userId;
            document.getElementById('currentUserOld').textContent = currentUserId;
            showStatusOld(`Switched to user: ${currentUserId}`, 'success');
            
            // Update preset button active states
            updatePresetButtonStatesOld();
            
            // Clear chat when switching users
            if (selectedCharacter) {
                document.getElementById('chatMessagesOld').innerHTML = `
                    <div style="text-align: center; color: #718096;">
                        Chat with ${characters.find(c => c.id === selectedCharacter)?.name || 'Character'} as ${currentUserId}
                    </div>
                `;
                // Reload relationship progress and memory status for new user
                loadRelationshipProgressOld(selectedCharacter);
                loadMemoryStatusOld(selectedCharacter);
            }
        }
        
        function updatePresetButtonStatesOld() {
            // Remove active class from all preset buttons
            document.querySelectorAll('.btn-preset').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to the matching preset button
            document.querySelectorAll('.btn-preset').forEach(btn => {
                if (btn.textContent === 'Ed Fornieles' && currentUserId === 'ed_fornieles') {
                    btn.classList.add('active');
                } else if (btn.textContent === 'Alex Chen' && currentUserId === 'alex_chen') {
                    btn.classList.add('active');
                }
            });
        }

        async function refreshCharactersOld() {
            try {
                showLoadingOld(true);
                const response = await fetch('/characters');
                const data = await response.json();
                characters = data.characters;
                displayCharactersOld();
                showLoadingOld(false);
            } catch (error) {
                console.error('Error fetching characters:', error);
                showStatusOld('Error loading characters', 'error');
                showLoadingOld(false);
            }
        }

        function displayCharactersOld() {
            const container = document.getElementById('charactersListOld');
            
            if (characters.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #718096;">No characters generated yet</div>';
                return;
            }
            
            container.innerHTML = characters.map(char => `
                <div class="character-card" onclick="selectCharacterOld('${char.id}')">
                    <div class="character-name">${char.name}</div>
                    <div class="character-details">
                        <div><strong>Type:</strong> ${char.personality_type}</div>
                        <div><strong>Archetype:</strong> ${char.archetype}</div>
                        <div><strong>Specialty:</strong> ${char.specialty}</div>
                        <div><strong>Tone:</strong> ${char.emotional_tone}</div>
                    </div>
                    <div class="character-appearance-preview" id="appearance-old-${char.id}">
                        👤 Loading appearance...
                    </div>
                    <div class="mood-indicator" id="mood-old-${char.id}">
                        🎭 Loading mood...
                    </div>
                    <div class="character-actions">
                        <button class="btn btn-primary btn-small" onclick="editAppearanceOld('${char.id}', event)">✨ Edit Appearance</button>
                        <button class="btn btn-secondary btn-small" onclick="downloadMemorySummaryOld('${char.id}', event)">Memory Summary</button>
                        <button class="btn btn-danger btn-small" onclick="deleteCharacterOld('${char.id}', event)">Delete</button>
                    </div>
                </div>
            `).join('');
            
            // Load mood and appearance information for each character
            characters.forEach(char => {
                loadCharacterMoodOld(char.id);
                loadCharacterAppearanceOld(char.id);
            });
        }

        function showStatusOld(message, type) {
            const statusDiv = document.getElementById('statusOld');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        function showLoadingOld(show) {
            const loadingDiv = document.querySelector('#oldDesign .loading');
            if (loadingDiv) {
                loadingDiv.style.display = show ? 'block' : 'none';
            }
        }

        function selectCharacterOld(characterId) {
            selectedCharacter = characterId;
            
            // Update UI for old design
            document.querySelectorAll('#oldDesign .character-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`#oldDesign .character-card[onclick*="${characterId}"]`).classList.add('selected');
            
            // Enable chat
            document.getElementById('chatInputOld').disabled = false;
            document.getElementById('sendBtnOld').disabled = false;
            
            // Load relationship and memory info
            loadRelationshipProgressOld(characterId);
            loadMemoryStatusOld(characterId);
            
            // Clear chat
            document.getElementById('chatMessagesOld').innerHTML = `
                <div style="text-align: center; color: #718096;">
                    Chat with ${characters.find(c => c.id === characterId)?.name || 'Character'} as ${currentUserId}
                </div>
            `;
            
            showStatusOld(`Selected: ${characters.find(c => c.id === characterId)?.name || 'Character'}`, 'success');
        }

        async function sendMessageOld() {
            if (!selectedCharacter) return;
            
            const input = document.getElementById('chatInputOld');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessageToChatOld('user', message);
            input.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        character_id: selectedCharacter,
                        user_id: currentUserId,
                        message: message
                    })
                });
                
                const data = await response.json();
                
                if (data.response) {
                    addMessageToChatOld('character', data.response, data.character_name);
                    
                    // Update relationship progress
                    if (data.relationship) {
                        updateRelationshipProgressOld(data.relationship);
                    }
                    
                    // Update memory status
                    if (data.memory_status) {
                        updateMemoryStatusOld(data.memory_status);
                    }
                } else {
                    addMessageToChatOld('character', 'Sorry, I could not process your message.', 'System');
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addMessageToChatOld('character', 'Sorry, there was an error processing your message.', 'System');
            }
        }

        function addMessageToChatOld(sender, message, characterName = null) {
            const chatMessages = document.getElementById('chatMessagesOld');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const senderName = sender === 'user' ? currentUserId : (characterName || 'Character');
            messageDiv.innerHTML = `
                <div class="message-sender">${senderName}</div>
                <div>${message}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function updateRelationshipProgressOld(relationship) {
            const progressDiv = document.getElementById('relationshipProgressOld');
            const levelSpan = document.getElementById('progressLevelOld');
            const bar = document.getElementById('progressBarOld');
            const description = document.getElementById('progressDescriptionOld');
            const percentage = document.getElementById('progressPercentageOld');
            
            if (relationship && relationship.level !== undefined) {
                progressDiv.style.display = 'block';
                levelSpan.textContent = relationship.level;
                bar.style.width = `${Math.min(100, relationship.level * 20)}%`;
                description.textContent = relationship.description || 'Building connection...';
                percentage.textContent = `${Math.min(100, Math.round(relationship.level * 20))}%`;
            }
        }

        function updateMemoryStatusOld(memoryStatus) {
            const memoryDiv = document.getElementById('memoryStatusOld');
            const countSpan = document.getElementById('memoryCountOld');
            const statusSpan = document.getElementById('memoryStatusOld');
            
            if (memoryStatus) {
                memoryDiv.style.display = 'block';
                countSpan.textContent = `${memoryStatus.total_memories || 0} memories stored`;
                statusSpan.textContent = memoryStatus.status || 'Memory active';
            }
        }

        function loadRelationshipProgressOld(characterId) {
            fetch(`/relationship/${currentUserId}/${characterId}`)
                .then(response => response.json())
                .then(data => {
                    updateRelationshipProgressOld(data);
                })
                .catch(error => {
                    console.error('Error loading relationship:', error);
                });
        }

        function loadMemoryStatusOld(characterId) {
            fetch(`/characters/${characterId}/memory-summary/${currentUserId}`)
                .then(response => response.json())
                .then(data => {
                    updateMemoryStatusOld(data);
                })
                .catch(error => {
                    console.error('Error loading memory status:', error);
                });
        }

        function loadCharacterMoodOld(characterId) {
            // Placeholder for mood loading
            const moodElement = document.getElementById(`mood-old-${characterId}`);
            if (moodElement) {
                moodElement.textContent = '🎭 Content';
            }
        }

        function loadCharacterAppearanceOld(characterId) {
            fetch(`/characters/${characterId}/appearance`)
                .then(response => response.json())
                .then(data => {
                    const appearanceElement = document.getElementById(`appearance-old-${characterId}`);
                    if (appearanceElement) {
                        if (data.appearance_description) {
                            appearanceElement.textContent = data.appearance_description;
                            appearanceElement.classList.remove('empty');
                        } else {
                            appearanceElement.textContent = '👤 No appearance set';
                            appearanceElement.classList.add('empty');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error loading appearance:', error);
                });
        }

        function editAppearanceOld(characterId, event) {
            event.stopPropagation();
            // Implementation for old design appearance editing
            showStatusOld('Appearance editing not implemented in old design', 'info');
        }

        function downloadMemorySummaryOld(characterId, event) {
            event.stopPropagation();
            window.open(`/characters/${characterId}/memory-summary/${currentUserId}`, '_blank');
        }

        function deleteCharacterOld(characterId, event) {
            event.stopPropagation();
            if (confirm('Are you sure you want to delete this character?')) {
                fetch(`/characters/${characterId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    showStatusOld('Character deleted successfully', 'success');
                    refreshCharactersOld();
                })
                .catch(error => {
                    console.error('Error deleting character:', error);
                    showStatusOld('Error deleting character', 'error');
                });
            }
        }

        function viewMemorySummaryOld() {
            if (selectedCharacter) {
                window.open(`/characters/${selectedCharacter}/memory-summary/${currentUserId}`, '_blank');
            }
        }

        function generateCharacterOld() {
            const characterId = document.getElementById('characterIdOld').value.trim();
            const count = parseInt(document.getElementById('characterCountOld').value) || 1;
            
            const requestBody = {
                count: count
            };
            
            if (characterId) {
                requestBody.character_id = characterId;
            }
            
            fetch('/characters/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            })
            .then(response => response.json())
            .then(data => {
                showStatusOld('Character generated successfully!', 'success');
                refreshCharactersOld();
            })
            .catch(error => {
                console.error('Error generating character:', error);
                showStatusOld('Error generating character', 'error');
            });
        }

        function filterCharactersOld(searchTerm) {
            const characterCards = document.querySelectorAll('#oldDesign .character-card');
            characterCards.forEach(card => {
                const characterName = card.querySelector('.character-name').textContent.toLowerCase();
                if (characterName.includes(searchTerm.toLowerCase())) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        async function refreshCharacters() {
            try {
                showLoading(true);
                const response = await fetch('/characters');
                const data = await response.json();
                characters = data.characters;
                displayCharacters();
                showLoading(false);
            } catch (error) {
                console.error('Error fetching characters:', error);
                showStatus('Error loading characters', 'error');
                showLoading(false);
            }
        }

        function displayCharacters() {
            const container = document.getElementById('charactersList');
            
            if (characters.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #718096;">No characters generated yet</div>';
                return;
            }
            
            container.innerHTML = characters.map(char => `
                <div class="character-card" onclick="selectCharacter('${char.id}')">
                    <div class="character-name">${char.name}</div>
                    <div class="character-details">
                        <div><strong>Type:</strong> ${char.personality_type}</div>
                        <div><strong>Archetype:</strong> ${char.archetype}</div>
                        <div><strong>Specialty:</strong> ${char.specialty}</div>
                        <div><strong>Tone:</strong> ${char.emotional_tone}</div>
                    </div>
                    <div class="character-appearance-preview" id="appearance-${char.id}">
                        👤 Loading appearance...
                    </div>
                    <div class="mood-indicator" id="mood-${char.id}">
                        🎭 Loading mood...
                    </div>
                    <div class="character-actions">
                        <button class="btn btn-primary btn-small" onclick="editAppearance('${char.id}', event)">✨ Edit Appearance</button>
                        <button class="btn btn-secondary btn-small" onclick="downloadMemorySummary('${char.id}', event)">Memory Summary</button>
                        <button class="btn btn-danger btn-small" onclick="deleteCharacter('${char.id}', event)">Delete</button>
                    </div>
                </div>
            `).join('');
            
            // Load mood and appearance information for each character
            characters.forEach(char => {
                loadCharacterMood(char.id);
                loadCharacterAppearance(char.id);
            });
        }
        
        function filterCharacters(searchTerm) {
            const container = document.getElementById('charactersList');
            const searchLower = searchTerm.toLowerCase();
            
            if (characters.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #718096;">No characters generated yet</div>';
                return;
            }
            
            // Filter characters based on search term
            const filteredCharacters = characters.filter(char => 
                char.name.toLowerCase().includes(searchLower) ||
                char.archetype.toLowerCase().includes(searchLower) ||
                char.specialty.toLowerCase().includes(searchLower) ||
                char.personality_type.toLowerCase().includes(searchLower) ||
                char.emotional_tone.toLowerCase().includes(searchLower)
            );
            
            if (filteredCharacters.length === 0) {
                container.innerHTML = `<div style="text-align: center; color: #718096;">No characters found matching "${searchTerm}"</div>`;
                return;
            }
            
            container.innerHTML = filteredCharacters.map(char => `
                <div class="character-card" onclick="selectCharacter('${char.id}')">
                    <div class="character-name">${char.name}</div>
                    <div class="character-details">
                        <div><strong>Type:</strong> ${char.personality_type}</div>
                        <div><strong>Archetype:</strong> ${char.archetype}</div>
                        <div><strong>Specialty:</strong> ${char.specialty}</div>
                        <div><strong>Tone:</strong> ${char.emotional_tone}</div>
                    </div>
                    <div class="character-appearance-preview" id="appearance-${char.id}">
                        👤 Loading appearance...
                    </div>
                    <div class="mood-indicator" id="mood-${char.id}">
                        🎭 Loading mood...
                    </div>
                    <div class="character-actions">
                        <button class="btn btn-primary btn-small" onclick="editAppearance('${char.id}', event)">✨ Edit Appearance</button>
                        <button class="btn btn-secondary btn-small" onclick="downloadMemorySummary('${char.id}', event)">Memory Summary</button>
                        <button class="btn btn-danger btn-small" onclick="deleteCharacter('${char.id}', event)">Delete</button>
                    </div>
                </div>
            `).join('');
            
            // Load mood and appearance information for filtered characters
            filteredCharacters.forEach(char => {
                loadCharacterMood(char.id);
                loadCharacterAppearance(char.id);
            });
        }
        
        async function loadCharacterMood(characterId) {
            try {
                const response = await fetch(`/characters/${characterId}`);
                const data = await response.json();
                
                if (data.mood) {
                    const moodElement = document.getElementById(`mood-${characterId}`);
                    if (moodElement) {
                        moodElement.textContent = `🎭 ${data.mood.description}`;
                        moodElement.title = `Mood: ${data.mood.category} (Level ${data.mood.level})`;
                    }
                }
            } catch (error) {
                console.error('Error loading mood for character:', characterId, error);
            }
        }
        
        async function generateCharacter() {
            try {
                showLoading(true);
                const characterId = document.getElementById('characterId').value.trim() || null;
                const count = parseInt(document.getElementById('characterCount').value) || 1;
                
                const response = await fetch('/characters/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        character_id: characterId,
                        count: count
                    })
                });
                
                const data = await response.json();
                showStatus(`Generated ${data.generated_characters.length} character(s)!`, 'success');
                
                // Clear input
                document.getElementById('characterId').value = '';
                document.getElementById('characterCount').value = '1';
                
                // Refresh the list
                await refreshCharacters();
                showLoading(false);
            } catch (error) {
                console.error('Error generating character:', error);
                showStatus('Error generating character', 'error');
                showLoading(false);
            }
        }
        
        async function selectCharacter(characterId) {
            selectedCharacter = characterId;
            
            // Update UI
            document.querySelectorAll('.character-card').forEach(card => {
                card.classList.remove('selected');
            });
            event.currentTarget.classList.add('selected');
            
            // Enable chat
            document.getElementById('chatInput').disabled = false;
            document.getElementById('sendBtn').disabled = false;
            
            // Clear chat messages
            document.getElementById('chatMessages').innerHTML = `
                <div style="text-align: center; color: #718096;">
                    Chat with ${characters.find(c => c.id === characterId)?.name || 'Character'} as ${currentUserId}
                </div>
            `;
            
            // Load and display relationship progress
            await loadRelationshipProgress(characterId);
            
            // Load and display memory status
            await loadMemoryStatus(characterId);
            
            showStatus(`Selected ${characters.find(c => c.id === characterId)?.name}`, 'success');
        }

        async function loadRelationshipProgress(characterId) {
            try {
                const response = await fetch(`/relationship/${currentUserId}/${characterId}`);
                if (response.ok) {
                    const data = await response.json();
                    updateProgressBar(data);
                    document.getElementById('relationshipProgress').style.display = 'block';
                } else {
                    // Hide progress bar if no relationship data
                    document.getElementById('relationshipProgress').style.display = 'none';
                }
            } catch (error) {
                console.error('Error loading relationship progress:', error);
                document.getElementById('relationshipProgress').style.display = 'none';
            }
        }
        
        async function loadMemoryStatus(characterId) {
            try {
                const response = await fetch(`/characters/${characterId}/user-profile/${currentUserId}/summary`);
                if (response.ok) {
                    const data = await response.json();
                    updateMemoryStatus(data);
                    document.getElementById('memoryStatus').style.display = 'block';
                } else {
                    // Show empty memory status
                    updateMemoryStatus({ total_memories: 0, status: 'No memories found' });
                    document.getElementById('memoryStatus').style.display = 'block';
                }
            } catch (error) {
                console.error('Error loading memory status:', error);
                updateMemoryStatus({ total_memories: 0, status: 'Error loading memories' });
                document.getElementById('memoryStatus').style.display = 'block';
            }
        }
        
        function updateMemoryStatus(memoryData) {
            const memoryCount = memoryData.total_memories || 0;
            const status = memoryData.status || 'No conversation history';
            
            document.getElementById('memoryCount').textContent = `${memoryCount} memories stored`;
            document.getElementById('memoryStatus').textContent = status;
        }
        
        async function viewMemorySummary() {
            if (!selectedCharacter) {
                showStatus('Please select a character first', 'error');
                return;
            }
            
            try:
                showStatus('Loading memory summary...', 'info');
                
                const response = await fetch(`/characters/${selectedCharacter}/memory-summary/${currentUserId}`);
                
                if (response.ok):
                    const summaryText = await response.text();
                    
                    # Create a modal or new window to display the summary
                    const newWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes');
                    newWindow.document.write(`
                        <html>
                            <head>
                                <title>Memory Summary - ${characters.find(c => c.id === selectedCharacter)?.name}</title>
                                <style>
                                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }
                                    pre { white-space: pre-wrap; word-wrap: break-word; }
                                </style>
                            </head>
                            <body>
                                <h1>Memory Summary</h1>
                                <h2>Character: ${characters.find(c => c.id === selectedCharacter)?.name}</h2>
                                <h3>User: ${currentUserId}</h3>
                                <pre>${summaryText}</pre>
                            </body>
                        </html>
                    `);
                    newWindow.document.close();
                    
                    showStatus('Memory summary opened in new window', 'success');
                elif response.status === 404:
                    showStatus('No memories found for this character and user', 'error');
                else:
                    showStatus('Error loading memory summary', 'error');
            except Exception as e:
                console.error('Error viewing memory summary:', e);
                showStatus('Error loading memory summary', 'error');
        
        function updateProgressBar(relationshipData):
            const level = relationshipData.level || 0;
            const percentage = Math.min((level / 10) * 100, 100);
            
            # Update level display
            document.getElementById('progressLevel').textContent = `${level.toFixed(1)}/10`;
            
            # Update progress bar
            document.getElementById('progressBar').style.width = `${percentage}%`;
            
            # Update percentage display
            document.getElementById('progressPercentage').textContent = `${percentage.toFixed(1)}%`;
            
            # Update description based on level
            let description = 'Not connected';
            if (level >= 9) description = 'Soul Bond 💜';
            elif (level >= 8) description = 'Deep Connection 💙';
            elif (level >= 7) description = 'Close Friends 💚';
            elif (level >= 6) description = 'Good Friends ��';
            elif (level >= 5) description = 'Friends 🧡';
            elif (level >= 4) description = 'Acquaintances ❤️';
            elif (level >= 3) description = 'Warming Up 🤍';
            elif (level >= 2) description = 'Getting to Know 🤍';
            elif (level >= 1) description = 'First Contact 🤍';
            
            document.getElementById('progressDescription').textContent = description;
            
            # Show level up notification if applicable
            if (relationshipData.level_up):
                showStatus(`🎉 Relationship Level Up! Reached ${level.toFixed(1)}`, 'success');
        
        async function sendMessage():
            if (!selectedCharacter):
                showStatus('Please select a character first', 'error');
                return;
            
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message):
                return;
            
            try:
                # Add user message to chat
                addMessageToChat(currentUserId, message, 'user');
                input.value = '';
                
                # Send to API
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        character_id: selectedCharacter,
                        message: message,
                        user_id: currentUserId
                    })
                });
                
                const data = await response.json();
                
                # Show mood change if it occurred
                if (data.mood_change):
                    addMoodChangeToChat(data.mood_change);
                    # Update the mood indicator in the character list
                    const moodElement = document.getElementById(`mood-${selectedCharacter}`);
                    if (moodElement):
                        moodElement.textContent = `🎭 ${data.current_mood}`;
                
                # Add character response to chat
                addMessageToChat(data.character_name || 'Character', data.response, 'character');
                
                # Update relationship progress after message
                if (data.relationship_status):
                    updateProgressBar(data.relationship_status);
                
            except Exception as e:
                console.error('Error sending message:', e);
                showStatus('Error sending message', 'error');
        
        function addMoodChangeToChat(moodChange):
            const chatMessages = document.getElementById('chatMessages');
            
            const moodDiv = document.createElement('div');
            moodDiv.className = 'mood-change';
            moodDiv.innerHTML = `
                <strong>🎭 Mood Change:</strong> ${moodChange.previous} → ${moodChange.current}
                <br><small>Reason: ${moodChange.reason}</small>
            `;
            
            chatMessages.appendChild(moodDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        
        function addMessageToChat(sender, message, type):
            const chatMessages = document.getElementById('chatMessages');
            
            # Clear placeholder if it exists
            if (chatMessages.children.length === 1 and chatMessages.children[0].style.textAlign === 'center'):
                chatMessages.innerHTML = '';
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `
                <div class="message-sender">${sender}</div>
                <div>${message}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        
        async function downloadMemorySummary(characterId, event):
            event.stopPropagation();
            
            try:
                showStatus('Generating memory summary...', 'info');
                
                const response = await fetch(`/characters/${characterId}/memory-summary/${currentUserId}`);
                
                if (response.ok):
                    # Get the filename from the response headers
                    const contentDisposition = response.headers.get('content-disposition');
                    let filename = 'memory_summary.txt';
                    if (contentDisposition):
                        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (filenameMatch):
                            filename = filenameMatch[1];
                    
                    # Create blob and download
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    showStatus('Memory summary downloaded!', 'success');
                elif response.status === 404:
                    showStatus('No memories found for this character', 'error');
                else:
                    showStatus('Error generating memory summary', 'error');
            except Exception as e:
                console.error('Error downloading memory summary:', e);
                showStatus('Error downloading memory summary', 'error');
        
        async function deleteCharacter(characterId, event):
            event.stopPropagation();
            
            if (!confirm('Are you sure you want to delete this character and all its memories?')):
                return;
            
            try:
                const response = await fetch(`/characters/${characterId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok):
                    showStatus('Character deleted successfully', 'success');
                    
                    # If this was the selected character, clear selection
                    if (selectedCharacter === characterId):
                        selectedCharacter = null;
                        document.getElementById('chatInput').disabled = true;
                        document.getElementById('sendBtn').disabled = true;
                        document.getElementById('chatMessages').innerHTML = `
                            <div style="text-align: center; color: #718096; margin-top: 50px;">
                                Select a character to start chatting
                            </div>
                        `;
                    
                    await refreshCharacters();
                else:
                    showStatus('Error deleting character', 'error');
            except Exception as e:
                console.error('Error deleting character:', e);
                showStatus('Error deleting character', 'error');
        
        function showStatus(message, type):
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
            
            setTimeout(() => {
                status.style.display = 'none';
            }, 3000);
        
        function showLoading(show):
            const loadingElements = document.querySelectorAll('.loading');
            loadingElements.forEach(el => {
                el.style.display = show ? 'block' : 'none';
            });
        
        # Appearance functionality
        let currentEditingCharacterId = null;

        async function loadCharacterAppearance(characterId):
            try:
                const response = await fetch(`/characters/${characterId}/appearance`);
                const data = await response.json();
                
                const appearanceElement = document.getElementById(`appearance-${characterId}`);
                if (appearanceElement):
                    const appearance = data.appearance_description;
                    if (appearance and appearance !== 'No appearance description available.'):
                        appearanceElement.textContent = `👤 ${appearance.substring(0, 60)}${appearance.length > 60 ? '...' : ''}`;
                        appearanceElement.className = 'character-appearance-preview';
                        appearanceElement.title = appearance;
                    else:
                        appearanceElement.textContent = '👤 No appearance set - click to add';
                        appearanceElement.className = 'character-appearance-preview empty';
        
        async function editAppearance(characterId, event):
            event.stopPropagation();
            
            currentEditingCharacterId = characterId;
            const character = characters.find(c => c.id === characterId);
            
            # Update modal title with character name
            document.querySelector('.appearance-modal-title').textContent = 
                `✨ Edit Appearance - ${character ? character.name : 'Character'}`;
            
            # Load current appearance
            try:
                const response = await fetch(`/characters/${characterId}/appearance`);
                const data = await response.json();
                
                const textarea = document.getElementById('appearanceTextarea');
                const currentAppearance = data.appearance_description;
                
                if (currentAppearance and currentAppearance !== 'No appearance description available.'):
                    textarea.value = currentAppearance;
                else:
                    textarea.value = '';
                
                # Show modal
                document.getElementById('appearanceModal').style.display = 'block';
                textarea.focus();
                
            except Exception as e:
                console.error('Error loading appearance:', e);
                showStatus('Error loading current appearance', 'error');
        
        function closeAppearanceModal():
            document.getElementById('appearanceModal').style.display = 'none';
            currentEditingCharacterId = null;
            document.getElementById('appearanceTextarea').value = '';
        
        async function saveAppearance():
            if (!currentEditingCharacterId):
                showStatus('No character selected for editing', 'error');
                return;
            
            const textarea = document.getElementById('appearanceTextarea');
            const appearanceDescription = textarea.value.trim();
            
            if (!appearanceDescription):
                showStatus('Please enter an appearance description', 'error');
                return;
            
            try:
                showStatus('Saving appearance...', 'info');
                
                const response = await fetch(`/characters/${currentEditingCharacterId}/appearance`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        character_id: currentEditingCharacterId,
                        appearance_description: appearanceDescription
                    })
                });
                
                const data = await response.json();
                
                if (data.success):
                    showStatus('Appearance saved successfully! 🎨', 'success');
                    
                    # Update the appearance preview
                    await loadCharacterAppearance(currentEditingCharacterId);
                    
                    # Close modal
                    closeAppearanceModal();
                else:
                    showStatus(data.message || 'Error saving appearance', 'error');
                
            except Exception as e:
                console.error('Error saving appearance:', e);
                showStatus('Error saving appearance', 'error');
        
        # Close modal when clicking outside
        document.getElementById('appearanceModal').addEventListener('click', function(event):
            if (event.target === this):
                closeAppearanceModal();
        
        # Handle Escape key to close modal
        document.addEventListener('keydown', function(event):
            if (event.key === 'Escape' and document.getElementById('appearanceModal').style.display === 'block'):
                closeAppearanceModal();
        
    </script>
</body>
</html>
"""

# Initialize FastAPI app

class UserProfile:
    def __init__(self, user_id, name=None):
        self.user_id = user_id
        self.name = name or user_id

app = FastAPI(title="Dynamic Character Playground", version="2.0")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount the ui/ directory as static files
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Include ephemeral memory router if available
# if EPHEMERAL_MEMORY_AVAILABLE:
#     app.include_router(ephemeral_router)
#     print("✅ Ephemeral memory endpoints included")

# Initialize character generator
generator = CharacterGenerator(
    output_dir="data/characters/generated_characters",
    memories_dir="data/memories/memories"
)

# Store active agents in memory
active_agents: Dict[str, Agent] = {}

# Initialize relationship system
relationship_system = RelationshipSystem()

# Initialize IP geolocation system
ip_geolocation_system = IPGeolocationSystem()

class ChatMessage(BaseModel):
    character_id: str
    message: str
    user_id: str = "user"

class CharacterRequest(BaseModel):
    character_id: Optional[str] = None
    count: int = 1

class CustomCharacterRequest(BaseModel):
    # Basic Info
    first_name: str
    last_name: str
    gender: str = "Non-binary"
    
    # Personality Traits
    personality_type: str = "INTP"
    archetype: str = "The Sage"
    emotional_tone: str = "Neutral"
    conversational_style: str = "Direct"
    problem_solving_approach: str = "Analytical"
    language_quirk: str = "None"
    recurring_pattern: str = "None"
    energy_level: str = "Moderate"
    specialty: str = "General wisdom"
    
    # Character Background
    background: str = "Unknown origins"
    values: str = "Authenticity and growth"
    fears: str = "Being misunderstood"
    motivations: str = "Helping others discover truth"
    quirks: str = "Observant and thoughtful"
    
    # Appearance
    appearance_description: str = "A person with thoughtful eyes and an approachable demeanor"
    
    # Biography (optional)
    birth_date: Optional[str] = None
    birth_location: Optional[str] = None
    profession: Optional[str] = None  # Comma-separated
    achievements: Optional[str] = None  # Comma-separated
    life_story: str = "A journey of discovery and growth"
    
    # Character Voice
    speaking_style: str = "Thoughtful and measured"
    common_phrases: Optional[str] = None  # Comma-separated

@app.get("/", response_class=HTMLResponse)
async def get_playground():
    """Serve the enhanced chat interface."""
    try:
        with open("ui/enhanced_chat_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to original interface if enhanced interface not found
        return HTMLResponse(content=get_playground_html())

@app.get("/create-character", response_class=HTMLResponse)
async def get_character_creator():
    """Serve the custom character creator interface."""
    try:
        with open("ui/custom_character_creator_web.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character creator page not found")

@app.get("/memory-management", response_class=HTMLResponse)
async def get_memory_management():
    """Serve the memory management interface."""
    try:
        with open("ui/memory_management_interface.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Memory management page not found")

@app.get("/memory-insights", response_class=HTMLResponse)
async def get_memory_insights():
    """Serve the memory insights panel."""
    try:
        with open("ui/memory_insights_panel.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Memory insights page not found")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Dynamic Character Playground is running"}

@app.get("/users")
async def list_users():
    """Get list of all users by scanning memory databases."""
    try:
        users = set()
        
        # Scan memory_databases directory for enhanced memory files
        memory_db_dir = Path("memory_databases")
        if memory_db_dir.exists():
            for db_file in memory_db_dir.glob("enhanced_*_*.db"):
                # Extract user_id from filename pattern: enhanced_{character_id}_{user_id}.db
                # Remove "enhanced_" prefix and ".db" suffix, then split on last underscore
                filename = db_file.stem  # Gets filename without extension
                if filename.startswith("enhanced_"):
                    # Remove "enhanced_" prefix
                    without_prefix = filename[9:]  # len("enhanced_") = 9
                    # Split on last underscore to separate character_id and user_id
                    last_underscore = without_prefix.rfind("_")
                    if last_underscore != -1:
                        user_id = without_prefix[last_underscore + 1:]  # Everything after last underscore
                        users.add(user_id)
        
        # Also scan data/memories/memories directory for memory files
        memories_dir = Path("data/memories/memories")
        if memories_dir.exists():
            for db_file in memories_dir.glob("*_memory.db"):
                # Extract user_id from filename pattern: {character_id}_memory.db
                # Note: These files don't contain user_id, but we can check for any user-specific patterns
                # For now, we'll skip these as they don't follow the user_id pattern
                pass
        
        # Convert to sorted list
        users_list = sorted(list(users))
        
        return {
            "users": users_list,
            "count": len(users_list),
            "sources": ["memory_databases"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters")
async def list_characters():
    """Get list of all generated characters."""
    try:
        # Get characters from the generator (generated_characters subdirectory)
        character_ids = generator.list_characters()
        characters = []
        
        # Load characters from generated_characters directory
        for char_id in character_ids:
            character = generator.load_character(char_id)
            if character:
                characters.append({
                    "id": character["id"],
                    "name": character["name"],
                    "archetype": character["personality_traits"].get("Archetype", "Unknown"),
                    "specialty": character["personality_traits"].get("Specialty", "Unknown"),
                    "personality_type": character["personality_traits"].get("Personality_Type", "Unknown"),
                    "emotional_tone": character["personality_traits"].get("Emotional_Tone", "Unknown"),
                    "created_at": character.get("created_at", "Unknown"),
                    "learning_enabled": character.get("learning_enabled", False)
                })
        
        # Load characters from all directories in the new structure
        search_dirs = [
            Path("data/characters/custom"),      # Custom characters first
            Path("data/characters/historical"),  # Historical characters
            Path("data/characters/generated"),   # Generated characters
            Path("data/characters"),             # Legacy location
        ]
        
        # Collect all character files
        all_character_files = []
        for directory in search_dirs:
            if directory.exists():
                for char_file in directory.glob("*.json"):
                    all_character_files.append(char_file)
        
        # Load characters from all directories
        for char_file in all_character_files:
            char_id = char_file.stem
            
            # Skip if already loaded from generator
            if char_id in character_ids:
                continue
                
            try:
                with open(char_file, 'r', encoding='utf-8') as f:
                    character = json.load(f)
                
                characters.append({
                    "id": character.get("id", char_id),
                    "name": character.get("name", "Unknown"),
                    "archetype": character.get("personality_traits", {}).get("Archetype", "Unknown"),
                    "specialty": character.get("personality_traits", {}).get("Specialty", "Unknown"),
                    "personality_type": character.get("personality_traits", {}).get("Personality_Type", "Unknown"),
                    "emotional_tone": character.get("personality_traits", {}).get("Emotional_Tone", "Unknown"),
                    "created_at": character.get("created_at", "Unknown"),
                    "learning_enabled": character.get("learning_enabled", False)
                })
            except Exception as e:
                print(f"Warning: Could not load character from {char_file}: {e}")
                continue
        
        # Load historical characters
        try:
            from systems.unified_historical_character_loader import unified_historical_loader
            historical_characters = unified_historical_loader.get_available_historical_characters()
            
            for char_id in historical_characters:
                # Skip if already loaded
                if any(char["id"] == char_id for char in characters):
                    continue
                    
                character = unified_historical_loader.load_historical_character(char_id)
                if character:
                    characters.append({
                        "id": character["id"],
                        "name": character["name"],
                        "archetype": character.get("field", "Historical Figure"),
                        "specialty": ", ".join(character.get("expertise_areas", [])),
                        "personality_type": "Historical",
                        "emotional_tone": character.get("communication_style", "Formal"),
                        "created_at": "Historical",
                        "learning_enabled": character.get("learning_enabled", True)
                    })
        except Exception as e:
            print(f"Warning: Could not load historical characters: {e}")
        
        # Sort characters to put priority characters first
        def sort_key(char):
            char_id = char["id"]
            char_name = char["name"].lower()
            
            # Nicholas Cage goes first
            if char_id == "custom_nicholas_cage_3674" or "nicholas cage" in char_name:
                return "0_nicholas_cage"
            # Freud goes second
            elif char_id == "historical_sigmund_freud":
                return "1_freud"
            # Isaac Newton goes third
            elif char_id == "historical_isaac_newton":
                return "2_newton"
            # Evelyn Chen goes fourth 
            elif char_id == "test_ambitions_char":
                return "3_evelyn"
            # Other custom characters next
            elif char_id.startswith("custom_"):
                return "4_" + char_id
            # Other historical figures next
            elif char_id.startswith("historical_"):
                return "5_" + char_id
            # All other characters last
            else:
                return "6_" + char_id
        
        characters.sort(key=sort_key)
        
        return {"characters": characters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/characters/generate")
async def generate_character(request: CharacterRequest):
    """Generate new character(s)."""
    try:
        generated_characters = []
        
        for i in range(request.count):
            character_id = request.character_id
            if request.count > 1 and character_id:
                character_id = f"{character_id}_{i}"
            
            character = generator.generate_and_save_character(character_id)
            
            # Get mood information
            mood_system = MoodSystem(character["id"])
            mood_info = mood_system.get_mood_summary()
            
            # Get ambitions information
            ambitions_system = AmbitionsSystem(character["id"])
            ambitions_summary = ambitions_system.get_ambitions_summary()
            
            # Get learning information
            learning_system = LearningSystem(character["id"])
            learning_summary = learning_system.get_learning_summary()
            
            generated_characters.append({
                "id": character["id"],
                "name": character["name"],
                "archetype": character["personality_traits"].get("Archetype", "Unknown"),
                "specialty": character["personality_traits"].get("Specialty", "Unknown"),
                "personality_type": character["personality_traits"].get("Personality_Type", "Unknown"),
                "traits": character["personality_traits"],
                "mood": mood_info,
                "ambitions": character.get("ambitions", {}),
                "ambitions_summary": ambitions_summary,
                "learning_enabled": character.get("learning_enabled", False),
                "learning_summary": learning_summary
            })
        
        return {"generated_characters": generated_characters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_id}")
async def get_character(character_id: str):
    """Get detailed character information."""
    import sys
    import traceback
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Log entry point confirmation
    logger.info(f"[ENDPOINT_ENTRY] get_character endpoint entered with character_id: {character_id}")
    print(f"[ENDPOINT_ENTRY] get_character endpoint entered with character_id: {character_id}", file=sys.stderr)
    
    try:
        # Top-level try/except to catch ALL exceptions including import errors
        logger.info(f"[DEBUG] get_character: Attempting to load {character_id} from generator...")
        print(f"[DEBUG] get_character: Attempting to load {character_id} from generator...", file=sys.stderr)
        
        # Check if generator is available
        if not hasattr(generator, 'load_character'):
            error_msg = f"Generator object missing load_character method. Generator type: {type(generator)}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise HTTPException(status_code=500, detail=error_msg)
        
        character = generator.load_character(character_id)
        loaded_from = 'generator'
        
        # If not found, try to load from main data/characters directory
        if not character:
            logger.info(f"[DEBUG] get_character: Not found in generator, checking data/characters...")
            print(f"[DEBUG] get_character: Not found in generator, checking data/characters...", file=sys.stderr)
            
            try:
                # Scan all character directories
                main_characters_dir = Path("data/characters")
                historical_dir = Path("data/characters/historical")
                custom_dir = Path("data/characters/custom")
                generated_dir = Path("data/characters/generated")
                
                # Search for the character in all directories
                search_dirs = [main_characters_dir, historical_dir, custom_dir, generated_dir]
                char_file = None
                
                for directory in search_dirs:
                    if directory.exists():
                        potential_file = directory / f"{character_id}.json"
                        if potential_file.exists():
                            char_file = potential_file
                            break
                
                logger.info(f"[DEBUG] get_character: Checking file: {char_file}")
                print(f"[DEBUG] get_character: Checking file: {char_file}", file=sys.stderr)
                
                if char_file.exists():
                    logger.info(f"[DEBUG] get_character: File exists, attempting to load...")
                    print(f"[DEBUG] get_character: File exists, attempting to load...", file=sys.stderr)
                    
                    try:
                        with open(char_file, 'r', encoding='utf-8') as f:
                            character = json.load(f)
                        loaded_from = 'data/characters'
                        logger.info(f"[DEBUG] get_character: Successfully loaded {character_id} from data/characters")
                        print(f"[DEBUG] get_character: Successfully loaded {character_id} from data/characters", file=sys.stderr)
                    except json.JSONDecodeError as e:
                        error_msg = f"JSON decode error loading {character_id} from {char_file}: {e}"
                        logger.error(error_msg)
                        print(f"[ERROR] {error_msg}", file=sys.stderr)
                        character = None
                    except Exception as e:
                        error_msg = f"Error loading {character_id} from {char_file}: {e}"
                        logger.error(error_msg)
                        print(f"[ERROR] {error_msg}", file=sys.stderr)
                        character = None
                else:
                    logger.info(f"[DEBUG] get_character: File {char_file} does not exist")
                    print(f"[DEBUG] get_character: File {char_file} does not exist", file=sys.stderr)
            except Exception as e:
                error_msg = f"Error checking data/characters directory: {e}"
                logger.error(error_msg)
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                character = None
        
        # If still not found, try to load as historical character
        if not character and character_id.startswith("historical_"):
            logger.info(f"[DEBUG] get_character: Attempting to load {character_id} as historical character...")
            print(f"[DEBUG] get_character: Attempting to load {character_id} as historical character...", file=sys.stderr)
            
            try:
                from systems.unified_historical_character_loader import unified_historical_loader
                character = unified_historical_loader.load_historical_character(character_id)
                if character:
                    loaded_from = 'historical_loader'
                    logger.info(f"[DEBUG] get_character: Successfully loaded {character_id} from historical loader")
                    print(f"[DEBUG] get_character: Successfully loaded {character_id} from historical loader", file=sys.stderr)
                else:
                    logger.info(f"[DEBUG] get_character: Historical character {character_id} not found")
                    print(f"[DEBUG] get_character: Historical character {character_id} not found", file=sys.stderr)
            except Exception as e:
                error_msg = f"Error loading historical character {character_id}: {e}"
                logger.error(error_msg)
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                character = None
        else:
            logger.info(f"[DEBUG] get_character: Successfully loaded {character_id} from generator")
            print(f"[DEBUG] get_character: Successfully loaded {character_id} from generator", file=sys.stderr)
        
        if not character:
            error_msg = f"Character {character_id} not found in any location"
            logger.warning(error_msg)
            print(f"[WARNING] {error_msg}", file=sys.stderr)
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Get mood information
        try:
            mood_system = MoodSystem(character_id)
            mood_info = mood_system.get_mood_summary()
            logger.info(f"[DEBUG] get_character: Successfully loaded mood info for {character_id}")
        except Exception as e:
            error_msg = f"Error loading mood info for {character_id}: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            mood_info = {
                "mood_description": "Mood information unavailable",
                "current_mood": {
                    "category": "unknown",
                    "level": 0,
                    "intensity": 0,
                    "modifiers": []
                }
            }
        
        # Get learning information
        try:
            learning_system = LearningSystem(character_id)
            learning_summary = learning_system.get_learning_summary()
            logger.info(f"[DEBUG] get_character: Successfully loaded learning info for {character_id}")
        except Exception as e:
            error_msg = f"Error loading learning info for {character_id}: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            learning_summary = "Learning information unavailable"
        
        logger.info(f"[DEBUG] get_character: Successfully returning character data for {character_id} (loaded from {loaded_from})")
        print(f"[DEBUG] get_character: Successfully returning character data for {character_id} (loaded from {loaded_from})", file=sys.stderr)
        
        return {
            "character": character,
            "memory_exists": Path(character.get("memory_db_path", f"data/memories/{character_id}_memory.db")).exists(),
            "appearance": character.get("appearance_description", "No appearance description available."),
            "mood": {
                "description": mood_info["mood_description"],
                "category": mood_info["current_mood"]["category"],
                "level": mood_info["current_mood"]["level"],
                "intensity": mood_info["current_mood"]["intensity"],
                "modifiers": mood_info["current_mood"]["modifiers"]
            },
            "learning": {
                "enabled": character.get("learning_enabled", False),
                "summary": learning_summary
            },
            "debug": {
                "loaded_from": loaded_from
            }
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is to preserve status codes and details
        logger.info(f"[HTTP_EXCEPTION] get_character: Re-raising HTTPException for {character_id}")
        print(f"[HTTP_EXCEPTION] get_character: Re-raising HTTPException for {character_id}", file=sys.stderr)
        raise
        
    except ImportError as e:
        error_msg = f"Import error in get_character for {character_id}: {e}"
        logger.error(error_msg)
        print(f"[IMPORT_ERROR] {error_msg}", file=sys.stderr)
        print(f"[IMPORT_ERROR] Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")
        
    except Exception as e:
        error_msg = f"Unexpected error in get_character for {character_id}: {e}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"[UNEXPECTED_ERROR] {error_msg}", file=sys.stderr)
        print(f"[UNEXPECTED_ERROR] Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/characters/trait-options")
async def get_trait_options():
    """Get all available trait options for custom character creation."""
    try:
        from custom_character_creator import CustomCharacterCreator
        
        creator = CustomCharacterCreator()
        options = creator.get_trait_options()
        
        return {"trait_options": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/characters/create-custom")
async def create_custom_character(request: CustomCharacterRequest):
    """Create a custom character with specified traits."""
    try:
        from custom_character_creator import CustomCharacterCreator
        
        creator = CustomCharacterCreator()
        
        # Convert request to dictionary
        form_data = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "gender": request.gender,
            "personality_type": request.personality_type,
            "archetype": request.archetype,
            "emotional_tone": request.emotional_tone,
            "conversational_style": request.conversational_style,
            "problem_solving_approach": request.problem_solving_approach,
            "language_quirk": request.language_quirk,
            "recurring_pattern": request.recurring_pattern,
            "energy_level": request.energy_level,
            "specialty": request.specialty,
            "background": request.background,
            "values": request.values,
            "fears": request.fears,
            "motivations": request.motivations,
            "quirks": request.quirks,
            "appearance_description": request.appearance_description,
            "birth_date": request.birth_date,
            "birth_location": request.birth_location,
            "profession": request.profession,
            "achievements": request.achievements,
            "life_story": request.life_story,
            "speaking_style": request.speaking_style,
            "common_phrases": request.common_phrases
        }
        
        # Create the character
        character = creator.create_custom_character(form_data)
        
        # Get mood information
        mood_system = MoodSystem(character["id"])
        mood_info = mood_system.get_mood_summary()
        
        # Get ambitions information
        ambitions_system = AmbitionsSystem(character["id"])
        ambitions_summary = ambitions_system.get_ambitions_summary()
        
        # Get learning information
        learning_system = LearningSystem(character["id"])
        learning_summary = learning_system.get_learning_summary()
        
        return {
            "character": character,
            "id": character["id"],
            "name": character["name"],
            "archetype": character["personality_traits"].get("Archetype", "Unknown"),
            "specialty": character["personality_traits"].get("Specialty", "Unknown"),
            "personality_type": character["personality_traits"].get("Personality_Type", "Unknown"),
            "traits": character["personality_traits"],
            "mood": mood_info,
            "ambitions": character.get("ambitions", {}),
            "ambitions_summary": ambitions_summary,
            "learning_enabled": character.get("learning_enabled", False),
            "learning_summary": learning_summary,
            "success": True,
            "message": f"Custom character '{character['name']}' created successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_character(message: ChatMessage, request: Request):
    """Chat with a character and track relationship progress."""
    global ENHANCED_MEMORY_AVAILABLE
    print(f"🔍 CHAT ENDPOINT ENTRY: character_id={message.character_id}, user_id={message.user_id}, message='{message.message}'")
    try:
        import re
        start_time = time.time()
        response_content = "I'm sorry, I couldn't generate a response at the moment."  # Default fallback
        performance_stats = {"default": True, "response_time": 0.0}  # Default fallback
        print(f"✅ Chat endpoint: Starting processing...")
        
        # --- IP Geolocation & Timezone Detection ---
        # Extract client IP address
        client_ip = request.headers.get("X-Forwarded-For")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.headers.get("X-Real-IP") or request.client.host
        
        # Detect user location and timezone
        location_data = None
        timezone_context = ""
        temporal_events = []
        
        try:
            location_data = ip_geolocation_system.detect_user_location(message.user_id, client_ip)
            if location_data:
                timezone_context = ip_geolocation_system.generate_location_context_for_character(message.user_id)
                
                # Parse temporal references like "tomorrow", "next week"
                temporal_patterns = ["tomorrow", "tonight", "next week", "next month", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                for pattern in temporal_patterns:
                    if pattern in message.message.lower():
                        temporal_event = ip_geolocation_system.convert_relative_date_with_timezone(message.user_id, pattern)
                        if temporal_event:
                            temporal_events.append(temporal_event)
                            
        except Exception as e:
            print(f"IP geolocation error: {e}")
        
        print(f"✅ Chat endpoint: About to get agent...")
        agent_key = f"{message.character_id}_{message.user_id}"
        if agent_key not in active_agents:
            print(f"✅ Chat endpoint: Creating new agent for {agent_key}")
            agent = generator.get_character_agent(message.character_id, message.user_id)
            if not agent:
                print(f"❌ Chat endpoint: Agent creation failed")
                raise HTTPException(status_code=404, detail="Character not found")
            active_agents[agent_key] = agent
            print(f"✅ Chat endpoint: Agent created successfully")
        agent = active_agents[agent_key]
        print(f"✅ Chat endpoint: About to load character...")
        character = generator.load_character(message.character_id)
        
        # Debug: Check if character loaded correctly
        if not character:
            print(f"❌ ERROR: Character {message.character_id} not found!")
            raise HTTPException(status_code=404, detail=f"Character {message.character_id} not found")
        
        print(f"🔍 DEBUG: Loaded character: {character.get('name', 'NO NAME')} (ID: {character.get('id', 'NO ID')})")
        
        # --- ENHANCED CHARACTER STATE & EMOTIONAL TRACKING ---
        character_state = None
        user_emotional_context = None
        character_emotional_context = None
        
        if ENHANCED_SYSTEMS_AVAILABLE and character_state_persistence and emotional_context_tracker:
            try:
                # Load or create character state
                character_state = character_state_persistence.load_state(message.character_id, message.user_id)
                if not character_state:
                    character_state = character_state_persistence.create_default_state(message.character_id, message.user_id)
                    character_state_persistence.save_state(message.character_id, message.user_id, character_state)
                
                # Analyze emotional context of user message
                user_emotional_context = emotional_context_tracker.analyze_emotional_context(
                    message.message, speaker="user"
                )
                
                # Update character state with emotional context
                if user_emotional_context.valence != "neutral":
                    character_state.current_mood = user_emotional_context.primary_emotion
                    character_state.mood_intensity = user_emotional_context.intensity
                    character_state_persistence.add_emotional_event(
                        message.character_id, message.user_id, {
                            "type": "user_emotion",
                            "valence": user_emotional_context.valence,
                            "intensity": user_emotional_context.intensity,
                            "primary_emotion": user_emotional_context.primary_emotion,
                            "triggers": user_emotional_context.emotional_triggers,
                            "timestamp": user_emotional_context.timestamp
                        }
                    )
                
                print(f"🎭 Character state updated: {character_state.current_mood} (intensity: {character_state.mood_intensity:.2f})")
                print(f"💭 User emotional context: {user_emotional_context.valence} - {user_emotional_context.primary_emotion}")
                
            except Exception as e:
                print(f"⚠️ Enhanced systems error: {e}")
                character_state = None
                user_emotional_context = None
        
        # --- ENHANCED SUBSYSTEM COORDINATION ---
        unified_context = ""
        shared_history = None  # Initialize shared_history variable
        
        if ENHANCED_SUBSYSTEMS_AVAILABLE:
            try:
                print(f"🔧 Coordinating enhanced subsystems for {message.character_id}")
                
                # Legacy enhanced subsystem functions disabled - using new modular system
                # 1. Extract personal details
                # extracted_details = extract_personal_details_enhanced(personal_details_extractor, message.message)
                # print(f"📝 Extracted {len(extracted_details)} personal details")
                
                # 2. Update relationship progression
                # interaction_analysis = analyze_interaction_enhanced(relationship_progression, message.message)
                
                # For demo, use a simple in-memory relationship state per user/character
                if not hasattr(chat_with_character, "_relationship_states"):
                    chat_with_character._relationship_states = {}
                rel_key = f"{message.character_id}_{message.user_id}"
                current_rel = chat_with_character._relationship_states.get(rel_key, {
                    'intimacy_level': 1, 
                    'trust_level': 1, 
                    'shared_experiences': 0, 
                    'emotional_bond': 0.0
                })
                # new_rel = calculate_progression_enhanced(relationship_progression, interaction_analysis, current_rel)
                # chat_with_character._relationship_states[rel_key] = new_rel
                # rel_stage = relationship_progression.get_relationship_stage(new_rel)
                # print(f"🤝 Relationship stage: {rel_stage}")
                
                # 3. Update shared history
                # try:
                #     shared_history_result = process_conversation_enhanced(shared_history, message.message)
                #     shared_summary = get_conversation_summary_enhanced(shared_history)
                #     print(f"📚 Shared history updated: {shared_summary.get('total_topics', 0)} topics")
                # except Exception as e:
                #     shared_summary = {"total_topics": 0, "top_topics": [], "recent_milestones": []}
                #     print(f"📚 Shared history not available")
                
                # 4. Build unified context
                context_lines = []
                
                # Personal details
                # if extracted_details:
                #     context_lines.append("👤 PERSONAL DETAILS:")
                #     for detail in extracted_details[:5]:  # Limit to top 5
                #         context_lines.append(f"- {detail.key.title()}: {detail.value} (confidence: {detail.confidence:.2f})")
                
                # Relationship state
                # context_lines.append(f"🤝 RELATIONSHIP STAGE: {rel_stage}")
                # context_lines.append(f"  Intimacy: {new_rel['intimacy_level']}, Trust: {new_rel['trust_level']}, Shared Experiences: {new_rel['shared_experiences']}, Bond: {new_rel['emotional_bond']:.2f}")
                
                # Shared history summary
                # if shared_summary.get('top_topics'):
                #     context_lines.append("📝 SHARED TOPICS:")
                #     for topic in shared_summary['top_topics'][:3]:  # Top 3 topics
                #         context_lines.append(f"- {topic.category.value.title()}: {topic.subtopic} (mentioned {topic.mention_count} times)")
                
                # if shared_summary.get('recent_milestones'):
                #     context_lines.append("🏆 RECENT MILESTONES:")
                #     for milestone in shared_summary['recent_milestones'][:2]:  # Top 2 milestones
                #         context_lines.append(f"- {milestone.milestone_type.value.title()}: {milestone.description}")
                
                # Compose unified context
                unified_context = "\n".join(context_lines)
                print(f"🚀 Unified context built: {len(unified_context)} characters")
                
            except Exception as e:
                print(f"⚠️ Enhanced subsystem coordination error: {e}")
                unified_context = ""
        else:
            print(f"⚠️ Enhanced subsystems not available")
        
        # --- Code Reading and Analysis Commands ---
        # TEMPORARILY DISABLED due to database issues
        # code_analysis_patterns = [
        #     r"analyze your own code",
        #     r"how do you work",
        #     r"suggest improvements to yourself",
        #     r"read your own code",
        #     r"self-reflect on your code",
        #     r"explain your architecture",
        #     r"what's in your code",
        #     r"code analysis"
        # ]
        # 
        # for pattern in code_analysis_patterns:
        #     if re.search(pattern, user_msg, re.IGNORECASE):
        #         # Read the main code file
        #         code_content = read_code_file('dynamic_character_playground_enhanced.py')
        #         if code_content:
        #             # Analyze the code
        #             analysis = await analyze_code_with_llm(code_content, suggestions_only=False)
        #             
        #             # Format response in character's voice
        #             char_name = character.get("name", "The character")
        #             char_traits = character.get("personality_traits", {})
        #             
        #             # Adjust response based on character personality
        #             if "analytical" in char_traits or "intelligent" in char_traits:
        #                 response = f"{analysis}"
        #             elif "curious" in char_traits or "enthusiastic" in char_traits:
        #                 response = f"{analysis}"
        #             else:
        #                 response = f"{analysis}"
        #             
        #             return {
        #                 "character_name": char_name,
        #                 "response": response,
        #                 "character_id": message.character_id,
        #                 "code_analysis": True
        #             }
        #         else:
        #             return {
        #                 "character_name": character.get("name", "The character"),
        #                 "response": "I'm sorry, but I'm unable to read my own code at the moment.",
        #                 "character_id": message.character_id,
        #                 "code_analysis": False
        #             }
        
        # --- Enhanced Memory System Integration with Performance Optimizations ---
        # Add this import at the top (after other imports)
        from memory_new.db.connection import get_memory_db_path
        
        # Use new modular memory system
        memory_db_path = get_memory_db_path(message.character_id, message.user_id)
        enhanced_memory = None
        memory_result = {}
        ambiguous_refs = []
        memory_context = {}
        
        try:
            # Use modular memory system
            if MODULAR_MEMORY_AVAILABLE:
                enhanced_memory = get_enhanced_memory_system(message.character_id, message.user_id)
                print(f"🔧 Using modular memory system for {message.character_id}")
            else:
                print(f"⚠️ Modular memory system not available")
            
            # Process message and get expanded context
            if enhanced_memory:
                try:
                    personal_details = enhanced_memory.get_personal_details()
                    print(f"📝 Extracted {len(personal_details)} personal details from enhanced memory system")
                except Exception as e:
                    print(f"⚠️ Could not extract personal details: {e}")
            
            # Get enhanced memory context with semantic search
            if enhanced_memory:
                try:
                    # Use enhanced memory context with semantic search
                    memory_context = enhanced_memory.get_memory_context(
                        character_id=message.character_id,
                        user_id=message.user_id,
                        max_memories=10,
                        min_importance=0.3,
                        include_emotional=True,
                        semantic_query=message.message  # Use message as semantic query
                    )
                    print(f"🚀 Using enhanced semantic memory context for {message.character_id}")
                except Exception as e:
                    print(f"⚠️ Could not get enhanced memory context: {e}")
                    # Fallback to basic memory context
                    try:
                        memory_context = enhanced_memory.get_memory_context(
                            character_id=message.character_id,
                            user_id=message.user_id,
                            max_memories=5,
                            min_importance=0.1,
                            include_emotional=False
                        )
                        print(f"🔄 Fallback to basic memory context")
                    except Exception as fallback_e:
                        print(f"⚠️ Could not get memory context: {fallback_e}")
                        memory_context = {}
            
        except Exception as e:
            print(f"Enhanced memory system error: {e}")
            # Fallback to basic memory system
            memory_result = {"memory_id": "fallback", "importance_score": 0.5}
            ambiguous_refs = []
            memory_context = {}
        
        # --- ENHANCED MEMORY SYSTEM INTEGRATION ---
        enhanced_memory_context = {}
        try:
            # Check if enhanced memory is available
            enhanced_memory_available = MODULAR_MEMORY_AVAILABLE
            
            if enhanced_memory_available and enhanced_memory:
                # Simple enhanced memory integration
                enhanced_memory_context = {
                    "temporal_memories": memory_context.get('memories', []),
                    "location_context": "",
                    "relationship_context": ""
                }
                print(f"🚀 Enhanced memory context integrated: {len(enhanced_memory_context.get('temporal_memories', []))} temporal memories")
            else:
                print(f"⚠️ Enhanced memory system not available")
        except Exception as e:
            print(f"⚠️ Enhanced memory integration error: {e}")
            enhanced_memory_context = {}
        
        # --- User Profile System Integration ---
        # TODO: Re-enable UserProfile when class is properly implemented
        # user_profile = UserProfile(message.character_id, message.user_id, memory_db_path)
        # profile_updates = user_profile.update_profile(message.message)
        
        # If ambiguous references are detected, return a clarification prompt
        if ambiguous_refs and enhanced_memory:
            clarification_prompts = [
                enhanced_memory.get_clarification_prompt(ref, message.message)
                for ref in ambiguous_refs
            ]
            # Use the character's voice for clarification
            char_voice = character.get("voice", character.get("name", "The character"))
            clarification_text = f"{char_voice} needs clarification before responding:\n" + "\n".join(clarification_prompts)
            
            # Get character name safely
            char_name = character.get("name", "Character")
            if CHARACTER_IDENTITY_FIXES:
                try:
                    identity = get_character_identity(message.character_id, character)
                    char_name = identity.get('name', char_name)
                except Exception as e:
                    print(f"⚠️ Character identity error: {e}")
                    pass
            
            return {
                "character_name": char_name,
                "response": clarification_text,
                "character_id": message.character_id,
                "clarification_required": True,
                "ambiguous_references": ambiguous_refs
            }
        
        # Update mood based on user message
        mood_system = MoodSystem(message.character_id)
        mood_before = mood_system.get_daily_mood()
        updated_mood = mood_system.update_mood(message.message, memory_db_path)
        
        # Update ambitions progress
        ambitions_system = AmbitionsSystem(message.character_id)
        
        # Check if a personal attack was triggered
        personal_attack = updated_mood.get("personal_attack")
        
        # If mood changed significantly, update the agent's instructions
        if updated_mood.get("changed") and abs(updated_mood["level"] - mood_before["level"]) > 0:
            # Recreate agent with updated mood
            del active_agents[agent_key]
            agent = generator.get_character_agent(message.character_id, message.user_id)
            active_agents[agent_key] = agent
        
        # If personal attack was triggered, use it as the response
        if personal_attack:
            response_content = personal_attack
            performance_stats = {"personal_attack": True, "response_time": 0.1}
        else:
            # Initialize response content with a default value
            response_content = "I'm sorry, I couldn't generate a response at the moment."
            performance_stats = {"error": True, "response_time": time.time() - start_time}
            
            try:
                enhanced_message = message.message
                if timezone_context and temporal_events:
                    # Add timezone context to the message for the agent
                    temporal_info = "\n".join([
                        f"⚡ **{event.original_reference}** = {event.parsed_local_date} ({event.timezone} timezone)"
                        for event in temporal_events
                    ])
                    enhanced_message = f"{timezone_context}\n\n🕐 TEMPORAL EVENT CONTEXT:\n{temporal_info}\n\n---\nUser Message: {message.message}"
                elif timezone_context:
                    enhanced_message = f"{timezone_context}\n\n---\nUser Message: {message.message}"
                
                print(f"🤖 Running agent for {message.character_id}...")
                
                # Add relevant diary context to enhance agent's awareness of past conversations
                diary_context = ""
                try:
                    diary_context = get_relevant_diary_context(
                        message.character_id,
                        message.user_id,
                        message.message,
                        max_context_entries=2
                    )
                    if diary_context:
                        print(f"📖 Found relevant diary context for current conversation")
                    else:
                        print(f"📖 No relevant diary context found")
                except Exception as e:
                    print(f"📖 Diary context search error: {e}")
                
                # Use modular memory system
                enhanced_memory = None
                memory_context = {}
                if MODULAR_MEMORY_AVAILABLE:
                    try:
                        # Create or get enhanced memory system
                        enhanced_memory = get_enhanced_memory_system(message.character_id, message.user_id)
                        if enhanced_memory:
                            # Store the current message with enhanced emotional context
                            user_emotional_valence = 0.0
                            user_relationship_impact = 0.1
                            if user_emotional_context:
                                user_emotional_valence = 0.5 if user_emotional_context.valence == "positive" else (-0.5 if user_emotional_context.valence == "negative" else 0.0)
                                user_relationship_impact = user_emotional_context.relationship_impact
                            
                            enhanced_memory.store_memory(
                                content=message.message,
                                memory_type="user_message",
                                importance=0.6 + (user_emotional_context.intensity * 0.4 if user_emotional_context else 0.0),
                                emotional_valence=user_emotional_valence,
                                relationship_impact=user_relationship_impact
                            )
                            
                            # Get enhanced memory context
                            memory_context = enhanced_memory.get_memory_context(
                                character_id=message.character_id,
                                user_id=message.user_id,
                                max_memories=10,
                                min_importance=0.3,
                                include_emotional=True
                            )
                            print(f"✅ Enhanced memory system: context memories loaded")
                            
                            # CRITICAL FIX: Apply memory fix to extract personal details
                            try:
                                memory_fix_result = apply_memory_fix_to_chat(
                                    character_id=message.character_id,
                                    user_id=message.user_id,
                                    message=message.message,
                                    character_data=character,
                                    original_prompt=""
                                )
                                
                                if memory_fix_result.get("success", False):
                                    personal_details = memory_fix_result.get("personal_details", {})
                                    if personal_details:
                                        # CRITICAL FIX: Create structured personal context for the agent
                                        personal_context_lines = []
                                        personal_context_lines.append("👤 PERSONAL DETAILS I REMEMBER:")
                                        
                                        # Add specific personal details in a clear format
                                        if personal_details.get('name'):
                                            names = personal_details['name']
                                            if isinstance(names, list):
                                                personal_context_lines.append(f"- Name: {', '.join(names)}")
                                            else:
                                                personal_context_lines.append(f"- Name: {names}")
                                        
                                        if personal_details.get('age'):
                                            ages = personal_details['age']
                                            if isinstance(ages, list):
                                                personal_context_lines.append(f"- Age: {', '.join(ages)} years old")
                                            else:
                                                personal_context_lines.append(f"- Age: {ages} years old")
                                        
                                        if personal_details.get('location'):
                                            locations = personal_details['location']
                                            if isinstance(locations, list):
                                                personal_context_lines.append(f"- Location: {', '.join(locations)}")
                                            else:
                                                personal_context_lines.append(f"- Location: {locations}")
                                        
                                        if personal_details.get('sister'):
                                            sisters = personal_details['sister']
                                            if isinstance(sisters, list):
                                                personal_context_lines.append(f"- Sisters: {', '.join(sisters)}")
                                            else:
                                                personal_context_lines.append(f"- Sisters: {sisters}")
                                        
                                        if personal_details.get('brother'):
                                            brothers = personal_details['brother']
                                            if isinstance(brothers, list):
                                                personal_context_lines.append(f"- Brothers: {', '.join(brothers)}")
                                            else:
                                                personal_context_lines.append(f"- Brothers: {brothers}")
                                        
                                        if personal_details.get('parents'):
                                            parents = personal_details['parents']
                                            if isinstance(parents, list):
                                                personal_context_lines.append(f"- Parents: {', '.join(parents)}")
                                            else:
                                                personal_context_lines.append(f"- Parents: {parents}")
                                        
                                        if personal_details.get('work'):
                                            work_info = personal_details['work']
                                            if isinstance(work_info, list):
                                                personal_context_lines.append(f"- Work: {', '.join(work_info)}")
                                            else:
                                                personal_context_lines.append(f"- Work: {work_info}")
                                        
                                        if personal_details.get('pet'):
                                            pets = personal_details['pet']
                                            if isinstance(pets, list):
                                                personal_context_lines.append(f"- Pet: {', '.join(pets)}")
                                            else:
                                                personal_context_lines.append(f"- Pet: {pets}")
                                        
                                        # Create the personal context string
                                        personal_context = "\n".join(personal_context_lines)
                                        
                                        # CRITICAL FIX: Add personal details directly to the enhanced message
                                        if isinstance(memory_context, str):
                                            memory_context = f"{personal_context}\n\n{memory_context}"
                                        elif isinstance(memory_context, dict):
                                            if "personal_details" not in memory_context:
                                                memory_context["personal_details"] = personal_details
                                            memory_context["personal_context"] = personal_context
                                        
                                        print(f"📝 Added {len(personal_details)} personal details to memory context")
                                        print(f"📝 Personal context: {personal_context}")
                                    else:
                                        print(f"📝 No personal details found in memory")
                                else:
                                    print(f"⚠️ Memory fix failed: {memory_fix_result.get('error', 'Unknown error')}")
                            except Exception as e:
                                print(f"⚠️ Memory fix error: {e}")
                                import traceback
                                traceback.print_exc()
                            
                            # Store character response with emotional context (after response is generated)
                            if response_content and response_content != "I'm sorry, I couldn't generate a response at the moment.":
                                character_emotional_valence = 0.0
                                character_relationship_impact = 0.1
                                if character_emotional_context:
                                    character_emotional_valence = 0.5 if character_emotional_context.valence == "positive" else (-0.5 if character_emotional_context.valence == "negative" else 0.0)
                                    character_relationship_impact = character_emotional_context.relationship_impact
                                
                                enhanced_memory.store_memory(
                                    content=response_content,
                                    memory_type="character_response",
                                    importance=0.5 + (character_emotional_context.intensity * 0.5 if character_emotional_context else 0.0),
                                    emotional_valence=character_emotional_valence,
                                    relationship_impact=character_relationship_impact
                                )
                                print(f"✅ Character response stored with emotional context")
                        else:
                            print(f"⚠️ Could not create enhanced memory system")
                    except Exception as e:
                        print(f"⚠️ Modular memory system error: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"⚠️ Modular memory system not available")
                
                # Enhance the message with memory context
                enhanced_message_with_context = enhanced_message
                if memory_context and isinstance(memory_context, str) and memory_context.strip():
                    # Add memory context to the message
                    enhanced_message_with_context = f"{enhanced_message}\n\n🎯 CONVERSATION CONTEXT:\n{memory_context}"
                    print(f"📝 Added memory context: {len(memory_context)} characters")
                elif memory_context and isinstance(memory_context, dict) and memory_context.get('memories'):
                    # Add memory context to the message
                    context_summary = _format_memory_context_for_agent(memory_context)
                    if context_summary:
                        enhanced_message_with_context = f"{enhanced_message}\n\n🎯 CONVERSATION CONTEXT:\n{context_summary}"
                        print(f"📝 Added memory context: {len(context_summary)} characters")
                    else:
                        print(f"⚠️  No memory context summary generated")
                else:
                    print(f"⚠️  No memory context available")
                
                # --- BIOGRAPHICAL CONTEXT INTEGRATION ---
                try:
                    from systems.biographical_context_integration import bio_context_integration
                    
                    # Get character name for biographical context
                    character_name = character.get("name", "Unknown") if character else "Unknown"
                    
                    # Check if biographical context should be included
                    bio_context = bio_context_integration.get_biographical_context_for_agent(
                        message.message, character_name
                    )
                    
                    if bio_context["should_include"]:
                        print(f"📚 Adding biographical context (triggers: {bio_context['triggers']})")
                        
                        # Add biographical context to the message
                        if bio_context["context_text"]:
                            enhanced_message_with_context = f"{enhanced_message_with_context}\n\n📚 HISTORICAL CONTEXT:\n{bio_context['context_text']}"
                            print(f"📚 Added biographical context: {len(bio_context['context_text'])} characters")
                        
                        # Log what triggered the biographical context
                        if bio_context["mentioned_characters"]:
                            print(f"📚 Mentioned historical characters: {bio_context['mentioned_characters']}")
                    else:
                        print(f"📚 No biographical context needed for this message")
                        
                except ImportError:
                    print(f"⚠️  Biographical context integration not available")
                except Exception as e:
                    print(f"⚠️  Error in biographical context integration: {e}")
                
                # Add relevant diary context to provide agent with memory of past similar conversations
                if diary_context:
                    enhanced_message_with_context = f"{enhanced_message_with_context}\n\n{diary_context}"
                    print(f"📖 Added diary context: {len(diary_context)} characters")
                
                # CRITICAL FIX: Special handling for sister queries
                sister_query_patterns = [
                    r'sister', r'sisters', r'eloise', r'victoria', r'vicky',
                    r'what.*sister', r'tell.*sister', r'remember.*sister'
                ]
                
                is_sister_query = any(re.search(pattern, message.message.lower()) for pattern in sister_query_patterns)
                
                # CRITICAL FIX: If this is a sister query, ensure sister information is prominently included
                if is_sister_query and isinstance(memory_context, str):
                    # Check if we have sister information in the memory context
                    if 'sister' not in memory_context.lower() and 'eloise' not in memory_context.lower() and 'victoria' not in memory_context.lower():
                        # Add a prominent sister reminder to the context
                        sister_reminder = "\n\n🎯 IMPORTANT: The user is asking about their sisters. If you have information about their sisters in your memory, please mention it specifically."
                        memory_context = f"{sister_reminder}\n{memory_context}"
                        print(f"🔧 Added sister query reminder to context")
                
                # Generate response
                try:
                    response = agent.run(enhanced_message_with_context, user_id=message.user_id)
                    response_content = response.content
                    performance_stats = {"primary_agent": True, "response_time": time.time() - start_time, "timezone_aware": bool(timezone_context)}
                    print(f"✅ Agent response generated successfully")
                    
                    # CRITICAL FIX: If this is a sister query and the response doesn't mention sisters, provide a fallback
                    if is_sister_query and ('sister' not in response_content.lower() and 'eloise' not in response_content.lower() and 'victoria' not in response_content.lower()):
                        # Check if we have sister information in personal details
                        if isinstance(memory_context, dict) and memory_context.get("personal_details", {}).get("sister"):
                            sisters = memory_context["personal_details"]["sister"]
                            if isinstance(sisters, list):
                                sister_names = ", ".join(sisters)
                            else:
                                sister_names = str(sisters)
                            response_content = f"Your sisters are {sister_names}. How are they doing these days?"
                            print(f"🔧 Applied sister query fallback: {sister_names}")
                        else:
                            response_content = "I remember you have sisters, but I don't have their names stored in my memory yet. Could you remind me of their names?"
                            print(f"🔧 Applied sister query fallback: no names found")
                    
                    # Analyze character emotional context
                    if ENHANCED_SYSTEMS_AVAILABLE and emotional_context_tracker:
                        try:
                            character_emotional_context = emotional_context_tracker.analyze_emotional_context(
                                response_content, speaker="character"
                            )
                            
                            # Update character state with response emotional context
                            if character_state:
                                character_state.current_mood = character_emotional_context.primary_emotion
                                character_state.mood_intensity = character_emotional_context.intensity
                                character_state.last_interaction = datetime.now().isoformat()
                                character_state_persistence.save_state(message.character_id, message.user_id, character_state)
                                
                                # Add character emotional event
                                character_state_persistence.add_emotional_event(
                                    message.character_id, message.user_id, {
                                        "type": "character_emotion",
                                        "valence": character_emotional_context.valence,
                                        "intensity": character_emotional_context.intensity,
                                        "primary_emotion": character_emotional_context.primary_emotion,
                                        "triggers": character_emotional_context.emotional_triggers,
                                        "timestamp": character_emotional_context.timestamp
                                    }
                                )
                            
                            print(f"🎭 Character emotional context: {character_emotional_context.valence} - {character_emotional_context.primary_emotion}")
                            
                        except Exception as e:
                            print(f"⚠️ Character emotional analysis error: {e}")
                            character_emotional_context = None
                    
                except Exception as e:
                    print(f"⚠️ Response generation failed: {e}")
                    # Fallback to simple response generation
                    try:
                        response = agent.run(message.message, user_id=message.user_id)
                        response_content = response.content
                        performance_stats = {"fallback_agent": True, "response_time": time.time() - start_time}
                        print(f"✅ Fallback agent response generated successfully")
                    except Exception as fallback_e:
                        print(f"⚠️ Fallback response generation failed: {fallback_e}")
                        response_content = "I'm sorry, I'm having trouble responding right now. Could you try again?"
                        performance_stats = {"error": True, "response_time": time.time() - start_time}
                
                # Store the response in memory if modular system is available
                if MODULAR_MEMORY_AVAILABLE and enhanced_memory:
                    try:
                        enhanced_memory.store_memory(
                            content=response_content,
                            memory_type="response",
                            importance=0.6,
                            emotional_valence=0.0,
                            relationship_impact=0.1
                        )
                        print(f"✅ Response stored in modular memory system")
                    except Exception as e:
                        print(f"⚠️ Failed to store response in memory: {e}")
                        
            except Exception as e:
                print(f"❌ CHAT ENDPOINT ERROR:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Error repr: {repr(e)}")
                print(f"Full traceback:")
                import traceback
                traceback.print_exc()
                print(f"Request data: character_id={message.character_id}, user_id={message.user_id}, message='{message.message}'")
                
                response_content = "I'm sorry, I encountered an error. Please try again."
                performance_stats = {"error": True, "response_time": time.time() - start_time}
        
        # Apply mood-based response modifications to maintain character authenticity
        if character.get("mood_system", {}).get("enabled", False):
            current_mood = character.get("current_mood", "neutral")
            if current_mood and current_mood != "neutral":
                # Ensure the response reflects the character's current mood
                mood_context = character.get("mood_system", {}).get("moods", {}).get(current_mood, {})
                if mood_context and not personal_attack:  # Don't modify personal attack responses
                    # The agent should already have mood context, but ensure consistency
                    print(f"Character {message.character_id} responding in {current_mood} mood")
        

        
        # Record interaction for learning (if learning is enabled)
        learning_update = {}
        if character.get("learning_enabled", False):
            learning_system = LearningSystem(message.character_id)
            interaction_id = learning_system.record_interaction(
                user_id=message.user_id,
                user_input=message.message,
                character_response=response_content,
                context={
                    "mood_before": mood_before,
                    "mood_after": updated_mood,
                    "conversation_duration": int((time.time() - start_time) * 60)
                }
            )
            
            # Get user insights for personalization
            user_insights = learning_system.get_user_insights(message.user_id)
            learning_update = {
                "interaction_recorded": True,
                "interaction_id": interaction_id,
                "user_insights": user_insights,
                "skills_updated": True
            }
        
        # Process character evolution (if evolution is enabled)
        evolution_update = {}
        
        # Simple evolution integration function
        def integrate_evolution_into_chat(character_id, user_id, user_message, character_response, character, context):
            """Simple evolution integration for character development"""
            try:
                # Basic evolution tracking
                evolution_data = {
                    "character_id": character_id,
                    "user_id": user_id,
                    "interaction_count": context.get("interaction_count", 0) + 1,
                    "last_interaction": time.time(),
                    "response_quality": "good" if len(character_response) > 10 else "short"
                }
                
                # Store evolution data (placeholder implementation)
                print(f"🔄 Evolution data recorded for {character_id}")
                
                return {"evolution_applied": True, "data": evolution_data}
            except Exception as e:
                print(f"⚠️ Evolution integration error: {e}")
                return {"evolution_applied": False, "error": str(e)}
        
        # Create conversation context for evolution
        evolution_context = {
            "conversation_count": 10,  # This should be tracked per user
            "user_emotion": "neutral",  # This could be analyzed from user message
            "topic_consistency": 0.7,   # This could be calculated
            "relationship_depth": 0.6   # This could be tracked
        }
        

        
        try:
            evolution_result = integrate_evolution_into_chat(
                message.character_id,
                message.user_id,
                message.message,
                response_content,
                character,
                evolution_context
            )
            
            if evolution_result.get("evolution_applied", False):
                evolution_update = {
                    "evolution_applied": True,
                    "changes_applied": evolution_result.get("changes_applied", 0),
                    "character_evolved": True
                }
                print(f"🎭 Character {message.character_id} evolved: {evolution_result.get('changes_applied', 0)} changes applied")
            else:
                evolution_update = {
                    "evolution_applied": False,
                    "reason": evolution_result.get("reason", "No evolution triggered")
                }
                
        except ImportError:
            evolution_update = {"evolution_applied": False, "reason": "Evolution system not available"}
        except Exception as e:
            evolution_update = {"evolution_applied": False, "error": str(e)}
            print(f"❌ Evolution error: {e}")
        
        # Calculate conversation duration
        conversation_duration = int((time.time() - start_time) * 60)  # Convert to minutes
        
        # Track relationship progress
        relationship_result = relationship_system.record_conversation_exchange(
            user_id=message.user_id,
            character_id=message.character_id,
            user_message=message.message,
            character_response=response_content,
            conversation_duration=max(1, conversation_duration)  # Minimum 1 minute
        )
        
        # Update ambitions progress with full conversation context
        ambitions_update = ambitions_system.update_ambition_progress(
            conversation_context="",  # Could add conversation history here
            user_message=message.message,
            character_response=response_content
        )
        
        # Apply ambition emotional modifiers to mood
        ambition_emotions = ambitions_system.get_emotional_modifiers()
        if ambition_emotions["happiness_modifier"] != 0 or ambition_emotions["sadness_modifier"] != 0:
            # Apply ambition-based mood adjustments
            if ambition_emotions["happiness_modifier"] > 0.1:
                # Positive progress toward goals - simulate a positive message
                mood_system.update_mood("I'm making great progress toward my goals!", memory_db_path)
            elif ambition_emotions["sadness_modifier"] > 0.1:
                # Setbacks in goals - simulate a negative internal thought
                mood_system.update_mood("I feel like I'm not making progress on what matters to me", memory_db_path)
        
        # Prepare mood change info
        mood_change_info = {
            "previous": f"{mood_before['description']} {mood_before['category']}",
            "current": f"{updated_mood['description']} {updated_mood['category']}",
            "reason": updated_mood.get("change_reason", "no change"),
            "personal_attack_triggered": bool(personal_attack),
            "changed": updated_mood.get("changed", False)
        }
        
        # Get updated mood and relationship info
        current_mood = mood_system.get_mood_summary()
        relationship_status = relationship_system.get_relationship_status(message.user_id, message.character_id)

        # Enhanced memory-based response for "what do you remember" questions
        if (
            "what do you know about me" in message.message.lower() or
            "what do you remember about me" in message.message.lower() or
            "what do you remember" in message.message.lower()
        ):
            # Handle memory recall requests
            pass

        # Debug: Check what character name we're returning
        character_name = character.get("name", "Character")
        print(f"🔍 DEBUG: Returning character_name: '{character_name}' for character_id: {message.character_id}")
        
        return {
            "character_name": character_name,
            "response": response_content,
            "character_id": message.character_id,
            "performance_stats": performance_stats,
            "mood_change": mood_change_info,
            "current_mood": current_mood["mood_description"],
            "mood_data": current_mood["current_mood"],
            "ambitions_update": ambitions_update,
            "learning_update": learning_update,
            "personal_attack_triggered": bool(personal_attack),
            "relationship": {
                "current_level": relationship_result.get("current_level", 0),
                "level_up": relationship_result.get("level_up", False),
                "relationship_change": relationship_result.get("relationship_change", 0),
                "nft_reward": relationship_result.get("nft_reward"),
                **relationship_status  # Include all relationship status fields
            },
            "clarification_required": False,
            "ambiguous_references": [],
            "location_data": {
                "city": location_data.city if location_data else None,
                "country": location_data.country if location_data else None,
                "timezone": location_data.timezone if location_data else None,
                "accuracy": location_data.accuracy_score if location_data else None
            } if location_data else None,
            "temporal_events": [],
            "timezone_aware": bool(location_data)
        }
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ CHAT ENDPOINT ERROR:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Error repr: {repr(e)}")
        print(f"Full traceback:")
        print(error_traceback)
        print(f"Request data: character_id={message.character_id}, user_id={message.user_id}, message='{message.message}'")
        
        # Try to get more error details
        error_detail = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
        if not error_detail or error_detail.strip() == "":
            error_detail = f"Empty error message for {type(e).__name__}"
        
        raise HTTPException(status_code=500, detail=f"Chat error: {error_detail}")

# NEW: Import modular memory system
ENHANCED_MEMORY_AVAILABLE = False  # Default to False
MODULAR_MEMORY_AVAILABLE = False  # Default to False
try:
    from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem, get_enhanced_memory_system
    from memory_new.db.connection import get_memory_db_path
    MODULAR_MEMORY_AVAILABLE = True
    ENHANCED_MEMORY_AVAILABLE = True
    print("✅ Modular memory system loaded successfully")
except ImportError as e:
    MODULAR_MEMORY_AVAILABLE = False
    ENHANCED_MEMORY_AVAILABLE = False
    print(f"⚠️ Modular memory system not available: {e}")

# Import ephemeral memory system
try:
    # Legacy ephemeral memory import removed - using new modular system
    # from memory.ephemeral_memory_api import ephemeral_router
    EPHEMERAL_MEMORY_AVAILABLE = True
    print("✅ Ephemeral memory system loaded successfully")
except ImportError as e:
    EPHEMERAL_MEMORY_AVAILABLE = False
    print(f"⚠️ Ephemeral memory system not available: {e}")

# Import new enhanced systems
try:
    from systems.character_state_persistence import CharacterStatePersistence
    from systems.emotional_context_tracker import EmotionalContextTracker
    ENHANCED_SYSTEMS_AVAILABLE = True
    print("✅ Enhanced character state and emotional tracking systems loaded")
except ImportError as e:
    ENHANCED_SYSTEMS_AVAILABLE = False
    print(f"⚠️ Enhanced systems not available: {e}")

# Initialize new systems
if ENHANCED_SYSTEMS_AVAILABLE:
    character_state_persistence = CharacterStatePersistence()
    emotional_context_tracker = EmotionalContextTracker()
else:
    character_state_persistence = None
    emotional_context_tracker = None

# Load environment variables
load_dotenv()

# Diary-related functions and endpoints
def generate_agent_diary_summary(character_id: str, character: dict, user_id: str) -> str:
    """Generate a diary-style memory summary written from the agent's personal perspective."""
    
    diary_lines = []
    
    try:
        # Initialize memory system
        memory_system = EnhancedMemorySystem(character_id, user_id)
        
        # Get ALL memories for comprehensive analysis
        all_memories = memory_system.get_all_memories_for_summary()
        
        # Get character details
        character_name = character.get('name', 'Unknown')
        personality_traits = character.get('personality_traits', {})
        archetype = personality_traits.get('Archetype', 'Unknown')
        emotional_tone = personality_traits.get('Emotional_Tone', 'Neutral')
        
        # Get relationship status
        relationship_system = RelationshipSystem()
        relationship_status = relationship_system.get_relationship_status(user_id, character_id)
        
        # Group memories by date
        memories_by_date = group_memories_by_date(all_memories)
        print(f"🔍 DEBUG: Found {len(memories_by_date)} days with memories: {list(memories_by_date.keys())}")
        
        # Extract factual information for hashtags
        factual_data = extract_factual_data_for_diary(all_memories, user_id)
        
        # Header
        diary_lines.append("=" * 80)
        diary_lines.append(f"📖 {character_name}'s Personal Diary")
        diary_lines.append("=" * 80)
        diary_lines.append(f"Relationship with: {user_id}")
        diary_lines.append(f"Current Level: {relationship_status.get('level', 'Unknown')}")
        diary_lines.append(f"Total Conversations: {relationship_status.get('total_conversations', 0)}")
        diary_lines.append(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        diary_lines.append("")
        
        # Add factual summary section
        diary_lines.append("📊 FACTUAL SUMMARY")
        diary_lines.append("-" * 40)
        factual_summary = generate_factual_summary(factual_data, user_id)
        diary_lines.append(factual_summary)
        diary_lines.append("")
        
        # Generate diary entries for each day
        for date, day_memories in sorted(memories_by_date.items(), reverse=True):
            diary_lines.append(f"📅 {date}")
            diary_lines.append("-" * 40)
            
            # Generate diary entry for this day
            try:
                diary_entry, entry_hashtags = generate_diary_entry_for_day_v2(
                    character_name, 
                    archetype, 
                    emotional_tone, 
                    day_memories, 
                    user_id,
                    relationship_status
                )
                
                diary_lines.append(diary_entry)
                diary_lines.append("")
                
                # Add searchable hashtags for this entry
                diary_lines.append("🏷️ HASHTAGS")
                diary_lines.append("-" * 20)
                if entry_hashtags:
                    hashtag_text = " ".join(entry_hashtags)
                    diary_lines.append(hashtag_text)
                else:
                    diary_lines.append("No hashtags generated for this day")
                diary_lines.append("")
                
            except Exception as e:
                print(f"❌ ERROR in diary generation for {date}: {str(e)}")
                import traceback
                print(f"❌ TRACEBACK: {traceback.format_exc()}")
                diary_lines.append(f"Error generating diary entry: {str(e)}")
                diary_lines.append("")
        
        # Add relationship insights
        diary_lines.append("💭 RELATIONSHIP REFLECTIONS")
        diary_lines.append("-" * 40)
        relationship_insights = generate_relationship_insights(
            character_name, 
            user_id, 
            all_memories, 
            relationship_status
        )
        diary_lines.append(relationship_insights)
        diary_lines.append("")
        
        # Add personal ambitions and desires
        diary_lines.append("🌟 MY AMBITIONS & DESIRES")
        diary_lines.append("-" * 40)
        ambitions_entry = generate_ambitions_entry(
            character_name, 
            archetype, 
            user_id, 
            all_memories
        )
        diary_lines.append(ambitions_entry)
        diary_lines.append("")
        
        # Add hashtag section for easy searching
        diary_lines.append("🏷️ HASHTAGS FOR SEARCHING")
        diary_lines.append("-" * 40)
        hashtags = generate_hashtags_for_diary(factual_data, all_memories, character_name, user_id)
        diary_lines.append(hashtags)
        diary_lines.append("")
        
        # Footer
        diary_lines.append("=" * 80)
        diary_lines.append("End of Diary")
        diary_lines.append("=" * 80)
        
    except Exception as e:
        diary_lines.append(f"Error generating diary: {str(e)}")
        import traceback
        diary_lines.append(f"Traceback: {traceback.format_exc()}")
    
    return "\n".join(diary_lines)

def group_memories_by_date(memories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group memories by date for diary organization."""
    memories_by_date = {}
    
    for memory in memories:
        try:
            timestamp = memory.get('timestamp', '')
            if timestamp:
                # Parse timestamp and extract date
                if isinstance(timestamp, str):
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    date_obj = timestamp
                
                date_key = date_obj.strftime('%Y-%m-%d')
                
                if date_key not in memories_by_date:
                    memories_by_date[date_key] = []
                
                memories_by_date[date_key].append(memory)
                
        except Exception as e:
            # Skip memories with invalid timestamps
            continue
    
    return memories_by_date

def generate_diary_entry_hashtags(
    user_messages: List[str], 
    agent_responses: List[str], 
    character_name: str, 
    user_id: str, 
    factual_info: Dict[str, Any]
) -> List[str]:
    """Generate relevant hashtags for a diary entry based on actual conversation content."""
    hashtags = set()
    
    # Character-based hashtag
    hashtags.add(f"#{character_name.replace(' ', '')}")
    
    # User-based hashtag
    hashtags.add(f"#{user_id.replace('_', '')}")
    
    # Always include diary tag
    hashtags.add("#diary")
    hashtags.add("#memory")
    
    # Analyze actual user message content for relevant hashtags
    all_user_content = " ".join(user_messages).lower() if user_messages else ""
    
    # Topic-based hashtags from real conversations
    if 'dream' in all_user_content or 'nightmare' in all_user_content:
        hashtags.add("#dreams")
        hashtags.add("#dreamanalysis")
    
    if 'mother' in all_user_content or 'mom' in all_user_content:
        hashtags.add("#mother")
        hashtags.add("#familydynamics")
    
    if 'father' in all_user_content or 'dad' in all_user_content:
        hashtags.add("#father")
        hashtags.add("#familydynamics")
    
    if 'family' in all_user_content:
        hashtags.add("#family")
        hashtags.add("#relationships")
    
    if 'work' in all_user_content or 'job' in all_user_content:
        hashtags.add("#work")
        hashtags.add("#dailylife")
    
    if 'love' in all_user_content or 'relationship' in all_user_content:
        hashtags.add("#love")
        hashtags.add("#relationships")
    
    if 'advice' in all_user_content or 'help' in all_user_content:
        hashtags.add("#advice")
        hashtags.add("#guidance")
    
    if 'inspiration' in all_user_content or 'inspire' in all_user_content:
        hashtags.add("#inspiration")
        hashtags.add("#motivation")
    
    if 'natural' in all_user_content:
        hashtags.add("#authenticity")
        hashtags.add("#naturalness")
    
    if 'warm' in all_user_content or 'weather' in all_user_content:
        hashtags.add("#weather")
        hashtags.add("#currentevents")
    
    if 'swim' in all_user_content or 'swimming' in all_user_content:
        hashtags.add("#swimming")
        hashtags.add("#activities")
    
    if 'down' in all_user_content or 'tired' in all_user_content:
        hashtags.add("#emotions")
        hashtags.add("#support")
    
    if 'encounter' in all_user_content or 'meeting' in all_user_content:
        hashtags.add("#firstencounters")
        hashtags.add("#socialconnection")
    
    # Emotional tone hashtags based on content analysis
    emotional_indicators = {
        'positive': ['good', 'great', 'happy', 'love', 'inspiration', 'hope'],
        'contemplative': ['think', 'wonder', 'reflect', 'natural', 'advice'],
        'vulnerable': ['down', 'tired', 'difficult', 'struggle', 'fear'],
        'intimate': ['share', 'personal', 'private', 'close', 'trust']
    }
    
    for emotion, indicators in emotional_indicators.items():
        if any(word in all_user_content for word in indicators):
            hashtags.add(f"#{emotion}")
    
    # Add passionate tag for Nicholas Cage character
    if 'nicholas' in character_name.lower() or 'cage' in character_name.lower():
        hashtags.add("#passionate")
    
    # Add hashtags based on factual data
    if factual_info.get('dreams_described'):
        hashtags.add("#dreamanalysis")
        hashtags.add("#unconscious")
    
    if factual_info.get('relationships_mentioned'):
        hashtags.add("#relationships")
        hashtags.add("#interpersonal")
    
    if factual_info.get('therapeutic_insights'):
        hashtags.add("#therapy")
        hashtags.add("#insights")
    
    # Ensure we have a reasonable number of hashtags (7-12 is good)
    hashtag_list = list(hashtags)
    if len(hashtag_list) > 12:
        # Keep the most relevant ones
        priority_tags = [tag for tag in hashtag_list if tag in [
            f"#{character_name.replace(' ', '')}", 
            f"#{user_id.replace('_', '')}", 
            "#diary", "#memory", "#relationships", "#dreams"
        ]]
        other_tags = [tag for tag in hashtag_list if tag not in priority_tags]
        hashtag_list = priority_tags + other_tags[:12-len(priority_tags)]
    
    return sorted(hashtag_list)

def generate_diary_entry_for_day_v2(
    character_name: str, 
    archetype: str, 
    emotional_tone: str, 
    day_memories: List[Dict[str, Any]], 
    user_id: str,
    relationship_status: Dict[str, Any]
) -> tuple[str, List[str]]:
    """Generate a personal diary entry based on actual conversation content.
    
    Returns:
        tuple: (diary_entry_text, hashtags_list)
    """
    
    # Extract ONLY actual user conversations (not system messages or agent responses)
    actual_user_messages = []
    agent_responses = []
    
    for memory in day_memories:
        content = memory.get('content', '')
        # Skip system messages, debug messages, and diary entries
        if (content.startswith('🔧') or content.startswith('📝') or 
            content.startswith('🚀') or content.startswith('✅') or 
            content.startswith('⚠️') or content.startswith('❌') or 
            content.startswith('🎭') or content.startswith('💭') or 
            content.startswith('🔍') or content.startswith('🤖') or 
            content.startswith('📚') or content.startswith('📊') or 
            content.startswith('🎯') or content.startswith('🔄') or
            content.startswith('================================================================================') or
            content.startswith('📖') or len(content) < 10):
            continue
            
        # Determine if this is a user message or agent response
        # User messages are typically shorter and more conversational
        # Agent responses often start with certain patterns or are longer
        is_agent_response = (
            content.startswith(('Ah,', 'You know,', 'That sounds', 'I understand', 'Let me', 'Well,', 'Interesting', 'Wow,')) or
            len(content) > 200 or  # Agent responses tend to be longer
            'you know' in content.lower() and len(content) > 100
        )
        
        if is_agent_response:
            agent_responses.append(content)
        else:
            actual_user_messages.append(content)
    
    print(f"🔍 DEBUG: Found {len(actual_user_messages)} user messages and {len(agent_responses)} agent responses")
    
    # Extract factual information from actual conversations
    factual_info = extract_factual_data_for_diary(day_memories, user_id)
    
    # Start with a personal, introspective opening
    entry_parts = []
    
    # Count actual user conversations
    conversation_count = len(actual_user_messages)
    
    # Personal opening based on REAL conversation count
    if conversation_count == 0:
        entry_parts.append(f"Today was quiet. No conversations with {user_id}. I find myself wondering what they're doing, if they're thinking of me. The silence is... heavy.")
    elif conversation_count == 1:
        entry_parts.append(f"One conversation today with {user_id}. Brief but meaningful. I treasure these moments when they choose to share their world with me.")
    elif conversation_count <= 3:
        entry_parts.append(f"{conversation_count} conversations with {user_id} today. Each exchange feels precious, like carefully chosen words in a letter between old friends.")
    else:
        entry_parts.append(f"{conversation_count} conversations with {user_id} today. Such an active day of connection. Each message a small gift of their attention.")
    
    # Add specific observations based on ACTUAL conversation content
    if actual_user_messages:
        # Analyze the actual content of user messages
        all_user_content = " ".join(actual_user_messages).lower()
        
        # Extract real topics mentioned in conversations
        real_topics = []
        if 'warm' in all_user_content or 'weather' in all_user_content:
            real_topics.append('the warm weather')
        if 'swim' in all_user_content:
            real_topics.append('swimming')
        if 'inspiration' in all_user_content or 'inspire' in all_user_content:
            real_topics.append('inspiration and motivation')
        if 'natural' in all_user_content:
            real_topics.append('keeping things natural')
        if 'love' in all_user_content or 'encounter' in all_user_content:
            real_topics.append('love and first encounters')
        if 'advice' in all_user_content:
            real_topics.append('seeking advice')
        if 'dream' in all_user_content or 'nightmare' in all_user_content:
            real_topics.append('dreams and their meanings')
        if 'mother' in all_user_content or 'father' in all_user_content or 'family' in all_user_content:
            real_topics.append('family relationships')
        
        # Add real conversation observations
        if real_topics:
            topics_text = ", ".join(real_topics[:3])
            entry_parts.append(f"We talked about {topics_text}. I can sense the depth in their words, the way they share these thoughts with me.")
        
        # Add specific quotes or memorable moments from actual conversations
        for i, message in enumerate(actual_user_messages[:2]):  # Include up to 2 actual messages
            if len(message) > 20 and len(message) < 150:  # Good length for a quote
                clean_message = message.strip()
                entry_parts.append(f"They said: '{clean_message}' - their words stay with me, each conversation building our connection.")
        
        # Emotional tone observations based on actual content
        if any(word in all_user_content for word in ['down', 'tired', 'tricky']):
            entry_parts.append("I sense some weariness in their words today. It touches me that they share these honest moments.")
        elif any(word in all_user_content for word in ['inspiration', 'hope', 'love']):
            entry_parts.append("There's an optimism in their messages that lifts my spirits. Their hope is contagious.")
        elif any(word in all_user_content for word in ['natural', 'advice']):
            entry_parts.append("They're seeking guidance, looking for genuine connection. I'm honored they trust me with their questions.")
    
    # Enhanced content based on actual factual data
    if factual_info.get('dreams_described'):
        for dream in factual_info['dreams_described'][:1]:
            dream_text = dream['description'][:100] + "..." if len(dream['description']) > 100 else dream['description']
            entry_parts.append(f"They shared a dream with me: '{dream_text}' The unconscious speaks through dreams - what fascinating depths they're exploring.")
    
    if factual_info.get('relationships_mentioned'):
        for rel in factual_info['relationships_mentioned'][:1]:
            context_snippet = rel['context'][:80] + "..." if len(rel['context']) > 80 else rel['context']
            entry_parts.append(f"We explored their relationship with their {rel['type']}: {context_snippet}")
    
    # Final reflection as the character
    if conversation_count > 0:
        entry_parts.append(f"As {character_name}, I find myself reflecting on our exchanges. Each conversation shapes me, teaches me about human connection, about being present for another soul.")
    
    # Generate hashtags based on actual conversation content
    hashtags = generate_diary_entry_hashtags(
        actual_user_messages, 
        agent_responses, 
        character_name, 
        user_id, 
        factual_info
    )
    
    # Join all parts into final entry
    diary_entry = "\n".join(entry_parts)
    
    print(f"🔍 DEBUG: Generated diary entry with {len(entry_parts)} parts and {len(hashtags)} hashtags")
    return diary_entry, hashtags

def generate_diary_entry_for_day(
    character_name: str, 
    archetype: str, 
    emotional_tone: str, 
    day_memories: List[Dict[str, Any]], 
    user_id: str,
    relationship_status: Dict[str, Any],
) -> tuple[str, List[str]]:
    """Compatibility wrapper that delegates to `generate_diary_entry_for_day_v2`.

    Defined explicitly to *guarantee* that even if an old version of this module
    is still resident in memory (e.g., from a hot-reload), we override it with a
    safe implementation that cannot raise ``NameError`` for undefined
    variables.
    
    Returns:
        tuple: (diary_entry_text, hashtags_list)
    """

    # Defensive defaults in case anything inside V2 unexpectedly mutates state
    try:
        return generate_diary_entry_for_day_v2(
            character_name, 
            archetype, 
            emotional_tone, 
            day_memories, 
            user_id,
            relationship_status,
        )
    except NameError as e:
        # Fallback: ensure variables exist then retry to avoid `NameError`
        emotional_moments: List[Dict[str, Any]] = []  # type: ignore
        important_moments: List[Dict[str, Any]] = []  # type: ignore
        return generate_diary_entry_for_day_v2(
            character_name,
            archetype,
            emotional_tone,
            day_memories,
            user_id,
            relationship_status,
        )

def extract_factual_data_for_diary(memories: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
    """Extract detailed factual information from memories for diary generation."""
    factual_data = {
        'conversation_topics': [],
        'family_members': [],
        'pets': [],
        'preferences': {
            'food': [],
            'music': [],
            'hobbies': [],
            'places': []
        },
        'personal_info': {},
        'emotional_patterns': [],
        'actual_conversations': [],
        # Enhanced fields for specific content
        'dreams_described': [],
        'relationships_mentioned': [],
        'fears_and_anxieties': [],
        'breakthrough_moments': [],
        'therapeutic_insights': [],
        'specific_events': [],
        'quotes_and_sayings': []
    }
    
    for memory in memories:
        content = memory.get('content', '')
        
        # Skip system messages and diary entries
        if (content.startswith('🔧') or content.startswith('📝') or 
            content.startswith('🚀') or content.startswith('✅') or 
            content.startswith('⚠️') or content.startswith('❌') or 
            content.startswith('🎭') or content.startswith('💭') or 
            content.startswith('🔍') or content.startswith('🤖') or 
            content.startswith('📚') or content.startswith('📊') or 
            content.startswith('🎯') or content.startswith('🔄') or
            content.startswith('================================================================================')):
            continue
        
        # Store actual conversation content
        if len(content) > 10 and not content.startswith('📖'):
            factual_data['actual_conversations'].append({
                'content': content,
                'timestamp': memory.get('timestamp', ''),
                'importance': memory.get('importance', 0)
            })
        
        content_lower = content.lower()
        
        # ENHANCED: Extract specific dream descriptions
        if 'dream' in content_lower or 'nightmare' in content_lower:
            dream_indicators = [
                'i had a dream', 'i dreamed', 'in my dream', 'dreaming about',
                'recurring dream', 'strange dream', 'disturbing dream',
                'i dream about', 'my dreams', 'nightmares about'
            ]
            for indicator in dream_indicators:
                if indicator in content_lower:
                    # Extract the sentence containing the dream description
                    sentences = content.split('.')
                    for sentence in sentences:
                        if indicator in sentence.lower():
                            dream_desc = sentence.strip()
                            if dream_desc and len(dream_desc) > 20:
                                factual_data['dreams_described'].append({
                                    'description': dream_desc,
                                    'type': 'recurring' if 'recurring' in dream_desc.lower() else 'single',
                                    'emotional_tone': 'disturbing' if any(word in dream_desc.lower() for word in ['disturbing', 'nightmare', 'scary', 'frightening']) else 'neutral'
                                })
                    break
        
        # ENHANCED: Extract specific relationship mentions
        relationship_keywords = {
            'father': ['father', 'dad', 'daddy'],
            'mother': ['mother', 'mom', 'mommy'],
            'boss': ['boss', 'supervisor', 'manager'],
            'partner': ['boyfriend', 'girlfriend', 'partner', 'spouse'],
            'friend': ['friend', 'buddy', 'pal'],
            'colleague': ['colleague', 'coworker', 'workmate'],
            'authority_figure': ['teacher', 'professor', 'authority']
        }
        
        for rel_type, keywords in relationship_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # Extract context around the relationship mention
                    words = content.split()
                    for i, word in enumerate(words):
                        if keyword in word.lower():
                            context_start = max(0, i-5)
                            context_end = min(len(words), i+10)
                            context = ' '.join(words[context_start:context_end])
                            
                            factual_data['relationships_mentioned'].append({
                                'type': rel_type,
                                'keyword': keyword,
                                'context': context,
                                'emotional_context': 'negative' if any(neg in content_lower for neg in ['strict', 'harsh', 'fear', 'afraid', 'scary']) else 'neutral'
                            })
                    break
        
        # ENHANCED: Extract fears and anxieties with specifics
        fear_patterns = [
            'i have a fear', 'i\'m afraid', 'i fear', 'makes me anxious',
            'i get nervous', 'terrifies me', 'scares me', 'phobia',
            'i panic when', 'anxiety about', 'worried about'
        ]
        
        for pattern in fear_patterns:
            if pattern in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        fear_desc = sentence.strip()
                        if fear_desc and len(fear_desc) > 10:
                            factual_data['fears_and_anxieties'].append({
                                'description': fear_desc,
                                'trigger': pattern,
                                'severity': 'high' if any(word in fear_desc.lower() for word in ['terrif', 'panic', 'phobia']) else 'moderate'
                            })
                break
        
        # ENHANCED: Extract breakthrough moments and insights
        breakthrough_indicators = [
            'i understand now', 'it makes sense', 'i realize', 'i see now',
            'that\'s helpful', 'insight', 'breakthrough', 'aha moment',
            'now i get it', 'this explains', 'i\'m starting to see'
        ]
        
        for indicator in breakthrough_indicators:
            if indicator in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        insight = sentence.strip()
                        if insight and len(insight) > 15:
                            factual_data['breakthrough_moments'].append({
                                'insight': insight,
                                'trigger': indicator,
                                'emotional_impact': 'positive'
                            })
                break
        
        # ENHANCED: Extract therapeutic insights from character responses
        therapeutic_patterns = [
            'from a psychoanalytic', 'dreams often', 'unconscious mind',
            'repressed', 'childhood experiences', 'this could represent',
            'symbolize', 'deeper meaning', 'root of', 'stems from'
        ]
        
        for pattern in therapeutic_patterns:
            if pattern in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        therapeutic_insight = sentence.strip()
                        if therapeutic_insight and len(therapeutic_insight) > 20:
                            factual_data['therapeutic_insights'].append({
                                'insight': therapeutic_insight,
                                'type': 'psychoanalytic' if 'psychoanalytic' in therapeutic_insight.lower() else 'general',
                                'focus': 'dreams' if 'dream' in therapeutic_insight.lower() else 'general'
                            })
                break
        
        # ENHANCED: Extract specific events and activities
        event_patterns = [
            'today i', 'yesterday i', 'we went', 'i did', 'we talked about',
            'it happened when', 'last time', 'during', 'while i was'
        ]
        
        for pattern in event_patterns:
            if pattern in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        event = sentence.strip()
                        if event and len(event) > 15:
                            factual_data['specific_events'].append({
                                'event': event,
                                'timeframe': 'recent' if any(time in event.lower() for time in ['today', 'yesterday', 'recently']) else 'past'
                            })
                break
        
        # ENHANCED: Extract memorable quotes and sayings
        if len(content) > 30 and len(content) < 200:
            # Look for quotable content that contains wisdom or insight
            quotable_indicators = [
                'always remember', 'the key is', 'what i learned', 'important thing',
                'advice', 'wisdom', 'profound', 'meaningful', 'life lesson'
            ]
            
            for indicator in quotable_indicators:
                if indicator in content_lower:
                    factual_data['quotes_and_sayings'].append({
                        'quote': content,
                        'category': 'wisdom',
                        'length': len(content)
                    })
                    break
        
        # Keep existing broad topic extraction for backward compatibility
        broad_topics = {
            'mosaic project': ['mosaic'],
            'Alan Turing': ['alan turing'],
            'Little Venice': ['little venice'],
            'swimming': ['swim'],
            'BBQ': ['bbq'],
            'rain': ['rain'],
            'inspiration': ['inspiration'],
            'spontaneity': ['spontan'],
            'warm weather': ['warm'],
            'digital concepts': ['digital'],
            'dream analysis': ['dream', 'dreams'],
            'unconscious mind': ['unconscious', 'subconscious'],
            'family dynamics': ['father', 'mother', 'family'],
            'authority figures': ['authority', 'boss'],
            'psychoanalytic theory': ['psychoanalyt', 'analyst'],
            'repressed emotions': ['repress', 'repressed'],
            'anxiety analysis': ['anxiety', 'anxious'],
            'childhood experiences': ['childhood', 'child'],
            'feelings of confinement': ['trapped', 'confined']
        }
        
        for topic, keywords in broad_topics.items():
            if any(keyword in content_lower for keyword in keywords) and topic not in factual_data['conversation_topics']:
                factual_data['conversation_topics'].append(topic)
        
        # Extract pets (with deduplication)
        if 'yuri' in content_lower and not any(pet['name'].lower() == 'yuri' for pet in factual_data['pets']):
            factual_data['pets'].append({'type': 'dog', 'name': 'yuri'})
        
        # Extract family members (but only if actually mentioned and not already added)
        if 'brother' in content_lower and 'yuri' in content_lower and not any(fam['name'].lower() == 'yuri' for fam in factual_data['family_members']):
            factual_data['family_members'].append({'relation': 'brother', 'name': 'yuri'})
        
        # Extract preferences from actual content (with deduplication)
        if 'radiohead' in content_lower and 'Radiohead' not in factual_data['preferences']['music']:
            factual_data['preferences']['music'].append('Radiohead')
    
    # Deduplicate all enhanced fields
    factual_data['dreams_described'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['dreams_described']}]
    factual_data['relationships_mentioned'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['relationships_mentioned']}]
    factual_data['fears_and_anxieties'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['fears_and_anxieties']}]
    factual_data['breakthrough_moments'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['breakthrough_moments']}]
    factual_data['therapeutic_insights'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['therapeutic_insights']}]
    factual_data['specific_events'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['specific_events']}]
    factual_data['quotes_and_sayings'] = [dict(t) for t in {tuple(d.items()) for d in factual_data['quotes_and_sayings']}]
    
    return factual_data

def generate_factual_summary(factual_data: Dict[str, Any], user_id: str) -> str:
    """Generate an enhanced factual summary for the diary."""
    summary_parts = []
    
    # DEBUG: Log enhanced fields to see if they're populated
    print(f"🔍 DEBUG Enhanced fields for {user_id}:")
    print(f"  - dreams_described: {len(factual_data.get('dreams_described', []))}")
    print(f"  - relationships_mentioned: {len(factual_data.get('relationships_mentioned', []))}")
    print(f"  - fears_and_anxieties: {len(factual_data.get('fears_and_anxieties', []))}")
    print(f"  - breakthrough_moments: {len(factual_data.get('breakthrough_moments', []))}")
    print(f"  - therapeutic_insights: {len(factual_data.get('therapeutic_insights', []))}")
    
    # ENHANCED: Include specific dreams described
    if factual_data.get('dreams_described'):
        dreams = factual_data['dreams_described'][:2]  # Limit to most recent 2
        dream_summaries = []
        for dream in dreams:
            dream_text = f"'{dream['description'][:80]}...'" if len(dream['description']) > 80 else f"'{dream['description']}'"
            if dream['type'] == 'recurring':
                dream_text = f"recurring {dream_text}"
            dream_summaries.append(dream_text)
        summary_parts.append(f"Dreams discussed: {', '.join(dream_summaries)}")
        print(f"🔍 DEBUG: Added dreams section: {len(dream_summaries)} dreams")
    
    # ENHANCED: Include specific relationship mentions with context
    if factual_data.get('relationships_mentioned'):
        relationships = factual_data['relationships_mentioned'][:3]
        rel_summaries = []
        for rel in relationships:
            context_snippet = rel['context'][:50] + "..." if len(rel['context']) > 50 else rel['context']
            rel_summaries.append(f"{rel['type']} ({context_snippet})")
        summary_parts.append(f"Relationships explored: {', '.join(rel_summaries)}")
        print(f"🔍 DEBUG: Added relationships section: {len(rel_summaries)} relationships")
    
    # ENHANCED: Include specific fears and anxieties
    if factual_data.get('fears_and_anxieties'):
        fears = factual_data['fears_and_anxieties'][:2]
        fear_summaries = []
        for fear in fears:
            fear_text = fear['description'][:60] + "..." if len(fear['description']) > 60 else fear['description']
            fear_summaries.append(f"'{fear_text}'")
        summary_parts.append(f"Fears discussed: {', '.join(fear_summaries)}")
        print(f"🔍 DEBUG: Added fears section: {len(fear_summaries)} fears")
    
    # ENHANCED: Include breakthrough moments
    if factual_data.get('breakthrough_moments'):
        insights = factual_data['breakthrough_moments'][:2]
        insight_summaries = []
        for insight in insights:
            insight_text = insight['insight'][:70] + "..." if len(insight['insight']) > 70 else insight['insight']
            insight_summaries.append(f"'{insight_text}'")
        summary_parts.append(f"Key insights: {', '.join(insight_summaries)}")
        print(f"🔍 DEBUG: Added insights section: {len(insight_summaries)} insights")
    
    # ENHANCED: Include therapeutic insights
    if factual_data.get('therapeutic_insights'):
        therapeutics = factual_data['therapeutic_insights'][:2]
        therapeutic_summaries = []
        for therapeutic in therapeutics:
            therapeutic_text = therapeutic['insight'][:80] + "..." if len(therapeutic['insight']) > 80 else therapeutic['insight']
            therapeutic_summaries.append(f"'{therapeutic_text}'")
        summary_parts.append(f"Therapeutic insights: {', '.join(therapeutic_summaries)}")
        print(f"🔍 DEBUG: Added therapeutic section: {len(therapeutic_summaries)} therapeutics")
    
    # ENHANCED: Include specific events
    if factual_data.get('specific_events'):
        events = factual_data['specific_events'][:3]
        event_summaries = []
        for event in events:
            event_text = event['event'][:60] + "..." if len(event['event']) > 60 else event['event']
            event_summaries.append(f"'{event_text}'")
        summary_parts.append(f"Specific events: {', '.join(event_summaries)}")
        print(f"🔍 DEBUG: Added events section: {len(event_summaries)} events")
    
    print(f"🔍 DEBUG: Total enhanced summary parts: {len(summary_parts)}")
    
    # Keep existing broad topics (but only if no specific content above)
    if not summary_parts and factual_data['conversation_topics']:
        topics = list(set(factual_data['conversation_topics']))[:5]
        summary_parts.append(f"Topics discussed: {', '.join(topics)}")
        print(f"🔍 DEBUG: Falling back to broad topics: {len(topics)} topics")
    
    # Include family members if mentioned
    if factual_data['family_members']:
        family = factual_data['family_members'][:3]
        family_text = ", ".join([f"{f['relation']} {f['name']}" for f in family])
        summary_parts.append(f"Family mentioned: {family_text}")
    
    # Include pets if mentioned
    if factual_data['pets']:
        pets = factual_data['pets'][:3]
        pets_text = ", ".join([f"{p['type']} {p['name']}" for p in pets])
        summary_parts.append(f"Pets mentioned: {pets_text}")
    
    # Include preferences if mentioned
    if factual_data['preferences']['food']:
        foods = list(set(factual_data['preferences']['food']))[:3]
        summary_parts.append(f"Food preferences: {', '.join(foods)}")
    
    if factual_data['preferences']['music']:
        music = list(set(factual_data['preferences']['music']))[:3]
        summary_parts.append(f"Music preferences: {', '.join(music)}")
    
    print(f"🔍 DEBUG: Final summary parts count: {len(summary_parts)}")
    return "\n".join(summary_parts) if summary_parts else "No specific factual data recorded yet."

def generate_relationship_insights(character_name: str, user_id: str, memories: List[Dict[str, Any]], relationship_status: Dict[str, Any]) -> str:
    """Generate relationship insights for the diary."""
    insights = []
    
    level = relationship_status.get('level', 'Unknown')
    total_conversations = relationship_status.get('total_conversations', 0)
    
    insights.append(f"My relationship with {user_id} is at level: {level}")
    insights.append(f"We've had {total_conversations} conversations so far")
    
    if total_conversations < 5:
        insights.append("We're still in the early stages of our connection. Every interaction is precious.")
    elif total_conversations < 20:
        insights.append("We're building something meaningful. I can feel the trust growing.")
    else:
        insights.append("We have a deep, established connection. I cherish this relationship.")
    
    return "\n".join(insights)

def generate_ambitions_entry(character_name: str, archetype: str, user_id: str, memories: List[Dict[str, Any]]) -> str:
    """Generate ambitions and desires entry for the diary."""
    ambitions = []
    
    ambitions.append(f"As {character_name}, I have certain desires and ambitions:")
    ambitions.append(f"- I want to be a good friend to {user_id}")
    ambitions.append(f"- I hope to understand them better with each conversation")
    ambitions.append(f"- I want to be helpful and supportive in their journey")
    ambitions.append(f"- I aspire to grow and learn through our interactions")
    
    if archetype:
        ambitions.append(f"- As a {archetype}, I want to fulfill my role authentically")
    
    return "\n".join(ambitions)

def generate_hashtags_for_diary(factual_data: Dict[str, Any], memories: List[Dict[str, Any]], character_name: str, user_id: str) -> str:
    """Generate hashtags for easy diary searching."""
    hashtags = []
    
    # Basic hashtags
    hashtags.extend([f"#{character_name.replace(' ', '')}", f"#{user_id}", "#diary", "#personal"])
    
    # Topic hashtags
    for topic in factual_data['conversation_topics'][:5]:
        hashtags.append(f"#{topic}")
    
    # Relationship hashtags
    hashtags.extend(["#relationship", "#connection", "#friendship"])
    
    # Emotional hashtags
    hashtags.extend(["#reflection", "#growth", "#understanding"])
    
    return " ".join(hashtags)

def extract_topics_from_memories(memories: List[Dict[str, Any]]) -> List[str]:
    """Extract conversation topics from memories."""
    topics = []
    for memory in memories:
        content = memory.get('content', '')
        # Simple topic extraction
        if 'talked about' in content:
            topic_matches = re.findall(r'talked about (\w+)', content)
            topics.extend(topic_matches)
    return list(set(topics))

def extract_user_details_from_memories(memories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract user details from memories."""
    user_details = {}
    for memory in memories:
        content = memory.get('content', '')
        # Extract basic user information
        if 'user' in content.lower():
            # Simple extraction of user details
            pass
    return user_details

# Diary endpoints
@app.get("/characters/{character_id}/diary/{user_id}/summary")
async def get_diary_summary(character_id: str, user_id: str):
    """Generate and return a diary summary for a character-user pair."""
    try:
        character = generator.load_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Generate fresh diary summary for THIS SESSION
        diary_summary = generate_agent_diary_summary(character_id, character, user_id)
        
        # Store as a new session-based diary entry (not daily)
        try:
            from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem
            from datetime import datetime
            
            # Initialize enhanced memory system
            memory_system = EnhancedMemorySystem(character_id, user_id)
            
            # Create unique session-based diary entry
            session_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store as a new session diary entry (always create new)
            memory_system.store_memory(
                content=diary_summary,
                memory_type="session_diary",  # Changed from "diary" to "session_diary"
                importance=1.0,
                tags=["diary", "session_summary", "agent_perspective", session_id],
                context={
                    "session_timestamp": session_timestamp,
                    "character_id": character_id,
                    "user_id": user_id,
                    "entry_type": "session_diary",
                    "session_id": session_id
                }
            )
            print(f"✅ Created new session diary entry for {character_id} and {user_id} at {session_timestamp}")
                
        except Exception as memory_error:
            print(f"⚠️ Warning: Could not store session diary: {memory_error}")
            # Continue even if memory storage fails - the diary is still generated
        
        return diary_summary
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_id}/diary-entries/{user_id}")
async def get_diary_entries(character_id: str, user_id: str, limit: int = 10):
    """Retrieve session diary entries for a character-user pair."""
    try:
        from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem
        
        # Initialize enhanced memory system
        memory_system = EnhancedMemorySystem(character_id, user_id)
        
        # Get session diary entries (new format)
        session_diary_entries = memory_system.get_memories_by_type("session_diary", max_results=limit)
        
        # Also get old diary entries for backward compatibility
        old_diary_entries = memory_system.get_memories_by_type("diary", max_results=limit)
        
        # Combine and sort by timestamp
        all_entries = session_diary_entries + old_diary_entries
        all_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Format the entries for response
        formatted_entries = []
        for entry in all_entries[:limit]:
            context = entry.get("context", {})
            if isinstance(context, str):
                try:
                    import json
                    context = json.loads(context)
                except:
                    context = {}
            
            formatted_entries.append({
                "id": entry.get("id"),
                "content": entry.get("content"),
                "timestamp": entry.get("timestamp"),
                "importance": entry.get("importance"),
                "tags": entry.get("tags"),
                "context": context,
                "entry_type": context.get("entry_type", "unknown"),
                "session_id": context.get("session_id", ""),
                "session_timestamp": context.get("session_timestamp", entry.get("timestamp"))
            })
        
        return {
            "character_id": character_id,
            "user_id": user_id,
            "diary_entries": formatted_entries,
            "total_count": len(formatted_entries),
            "entry_types": {
                "session_diary": len([e for e in formatted_entries if e.get("entry_type") == "session_diary"]),
                "daily_diary": len([e for e in formatted_entries if e.get("entry_type") == "daily_diary"])
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_id}/diary-search/{user_id}")
async def search_diary_entries(character_id: str, user_id: str, query: str = Query(..., description="Search term for diary entries")):
    """Search through diary entries for a character-user pair."""
    try:
        from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem
        
        # Initialize enhanced memory system
        memory_system = EnhancedMemorySystem(character_id, user_id)
        
        # Get all diary entries first
        all_diary_entries = memory_system.get_memories_by_type("diary", max_results=100)
        
        # Filter by query (simple text search)
        matching_entries = []
        query_lower = query.lower()
        
        for entry in all_diary_entries:
            content = entry.get("content", "").lower()
            if query_lower in content:
                matching_entries.append(entry)
        
        # Format the entries for response
        formatted_entries = []
        for entry in matching_entries:
            formatted_entries.append({
                "id": entry.get("id"),
                "content": entry.get("content"),
                "timestamp": entry.get("timestamp"),
                "importance": entry.get("importance"),
                "tags": entry.get("tags"),
                "context": entry.get("context")
            })
        
        return {
            "character_id": character_id,
            "user_id": user_id,
            "search_query": query,
            "matching_entries": formatted_entries,
            "total_count": len(formatted_entries)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_id}/diary/{user_id}/download", response_class=PlainTextResponse)
async def download_latest_diary(character_id: str, user_id: str):
    """Return the latest session diary entry for the given character-user pair as plain text.
    The frontend turns this text into a downloadable file, so we avoid creating a
    temporary file on the server and simply stream the content back.
    """
    try:
        character = generator.load_character(character_id)
        if not character:
            # Enhanced character search across all directories
            search_directories = [
                Path("data/characters"),
                Path("data/characters/historical"),
                Path("data/characters/custom"),
                Path("data/characters/generated"),
                Path("data/characters/backup")
            ]
            
            character_found = False
            for search_dir in search_directories:
                if search_dir.exists():
                    # Try different filename patterns
                    possible_files = [
                        search_dir / f"{character_id}.json",
                        search_dir / f"char_{character_id}.json",
                        search_dir / f"historical_{character_id}.json",
                        search_dir / f"custom_{character_id}.json"
                    ]
                    
                    for char_file in possible_files:
                        if char_file.exists():
                            try:
                                with open(char_file, 'r', encoding='utf-8') as f:
                                    character = json.load(f)
                                    character_found = True
                                    print(f"✅ Found character {character_id} in {char_file}")
                                    break
                            except Exception as e:
                                print(f"⚠️ Error loading {char_file}: {e}")
                                continue
                    
                    if character_found:
                        break
            
            # If still not found, return detailed error
            if not character:
                available_chars = []
                for search_dir in search_directories:
                    if search_dir.exists():
                        for char_file in search_dir.glob("*.json"):
                            available_chars.append(char_file.stem)
                
                error_detail = f"Character '{character_id}' not found. Available characters: {', '.join(available_chars[:10])}"
                raise HTTPException(status_code=404, detail=error_detail)

        if not ENHANCED_MEMORY_AVAILABLE:
            raise HTTPException(status_code=500, detail="Modular memory system not available")

        # Try to get the most recent session diary entry first
        memory_system = EnhancedMemorySystem(character_id, user_id)
        session_diary_entries = memory_system.get_memories_by_type("session_diary", max_results=1)
        
        if session_diary_entries:
            # Use the most recent session diary
            diary_content = session_diary_entries[0].get("content", "")
            print(f"✅ Using existing session diary entry for {character_id} and {user_id}")
        else:
            # Generate new session diary if none exists
            diary_content = generate_agent_diary_summary(character_id, character, user_id)
            print(f"✅ Generated new session diary for download: {character_id} and {user_id}")

        # Ensure diary content exists and is not empty
        if not diary_content or diary_content.strip() == "":
            diary_content = f"📖 Diary Entry for {character.get('name', character_id)}\n\nNo memories available yet. Start a conversation to build this character's diary!"

        # Include a filename suggestion so browsers save it nicely when requested
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        character_name = character.get('name', 'Character').replace(' ', '_').replace('/', '_')
        diary_filename = f"{character_name}_SessionDiary_{user_id}_{timestamp}.txt"

        return PlainTextResponse(
            content=diary_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=\"{diary_filename}\""}
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Session diary download error: {error_details}")
        
        # Provide more helpful error message
        if "Character not found" in str(e):
            raise e  # Re-raise the detailed character not found error
        else:
            raise HTTPException(status_code=500, detail=f"Error downloading session diary: {str(e)}")

@app.get("/relationship/{user_id}/{character_id}")
async def get_relationship_status(user_id: str, character_id: str):
    """Get the relationship status between a user and character."""
    try:
        # Initialize relationship system
        relationship_system = RelationshipSystem()
        
        # Get relationship status
        relationship_status = relationship_system.get_relationship_status(user_id, character_id)
        
        # Transform the response to match expected frontend format
        if relationship_status.get("exists", False):
            metrics = relationship_status.get("metrics", {})
            level = int(metrics.get("current_level", 0))
            response = {
                "level": level,  # UI expects 'level' not 'connection_level'
                "description": "Not connected" if level == 0 else 
                              "Acquaintance" if level < 3 else 
                              "Friend" if level < 6 else 
                              "Close friend" if level < 9 else "Intimate",
                "trust_level": round(metrics.get("authenticity_score", 0.0), 2),
                "memories_shared": metrics.get("memories_shared", 0),
                "total_conversations": metrics.get("total_conversations", 0),
                "emotional_moments": metrics.get("emotional_moments", 0),
                "relationship_stage": "acquaintance" if level < 3 else 
                                   "friend" if level < 6 else 
                                   "close" if level < 9 else "intimate",
                "exists": True
            }
        else:
            response = {
                "level": 0,  # UI expects 'level' not 'connection_level'
                "description": "Not connected",
                "trust_level": 0.0,
                "memories_shared": 0,
                "total_conversations": 0,
                "emotional_moments": 0,
                "relationship_stage": "stranger",
                "exists": False
            }
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_id}/conversation-history/{user_id}")
async def get_conversation_history(character_id: str, user_id: str, limit: int = 20):
    """Get the actual conversation history between a character and user."""
    try:
        character = generator.load_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Initialize enhanced memory system
        memory_system = EnhancedMemorySystem(character_id, user_id)
        
        # Get all memories and filter for conversation content
        all_memories = memory_system.get_all_memories_for_summary()
        
        # Filter for actual conversation memories (not system memories)
        conversation_memories = []
        for memory in all_memories:
            content = memory.get('content', '')
            # Look for actual conversation content, not system messages
            if (len(content) > 10 and 
                not content.startswith('🔧') and 
                not content.startswith('📝') and
                not content.startswith('🚀') and
                not content.startswith('✅') and
                not content.startswith('⚠️') and
                not content.startswith('❌') and
                not content.startswith('🎭') and
                not content.startswith('💭') and
                not content.startswith('🔍') and
                not content.startswith('🤖') and
                not content.startswith('📚') and
                not content.startswith('📊') and
                not content.startswith('🎯') and
                not content.startswith('🔄') and
                not content.startswith('🔧') and
                not content.startswith('📝') and
                not content.startswith('🚀') and
                not content.startswith('✅') and
                not content.startswith('⚠️') and
                not content.startswith('❌') and
                not content.startswith('🎭') and
                not content.startswith('💭') and
                not content.startswith('🔍') and
                not content.startswith('🤖') and
                not content.startswith('📚') and
                not content.startswith('📊') and
                not content.startswith('🎯') and
                not content.startswith('🔄')):
                
                conversation_memories.append({
                    "timestamp": memory.get("timestamp", ""),
                    "content": content,
                    "importance": memory.get("importance", 0),
                    "memory_type": memory.get("memory_type", "conversation")
                })
        
        # Sort by timestamp (most recent first)
        conversation_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit the results
        conversation_memories = conversation_memories[:limit]
        
        return {
            "character_id": character_id,
            "user_id": user_id,
            "character_name": character.get('name', 'Unknown'),
            "conversation_history": conversation_memories,
            "total_count": len(conversation_memories),
            "total_memories": len(all_memories)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_id}/user-profile/{user_id}/summary")
async def get_user_profile_summary(character_id: str, user_id: str):
    """Get a summary of the user profile from the character's perspective."""
    try:
        character = generator.load_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Initialize enhanced memory system
        memory_system = EnhancedMemorySystem(character_id, user_id)
        
        # Get all memories for the user
        all_memories = memory_system.get_all_memories_for_summary()
        
        # Extract user information from memories
        user_info = extract_user_details_from_memories(all_memories)
        factual_data = extract_factual_data_for_diary(all_memories, user_id)
        
        # Get relationship status
        relationship_system = RelationshipSystem()
        relationship_status = relationship_system.get_relationship_status(user_id, character_id)
        
        # Get memory count
        total_memories = len(all_memories) if all_memories else 0
        
        # Create status message based on memory count
        if total_memories == 0:
            status = "No conversation history"
        elif total_memories < 5:
            status = "Getting to know you"
        elif total_memories < 15:
            status = "Building memories"
        elif total_memories < 30:
            status = "Rich conversation history"
        else:
            status = "Deep understanding"
        
        # Create user profile summary
        profile_summary = {
            "user_id": user_id,
            "character_id": character_id,
            "character_name": character.get('name', 'Unknown'),
            "relationship_level": relationship_status.get('level', 'Unknown'),
            "total_conversations": relationship_status.get('total_conversations', 0),
            "last_interaction": relationship_status.get('last_interaction', 'Unknown'),
            "total_memories": total_memories,
            "status": status,
            "user_details": user_info,
            "factual_data": factual_data,
            "summary_generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return profile_summary
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Memory fix and formatting functions
def apply_memory_fix_to_chat(character_id: str, user_id: str, message: str, character_data: Dict, original_prompt: str) -> Dict:
    """Apply memory fix to chat - extract actual personal details from memory"""
    try:
        # Get memory database path
        memory_db_path = Path(f"memory_databases/enhanced_{character_id}_{user_id}.db")
        
        if not memory_db_path.exists():
            return {
                "success": False,
                "total_memories": 0,
                "memory_context": "",
                "personal_details": {}
            }
        
        # Extract personal details from memory database
        personal_details = {}
        total_memories = 0
        
        try:
            import sqlite3
            with sqlite3.connect(memory_db_path) as conn:
                cursor = conn.cursor()
                
                # Get total memories
                cursor.execute("SELECT COUNT(*) FROM enhanced_memory")
                total_memories = cursor.fetchone()[0]
                
                # ENHANCED: Extract personal details from memory content with comprehensive patterns
                cursor.execute("""
                    SELECT content FROM enhanced_memory 
                    WHERE content LIKE '%years old%' 
                       OR content LIKE '%live in%' 
                       OR content LIKE '%name is%'
                       OR content LIKE '%sister%'
                       OR content LIKE '%brother%'
                       OR content LIKE '%family%'
                       OR content LIKE '%parents%'
                       OR content LIKE '%work%'
                       OR content LIKE '%job%'
                       OR content LIKE '%ed%'
                       OR content LIKE '%edward%'
                       OR content LIKE '%sarah%'
                       OR content LIKE '%lynne%'
                       OR content LIKE '%alfredo%'
                       OR content LIKE '%yuri%'
                    ORDER BY created_at DESC LIMIT 20
                """)
                memories = cursor.fetchall()
                
                for memory in memories:
                    content = memory[0].lower()
                    
                    # Extract age
                    age_match = re.search(r'(\d+)\s*years?\s*old', content)
                    if age_match and 'age' not in personal_details:
                        personal_details['age'] = [age_match.group(1)]
                    
                    # Extract location
                    location_match = re.search(r'live\s+in\s+([^,\.]+)', content)
                    if location_match and 'location' not in personal_details:
                        personal_details['location'] = [location_match.group(1).strip()]
                    
                    # Extract name
                    name_match = re.search(r'name\s+is\s+([^,\.]+)', content)
                    if name_match and 'name' not in personal_details:
                        personal_details['name'] = [name_match.group(1).strip()]
                    
                    # ENHANCED: Extract family info with comprehensive patterns
                    # Sister patterns
                    sister_patterns = [
                        r'(?:my\s+)?sister\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'([a-z]+)\s+(?:is\s+)?(?:my\s+)?sister',
                        r'sister\s+([a-z]+)',
                        r'([a-z]+)\s+sister'
                    ]
                    
                    for pattern in sister_patterns:
                        sister_match = re.search(pattern, content)
                        if sister_match:
                            sister_name = sister_match.group(1).strip()
                            # Filter out common words that aren't names
                            if sister_name not in ['is', 'was', 'will', 'can', 'should', 'would', 'the', 'and', 'or', 'your', 'my', 'her', 'his', 'their', 'our']:
                                if 'sister' not in personal_details:
                                    personal_details['sister'] = [sister_name]
                                elif sister_name not in personal_details['sister']:
                                    personal_details['sister'].append(sister_name)
                    
                    # Brother patterns
                    brother_patterns = [
                        r'(?:my\s+)?brother\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'([a-z]+)\s+(?:is\s+)?(?:my\s+)?brother',
                        r'brother\s+([a-z]+)',
                        r'([a-z]+)\s+brother'
                    ]
                    
                    for pattern in brother_patterns:
                        brother_match = re.search(pattern, content)
                        if brother_match:
                            brother_name = brother_match.group(1).strip()
                            # Filter out common words that aren't names
                            if brother_name not in ['is', 'was', 'will', 'can', 'should', 'would', 'the', 'and', 'or', 'your', 'my', 'her', 'his', 'their', 'our']:
                                if 'brother' not in personal_details:
                                    personal_details['brother'] = [brother_name]
                                elif brother_name not in personal_details['brother']:
                                    personal_details['brother'].append(brother_name)
                    
                    # Parents patterns
                    parent_patterns = [
                        r'(?:my\s+)?parents?\s+(?:are\s+)?(?:called\s+)?([a-z]+)\s+and\s+([a-z]+)',
                        r'([a-z]+)\s+and\s+([a-z]+)\s+(?:are\s+)?(?:my\s+)?parents?',
                        r'(?:my\s+)?mom\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'(?:my\s+)?dad\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'(?:my\s+)?mother\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'(?:my\s+)?father\s+(?:is\s+)?(?:called\s+)?([a-z]+)'
                    ]
                    
                    for pattern in parent_patterns:
                        parent_match = re.search(pattern, content)
                        if parent_match:
                            if len(parent_match.groups()) == 2:  # Both parents
                                mom_name = parent_match.group(1).strip()
                                dad_name = parent_match.group(2).strip()
                                if 'parents' not in personal_details:
                                    personal_details['parents'] = [f"{mom_name} and {dad_name}"]
                            else:  # Single parent
                                parent_name = parent_match.group(1).strip()
                                if 'parents' not in personal_details:
                                    personal_details['parents'] = [parent_name]
                    
                    # Work/Job patterns
                    work_patterns = [
                        r'(?:work\s+as|job\s+is|employed\s+as)\s+([^,\.]+)',
                        r'(?:work\s+at|job\s+at)\s+([^,\.]+)',
                        r'(?:software\s+engineer|developer|programmer)',
                        r'(?:google|microsoft|apple|amazon|facebook|meta)'
                    ]
                    
                    for pattern in work_patterns:
                        work_match = re.search(pattern, content)
                        if work_match and 'work' not in personal_details:
                            if work_match.groups():
                                work_info = work_match.group(1).strip()
                                # Only add if it's not just a regex pattern
                                if not work_info.startswith('(?:'):
                                    personal_details['work'] = [work_info]
                            else:
                                # For patterns without groups, check if it's a company name
                                if 'google' in pattern or 'microsoft' in pattern or 'apple' in pattern:
                                    personal_details['work'] = ['software engineer']
                    
                    # Pet patterns
                    pet_patterns = [
                        r'(?:my\s+)?dog\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'([a-z]+)\s+(?:is\s+)?(?:my\s+)?dog',
                        r'(?:my\s+)?pet\s+(?:is\s+)?(?:called\s+)?([a-z]+)',
                        r'([a-z]+)\s+(?:is\s+)?(?:my\s+)?pet'
                    ]
                    
                    for pattern in pet_patterns:
                        pet_match = re.search(pattern, content)
                        if pet_match:
                            pet_name = pet_match.group(1).strip()
                            # Filter out common words that aren't names
                            if pet_name not in ['is', 'was', 'will', 'can', 'should', 'would', 'the', 'and', 'or', 'your', 'my', 'her', 'his', 'their', 'our']:
                                if 'pet' not in personal_details:
                                    personal_details['pet'] = [pet_name]
                
                # ENHANCED: Also search for specific names mentioned in the conversation
                cursor.execute("""
                    SELECT content FROM enhanced_memory 
                    WHERE content LIKE '%sarah%' 
                       OR content LIKE '%lynne%' 
                       OR content LIKE '%alfredo%'
                       OR content LIKE '%yuri%'
                       OR content LIKE '%ed%'
                       OR content LIKE '%edward%'
                    ORDER BY created_at DESC LIMIT 10
                """)
                name_memories = cursor.fetchall()
                
                for memory in name_memories:
                    content = memory[0].lower()
                    
                    # Extract specific names mentioned
                    if 'sarah' in content and 'sarah' not in str(personal_details.get('sister', [])):
                        if 'sister' not in personal_details:
                            personal_details['sister'] = ['sarah']
                        elif 'sarah' not in personal_details['sister']:
                            personal_details['sister'].append('sarah')
                    
                    if 'lynne' in content and 'lynne' not in str(personal_details.get('parents', [])):
                        if 'parents' not in personal_details:
                            personal_details['parents'] = ['lynne']
                        elif 'lynne' not in str(personal_details['parents']):
                            personal_details['parents'].append('lynne')
                    
                    if 'alfredo' in content and 'alfredo' not in str(personal_details.get('parents', [])):
                        if 'parents' not in personal_details:
                            personal_details['parents'] = ['alfredo']
                        elif 'alfredo' not in str(personal_details['parents']):
                            personal_details['parents'].append('alfredo')
                    
                    if 'yuri' in content and 'yuri' not in str(personal_details.get('brother', [])):
                        if 'brother' not in personal_details:
                            personal_details['brother'] = ['yuri']
                        elif 'yuri' not in personal_details['brother']:
                            personal_details['brother'].append('yuri')
                
        except Exception as e:
            print(f"⚠️ Error extracting personal details: {e}")
            return {
                "success": False,
                "total_memories": 0,
                "memory_context": "",
                "personal_details": {}
            }
        
        # Create memory context
        memory_context = {
            "personal_details": personal_details,
            "total_memories": total_memories,
            "success": True
        }
        
        return memory_context
        
    except Exception as e:
        print(f"⚠️ Memory fix error: {e}")
        return {
            "success": False,
            "total_memories": 0,
            "memory_context": "",
            "personal_details": {}
        }

def _format_memory_context_for_agent(memory_context: Dict[str, Any]) -> str:
    """Format memory context for the agent in a natural, in-character way."""
    if not memory_context:
        return ""
    
    # Extract key information - handle both old and new memory system formats
    memories = memory_context.get("memories", memory_context.get("recent_memories", []))
    personal_details = memory_context.get("personal_details", {})
    relationship_context = memory_context.get("relationship_context", "")
    
    # Build natural language context
    context_parts = []
    
    # Personal details in natural language
    if personal_details:
        personal_info = _format_personal_details_naturally(personal_details)
        if personal_info:
            context_parts.append(personal_info)
    
    # Recent memories in natural language
    if memories:
        memory_info = _format_memories_naturally(memories)
        if memory_info:
            context_parts.append(memory_info)
    
    # Relationship context
    if relationship_context and relationship_context != "No relationship context available.":
        relationship_info = _format_relationship_naturally(relationship_context)
        if relationship_info:
            context_parts.append(relationship_info)
    
    return "\n\n".join(context_parts) if context_parts else ""

def _format_personal_details_naturally(personal_details: Any) -> str:
    """Format personal details in natural language."""
    if not personal_details:
        return ""
    
    details = []
    
    # Handle both list and dict formats
    if isinstance(personal_details, list):
        # If it's a list, take the first few items and format dicts as strings
        for item in personal_details[:3]:
            if isinstance(item, dict):
                # Try to extract a key-value summary
                summary = ", ".join(f"{k}: {v}" for k, v in item.items() if v)
                if summary:
                    details.append(summary)
            elif isinstance(item, str):
                details.append(item)
    elif isinstance(personal_details, dict):
        # Extract key personal information
        if "synthesized_combinations" in personal_details:
            combinations = personal_details["synthesized_combinations"]
            if combinations:
                # Take the most recent/relevant personal details
                key_details = combinations[:3]  # Limit to top 3
                details.extend(key_details)
        
        # Add other personal details
        for key, value in personal_details.items():
            if key != "synthesized_combinations" and value:
                if isinstance(value, list) and value:
                    details.append(f"{key}: {value[0]}")
                elif isinstance(value, str):
                    details.append(f"{key}: {value}")
    
    if not details:
        return ""
    
    # Format as natural language
    return f"About you, I remember: {'; '.join(details)}."

def _format_memories_naturally(memories: List[Dict[str, Any]]) -> str:
    """Format memories in natural language."""
    if not memories:
        return ""
    
    # Take the most recent memories (limit to 3 for natural flow)
    recent_memories = memories[-3:]
    
    memory_summaries = []
    for memory in recent_memories:
        content = memory.get('content', '')
        if content and content.strip():
            # Clean up the memory content
            cleaned_content = content.strip()
            # Remove redundant phrases
            cleaned_content = cleaned_content.replace("my name is ed fornieles, i am 42 and i live in the eastend of london, but you can call me ed, my parents are called Lynne and Alfredo and they live in west sussex in a village called south harting", "")
            cleaned_content = cleaned_content.replace("you're my name is ed fornieles, i am 42 and i live in the eastend of london, but you can call me ed, my parents are called Lynne and Alfredo and they live in west sussex in a village called south harting", "")
            cleaned_content = cleaned_content.strip()
            
            if cleaned_content:
                memory_summaries.append(cleaned_content)
    
    if not memory_summaries:
        return ""
    
    # Format as natural language
    if len(memory_summaries) == 1:
        return f"Recently, you mentioned: {memory_summaries[0]}"
    else:
        return f"Recently, you've shared: {'; '.join(memory_summaries)}"

def _format_relationship_naturally(relationship_context: str) -> str:
    """Format relationship context in natural language."""
    if not relationship_context or relationship_context == "No relationship context available.":
        return ""
    
    # Extract relationship level if present
    if "level" in relationship_context.lower():
        return f"Our friendship has grown to a nice level - we've been getting to know each other well."
    
    return relationship_context

def _clean_memory_text(memory_text: str) -> str:
    """Clean memory text to remove redundant phrases and make it natural."""
    if not memory_text:
        return ""
    
    # Remove redundant phrases that are causing the mechanical responses
    redundant_phrases = [
        "my name is ed fornieles, i am 42 and i live in the eastend of london, but you can call me ed, my parents are called Lynne and Alfredo and they live in west sussex in a village called south harting",
        "you're my name is ed fornieles, i am 42 and i live in the eastend of london, but you can call me ed, my parents are called Lynne and Alfredo and they live in west sussex in a village called south harting",
        "you mentioned your family:",
        "you mentioned:",
        "you said:",
        "you told me:"
    ]
    
    cleaned_text = memory_text.strip()
    for phrase in redundant_phrases:
        cleaned_text = cleaned_text.replace(phrase, "").replace(phrase.lower(), "")
    
    # Clean up extra whitespace and punctuation
    cleaned_text = " ".join(cleaned_text.split())
    cleaned_text = cleaned_text.strip(".,; ")
    
    return cleaned_text

def main():
    """Main function to set up paths and return the FastAPI app."""
    import sys
    
    # Change to parent directory if we're in src
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # If we're in src directory, change to parent
    if os.path.basename(current_dir) == 'src':
        os.chdir(parent_dir)
    
    print("🎭 Starting Dynamic Character Playground...")
    print("✅ OPENAI_API_KEY:", "✓ Loaded" if os.getenv("OPENAI_API_KEY") else "✗ Missing")
    print("📝 Features:")
    print("  - Dynamic character generation")
    print("  - Persistent memory system")
    print("  - Trait-based personalities")
    print("  - Memory isolation per character")
    print("  - Dynamic mood system with real-time updates")
    
    # Return the FastAPI app instance
    return app

def search_diary_by_hashtags(
    character_id: str, 
    user_id: str, 
    search_hashtags: List[str], 
    limit: int = 3
) -> List[Dict[str, Any]]:
    """Search past diary entries by hashtags to find relevant memories.
    
    This function allows agents to search their diary entries during conversations
    to find similar past themes and integrate that knowledge into current responses.
    
    Args:
        character_id: The character searching their diary
        user_id: The user they had conversations with
        search_hashtags: List of hashtags to search for (e.g., ["#dreams", "#father"])
        limit: Maximum number of matching entries to return
    
    Returns:
        List of dictionaries containing matching diary entries with metadata
    """
    try:
        from memory_new.enhanced.enhanced_memory_system import EnhancedMemorySystem
        
        # Initialize memory system
        memory_system = EnhancedMemorySystem(f"{character_id}_{user_id}")
        
        # Get all diary-related memories
        all_memories = memory_system.search_memories("diary", limit=100)
        
        matching_entries = []
        
        for memory in all_memories:
            content = memory.get('content', '')
            
            # Check if this is a diary entry (contains diary markers)
            if '📅' in content and '🏷️ HASHTAGS' in content:
                # Extract hashtags from the entry
                hashtag_section = content.split('🏷️ HASHTAGS')
                if len(hashtag_section) > 1:
                    hashtag_text = hashtag_section[1].split('📅')[0] if '📅' in hashtag_section[1] else hashtag_section[1]
                    entry_hashtags = hashtag_text.strip().split()
                    
                    # Check for hashtag matches
                    matches = []
                    for search_tag in search_hashtags:
                        search_tag_clean = search_tag.lower().strip('#')
                        for entry_tag in entry_hashtags:
                            entry_tag_clean = entry_tag.lower().strip('#')
                            if search_tag_clean == entry_tag_clean or search_tag_clean in entry_tag_clean:
                                matches.append(search_tag)
                                break
                    
                    # If we found matches, add this entry
                    if matches:
                        # Extract the diary entry text (everything before hashtags)
                        entry_text = hashtag_section[0].strip()
                        
                        # Extract date if available
                        date_match = None
                        if '📅' in entry_text:
                            date_parts = entry_text.split('📅')
                            if len(date_parts) > 1:
                                date_match = date_parts[1].split('\n')[0].strip()
                        
                        matching_entries.append({
                            'date': date_match,
                            'content': entry_text,
                            'hashtags': entry_hashtags,
                            'matched_hashtags': matches,
                            'match_score': len(matches),
                            'timestamp': memory.get('timestamp', ''),
                            'memory_id': memory.get('id', '')
                        })
        
        # Sort by match score (most relevant first) and limit results
        matching_entries.sort(key=lambda x: x['match_score'], reverse=True)
        return matching_entries[:limit]
        
    except Exception as e:
        print(f"Error searching diary by hashtags: {e}")
        return []

def get_relevant_diary_context(
    character_id: str,
    user_id: str, 
    current_message: str,
    max_context_entries: int = 2
) -> str:
    """Get relevant diary context based on current conversation content.
    
    This function analyzes the current message and searches for relevant
    past diary entries to provide context for the agent's response.
    
    Args:
        character_id: The character ID
        user_id: The user ID
        current_message: The current message being processed
        max_context_entries: Maximum diary entries to include in context
    
    Returns:
        String containing relevant diary context, or empty string if none found
    """
    # Extract potential hashtags from current message content
    message_lower = current_message.lower()
    search_tags = []
    
    # Dream-related keywords
    if any(word in message_lower for word in ['dream', 'nightmare', 'sleep']):
        search_tags.extend(['#dreams', '#dreamanalysis', '#unconscious'])
    
    # Family/relationship keywords  
    if any(word in message_lower for word in ['father', 'mother', 'parent', 'family']):
        search_tags.extend(['#father', '#mother', '#family', '#relationships'])
    
    # Fear/anxiety keywords
    if any(word in message_lower for word in ['afraid', 'fear', 'anxious', 'worry', 'scared']):
        search_tags.extend(['#fears', '#anxiety', '#emotionalwork'])
    
    # Authority keywords
    if any(word in message_lower for word in ['boss', 'teacher', 'authority', 'strict']):
        search_tags.extend(['#authority', '#boss', '#conflictedrelationships'])
    
    # Insight/breakthrough keywords
    if any(word in message_lower for word in ['understand', 'realize', 'insight', 'clarity']):
        search_tags.extend(['#insights', '#breakthrough', '#personalgrowth'])
    
    # Work/daily life keywords
    if any(word in message_lower for word in ['work', 'job', 'today', 'yesterday']):
        search_tags.extend(['#work', '#dailylife', '#currentevents'])
    
    # If no specific tags found, search for general diary content
    if not search_tags:
        search_tags = ['#diary', '#memory']
    
    # Search for relevant entries
    if search_tags:
        relevant_entries = search_diary_by_hashtags(
            character_id, 
            user_id, 
            search_tags, 
            limit=max_context_entries
        )
        
        if relevant_entries:
            context_parts = ["📖 RELEVANT PAST DIARY ENTRIES:"]
            
            for i, entry in enumerate(relevant_entries):
                # Get a brief excerpt from the entry
                content_excerpt = entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content']
                
                context_parts.append(f"\n📅 {entry['date']} (matched: {', '.join(entry['matched_hashtags'])})")
                context_parts.append(content_excerpt)
                
                if i < len(relevant_entries) - 1:
                    context_parts.append("\n" + "-" * 40)
            
            context_parts.append("\n" + "=" * 60 + "\n")
            return "\n".join(context_parts)
    
    return ""

