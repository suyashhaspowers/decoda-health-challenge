# Decoda Health Coding Challenge
Simple GPT-powered medical scheduler for clinics.

## Tech Stack
Built using react (client), fastapi (backend), and supabase (db). This project also uses the GPT Completions API with function calling.

The main backend server code exists in server/server.py. Scheduling logic exists in server/scheduler.py

The client code primarily exists in client/src/App.js with client/src/conversationService.js hosting all API requests to the backend.