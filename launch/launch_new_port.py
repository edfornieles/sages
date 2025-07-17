#!/usr/bin/env python3
"""
Launcher script to start the Dynamic Character Playground on a new, unused port.
This script will automatically find an available port and launch the server.
"""

import sys
import os
import socket
import subprocess
import time
from pathlib import Path

def find_available_port(start_port=8000, max_attempts=50):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")

def check_port_availability(port):
    """Check if a specific port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def launch_server(port):
    """Launch the server on the specified port."""
    print(f"🚀 Launching Dynamic Character Playground on port {port}...")
    
    # Change to the project root directory (parent of launch folder)
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Set up environment for proper imports
    env = os.environ.copy()
    env['PYTHONPATH'] = str(script_dir)
    
    # Build the command to run the server using the improved launcher
    cmd = [
        sys.executable, 
        "launch/launch_server.py",
        f"--port={port}"
    ]
    
    print(f"📋 Command: {' '.join(cmd)}")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"🎭 Character Creator: http://localhost:{port}/create-character")
    print(f"📊 Health Check: http://localhost:{port}/health")
    print("\n" + "="*60)
    print("🎮 Starting server... (Press Ctrl+C to stop)")
    print("="*60)
    
    try:
        # Start the server process with proper environment
        process = subprocess.Popen(cmd, cwd=script_dir, env=env)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is None:
            print(f"✅ Server started successfully on port {port}")
            print(f"🌐 Open your browser to: http://localhost:{port}")
            
            # Keep the script running
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")
        else:
            print(f"❌ Server failed to start on port {port}")
            return_code = process.returncode
            print(f"Exit code: {return_code}")
            
    except Exception as e:
        print(f"❌ Error launching server: {e}")
        return False
    
    return True

def main():
    """Main function to find available port and launch server."""
    print("🎭 Dynamic Character Playground - New Port Launcher")
    print("="*50)
    
    # Check if we're in the right directory (from launch folder perspective)
    project_root = Path(__file__).parent.parent
    if not (project_root / "launch/launch_server.py").exists():
        print("❌ Error: Could not find launch/launch_server.py")
        print("Please ensure this script is in the launch folder of the project")
        return False
    
    # Find an available port
    print("🔍 Finding available port...")
    try:
        port = find_available_port(start_port=8000)
        print(f"✅ Found available port: {port}")
    except RuntimeError as e:
        print(f"❌ {e}")
        return False
    
    # Double-check port availability
    if not check_port_availability(port):
        print(f"❌ Port {port} is not actually available")
        return False
    
    # Launch the server
    return launch_server(port)

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 