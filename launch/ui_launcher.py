#!/usr/bin/env python3
"""
UI Launcher for Enhanced Dynamic Character Playground
Launches all UI interfaces on different ports for comprehensive access
"""

import uvicorn
import asyncio
import threading
import time
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def start_main_server():
    """Start the main server with all UI endpoints."""
    print("🚀 Starting main server with all UI endpoints...")
    uvicorn.run(
        "core.dynamic_character_playground_enhanced:app",
        host="127.0.0.1",
        port=8004,
        reload=False,
        log_level="info"
    )

def start_ui_server(port, ui_type):
    """Start a dedicated UI server for specific interface."""
    print(f"🎨 Starting {ui_type} server on port {port}...")
    
    # Create a simple FastAPI app for the specific UI
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    
    app = FastAPI(title=f"{ui_type} Interface")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="ui"), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def serve_ui():
        """Serve the specific UI interface."""
        ui_file = f"ui/{ui_type.lower().replace(' ', '_')}.html"
        try:
            with open(ui_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"{ui_type} interface not found")
    
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False, log_level="info")

def main():
    """Main launcher function."""
    print("🎭 Enhanced Dynamic Character Playground - UI Launcher")
    print("=" * 60)
    
    # Check if UI files exist
    ui_files = [
        "ui/enhanced_chat_interface.html",
        "ui/custom_character_creator_web.html", 
        "ui/memory_management_interface.html",
        "ui/memory_insights_panel.html"
    ]
    
    missing_files = []
    for ui_file in ui_files:
        if not Path(ui_file).exists():
            missing_files.append(ui_file)
    
    if missing_files:
        print("❌ Missing UI files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all UI files are present before launching.")
        return
    
    print("✅ All UI files found!")
    print("\n🚀 Launching UI interfaces...")
    print("\nAvailable interfaces:")
    print("   📱 Main Chat Interface: http://localhost:8004/")
    print("   🎨 Character Creator: http://localhost:8004/create-character")
    print("   🧠 Memory Management: http://localhost:8004/memory-management")
    print("   📊 Memory Insights: http://localhost:8004/memory-insights")
    print("\n   🔧 API Health Check: http://localhost:8004/health")
    print("   📋 Characters List: http://localhost:8004/characters")
    print("   👥 Users List: http://localhost:8004/users")
    
    print("\n" + "=" * 60)
    print("🎯 Starting main server with all endpoints...")
    print("   Press Ctrl+C to stop all servers")
    print("=" * 60)
    
    try:
        # Start the main server (includes all UI endpoints)
        start_main_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all servers...")
        print("✅ All servers stopped successfully!")

if __name__ == "__main__":
    main() 