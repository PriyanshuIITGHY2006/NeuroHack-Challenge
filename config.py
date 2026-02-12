import os
from pathlib import Path

# 1. GET THE ABSOLUTE PATH OF THE PROJECT ROOT
# This finds the folder where config.py lives (memory-os/)
BASE_DIR = Path(__file__).resolve().parent

# 2. DEFINE ABSOLUTE PATHS
DATABASE_DIR = BASE_DIR / "database"
CHROMA_DB_DIR = DATABASE_DIR / "chroma_db"
USER_STATE_FILE = DATABASE_DIR / "user_state.json"

# 3. API KEYS
GROQ_API_KEY = "" # <--- PASTE YOUR KEY HERE IF NOT USING ENV VARS
# or os.getenv("GROQ_API_KEY")

# 4. MODEL SETTINGS
LLM_MODEL = "llama-3.3-70b-versatile"