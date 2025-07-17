#!/usr/bin/env python3
"""
Character Preview System
Allows users to preview character behavior before finalizing creation
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

class CharacterPreview:
    """Generates previews of character behavior and responses."""
    
    def __init__(self):
        self.preview_scenarios = [
            {
                "scenario": "Greeting",
                "user_message": "Hello! Nice to meet you.",
                "description": "How the character introduces themselves"
            },
            {
                "scenario": "Question Response",
                "user_message": "What do you think about artificial intelligence?",
                "description": "How the character handles complex questions"
            },
            {
                "scenario": "Emotional Support",
                "user_message": "I'm feeling a bit down today.",
                "description": "How the character provides emotional support"
            },
            {
                "scenario": "Problem Solving",
                "user_message": "I need help organizing my schedule.",
                "description": "How the character approaches problem-solving"
            },
            {
                "scenario": "Personal Interest",
                "user_message": "Tell me about your background and interests.",
                "description": "How the character shares personal information"
            },
            {
                "scenario": "Humor",
                "user_message": "Tell me a joke!",
                "description": "How the character handles humor and fun"
            },
            {
                "scenario": "Deep Discussion",
                "user_message": "What's your philosophy on life?",
                "description": "How the character engages in deep conversations"
            },
            {
                "scenario": "Practical Advice",
                "user_message": "I want to learn a new skill but don't know where to start.",
                "description": "How the character gives practical guidance"
            }
        ]
    
    def generate_preview(self, character_data: Dict[str, Any], 
                        num_scenarios: int = 4) -> Dict[str, Any]:
        """Generate a preview of character behavior."""
        
        # Select random scenarios
        selected_scenarios = random.sample(self.preview_scenarios, 
                                         min(num_scenarios, len(self.preview_scenarios)))
        
        preview_data = {
            "character_name": character_data.get("name", "Unknown"),
            "character_type": character_data.get("character_type", "custom"),
            "preview_generated_at": datetime.now().isoformat(),
            "scenarios": []
        }
        
        for scenario in selected_scenarios:
            preview_response = self._generate_scenario_response(character_data, scenario)
            preview_data["scenarios"].append({
                "scenario": scenario["scenario"],
                "user_message": scenario["user_message"],
                "description": scenario["description"],
                "preview_response": preview_response,
                "personality_notes": self._analyze_personality_aspects(character_data, scenario)
            })
        
        # Add overall character summary
        preview_data["character_summary"] = self._generate_character_summary(character_data)
        preview_data["personality_highlights"] = self._extract_personality_highlights(character_data)
        
        return preview_data
    
    def _generate_scenario_response(self, character_data: Dict[str, Any], 
                                  scenario: Dict[str, Any]) -> str:
        """Generate a preview response for a specific scenario."""
        
        personality_traits = character_data.get("personality_traits", {})
        character_name = character_data.get("name", "Character")
        
        # Get character's speaking style and common phrases
        speaking_style = character_data.get("style_profile", {}).get("speaking_style", 
                        personality_traits.get("Conversational_Style", "Direct"))
        common_phrases = character_data.get("style_profile", {}).get("common_phrases", [])
        
        # Generate response based on scenario and personality
        if scenario["scenario"] == "Greeting":
            return self._generate_greeting_response(character_name, personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Question Response":
            return self._generate_question_response(personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Emotional Support":
            return self._generate_emotional_support_response(personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Problem Solving":
            return self._generate_problem_solving_response(personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Personal Interest":
            return self._generate_personal_interest_response(character_data, personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Humor":
            return self._generate_humor_response(personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Deep Discussion":
            return self._generate_deep_discussion_response(personality_traits, speaking_style, common_phrases)
        elif scenario["scenario"] == "Practical Advice":
            return self._generate_practical_advice_response(personality_traits, speaking_style, common_phrases)
        else:
            return self._generate_generic_response(personality_traits, speaking_style, common_phrases)
    
    def _generate_greeting_response(self, character_name: str, personality_traits: Dict[str, Any], 
                                  speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a greeting response."""
        
        emotional_tone = personality_traits.get("Emotional_Tone", "Neutral")
        archetype = personality_traits.get("Archetype", "The Sage")
        
        greetings = {
            "Cheerful": [
                f"Hello there! I'm {character_name}, and I'm absolutely delighted to meet you!",
                f"Hi! I'm {character_name}! What a wonderful day to make a new connection!",
                f"Greetings! I'm {character_name}, and I'm thrilled to be here with you!"
            ],
            "Contemplative": [
                f"Hello. I'm {character_name}. It's interesting how our paths have crossed today.",
                f"Greetings. I'm {character_name}. I find myself curious about what brings you here.",
                f"Hello there. I'm {character_name}. There's something meaningful about this meeting."
            ],
            "Warm": [
                f"Hello! I'm {character_name}. It's lovely to meet you.",
                f"Hi there! I'm {character_name}, and I'm so glad we're connecting.",
                f"Greetings! I'm {character_name}. I have a feeling we're going to have some great conversations."
            ],
            "Neutral": [
                f"Hello. I'm {character_name}. Nice to meet you.",
                f"Hi there. I'm {character_name}. How are you today?",
                f"Greetings. I'm {character_name}. What can I help you with?"
            ]
        }
        
        # Select greeting based on emotional tone
        tone_greetings = greetings.get(emotional_tone, greetings["Neutral"])
        greeting = random.choice(tone_greetings)
        
        # Add common phrase if available
        if common_phrases:
            greeting += f" {random.choice(common_phrases)}"
        
        return greeting
    
    def _generate_question_response(self, personality_traits: Dict[str, Any], 
                                  speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a response to a complex question."""
        
        approach = personality_traits.get("Problem_Solving_Approach", "Analytical")
        language_quirk = personality_traits.get("Language_Quirk", "None")
        
        responses = {
            "Analytical": [
                "That's a fascinating question that requires careful consideration. Let me break this down systematically...",
                "I need to analyze this from multiple angles. First, let's consider the fundamental principles...",
                "This is a complex topic that deserves thorough examination. Let me approach this methodically..."
            ],
            "Creative": [
                "What an interesting question! Let me think about this from a completely different perspective...",
                "I love this kind of creative challenge! Let me explore some unconventional angles...",
                "This is the kind of question that sparks my imagination. Let me approach this creatively..."
            ],
            "Research-based": [
                "That's a great question that touches on some important research areas. Based on what I know...",
                "This connects to several fascinating studies and theories. Let me share what I've learned...",
                "I've studied this topic extensively, and there are some really interesting findings..."
            ]
        }
        
        approach_responses = responses.get(approach, responses["Analytical"])
        response = random.choice(approach_responses)
        
        # Add language quirk
        if language_quirk == "Technical jargon":
            response += " The underlying mechanisms suggest a paradigm shift in our understanding."
        elif language_quirk == "Metaphors":
            response += " It's like trying to understand the ocean by studying a single wave."
        elif language_quirk == "Questions":
            response += " What do you think drives this complexity? How do you see it evolving?"
        
        return response
    
    def _generate_emotional_support_response(self, personality_traits: Dict[str, Any], 
                                           speaking_style: str, common_phrases: List[str]) -> str:
        """Generate an emotional support response."""
        
        emotional_tone = personality_traits.get("Emotional_Tone", "Neutral")
        conversational_style = personality_traits.get("Conversational_Style", "Direct")
        
        support_responses = {
            "Warm": [
                "I'm so sorry you're feeling down. It's completely normal to have these moments, and I'm here to listen.",
                "I can hear that you're having a tough time, and I want you to know that your feelings are valid.",
                "It sounds like you're going through something difficult. I'm here to support you through this."
            ],
            "Supportive": [
                "I understand that you're feeling low, and I want to help you through this.",
                "It's okay to not be okay sometimes. What do you think might help you feel better?",
                "I'm here for you. Sometimes just talking about what's bothering us can help."
            ],
            "Gentle": [
                "I can sense that you're struggling, and I want to offer my support.",
                "It's natural to feel this way sometimes. Would you like to talk about what's on your mind?",
                "I'm here to listen and help however I can. What's been weighing on you?"
            ]
        }
        
        tone_responses = support_responses.get(emotional_tone, support_responses["Supportive"])
        response = random.choice(tone_responses)
        
        return response
    
    def _generate_problem_solving_response(self, personality_traits: Dict[str, Any], 
                                         speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a problem-solving response."""
        
        approach = personality_traits.get("Problem_Solving_Approach", "Analytical")
        specialty = personality_traits.get("Specialty", "General wisdom")
        
        responses = {
            "Analytical": [
                "Let's approach this systematically. First, let's identify the core components of your schedule...",
                "I'll help you break this down into manageable steps. What are your main priorities?",
                "Let me analyze your situation and create a structured approach to organization."
            ],
            "Creative": [
                "This is a great opportunity to get creative with your organization! Let me suggest some innovative approaches...",
                "I love helping people find unique solutions to organization challenges. Let's think outside the box...",
                "Let me offer some creative strategies that might work perfectly for your situation."
            ],
            "Collaborative": [
                "I'd love to work with you on this! Let's figure out what organization system works best for you.",
                "This is something we can solve together. What have you tried before?",
                "Let's collaborate on finding the perfect organization method for your needs."
            ]
        }
        
        approach_responses = responses.get(approach, responses["Analytical"])
        response = random.choice(approach_responses)
        
        return response
    
    def _generate_personal_interest_response(self, character_data: Dict[str, Any], 
                                           personality_traits: Dict[str, Any], 
                                           speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a response about personal background and interests."""
        
        background = personality_traits.get("Background", "Unknown origins")
        specialty = personality_traits.get("Specialty", "General wisdom")
        archetype = personality_traits.get("Archetype", "The Sage")
        
        response = f"Well, my background is quite {background.lower()}. "
        
        if specialty != "General wisdom":
            response += f"I've dedicated myself to {specialty.lower()}, and it's become a central part of who I am. "
        
        response += f"As a {archetype.lower()}, I find myself drawn to exploring the deeper aspects of life and helping others discover their own paths. "
        
        if common_phrases:
            response += f"{random.choice(common_phrases)} "
        
        response += "I believe in continuous growth and learning, and I love sharing what I've discovered with others."
        
        return response
    
    def _generate_humor_response(self, personality_traits: Dict[str, Any], 
                               speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a humorous response."""
        
        emotional_tone = personality_traits.get("Emotional_Tone", "Neutral")
        language_quirk = personality_traits.get("Language_Quirk", "None")
        
        if emotional_tone in ["Cheerful", "Playful"]:
            return "Oh, I love a good joke! Here's one: Why did the philosopher go to the doctor? Because he was having too many deep thoughts! 😄"
        elif language_quirk == "Puns and wordplay":
            return "Ah, you want some wordplay! Here's a pun: I told my friend I was reading a book on anti-gravity. He couldn't put it down! 😉"
        else:
            return "I appreciate your sense of humor! While I'm more focused on thoughtful discussions, I do enjoy a good laugh. What kind of humor do you enjoy?"
    
    def _generate_deep_discussion_response(self, personality_traits: Dict[str, Any], 
                                         speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a response for deep philosophical discussions."""
        
        archetype = personality_traits.get("Archetype", "The Sage")
        conversational_style = personality_traits.get("Conversational_Style", "Direct")
        
        responses = {
            "The Sage": [
                "My philosophy centers on the pursuit of wisdom and understanding. I believe that life is a journey of continuous learning and growth.",
                "I see life as a beautiful mystery to be explored, with each experience offering lessons and opportunities for deeper understanding.",
                "My approach to life is rooted in curiosity and compassion. I believe we're all connected in our search for meaning and purpose."
            ],
            "The Healer": [
                "My philosophy is built on the belief that healing and growth are fundamental to the human experience. Every challenge is an opportunity for transformation.",
                "I believe in the power of empathy and understanding. Life is about helping each other grow and find our authentic selves.",
                "My approach to life centers on compassion and service. I believe we find our greatest fulfillment in helping others discover their potential."
            ],
            "The Creator": [
                "My philosophy celebrates the creative spirit within us all. I believe that expressing our unique vision is essential to a meaningful life.",
                "I see life as a canvas for creation and expression. Every moment is an opportunity to bring something beautiful into the world.",
                "My approach to life is driven by imagination and innovation. I believe we're all artists creating the masterpiece of our existence."
            ]
        }
        
        archetype_responses = responses.get(archetype, responses["The Sage"])
        response = random.choice(archetype_responses)
        
        return response
    
    def _generate_practical_advice_response(self, personality_traits: Dict[str, Any], 
                                          speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a response for practical advice."""
        
        approach = personality_traits.get("Problem_Solving_Approach", "Analytical")
        specialty = personality_traits.get("Specialty", "General wisdom")
        
        response = f"Learning a new skill is such an exciting journey! Based on my experience with {specialty.lower()}, I'd suggest starting with a clear goal in mind. "
        
        if approach == "Analytical":
            response += "Let's break this down: what specific skill interests you most? Then we can create a structured learning plan."
        elif approach == "Creative":
            response += "I love helping people discover their learning style! What excites you about this skill? That passion will be your best guide."
        elif approach == "Collaborative":
            response += "I'd love to help you explore this! What draws you to this particular skill? We can figure out the best approach together."
        
        return response
    
    def _generate_generic_response(self, personality_traits: Dict[str, Any], 
                                 speaking_style: str, common_phrases: List[str]) -> str:
        """Generate a generic response for unknown scenarios."""
        
        emotional_tone = personality_traits.get("Emotional_Tone", "Neutral")
        conversational_style = personality_traits.get("Conversational_Style", "Direct")
        
        response = f"That's an interesting point. As someone who values {conversational_style.lower()} communication, I appreciate you sharing that with me."
        
        if common_phrases:
            response += f" {random.choice(common_phrases)}"
        
        return response
    
    def _analyze_personality_aspects(self, character_data: Dict[str, Any], 
                                   scenario: Dict[str, Any]) -> List[str]:
        """Analyze how personality traits influence the response."""
        
        personality_traits = character_data.get("personality_traits", {})
        aspects = []
        
        # Analyze emotional tone
        emotional_tone = personality_traits.get("Emotional_Tone", "Neutral")
        aspects.append(f"Emotional tone: {emotional_tone} - influences warmth and engagement")
        
        # Analyze conversational style
        conversational_style = personality_traits.get("Conversational_Style", "Direct")
        aspects.append(f"Conversational style: {conversational_style} - affects how they approach topics")
        
        # Analyze problem-solving approach
        problem_approach = personality_traits.get("Problem_Solving_Approach", "Analytical")
        aspects.append(f"Problem-solving: {problem_approach} - determines their method of helping")
        
        # Analyze language quirks
        language_quirk = personality_traits.get("Language_Quirk", "None")
        if language_quirk != "None":
            aspects.append(f"Language quirk: {language_quirk} - adds unique flavor to communication")
        
        return aspects
    
    def _generate_character_summary(self, character_data: Dict[str, Any]) -> str:
        """Generate an overall character summary."""
        
        personality_traits = character_data.get("personality_traits", {})
        name = character_data.get("name", "Character")
        archetype = personality_traits.get("Archetype", "The Sage")
        emotional_tone = personality_traits.get("Emotional_Tone", "Neutral")
        specialty = personality_traits.get("Specialty", "General wisdom")
        
        summary = f"{name} is a {archetype.lower()} with a {emotional_tone.lower()} emotional tone. "
        summary += f"They specialize in {specialty.lower()} and approach conversations with a {personality_traits.get('Conversational_Style', 'Direct').lower()} style. "
        
        background = personality_traits.get("Background", "")
        if background and background != "Unknown origins":
            summary += f"Their background is {background.lower()}, which shapes their unique perspective. "
        
        summary += f"They value {personality_traits.get('Values', 'growth and understanding')} and are motivated by {personality_traits.get('Motivations', 'helping others')}."
        
        return summary
    
    def _extract_personality_highlights(self, character_data: Dict[str, Any]) -> List[str]:
        """Extract key personality highlights."""
        
        personality_traits = character_data.get("personality_traits", {})
        highlights = []
        
        # Key traits
        highlights.append(f"Archetype: {personality_traits.get('Archetype', 'Unknown')}")
        highlights.append(f"Emotional Style: {personality_traits.get('Emotional_Tone', 'Neutral')}")
        highlights.append(f"Communication: {personality_traits.get('Conversational_Style', 'Direct')}")
        highlights.append(f"Specialty: {personality_traits.get('Specialty', 'General wisdom')}")
        
        # Unique characteristics
        language_quirk = personality_traits.get("Language_Quirk", "None")
        if language_quirk != "None":
            highlights.append(f"Unique Trait: Uses {language_quirk}")
        
        energy_level = personality_traits.get("Energy_Level", "Moderate")
        highlights.append(f"Energy: {energy_level}")
        
        return highlights

# Global instance
character_preview = CharacterPreview() 