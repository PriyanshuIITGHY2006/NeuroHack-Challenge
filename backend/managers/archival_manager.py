import chromadb
import uuid
import config # Import the new config

class ArchivalMemoryManager:
    def __init__(self):
        # FIX: Use the absolute path from config
        print(f"[SYSTEM] Connecting to ChromaDB at: {config.CHROMA_DB_DIR}")
        self.client = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))
        
        self.semantic = self.client.get_or_create_collection(
            name="semantic_memory",
            metadata={"hnsw:space": "cosine"}
        )
        self.episodic = self.client.get_or_create_collection(
            name="conversation_logs",
            metadata={"hnsw:space": "cosine"}
        )

    def add_memory(self, content, role, turn_number):
        memory_id = f"mem_{uuid.uuid4().hex[:8]}"
        self.episodic.add(
            documents=[content],
            metadatas=[{
                "role": role,
                "turn_number": turn_number,
                "origin_turn": turn_number
            }],
            ids=[memory_id]
        )
        return memory_id

    def search_memory(self, query, n_results=3):
        results = self.semantic.query(
            query_texts=[query],
            n_results=n_results
        )
        memories = []
        if results['ids'] and results['ids'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                mem_id = results['ids'][0][i]
                mem_obj = {
                    "memory_id": mem_id,
                    "content": doc,
                    "origin_turn": meta.get("origin_turn", 0),
                    "last_used_turn": meta.get("last_used_turn", 0),
                    "distance": results['distances'][0][i]
                }
                memories.append(mem_obj)
        return memories

    # (Keep add_fact, add_episode, retrieve_relevant_context as they were...)
    # [Insert previous code for those methods here if needed, or leave them if you didn't delete them]

    # --- KEEPING YOUR ORIGINAL METHODS (To prevent breaking other logic) ---
    def add_fact(self, content, turn_number, confidence=1.0):
        # 1. Check Redundancy
        results = self.semantic.query(
            query_texts=[content],
            n_results=1
        )
        
        if results['ids'] and results['ids'][0] and results['distances'][0][0] < 0.15:
            existing_id = results['ids'][0][0]
            current_meta = results['metadatas'][0][0]
            current_meta['last_used_turn'] = turn_number
            current_meta['count'] = current_meta.get('count', 1) + 1
            
            self.semantic.update(ids=[existing_id], metadatas=[current_meta])
            return existing_id, f"Memory Refreshed (Merged with {existing_id})"

        memory_id = f"fact_{uuid.uuid4().hex[:8]}"
        self.semantic.add(
            documents=[content],
            metadatas=[{
                "type": "fact",
                "origin_turn": turn_number,
                "last_used_turn": turn_number,
                "count": 1,
                "confidence": confidence
            }],
            ids=[memory_id]
        )
        return memory_id, "New Memory Stored"

    def add_episode(self, user_msg, bot_msg, turn_number):
        """Standard logging of the conversation"""
        memory_id = f"ep_{uuid.uuid4().hex[:8]}"
        content = f"User: {user_msg}\nAssistant: {bot_msg}"
        self.episodic.add(
            documents=[content],
            metadatas=[{"turn": turn_number}],
            ids=[memory_id]
        )

    def retrieve_relevant_context(self, query, turn_number, n_results=3):
        results = self.semantic.query(
            query_texts=[query],
            n_results=n_results
        )
        
        memories = []
        if results['ids'] and results['ids'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                mem_id = results['ids'][0][i]
                
                mem_obj = {
                    "memory_id": mem_id,
                    "content": doc,
                    "origin_turn": meta.get("origin_turn", 0),
                    "last_used_turn": turn_number,
                    "distance": results['distances'][0][i]
                }
                memories.append(mem_obj)
                
                meta['last_used_turn'] = turn_number
                self.semantic.update(ids=[mem_id], metadatas=[meta])

        return memories