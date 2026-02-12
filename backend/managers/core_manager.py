import json
import config
import chromadb
from groq import Groq
from datetime import datetime
import re

class CoreMemoryManager:
    def __init__(self):
        self.filepath = config.USER_STATE_FILE
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))
        
        # Connect to our new Vector Indices
        self.event_collection = self.chroma_client.get_or_create_collection("timeline_events")
        self.entity_collection = self.chroma_client.get_or_create_collection("entity_facts")
        
        self.schema_map = {"city": "primary_location", "job": "occupation", "work": "occupation"}
        self._initialize_db()

    def _initialize_db(self):
        if not self.filepath.exists():
            self.save_state({"user_profile": {"name": None, "preferences": []}, "entities": {}, "knowledge_base": {}, "events": [], "system_stats": {"total_turns": 0}})

    def load_state(self):
        try:
            with open(self.filepath, 'r') as f: return json.load(f)
        except: return {}

    def save_state(self, data):
        with open(self.filepath, 'w') as f: json.dump(data, f, indent=4)

    def increment_turn(self):
        data = self.load_state()
        data["system_stats"]["total_turns"] = data.get("system_stats", {}).get("total_turns", 0) + 1
        self.save_state(data)
        return data["system_stats"]["total_turns"]

    # --- OPTIMIZED VECTOR SEARCH LOGIC ---
    def get_core_prompt(self, recent_history_text="", archival_context=[]):
        data = self.load_state()
        
        # --- FIX: GET SIMULATION TIME, NOT REAL TIME ---
        try:
            # Use the date of the last event in memory as "Today"
            last_event_date = data["events"][-1]["date"]
            current_year = int(last_event_date.split("-")[0])
        except (IndexError, KeyError, ValueError):
            # Fallback if no events exist
            current_year = datetime.now().year
            
        # 1. USER PROFILE
        profile_str = "USER PROFILE:\n" + "\n".join([f"- {k}: {v}" for k, v in data.get("user_profile", {}).items() if v])
        
        # 2. SEMANTIC SEARCH (Entities)
        entity_results = self.entity_collection.query(
            query_texts=[recent_history_text],
            n_results=5,
            include=["documents", "distances", "metadatas"]
        )
        
        relevant_entities = []
        if entity_results['documents']:
            for i, doc in enumerate(entity_results['documents'][0]):
                dist = entity_results['distances'][0][i]
                if dist < 1.2:
                    relevant_entities.append(f"- {doc}")

        # 3. SEMANTIC SEARCH (Timeline Events)
        event_results = self.event_collection.query(
            query_texts=[recent_history_text],
            n_results=5,
            include=["documents", "distances", "metadatas"]
        )
        
        relevant_events = []
        if event_results['documents']:
            # CALCULATE RELATIVE DATES
            target_year = None
            
            # Check for explicit years ("2025")
            explicit_match = re.search(r'\b(20\d{2})\b', recent_history_text)
            if explicit_match:
                target_year = explicit_match.group(1)
            # Check for relative phrases using SIMULATION time
            elif "last year" in recent_history_text.lower():
                target_year = str(current_year - 1)
            elif "this year" in recent_history_text.lower():
                target_year = str(current_year)

            for i, doc in enumerate(event_results['documents'][0]):
                meta = event_results['metadatas'][0][i]
                dist = event_results['distances'][0][i]
                
                # CHECK MATCH
                is_year_match = target_year and (target_year in meta['date'])
                
                # DYNAMIC THRESHOLDING
                # Boost if the calculated year matches
                threshold = 1.4 if is_year_match else 1.1
                
                if dist < threshold:
                    event_str = f"- [Turn {meta['turn']} | {meta['date']}] {doc}"
                    if is_year_match:
                        relevant_events.insert(0, event_str) # Prioritize
                    else:
                        relevant_events.append(event_str)

        # 4. ARCHIVAL CONTEXT
        archival_str = "PAST CONVERSATIONS:\n"
        if archival_context:
            for mem in archival_context:
                archival_str += f"- [Turn {mem.get('origin_turn')}]: {mem.get('content')}\n"

        # Combine
        entities_block = "RELEVANT ENTITIES:\n" + "\n".join(relevant_entities) if relevant_entities else "ENTITIES: [None]"
        events_block = "RELEVANT TIMELINE:\n" + "\n".join(relevant_events) if relevant_events else "TIMELINE: [No relevant past events]"
        
        return f"{profile_str}\n\n{entities_block}\n\n{events_block}\n\n{archival_str}"

    # --- TOOLS ---
    def update_entity(self, name, relationship, attributes):
        res = self._update_entity_json(name, relationship, attributes)
        clean_name = re.sub(r'\s*\(.*?\)', '', name).strip()
        desc = f"{clean_name} is {relationship}. Attributes: {json.dumps(attributes)}"
        self.entity_collection.upsert(
            ids=[f"entity_{clean_name.lower()}"],
            documents=[desc],
            metadatas={"name": clean_name, "type": "entity"}
        )
        return res

    def log_event(self, description):
        res = self._log_event_json(description)
        data = self.load_state()
        last_event = data["events"][-1]
        self.event_collection.add(
            ids=[f"event_{last_event['turn']}"],
            documents=[last_event['description']],
            metadatas={"turn": last_event['turn'], "date": last_event['date']}
        )
        return res

    def _update_entity_json(self, name, relationship, attributes):
        data = self.load_state()
        entities = data.get("entities", {})
        clean_name = re.sub(r'\s*\(.*?\)', '', name).strip()
        key = clean_name.lower()
        if key not in entities:
            entities[key] = {"name": clean_name, "relationship": relationship, "attributes": {}}
        if relationship: entities[key]["relationship"] = relationship
        if attributes: entities[key]["attributes"].update(attributes)
        data["entities"] = entities
        self.save_state(data)
        return f"Entity Synced: {clean_name}"

    def _log_event_json(self, description):
        data = self.load_state()
        turn = data["system_stats"]["total_turns"]
        data["events"].append({"turn": turn, "description": description, "date": datetime.now().strftime("%Y-%m-%d")})
        self.save_state(data)
        return "Event Logged."

    def update_profile(self, key, value):
        data = self.load_state()
        profile = data.get("user_profile", {})
        norm_key = self.schema_map.get(key.lower(), key.lower().replace(" ", "_"))
        if norm_key in ["preferences", "goals"] or isinstance(profile.get(norm_key), list):
            current = profile.get(norm_key, [])
            if value not in current: current.append(value)
            profile[norm_key] = current
        else:
            profile[norm_key] = value
        data["user_profile"] = profile
        self.save_state(data)
        return f"Updated Profile: {norm_key}"

    def remove_from_profile(self, key, value_to_remove):
        data = self.load_state()
        if key in data["user_profile"] and isinstance(data["user_profile"][key], list):
            data["user_profile"][key] = [x for x in data["user_profile"][key] if value_to_remove.lower() not in x.lower()]
            self.save_state(data)
            return f"Removed {value_to_remove}."
        return "Not found."

    def add_general_knowledge(self, topic, content):
        data = self.load_state()
        data.setdefault("knowledge_base", {})[topic.lower()] = content
        self.save_state(data)
        return "Knowledge Saved."