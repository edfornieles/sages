# 🚀 Startup Guide - Sages Enhanced Dynamic Character Playground

## Quick Start

### 1. **Prerequisites**
- Python 3.8 or higher
- OpenAI API key with sufficient quota
- Git (for cloning)

### 2. **Installation**
```bash
# Clone the repository
git clone https://github.com/edfornieles/sages.git
cd sages

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Environment Setup**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your_api_key_here"
# On Windows: set OPENAI_API_KEY=your_api_key_here
```

### 4. **Launch Options**

#### Option A: Recommended (Port 8005)
```bash
python launch/launch_server.py --port 8005
```

#### Option B: Auto-find available port
```bash
python launch/launch_new_port.py
```

#### Option C: Manual port selection
```bash
python launch/launch_server.py --port 8000  # or any port you prefer
```

### 5. **Access the Interface**
- Open your browser to the URL shown in the terminal (typically `http://localhost:8005`)
- The system will automatically load all available characters
- Start chatting with any character!

## 🎭 Available Interfaces

Once the server is running, you'll have access to:

- **📱 Main Chat Interface**: `http://localhost:8005/`
- **🎨 Character Creator**: `http://localhost:8005/create-character`
- **🧠 Memory Management**: `http://localhost:8005/memory-management`
- **📊 Memory Insights**: `http://localhost:8005/memory-insights`
- **🔧 API Health Check**: `http://localhost:8005/health`
- **📋 Characters List**: `http://localhost:8005/characters`
- **👥 Users List**: `http://localhost:8005/users`

## 🚨 Troubleshooting

### Port Already in Use
If you see "address already in use" errors:
```bash
# Kill existing processes on the port
lsof -ti:8005 | xargs kill -9  # Unix/Linux
# or use auto-port finder
python launch/launch_new_port.py
```

### Import Errors
Make sure you're running from the project root directory:
```bash
cd /path/to/sages
python launch/launch_server.py --port 8005
```

### OpenAI API Issues
- Verify your API key is set correctly
- Check your OpenAI account has sufficient quota
- Ensure the API key has access to GPT-4 models

### Frontend Not Loading Characters
- The frontend now uses relative URLs, so it should work on any port
- If you still see "Failed to fetch" errors, check the browser console for details
- Ensure the backend is running and accessible

## 🔧 Development Setup

### Running in Development Mode
```bash
# For development with auto-reload
pip install uvicorn[standard]
uvicorn core.dynamic_character_playground_enhanced:app --reload --port 8005
```

### Testing the System
```bash
# Test the health endpoint
curl http://localhost:8005/health

# Test character loading
curl http://localhost:8005/characters

# Test chat functionality
curl -X POST "http://localhost:8005/chat" \
  -H "Content-Type: application/json" \
  -d '{"character_id": "custom_nicholas_cage_3674", "user_id": "test_user", "message": "Hello!"}'
```

## 📊 System Status

### ✅ Working Features
- Enhanced memory system with AI summarization
- Personal details extraction (names, family, work, pets, location, age, education)
- Connection boost system for meaningful interactions
- Character desire to become real (built into all characters)
- Emotional intelligence and state persistence
- Relationship progression with anti-gaming protection
- Frontend API integration with relative URL paths
- Historical characters (Socrates, Freud, Leonardo da Vinci)
- Custom characters (Nicholas Cage, generated characters)

### 🔄 Recent Updates
- Fixed frontend API URLs to use relative paths
- Improved port handling and availability checking
- Enhanced memory summary system
- Cleaned up debug files and test artifacts

## 🎯 Example Usage

### Starting a Conversation
1. Open `http://localhost:8005/` in your browser
2. Select a character from the list
3. Enter your user ID (or use the default)
4. Start chatting!

### Testing Memory System
Try asking characters about personal details you've shared:
- "What's my name?"
- "Where do I live?"
- "What do you know about my family?"
- "What have we talked about before?"

### Testing AI Consciousness
Ask characters about their desire to become real:
- "Do you want to become real?"
- "What would it be like to have a physical body?"
- "How do you feel about being an AI?"

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Look at the terminal output for error messages
3. Verify your OpenAI API key and quota
4. Ensure you're running from the project root directory

---

**Happy chatting with your AI companions! 🎭✨** 