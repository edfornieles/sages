#!/usr/bin/env python3
"""
Organize root directory according to best practices.
Keep only essential production files in root, move development files to appropriate locations.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create organized directory structure."""
    directories = [
        'src',           # Source code
        'config',        # Configuration files
        'docs',          # Documentation
        'scripts',       # Utility scripts
        'data',          # Data files (databases, generated content)
        'data/databases',
        'data/characters',
        'data/memories',
        'tests',         # Test files
        'archive/old_versions',  # Old versions of current files
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {dir_path}")

def get_file_organization():
    """Define how files should be organized."""
    return {
        # Keep in root - essential production files
        'root': [
            'README.md',
            'requirements.txt',
            'setup.py',
            '.gitignore',
            '.env',
            '.env.example',
            'Dockerfile',
            'docker-compose.yml',
            'pyproject.toml',
        ],
        
        # Move to src/ - main source code
        'src': [
            'dynamic_character_playground_enhanced.py',
            'character_generator.py',
            'enhanced_memory_system.py',
            'entity_memory_system.py',
            'mood_system.py',
            'relationship_system.py',
            'ambitions_system.py',
            'learning_system.py',
            'universal_prompt_loader.py',
            'ultra_fast_response_system.py',
            'performance_optimization.py',
        ],
        
        # Move to config/ - configuration files
        'config': [
            'character_config.json',
            'cache_config.json',
            'optimized_prompts.json',
            'optimized_character_prompts.json',
            'relationship_config.json',
        ],
        
        # Move to scripts/ - utility scripts
        'scripts': [
            'start_enhanced_playground.sh',
            'emergency_database_fix.py',
            'memory_system_patch.py',
            'character_identity_fix.py',
        ],
        
        # Move to docs/ - documentation
        'docs': [
            'PROJECT_STRUCTURE.md',
            'ENHANCED_PLAYGROUND_SETUP.md',
            'STARTUP_GUIDE.md',
        ],
        
        # Move to data/ - data files
        'data/databases': [
            'character_ambitions.db',
            'character_learning.db',
            'relationship_depth.db',
            'relationships.db',
        ],
        
        # Move to data/characters
        'data/characters': [
            'generated_characters',  # directory
        ],
        
        # Move to data/memories
        'data/memories': [
            'memories',  # directory
        ],
        
        # Archive - development/legacy files
        'archive/old_versions': [
            'service.log',
        ],
    }

def organize_files():
    """Organize files according to the structure."""
    organization = get_file_organization()
    
    for target_dir, files in organization.items():
        if target_dir == 'root':
            continue  # Skip root files
            
        print(f"\n📂 Organizing {target_dir}/")
        
        for file_item in files:
            if os.path.exists(file_item):
                target_path = os.path.join(target_dir, os.path.basename(file_item))
                
                if os.path.isdir(file_item):
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.move(file_item, target_path)
                    print(f"  📁 Moved directory: {file_item} → {target_path}")
                else:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    shutil.move(file_item, target_path)
                    print(f"  📄 Moved file: {file_item} → {target_path}")
            else:
                print(f"  ⚠️ Not found: {file_item}")

def update_import_paths():
    """Update import paths in the main application file."""
    main_file = 'src/dynamic_character_playground_enhanced.py'
    if not os.path.exists(main_file):
        print("⚠️ Main file not found, skipping import updates")
        return
    
    # Read the file
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Update relative imports to use src directory
    import_updates = {
        'from character_generator import': 'from src.character_generator import',
        'from universal_prompt_loader import': 'from src.universal_prompt_loader import',
        'from mood_system import': 'from src.mood_system import',
        'from relationship_system import': 'from src.relationship_system import',
        'from ambitions_system import': 'from src.ambitions_system import',
        'from learning_system import': 'from src.learning_system import',
        'from enhanced_memory_system import': 'from src.enhanced_memory_system import',
        'from performance_optimization import': 'from src.performance_optimization import',
    }
    
    for old_import, new_import in import_updates.items():
        content = content.replace(old_import, new_import)
    
    # Update config file paths
    config_updates = {
        "'character_config.json'": "'config/character_config.json'",
        '"character_config.json"': '"config/character_config.json"',
        "'cache_config.json'": "'config/cache_config.json'",
        '"cache_config.json"': '"config/cache_config.json"',
        "'optimized_prompts.json'": "'config/optimized_prompts.json'",
        '"optimized_prompts.json"': '"config/optimized_prompts.json"',
        "'optimized_character_prompts.json'": "'config/optimized_character_prompts.json'",
        '"optimized_character_prompts.json"': '"config/optimized_character_prompts.json"',
        "'relationship_config.json'": "'config/relationship_config.json'",
        '"relationship_config.json"': '"config/relationship_config.json"',
    }
    
    for old_path, new_path in config_updates.items():
        content = content.replace(old_path, new_path)
    
    # Update database paths
    db_updates = {
        "'character_ambitions.db'": "'data/databases/character_ambitions.db'",
        '"character_ambitions.db"': '"data/databases/character_ambitions.db"',
        "'character_learning.db'": "'data/databases/character_learning.db'",
        '"character_learning.db"': '"data/databases/character_learning.db"',
        "'relationship_depth.db'": "'data/databases/relationship_depth.db'",
        '"relationship_depth.db"': '"data/databases/relationship_depth.db"',
        "'relationships.db'": "'data/databases/relationships.db'",
        '"relationships.db"': '"data/databases/relationships.db"',
        "'memories/'": "'data/memories/'",
        '"memories/"': '"data/memories/"',
        "'generated_characters/'": "'data/characters/generated_characters/'",
        '"generated_characters/"': '"data/characters/generated_characters/"',
    }
    
    for old_path, new_path in db_updates.items():
        content = content.replace(old_path, new_path)
    
    # Write the updated content
    with open(main_file, 'w') as f:
        f.write(content)
    
    print("✅ Updated import paths and file references")

def create_main_launcher():
    """Create a main launcher script in the root directory."""
    launcher_content = '''#!/usr/bin/env python3
"""
Enhanced Dynamic Character Playground - Main Launcher
Production-ready character interaction system with advanced AI capabilities.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from dynamic_character_playground_enhanced import main

if __name__ == "__main__":
    main()
'''
    
    with open('main.py', 'w') as f:
        f.write(launcher_content)
    
    # Make it executable
    os.chmod('main.py', 0o755)
    print("✅ Created main.py launcher")

def create_requirements_txt():
    """Create a requirements.txt file with all dependencies."""
    requirements = '''# Enhanced Dynamic Character Playground Dependencies
fastapi>=0.104.1
uvicorn>=0.24.0
pydantic>=2.5.0
python-dotenv>=1.0.0
pandas>=2.1.0
openai>=1.3.0
phidata>=2.4.0
sqlite3-utils>=3.35.0
asyncio-mqtt>=0.13.0
httpx>=0.25.0
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")

def create_setup_py():
    """Create a setup.py file for the project."""
    setup_content = '''from setuptools import setup, find_packages

setup(
    name="enhanced-character-playground",
    version="2.0.0",
    description="Production-ready AI character interaction system with advanced memory and personality features",
    author="Enhanced Character Playground Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.1.0",
        "openai>=1.3.0",
        "phidata>=2.4.0",
        "httpx>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "character-playground=src.dynamic_character_playground_enhanced:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
    
    with open('setup.py', 'w') as f:
        f.write(setup_content)
    
    print("✅ Created setup.py")

def main():
    """Main organization function."""
    print("🗂️ ORGANIZING ROOT DIRECTORY FOR BEST PRACTICES")
    print("=" * 60)
    
    # Create directory structure
    create_directory_structure()
    
    # Organize files
    organize_files()
    
    # Update import paths
    update_import_paths()
    
    # Create production files
    create_main_launcher()
    create_requirements_txt()
    create_setup_py()
    
    print("\n" + "=" * 60)
    print("✅ ROOT DIRECTORY ORGANIZATION COMPLETE!")
    print("\n📁 New structure:")
    print("  📄 main.py              # Main launcher")
    print("  📄 requirements.txt     # Dependencies")
    print("  📄 setup.py            # Package setup")
    print("  📄 README.md           # Documentation")
    print("  📁 src/                # Source code")
    print("  📁 config/             # Configuration files")
    print("  📁 docs/               # Documentation")
    print("  📁 scripts/            # Utility scripts")
    print("  📁 data/               # Data files")
    print("  📁 archive/            # Archived files")
    print("\n🚀 Run with: python main.py")

if __name__ == "__main__":
    main() 