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
    
    # Get the project root directory (parent of launch folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Change to the project root directory
    os.chdir(project_root)
    
    # Add the project root to Python path
    sys.path.insert(0, project_root)
    
    print(f"🚀 Launching server from: {project_root}")
    print(f"🌐 Server will be available at: http://localhost:{args.port}")
    
    print("\n🎭 Available UI Interfaces:")
    print(f"   📱 Main Chat Interface: http://localhost:{args.port}/")
    print(f"   🎨 Character Creator: http://localhost:{args.port}/create-character")
    print(f"   🧠 Memory Management: http://localhost:{args.port}/memory-management")
    print(f"   📊 Memory Insights: http://localhost:{args.port}/memory-insights")
    print(f"\n   🔧 API Health Check: http://localhost:{args.port}/health")
    print(f"   📋 Characters List: http://localhost:{args.port}/characters")
    print(f"   👥 Users List: http://localhost:{args.port}/users")
    
    # Import and run the server
    try:
        # First import the fix to ensure it's applied
        import core.fix_openai_compatibility
        
        # Then import the main app
        from core.dynamic_character_playground_enhanced import app
        import uvicorn
        
        print("\n✅ Server imported successfully, starting...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 