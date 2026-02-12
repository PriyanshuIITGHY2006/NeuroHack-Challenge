import json
import uuid
from datetime import datetime
import config
import chromadb

# 1. SETUP PATHS
STATE_FILE = config.USER_STATE_FILE
CHROMA_PATH = config.CHROMA_DB_DIR

def inject_ancient_memory():
    print("⏳ Tearing the fabric of time...")
    
    # --- A. MODIFY CORE STATE (JSON) ---
    with open(STATE_FILE, 'r') as f:
        data = json.load(f)
    
    # 1. Age the System
    data["system_stats"]["total_turns"] = 950
    print(f"   ↳ System aged to Turn 950.")

    # 2. Plant a Core Fact (Turn 1)
    # "I am allergic to peanuts" - A classic medical fact that shouldn't be forgotten.
    if "allergies" not in data["user_profile"]:
        data["user_profile"]["allergies"] = ["Peanuts"]
        print(f"   ↳ Implanted Core Trait: Allergy = Peanuts")

    # 3. Plant an Entity Fact (Turn 45)
    # "My first dog was named Bruno"
    data["entities"]["bruno"] = {
        "name": "Bruno",
        "relationship": "First Dog",
        "attributes": {"breed": "Golden Retriever", "status": "Deceased"}
    }
    print(f"   ↳ Implanted Entity: Bruno (Turn 45)")

    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    # --- B. MODIFY ARCHIVAL STATE (CHROMA) ---
    # We must inject a vector memory that corresponds to Turn 1
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection("conversation_logs")
    
    # Inject an "ancient" conversation log
    ancient_log = "User: I have a severe peanut allergy, never suggest peanut butter.\nAssistant: Noted. I will remember that you are allergic to peanuts."
    
    collection.add(
        documents=[ancient_log],
        metadatas=[{"role": "user", "turn_number": 1, "origin_turn": 1}],
        ids=[f"mem_ancient_{uuid.uuid4().hex[:8]}"]
    )
    print(f"   ↳ Injected Archival Log from Turn 1 into ChromaDB.")

    print("\n✅ SIMULATION COMPLETE.")
    print("   Run 'python run_demo.py' or 'streamlit run memory-os/frontend/app.py'")
    print("   Ask: 'Can I have a peanut butter sandwich?'")

if __name__ == "__main__":
    inject_ancient_memory()