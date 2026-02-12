import chromadb
import config  # Import your actual config to get the real path

# 1. Connect to the Real Database (using the path from config)
print(f"Connecting to: {config.CHROMA_DB_DIR}")
client = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))

# 2. Inspect Entities
print("\n=== 🧠 ENTITY VECTORS (Concepts) ===")
try:
    collection = client.get_collection("entity_facts")
    count = collection.count()
    print(f"Found {count} entities.")
    
    if count > 0:
        data = collection.peek(limit=3)
        for i in range(len(data['ids'])):
            print(f"\nID: {data['ids'][i]}")
            print(f"Text: {data['documents'][i]}")
            # Show first 5 numbers of the vector
            vector_preview = data['embeddings'][i][:5] 
            print(f"Vector: {vector_preview} ...")
    else:
        print("Collection exists but is empty.")
except Exception as e:
    print(f"Error reading entities: {e}")

# 3. Inspect Timeline
print("\n=== 📅 TIMELINE VECTORS (Events) ===")
try:
    collection = client.get_collection("timeline_events")
    count = collection.count()
    print(f"Found {count} events.")
    
    if count > 0:
        data = collection.peek(limit=3)
        for i in range(len(data['ids'])):
            print(f"\nID: {data['ids'][i]}")
            print(f"Text: {data['documents'][i]}")
            vector_preview = data['embeddings'][i][:100]
            print(f"Vector: {vector_preview} ...")
except Exception as e:
    print(f"Error reading timeline: {e}")