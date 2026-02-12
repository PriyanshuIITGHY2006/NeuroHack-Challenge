from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from backend.logic.orchestrator import Orchestrator

# Initialize App and Orchestrator
app = FastAPI()
orchestrator = Orchestrator()

# Define Request Model
class ChatRequest(BaseModel):
    message: str

# Define API Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Unpack the 3 values from orchestrator
    response_text, active_memories, debug_prompt = orchestrator.process_message(request.message)
    
    return {
        "response": response_text,
        "active_memories": active_memories,
        "debug_prompt": debug_prompt  # <--- Send this to frontend
    }

# Entry Point for 'python -m backend.server'
if __name__ == "__main__":
    print("🚀 Starting MemoryOS Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)