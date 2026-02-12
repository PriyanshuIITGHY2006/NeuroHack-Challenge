import json
from groq import Groq, BadRequestError, RateLimitError
import config
from backend.logic.prompts import SYSTEM_PROMPT_TEMPLATE
from backend.managers.core_manager import CoreMemoryManager
from backend.managers.archival_manager import ArchivalMemoryManager
from backend.managers.buffer_manager import BufferManager
import threading
import re

client = Groq(api_key=config.GROQ_API_KEY)

class Orchestrator:
    def __init__(self):
        self.core = CoreMemoryManager()
        self.archive = ArchivalMemoryManager()
        self.buffer = BufferManager(max_turns=10)
        
        # Tools Schema
        self.tools_schema = [
            {"type": "function", "function": {"name": "core_memory_update", "description": "Save PERMANENT user traits.", "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}}},
            {"type": "function", "function": {"name": "delete_core_memory", "description": "REMOVE outdated info.", "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value_to_remove": {"type": "string"}}, "required": ["key", "value_to_remove"]}}},
            {"type": "function", "function": {"name": "update_entity_memory", "description": "Update people/places.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "relationship": {"type": "string"}, "attributes": {"type": "object"}}, "required": ["name", "attributes"]}}},
            {"type": "function", "function": {"name": "log_event", "description": "Log a timeline event.", "parameters": {"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]}}},
            {"type": "function", "function": {"name": "save_knowledge", "description": "Save facts/codes.", "parameters": {"type": "object", "properties": {"topic": {"type": "string"}, "content": {"type": "string"}}, "required": ["topic", "content"]}}},
            {"type": "function", "function": {"name": "archival_memory_search", "description": "Search history.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}
        ]

    def process_message(self, user_message):
        try:
            current_turn = self.core.increment_turn()
            self.buffer.add_turn("user", user_message)
            
            # --- PROACTIVE SEARCH ---
            recent_history = [msg["content"] for msg in self.buffer.get_messages()[-2:]]
            recent_history.append(user_message)
            search_query = " ".join(recent_history)

            # 1. Search ChromaDB
            archival_results = self.archive.search_memory(user_message, n_results=3)
            
            # 2. Get Context from Core
            core_context = self.core.get_core_prompt(
                recent_history_text=search_query, 
                archival_context=archival_results
            )
            
            # 3. GENERATE FULL SYSTEM PROMPT
            system_instruction = SYSTEM_PROMPT_TEMPLATE.format(core_memory_block=core_context)
            
            messages = [{"role": "system", "content": system_instruction}]
            for msg in self.buffer.get_messages():
                if msg["content"] != user_message:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})

            active_memories = archival_results
            final_response_text = ""

            for _ in range(3):
                try:
                    completion = client.chat.completions.create(
                        model=config.LLM_MODEL,
                        messages=messages,
                        tools=self.tools_schema,
                        tool_choice="auto",
                        parallel_tool_calls=True, 
                        max_tokens=1024
                    )
                except RateLimitError:
                    return "System Limit Reached: Please wait a moment.", [], "" # <--- Fixed: Return 3 values
                except BadRequestError as e:
                    if "tool_use_failed" in str(e):
                        messages.append({"role": "user", "content": "SYSTEM ERROR: Invalid tool format."})
                        continue
                    else:
                        raise e
                
                response_message = completion.choices[0].message
                
                if response_message.tool_calls:
                    messages.append(response_message)
                    for tool_call in response_message.tool_calls:
                        fname = tool_call.function.name
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except:
                            args = {}
                        
                        result = "Success"
                        try:
                            if fname == "core_memory_update": result = self.core.update_profile(args["key"], args["value"])
                            elif fname == "delete_core_memory": result = self.core.remove_from_profile(args["key"], args["value_to_remove"])
                            elif fname == "update_entity_memory": result = self.core.update_entity(args["name"], args.get("relationship"), args["attributes"])
                            elif fname == "log_event": result = self.core.log_event(args["description"])
                            elif fname == "save_knowledge": result = self.core.add_general_knowledge(args["topic"], args["content"])
                            elif fname == "archival_memory_search":
                                search_res = self.archive.search_memory(args["query"])
                                active_memories.extend(search_res)
                                result = json.dumps(search_res)
                        except Exception as e:
                            result = f"Error: {str(e)}"

                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": fname,
                            "content": str(result)
                        })
                else:
                    content = response_message.content if response_message.content else ""
                    if "<function" in content or ("{" in content and "type" in content and "function" in content):
                        messages.append({"role": "user", "content": "SYSTEM ERROR: Raw code detected."})
                        continue
                    final_response_text = content
                    break
            
            if not final_response_text:
                final_response_text = "I'm having trouble retrieving that information right now."
            
            if final_response_text:
                self.buffer.add_turn("assistant", final_response_text)
                def background_save():
                    self.archive.add_memory(f"Bot: {final_response_text}", "assistant", current_turn)
                save_thread = threading.Thread(target=background_save)
                save_thread.start()

            # --- RETURN 3 VALUES (FIXED) ---
            return final_response_text, active_memories, system_instruction

        except Exception as e:
            print(f"--- ORCHESTRATOR CRASHED --- \n{str(e)}")
            # --- RETURN 3 VALUES (FIXED) ---
            return f"System Error: {str(e)}", [], ""