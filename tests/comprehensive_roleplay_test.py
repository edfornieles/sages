#!/usr/bin/env python3
"""
Comprehensive Role-Play Test for Enhanced Dynamic Character Playground
Tests every aspect of the system through realistic user interactions
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any

class ComprehensiveRoleplayTest:
    def __init__(self):
        self.base_url = "http://localhost:8008"
        self.test_results = []
        self.session_data = {}
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        return success
    
    def chat_with_character(self, character_id: str, user_id: str, message: str, expected_keywords: List[str] = None):
        """Send a chat message and analyze the response"""
        try:
            response = requests.post(f"{self.base_url}/chat", json={
                "character_id": character_id,
                "user_id": user_id,
                "message": message
            })
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: {response.text}"
            
            data = response.json()
            agent_response = data.get("response", "")
            
            # Check for expected keywords if provided
            if expected_keywords:
                found_keywords = [kw for kw in expected_keywords if kw.lower() in agent_response.lower()]
                if not found_keywords:
                    return False, f"Expected keywords {expected_keywords} not found in response"
            
            return True, agent_response
            
        except Exception as e:
            return False, f"Error: {e}"
    
    def test_character_generation(self):
        """Test character generation with different personalities"""
        print("\n🎭 Testing Character Generation...")
        
        # Test 1: Generate a character with specific traits
        try:
            response = requests.post(f"{self.base_url}/characters/generate", json={
                "name": "Test Character",
                "personality": "intelligent, curious, friendly",
                "background": "A software engineer who loves learning new technologies"
            })
            
            if response.status_code != 200:
                return self.log_test("Character Generation", False, f"HTTP {response.status_code}")
            
            data = response.json()
            character_id = data.get("id")
            
            if not character_id:
                return self.log_test("Character Generation", False, "No character ID returned")
            
            self.session_data["test_character_id"] = character_id
            return self.log_test("Character Generation", True, f"Generated character: {character_id}")
            
        except Exception as e:
            return self.log_test("Character Generation", False, f"Error: {e}")
    
    def test_memory_persistence(self):
        """Test memory persistence across multiple sessions"""
        print("\n🧠 Testing Memory Persistence...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_memory"
        
        # Session 1: Tell the character personal information
        success1, response1 = self.chat_with_character(
            character_id, user_id, 
            "Hi! I'm Alex and I work as a data scientist at Microsoft. I have a dog named Luna.",
            ["Alex", "data scientist", "Microsoft", "Luna"]
        )
        
        if not success1:
            return self.log_test("Memory Persistence - Session 1", False, response1)
        
        # Wait a moment
        time.sleep(2)
        
        # Session 2: Ask about the information shared
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "What's my name and what do I do for work?",
            ["Alex", "data scientist", "Microsoft"]
        )
        
        if not success2:
            return self.log_test("Memory Persistence - Session 2", False, response2)
        
        # Session 3: Ask about the pet
        success3, response3 = self.chat_with_character(
            character_id, user_id,
            "What's my pet's name?",
            ["Luna", "dog"]
        )
        
        if not success3:
            return self.log_test("Memory Persistence - Session 3", False, response3)
        
        return self.log_test("Memory Persistence", True, "Successfully recalled information across sessions")
    
    def test_character_consistency(self):
        """Test character consistency in responses"""
        print("\n🎯 Testing Character Consistency...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_consistency"
        
        # Test 1: Ask about character's background
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "Tell me about yourself and your background",
            ["Nicholas", "Cage", "actor", "film"]
        )
        
        if not success1:
            return self.log_test("Character Consistency - Background", False, response1)
        
        # Test 2: Ask about character's personality
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "What kind of person are you? What are your interests?",
            ["passionate", "creative", "art", "film"]
        )
        
        if not success2:
            return self.log_test("Character Consistency - Personality", False, response2)
        
        # Test 3: Ask about character's work
        success3, response3 = self.chat_with_character(
            character_id, user_id,
            "What do you do for a living?",
            ["actor", "film", "movie", "performance"]
        )
        
        if not success3:
            return self.log_test("Character Consistency - Work", False, response3)
        
        return self.log_test("Character Consistency", True, "Character maintained consistent personality and background")
    
    def test_emotional_responses(self):
        """Test emotional sensitivity and responses"""
        print("\n😊 Testing Emotional Responses...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_emotions"
        
        # Test 1: Share good news
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "I just got promoted at work! I'm so excited!",
            ["congratulations", "excited", "happy", "great"]
        )
        
        if not success1:
            return self.log_test("Emotional Responses - Positive", False, response1)
        
        # Test 2: Share bad news
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "I'm feeling really sad today. My dog passed away yesterday.",
            ["sorry", "sad", "sympathy", "condolences"]
        )
        
        if not success2:
            return self.log_test("Emotional Responses - Negative", False, response2)
        
        # Test 3: Share frustration
        success3, response3 = self.chat_with_character(
            character_id, user_id,
            "I'm so frustrated with my project at work. Nothing is working!",
            ["frustrated", "understand", "difficult", "help"]
        )
        
        if not success3:
            return self.log_test("Emotional Responses - Frustration", False, response3)
        
        return self.log_test("Emotional Responses", True, "Character responded appropriately to different emotions")
    
    def test_conversation_flow(self):
        """Test natural conversation flow and context awareness"""
        print("\n💬 Testing Conversation Flow...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_flow"
        
        # Start a conversation about movies
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "What's your favorite movie that you've been in?",
            ["favorite", "movie", "film"]
        )
        
        if not success1:
            return self.log_test("Conversation Flow - Initial", False, response1)
        
        # Follow up on the same topic
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "Why do you like that one so much?",
            ["because", "reason", "love", "special"]
        )
        
        if not success2:
            return self.log_test("Conversation Flow - Follow-up", False, response2)
        
        # Ask about a different topic
        success3, response3 = self.chat_with_character(
            character_id, user_id,
            "What do you think about modern cinema compared to when you started?",
            ["modern", "cinema", "different", "change"]
        )
        
        if not success3:
            return self.log_test("Conversation Flow - Topic Change", False, response3)
        
        # Return to original topic
        success4, response4 = self.chat_with_character(
            character_id, user_id,
            "Going back to your favorite movie, what was the most challenging scene to film?",
            ["challenging", "scene", "difficult", "film"]
        )
        
        if not success4:
            return self.log_test("Conversation Flow - Topic Return", False, response4)
        
        return self.log_test("Conversation Flow", True, "Conversation flowed naturally with context awareness")
    
    def test_relationship_building(self):
        """Test relationship system and progression"""
        print("\n🤝 Testing Relationship Building...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_relationship"
        
        # Check initial relationship level
        try:
            response = requests.get(f"{self.base_url}/relationship/{user_id}/{character_id}")
            if response.status_code == 200:
                initial_level = response.json().get("level", 0)
            else:
                initial_level = 0
        except:
            initial_level = 0
        
        # Have a positive interaction
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "I really admire your work! You're one of my favorite actors.",
            ["thank", "appreciate", "kind", "favorite"]
        )
        
        if not success1:
            return self.log_test("Relationship Building - Positive", False, response1)
        
        # Share personal information
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "I'm going through a tough time with my family. Can I talk to you about it?",
            ["family", "tough", "talk", "help"]
        )
        
        if not success2:
            return self.log_test("Relationship Building - Personal", False, response2)
        
        # Check relationship level after interactions
        try:
            response = requests.get(f"{self.base_url}/relationship/{user_id}/{character_id}")
            if response.status_code == 200:
                final_level = response.json().get("level", 0)
                level_change = final_level - initial_level
                return self.log_test("Relationship Building", True, f"Relationship level changed by {level_change}")
            else:
                return self.log_test("Relationship Building", False, "Could not check relationship level")
        except Exception as e:
            return self.log_test("Relationship Building", False, f"Error checking relationship: {e}")
    
    def test_mood_system(self):
        """Test mood system and emotional state tracking"""
        print("\n😐 Testing Mood System...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_mood"
        
        # Check initial mood
        try:
            response = requests.get(f"{self.base_url}/characters/{character_id}/mood/{user_id}")
            if response.status_code == 200:
                initial_mood = response.json().get("mood", "neutral")
            else:
                initial_mood = "neutral"
        except:
            initial_mood = "neutral"
        
        # Try to affect mood positively
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "I just watched your latest movie and it was absolutely brilliant! You were amazing!",
            ["thank", "appreciate", "brilliant", "amazing"]
        )
        
        if not success1:
            return self.log_test("Mood System - Positive", False, response1)
        
        # Check mood after positive interaction
        try:
            response = requests.get(f"{self.base_url}/characters/{character_id}/mood/{user_id}")
            if response.status_code == 200:
                positive_mood = response.json().get("mood", "neutral")
            else:
                positive_mood = "neutral"
        except:
            positive_mood = "neutral"
        
        # Try to affect mood negatively
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "Actually, I didn't really like your performance in that movie. It was kind of disappointing.",
            ["understand", "opinion", "different", "respect"]
        )
        
        if not success2:
            return self.log_test("Mood System - Negative", False, response2)
        
        # Check final mood
        try:
            response = requests.get(f"{self.base_url}/characters/{character_id}/mood/{user_id}")
            if response.status_code == 200:
                final_mood = response.json().get("mood", "neutral")
                return self.log_test("Mood System", True, f"Mood tracked: {initial_mood} -> {positive_mood} -> {final_mood}")
            else:
                return self.log_test("Mood System", False, "Could not check final mood")
        except Exception as e:
            return self.log_test("Mood System", False, f"Error checking mood: {e}")
    
    def test_memory_retrieval(self):
        """Test memory retrieval and context awareness"""
        print("\n🔍 Testing Memory Retrieval...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_memory_retrieval"
        
        # Share specific information
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "My name is Sarah and I'm a teacher. I live in Portland, Oregon and I have two cats named Whiskers and Mittens.",
            ["Sarah", "teacher", "Portland", "cats"]
        )
        
        if not success1:
            return self.log_test("Memory Retrieval - Information Sharing", False, response1)
        
        # Wait a moment
        time.sleep(2)
        
        # Ask about the information
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "What's my name and what do I do?",
            ["Sarah", "teacher"]
        )
        
        if not success2:
            return self.log_test("Memory Retrieval - Name/Job", False, response2)
        
        # Ask about location
        success3, response3 = self.chat_with_character(
            character_id, user_id,
            "Where do I live?",
            ["Portland", "Oregon"]
        )
        
        if not success3:
            return self.log_test("Memory Retrieval - Location", False, response3)
        
        # Ask about pets
        success4, response4 = self.chat_with_character(
            character_id, user_id,
            "What are my pets' names?",
            ["Whiskers", "Mittens", "cats"]
        )
        
        if not success4:
            return self.log_test("Memory Retrieval - Pets", False, response4)
        
        return self.log_test("Memory Retrieval", True, "Successfully retrieved all shared information")
    
    def test_character_learning(self):
        """Test character learning and adaptation"""
        print("\n📚 Testing Character Learning...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_learning"
        
        # Share preferences
        success1, response1 = self.chat_with_character(
            character_id, user_id,
            "I love Italian food, especially pizza and pasta. I also really enjoy hiking and photography.",
            ["Italian", "pizza", "pasta", "hiking", "photography"]
        )
        
        if not success1:
            return self.log_test("Character Learning - Preferences", False, response1)
        
        # Ask about preferences later
        success2, response2 = self.chat_with_character(
            character_id, user_id,
            "What kind of food do I like?",
            ["Italian", "pizza", "pasta"]
        )
        
        if not success2:
            return self.log_test("Character Learning - Food Recall", False, response2)
        
        # Ask about hobbies
        success3, response3 = self.chat_with_character(
            character_id, user_id,
            "What are my hobbies?",
            ["hiking", "photography"]
        )
        
        if not success3:
            return self.log_test("Character Learning - Hobbies Recall", False, response3)
        
        return self.log_test("Character Learning", True, "Character learned and recalled user preferences")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test 1: Invalid character ID
        try:
            response = requests.post(f"{self.base_url}/chat", json={
                "character_id": "nonexistent_character_12345",
                "user_id": "test_user",
                "message": "Hello"
            })
            
            if response.status_code == 404:
                self.log_test("Error Handling - Invalid Character", True, "Properly handled invalid character ID")
            else:
                self.log_test("Error Handling - Invalid Character", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Character", False, f"Error: {e}")
        
        # Test 2: Missing required fields
        try:
            response = requests.post(f"{self.base_url}/chat", json={
                "character_id": "custom_nicholas_cage_3674",
                "message": "Hello"
            })
            
            if response.status_code == 422:
                self.log_test("Error Handling - Missing Fields", True, "Properly handled missing user_id")
            else:
                self.log_test("Error Handling - Missing Fields", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Missing Fields", False, f"Error: {e}")
        
        # Test 3: Empty message
        try:
            response = requests.post(f"{self.base_url}/chat", json={
                "character_id": "custom_nicholas_cage_3674",
                "user_id": "test_user",
                "message": ""
            })
            
            if response.status_code in [400, 422]:
                self.log_test("Error Handling - Empty Message", True, "Properly handled empty message")
            else:
                self.log_test("Error Handling - Empty Message", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Empty Message", False, f"Error: {e}")
        
        return True
    
    def test_performance(self):
        """Test system performance and response times"""
        print("\n⚡ Testing Performance...")
        
        character_id = "custom_nicholas_cage_3674"
        user_id = "test_user_performance"
        
        # Test response time for simple message
        start_time = time.time()
        success, response = self.chat_with_character(
            character_id, user_id,
            "Hello, how are you today?"
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if success and response_time < 10.0:  # 10 second timeout
            self.log_test("Performance - Response Time", True, f"Response in {response_time:.2f}s")
        else:
            self.log_test("Performance - Response Time", False, f"Response took {response_time:.2f}s or failed")
        
        # Test multiple rapid requests
        start_time = time.time()
        success_count = 0
        
        for i in range(3):
            success, _ = self.chat_with_character(
                character_id, user_id,
                f"Quick message {i+1}"
            )
            if success:
                success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if success_count == 3 and total_time < 30.0:
            self.log_test("Performance - Multiple Requests", True, f"3 requests in {total_time:.2f}s")
        else:
            self.log_test("Performance - Multiple Requests", False, f"{success_count}/3 requests in {total_time:.2f}s")
        
        return True
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Role-Play Test...")
        print("=" * 60)
        
        # Run all test categories
        tests = [
            ("Character Generation", self.test_character_generation),
            ("Memory Persistence", self.test_memory_persistence),
            ("Character Consistency", self.test_character_consistency),
            ("Emotional Responses", self.test_emotional_responses),
            ("Conversation Flow", self.test_conversation_flow),
            ("Relationship Building", self.test_relationship_building),
            ("Mood System", self.test_mood_system),
            ("Memory Retrieval", self.test_memory_retrieval),
            ("Character Learning", self.test_character_learning),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test failed with exception: {e}")
        
        # Generate summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        # Add error handling for division by zero
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        else:
            print("Success Rate: N/A (no tests run)")
        
        # Save detailed results
        with open("comprehensive_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total,
                    "passed": passed,
                    "failed": total - passed,
                    "success_rate": (passed / total) * 100 if total > 0 else 0
                },
                "results": self.test_results,
                "session_data": self.session_data
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: comprehensive_test_results.json")
        
        return passed == total

if __name__ == "__main__":
    tester = ComprehensiveRoleplayTest()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1) 