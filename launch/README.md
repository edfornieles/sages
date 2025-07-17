# Launch Scripts

This folder contains all the launch scripts for the Dynamic Character Playground.

## Available Scripts

### Quick Launch Scripts
- **`quick_launch.sh`** - Unix/Linux quick launcher with auto-port finder
- **`quick_launch.bat`** - Windows quick launcher with auto-port finder

### Advanced Launch Scripts
- **`launch_new_port.py`** - Python script that finds an available port and launches the server
- **`launch_new_port.sh`** - Unix/Linux script that finds an available port and launches the server
- **`launch_new_port.bat`** - Windows script that finds an available port and launches the server
- **`launch_server.py`** - Simple Python server launcher with configurable port

### UI Launcher
- **`ui_launcher.py`** - Comprehensive UI launcher with all interfaces

## Available UI Interfaces

Once the server is running, you can access:

### Main Interfaces
- **📱 Chat Interface**: `/` - Main character chat interface
- **🎨 Character Creator**: `/create-character` - Create custom characters
- **🧠 Memory Management**: `/memory-management` - Manage and edit memories
- **📊 Memory Insights**: `/memory-insights` - View memory analytics and insights

### API Endpoints
- **🔧 Health Check**: `/health` - Server health status
- **📋 Characters List**: `/characters` - List all available characters
- **👥 Users List**: `/users` - List all users with memory data
- **💬 Chat API**: `/chat` - POST endpoint for character conversations

## Usage

### From Project Root
```bash
# Unix/Linux
./launch/quick_launch.sh
# or
python launch/launch_new_port.py

# Windows
launch\quick_launch.bat
# or
python launch\launch_new_port.py
```

### From Launch Folder
```bash
# Unix/Linux
cd launch
./quick_launch.sh
# or
./launch_new_port.sh

# Windows
cd launch
quick_launch.bat
# or
launch_new_port.bat
```

## Features

- **Auto-port finding**: Scripts automatically find available ports starting from 8000
- **Cross-platform support**: Scripts for Unix/Linux, Windows, and Python
- **Virtual environment handling**: Automatically activates the `.venv` environment
- **API key management**: Prompts for OpenAI API key if not set
- **Error handling**: Comprehensive error checking and user feedback

## Requirements

- Python 3.8+
- Virtual environment (`.venv`) with dependencies installed
- OpenAI API key (set as environment variable or prompted for) 