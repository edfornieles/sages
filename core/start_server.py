#!/usr/bin/env python3
"""Simple launcher for the Dynamic Character Playground.

This script ensures the repository root is on ``sys.path``, imports the FastAPI
application object via ``core.dynamic_character_playground_enhanced.main`` and
boots it with uvicorn.  All of the heavy-lifting (initialising subsystems, etc.)
occurs inside ``core/dynamic_character_playground_enhanced.py``.
"""

import os
import sys
import socket
import argparse
import uvicorn

# Guarantee the project root is importable
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False


def validate_port(port: int) -> bool:
    """Validate that port is in valid range."""
    return 1 <= port <= 65535


def check_environment() -> bool:
    """Check for required environment variables."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Make sure to set these in your .env file or environment")
        return False
    
    return True


def parse_arguments() -> int:
    """Parse command line arguments and return the port number."""
    parser = argparse.ArgumentParser(
        description="Launch the Dynamic Character Playground server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python core/start_server.py                    # Start on default port 8001
  python core/start_server.py --port 8080       # Start on port 8080
  python core/start_server.py --port=8080       # Alternative syntax
        """
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=8001,
        help='Port to run the server on (default: 8001)'
    )
    
    args = parser.parse_args()
    
    # Validate port range
    if not validate_port(args.port):
        print(f"❌ Invalid port {args.port}. Port must be between 1 and 65535.")
        sys.exit(1)
    
    # Check if port is available
    if not is_port_available(args.port):
        print(f"❌ Port {args.port} is already in use.")
        print("💡 Try a different port with --port <number>")
        sys.exit(1)
    
    return args.port


def main():
    """Entry-point for ``python core/start_server.py``."""

    print("🎭 Dynamic Character Playground Launcher")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Parse arguments and validate port
    port = parse_arguments()
    
    # Import the app factory (done here to avoid import errors before env check)
    try:
        from core.dynamic_character_playground_enhanced import main as app_factory
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        print("💡 Make sure you're running from the project root directory")
        sys.exit(1)

    # Build the FastAPI app via the factory
    try:
        app = app_factory()
    except Exception as e:
        print(f"❌ Failed to create application: {e}")
        sys.exit(1)

    print(f"🚀 Launching Dynamic Character Playground on http://localhost:{port}")
    print("📝 Features loaded: Dynamic characters, Memory system, Mood tracking")
    print("🌐 Access the web interface at the URL above")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

