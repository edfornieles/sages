#!/usr/bin/env python3
"""
Simple server launcher that runs from the correct directory
"""

import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='Launch Dynamic Character Playground')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    args = parser.parse_args()
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Add the current directory to Python path
    sys.path.insert(0, script_dir)
    
    print(f"🚀 Launching server from: {script_dir}")
    print(f"🌐 Server will be available at: http://localhost:{args.port}")
    
    # Import and run the server
    try:
        # First import the fix to ensure it's applied
        import core.fix_openai_compatibility
        
        # Then import the main app
        from core.dynamic_character_playground_enhanced import app
        import uvicorn
        
        print("✅ Server imported successfully, starting...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 