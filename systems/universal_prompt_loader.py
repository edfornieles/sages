#!/usr/bin/env python3
"""
Universal Prompt Loader

This module loads universal prompts and rules from a text file and integrates them
with the character generation system, similar to the original sages project.
"""

from pathlib import Path
from typing import List, Optional


class UniversalPromptLoader:
    """Loads and manages universal prompts for all characters."""
    
    def __init__(self, prompts_file: str = "universal_prompts.txt"):
        """Initialize the prompt loader with a prompts file."""
        self.prompts_file = prompts_file
        self._cached_prompts: Optional[List[str]] = None
    
    def load_prompts(self) -> List[str]:
        """Load prompts from the text file, filtering out comments and empty lines."""
        if self._cached_prompts is not None:
            return self._cached_prompts
            
        prompts = []
        prompts_path = Path(self.prompts_file)
        
        if not prompts_path.exists():
            print(f"Warning: Universal prompts file not found: {self.prompts_file}")
            return []
        
        try:
            with open(prompts_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        prompts.append(line)
            
            self._cached_prompts = prompts
            return prompts
            
        except Exception as e:
            print(f"Error loading universal prompts: {e}")
            return []
    
    def get_universal_instructions(self) -> List[str]:
        """Get universal instructions formatted for phidata agents."""
        prompts = self.load_prompts()
        if not prompts:
            return []
        
        # Format prompts as instructions
        instructions = [
            "UNIVERSAL CHARACTER GUIDELINES:",
            "Follow these universal rules while maintaining your unique personality:"
        ]
        
        for prompt in prompts:
            instructions.append(f"- {prompt}")
        
        return instructions
    
    def get_universal_prompt_text(self) -> str:
        """Get universal prompts as a single formatted text block."""
        prompts = self.load_prompts()
        if not prompts:
            return ""
        
        prompt_text = "\n\nUNIVERSAL CHARACTER GUIDELINES:\n"
        prompt_text += "Follow these universal rules while maintaining your unique personality:\n\n"
        
        for prompt in prompts:
            prompt_text += f"• {prompt}\n"
        
        return prompt_text
    
    def reload_prompts(self):
        """Force reload prompts from file (useful for development)."""
        self._cached_prompts = None
        return self.load_prompts()


# Global instance for easy access
universal_prompts = UniversalPromptLoader()


def get_universal_instructions() -> List[str]:
    """Convenience function to get universal instructions."""
    return universal_prompts.get_universal_instructions()


def get_universal_prompt_text() -> str:
    """Convenience function to get universal prompt text."""
    return universal_prompts.get_universal_prompt_text()


if __name__ == "__main__":
    # Test the loader
    loader = UniversalPromptLoader()
    prompts = loader.load_prompts()
    
    print("Loaded Universal Prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. {prompt}")
    
    print("\nFormatted Instructions:")
    instructions = loader.get_universal_instructions()
    for instruction in instructions:
        print(instruction)
    
    print("\nFormatted Text Block:")
    print(loader.get_universal_prompt_text()) 