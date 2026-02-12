import json
import chromadb
import config
from chromadb.utils import embedding_functions

# CONFIG
STATE_FILE = config.USER_STATE_FILE
CHROMA_PATH = config.CHROMA_DB_DIR

def migrate():
    print("🚀 MIGRATING TO VECTOR SPACE...")
    
    # 1. Load JSON Data
    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: user_state.json not found. Run populate_db.py first.")
        return
    
    # 2. Connect to Chroma
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # --- A. MIGRATE EVENTS ---
    print("   ...Indexing Timeline Events")
    # Delete existing collection if it exists to start fresh/clean
    try:
        client.delete_collection("timeline_events")
    except:
        pass
        
    event_collection = client.get_or_create_collection(name="timeline_events")
    
    events = data.get("events", [])
    if events:
        # FIX: Add unique index 'i' to ID to prevent DuplicateIDError on same turns
        ids = [f"event_{e['turn']}_{i}" for i, e in enumerate(events)]
        docs = [e['description'] for e in events]
        metas = [{"turn": e['turn'], "date": e['date']} for e in events]
        
        # Batch insert (Chroma handles batches better)
        batch_size = 100
        for i in range(0, len(events), batch_size):
            event_collection.add(
                ids=ids[i:i+batch_size],
                documents=docs[i:i+batch_size],
                metadatas=metas[i:i+batch_size]
            )
            print(f"      -> Indexed {min(i+batch_size, len(events))}/{len(events)} events")

    # --- B. MIGRATE ENTITIES ---
    print("   ...Indexing Entities")
    try:
        client.delete_collection("entity_facts")
    except:
        pass
        
    entity_collection = client.get_or_create_collection(name="entity_facts")
    
    entities = data.get("entities", {})
    if entities:
        e_ids = []
        e_docs = []
        e_metas = []
        
        for key, info in entities.items():
            # Create a rich description for the vector
            # "Ravikant is my boss, acts generous, knows C++, lives in Bandra"
            desc = f"{info['name']} is {info.get('relationship')}. Attributes: {json.dumps(info.get('attributes'))}"
            
            e_ids.append(f"entity_{key}")
            e_docs.append(desc)
            e_metas.append({"name": info['name'], "type": "entity"})
            
        entity_collection.add(ids=e_ids, documents=e_docs, metadatas=e_metas)

    print("✅ MIGRATION COMPLETE. Your memory is now Vectorized.")

if __name__ == "__main__":
    migrate()