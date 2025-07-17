#!/usr/bin/env python3
"""
Simulate Relationship Growth

This script simulates a meaningful conversation between a user and a character to increase the connection level.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from systems.relationship_system import RelationshipSystem
from characters.character_generator import CharacterGenerator
import time

user_id = "ed_fornieles"
character_id = "historical_isaac_newton"

# Conversation messages (user, character response)
conversation = [
    ("Hello Sir Isaac! I'm fascinated by your work on gravity. How did you come up with the idea?",
     "Greetings! The idea of gravity came to me as I pondered the motion of the moon and the fall of an apple. I realized the same force could govern both."),
    ("That's incredible. Did you ever doubt your own theories?",
     "Indeed, I questioned my findings many times. Scientific progress demands skepticism and rigorous proof."),
    ("What motivated you to keep searching for answers, even when it was difficult?",
     "A relentless curiosity and a desire to uncover the laws of nature drove me onward, even in solitude."),
    ("Do you believe your discoveries changed the world?",
     "I believe they provided a new framework for understanding the universe, but science is always evolving.")
]

def print_connection_level():
    relationship_system = RelationshipSystem()
    status = relationship_system.get_relationship_status(user_id, character_id)
    level = status.get("level", 0)
    print(f"Current connection level between {user_id} and {character_id}: {level}")

if __name__ == "__main__":
    print("\n--- Before Conversation ---")
    print_connection_level()

    relationship_system = RelationshipSystem()
    for user_msg, char_resp in conversation:
        relationship_system.record_conversation_exchange(user_id, character_id, user_msg, char_resp, conversation_duration=2)
        time.sleep(2)  # Add delay between messages to respect relationship system timing

    print("\n--- After Conversation ---")
    print_connection_level()
    # Print full relationship metrics for debugging
    status = relationship_system.get_relationship_status(user_id, character_id)
    print("Full relationship metrics:")
    for k, v in status.get("metrics", {}).items():
        print(f"  {k}: {v}")
    if "next_level_progress" in status:
        print("Next level progress:")
        for req, prog in status["next_level_progress"].items():
            print(f"  {req}: {prog}") 