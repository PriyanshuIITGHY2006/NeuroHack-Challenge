import json
import shutil
import os
import config

# 1. RESET JSON (Structured Memory)
filepath = config.USER_STATE_FILE

# Define a truly empty state (or keep your default profile if preferred)
blank_state = {
    "user_profile": {
        "name": "Priyanshu",  # Keep default name or set to None
        "primary_location": None,
        "occupation": None,
        "preferences": [],
        "greeting": None
    },
    "entities": {},        # Wiped
    "knowledge_base": {},  # Wiped
    "events": [],          # Wiped
    "system_stats": {"total_turns": 0}
}

with open(filepath, "w") as f:
    json.dump(blank_state, f, indent=4)
print("✅ JSON Memory: Wiped (Reset to blank profile).")

# 2. RESET CHROMADB (Vector Memory)
# We simply delete the folder. Chroma will recreate it automatically on next run.
chroma_dir = config.CHROMA_DB_DIR

if os.path.exists(chroma_dir):
    try:
        shutil.rmtree(chroma_dir)
        print(f"✅ Vector Memory: Wiped (Deleted {chroma_dir}).")
    except Exception as e:
        print(f"❌ Error deleting ChromaDB: {e}")
else:
    print("ℹ️ Vector Memory: Already empty.")

print("\n🚀 SYSTEM RESET COMPLETE. Restart your server now.")