#!/usr/bin/env python3
"""
Simple server launcher that runs from the correct directory
"""

import os
import sys
import subprocess
import argparse
import socket

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None

def main():
    parser = argparse.ArgumentParser(description='Launch Dynamic Character Playground')
    parser.add_argument('--port', type=int, default=None, help='Port to run on (auto-find if not specified)')
    parser.add_argument('--auto-port', action='store_true', help='Automatically find available port')
    args = parser.parse_args()
    
    # Get the project root directory (parent of launch folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Change to the project root directory
    os.chdir(project_root)
    
    # Add the project root to Python path
    sys.path.insert(0, project_root)
    
    # Determine port
    if args.port is not None:
        port = args.port
        if not is_port_available(port):
            print(f"❌ Port {port} is not available")
            return 1
    elif args.auto_port:
        port = find_available_port()
        if port is None:
            print("❌ No available ports found")
            return 1
    else:
        # Default behavior: try 8005, then auto-find
        port = 8005 if is_port_available(8005) else find_available_port()
        if port is None:
            print("❌ No available ports found")
            return 1
    
    print(f"🚀 Launching server from: {project_root}")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    
    print("\n🎭 Available UI Interfaces:")
    print(f"   📱 Main Chat Interface: http://localhost:{port}/")
    print(f"   🎨 Character Creator: http://localhost:{port}/create-character")
    print(f"   🧠 Memory Management: http://localhost:{port}/memory-management")
    print(f"   📊 Memory Insights: http://localhost:{port}/memory-insights")
    print(f"\n   🔧 API Health Check: http://localhost:{port}/health")
    print(f"   📋 Characters List: http://localhost:{port}/characters")
    print(f"   👥 Users List: http://localhost:{port}/users")
    
    # Import and run the server
    try:
        # First import the fix to ensure it's applied
        import core.fix_openai_compatibility
        
        # Then import the main app
        from core.dynamic_character_playground_enhanced import app
        import uvicorn
        
        print("\n✅ Server imported successfully, starting...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 