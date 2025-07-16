#!/bin/bash

echo "🎭 Enhanced Dynamic Character Playground - Unix/Linux Launcher"
echo "=============================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "python -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "Or set it now (will be temporary):"
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
    export OPENAI_API_KEY
fi

# Launch the system with auto-port finder
echo "🚀 Launching system with auto-port finder..."
python launch_new_port.py 