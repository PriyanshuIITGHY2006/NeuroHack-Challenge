#!/bin/bash
echo "Starting MemoryOS Backend..."
python backend/server.py &
sleep 5
echo "Starting Frontend..."
streamlit run frontend/app.py