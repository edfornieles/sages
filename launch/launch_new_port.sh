#!/bin/bash

# Dynamic Character Playground - New Port Launcher
# This script finds an available port and launches the server

echo "🎭 Dynamic Character Playground - New Port Launcher"
echo "=================================================="

# Check if we're in the right directory (from launch folder perspective)
if [ ! -f "../core/dynamic_character_playground_enhanced.py" ]; then
    echo "❌ Error: Could not find core/dynamic_character_playground_enhanced.py"
    echo "Please ensure this script is in the launch folder of the project"
    exit 1
fi

# Function to find available port
find_available_port() {
    local start_port=8000
    local max_attempts=50
    
    for ((port=start_port; port<start_port+max_attempts; port++)); do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return 0
        fi
    done
    return 1
}

# Find available port
echo "🔍 Finding available port..."
PORT=$(find_available_port)

if [ $? -ne 0 ]; then
    echo "❌ Could not find an available port in range 8000-8049"
    exit 1
fi

echo "✅ Found available port: $PORT"

# Change to project root directory
cd ..

# Set PYTHONPATH for proper imports
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Launch the server
echo "🚀 Launching Dynamic Character Playground on port $PORT..."
echo "🌐 Server will be available at: http://localhost:$PORT"
echo "🎭 Character Creator: http://localhost:$PORT/create-character"
echo "📊 Health Check: http://localhost:$PORT/health"
echo ""
echo "============================================================"
echo "🎮 Starting server... (Press Ctrl+C to stop)"
echo "============================================================"

# Start the server
python3 core/dynamic_character_playground_enhanced.py --port=$PORT 