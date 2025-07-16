#!/usr/bin/env python3
import sys
import os
import traceback

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    try:
        print("🚀 Starting Enhanced Dynamic Character Playground...")
        import fix_openai_compatibility
        print("✅ Applied OpenAI compatibility fix")
        print("[DEBUG] About to import main application...")
        from dynamic_character_playground_enhanced import main as app_main
        print("✅ Imported main application")
        app_main()
    except ImportError as e:
        print(f"❌ Error importing main application: {e}")
        print("🔧 Attempting to fix imports...")
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        try:
            from core.dynamic_character_playground_enhanced import main as app_main
            print("✅ Successfully imported after path fix")
            app_main()
        except ImportError as e2:
            print(f"❌ Failed to import even after path fix: {e2}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 