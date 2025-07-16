# 🚀 Dynamic Character Playground - New Port Launcher

This directory contains launcher scripts that automatically find an available port and start the Dynamic Character Playground server.

## 📁 Available Launchers

### 1. Python Launcher (`launch_new_port.py`)
- **Platform**: Cross-platform (Python 3.6+)
- **Usage**: `python launch_new_port.py`
- **Features**: 
  - Automatically finds available port starting from 8000
  - Sets proper PYTHONPATH for imports
  - Graceful error handling
  - Process management

### 2. Shell Script Launcher (`launch_new_port.sh`)
- **Platform**: macOS/Linux
- **Usage**: `./launch_new_port.sh`
- **Features**:
  - Fast port detection using `lsof`
  - Sets PYTHONPATH automatically
  - Simple and lightweight

### 3. Windows Batch Launcher (`launch_new_port.bat`)
- **Platform**: Windows
- **Usage**: `launch_new_port.bat`
- **Features**:
  - Uses Python socket binding for port detection
  - Windows-compatible commands
  - Pause on exit for error viewing

## 🎯 How It Works

1. **Port Detection**: Each launcher scans ports starting from 8000 to find an available one
2. **Environment Setup**: Sets PYTHONPATH to ensure proper module imports
3. **Server Launch**: Starts the Dynamic Character Playground on the found port
4. **URL Display**: Shows the URLs for accessing the application

## 🌐 Access URLs

Once launched, you can access the application at:
- **Main Interface**: `http://localhost:[PORT]`
- **Character Creator**: `http://localhost:[PORT]/create-character`
- **Health Check**: `http://localhost:[PORT]/health`
- **Character List**: `http://localhost:[PORT]/characters`

## 🔧 Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
1. The launcher will automatically find the next available port
2. Check the output for the actual port being used
3. Use the displayed URLs to access the application

### Import Errors
If you see import errors:
1. Make sure you're running from the project root directory
2. The launcher should automatically set PYTHONPATH
3. Try using the Python launcher (`launch_new_port.py`) for better error handling

### Server Won't Start
If the server fails to start:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Ensure your `.env` file is configured with `OPENAI_API_KEY`
3. Check the console output for specific error messages

## 🎮 Quick Start

1. **Navigate to project root**:
   ```bash
   cd /path/to/phidata-main_sages_memory
   ```

2. **Choose your launcher**:
   ```bash
   # Python (recommended)
   python launch_new_port.py
   
   # Shell script (macOS/Linux)
   ./launch_new_port.sh
   
   # Windows batch
   launch_new_port.bat
   ```

3. **Open your browser** to the displayed URL

4. **Stop the server** with `Ctrl+C`

## 📊 Current Status

- ✅ **Port 8000**: Available and working
- ✅ **Port 8001**: Available
- ✅ **Port 8002**: Available
- ✅ **Port 8003**: Available
- ✅ **Port 8004**: Available
- ❌ **Port 8005**: In use by another process
- ❌ **Port 8006**: In use by another process
- ✅ **Port 8007+**: Available

## 🔄 Multiple Instances

You can run multiple instances of the playground by:
1. Using different launcher scripts
2. Manually specifying ports: `python core/dynamic_character_playground_enhanced.py --port=8007`
3. Each instance will have isolated memory and character data

## 📝 Notes

- The launcher automatically handles port conflicts
- All instances use the same character data directory
- Memory databases are isolated per character-user combination
- The server runs on `0.0.0.0` to accept connections from any IP 