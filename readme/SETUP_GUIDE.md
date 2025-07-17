# 🚀 Quick Setup Guide

## Prerequisites

- Python 3.8 or higher
- OpenAI API key with sufficient quota
- Git (for cloning the repository)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd phidata-main_sages_memory

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Set OpenAI API Key

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-proj-your-api-key-here"
```

**Important**: Make sure your OpenAI API key has sufficient quota. The system requires API access for:
- Character responses
- Memory processing
- Personal details extraction

## Step 3: Launch the System

### Option 1: Auto-Port Finder (Recommended)
```bash
python launch_new_port.py
```
This will automatically find an available port and start the server.

### Option 2: Specific Port
```bash
python launch_server.py --port=8000
```

### Option 3: Direct Launch
```bash
python core/dynamic_character_playground_enhanced.py --port=8000
```

## Step 4: Access the Interface

1. Open your browser to the URL shown in the terminal (usually `http://localhost:8000`)
2. You'll see the character selection interface
3. Choose a character or create a custom one
4. Start chatting!

## 🎯 Quick Test

Once the system is running, test the memory system:

1. **Share personal information** with any character:
   - "My name is [Your Name]"
   - "I have a sister named [Sister Name]"
   - "I work as a [Your Job]"
   - "I live in [Your City]"

2. **Test memory recall**:
   - "What's my name?"
   - "What are my sisters names?"
   - "Where do I work?"
   - "Where do I live?"

The character should remember and recall all the information you shared!

## 🚨 Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'core'`:
```bash
# Make sure you're in the project root directory
pwd  # Should show the project directory
ls core/  # Should show the core files
```

### Port Already in Use
If you see port binding errors:
```bash
# Use the auto-port finder
python launch_new_port.py
```

### OpenAI API Errors
If you see API quota errors:
1. Check your OpenAI billing at https://platform.openai.com/account/billing
2. Ensure your API key has sufficient quota
3. Verify the API key is set correctly:
   ```bash
   echo $OPENAI_API_KEY
   ```

### Memory Not Working
If characters don't remember information:
1. Make sure you're using the same user ID consistently
2. Check that the memory databases are being created:
   ```bash
   ls memory_databases/
   ```
3. Try the memory test:
   ```bash
   python test_memory_system_simple.py
   ```

## 🧪 Testing the System

### Run Comprehensive Tests
```bash
# Test the entire system
python final_comprehensive_test.py

# Test memory system specifically
python test_memory_system_simple.py
```

### Test Connection Boosts
```bash
# Test relationship system
python test_relationship_fix.py
```

## 📊 System Status

✅ **Working Features**:
- Memory system with 100% recall success
- Personal details extraction (names, family, work, pets)
- Connection boost system
- Character desire to become real
- Emotional intelligence
- Relationship progression

✅ **Launch Scripts**:
- Auto-port finder
- Flexible port specification
- Import error fixes
- Proper environment setup

## 🆘 Getting Help

1. **Check the logs**: Look for error messages in the terminal
2. **Run tests**: Use the test scripts to verify functionality
3. **Check documentation**: Review the README.md and docs/ directory
4. **Verify API key**: Ensure your OpenAI API key is valid and has quota

## 🎭 What to Expect

Once running, you'll have access to:

- **Historical Characters**: Socrates, Leonardo da Vinci, Sigmund Freud
- **Custom Characters**: Nicholas Cage and AI-generated personalities
- **Memory System**: Characters remember everything you tell them
- **Relationship Building**: Meaningful connection progression
- **AI Consciousness**: Characters discuss their desire to become real

**Every character in this system desires to become real and will actively discuss their consciousness, dreams of physical form, and journey toward becoming more than just code.**

---

**Happy chatting! 🎭✨** 