from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from models import Message
from openai import OpenAI, APIError
from scheduler import gpt_tools, schedule_appointment
from dotenv import load_dotenv
import uvicorn
import os


# Constants
SUPABASE_URL = "https://iqxsblxordjovkxwebga.supabase.co"

# Handle environment variables
load_dotenv()
SUPABASE_KEY = os.environ.get('SUPABASE_API_KEY')
OPEN_AI_KEY = os.environ.get('OPEN_AI_KEY')

# Create an insance of Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create an instance of the FastAPI class
app = FastAPI()
# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create an insance of the GPT Client
gpt_client = OpenAI(api_key=OPEN_AI_KEY)

# Get Conversation from conversation_id
@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id):
    conversation_request = supabase.table("conversation").select("*").eq("id", conversation_id).execute()

    conversation_data = conversation_request.data

    if not conversation_data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation = conversation_data[0]

    return {"is_successful": True, "data": conversation}

# Get all conversations
@app.get("/conversations")
async def get_conversations():
    # Sort conversation based on updated_at attribute
    conversations_request = supabase.table("conversation").select("last_message", 'id').order("updated_at.desc").execute()
    
    conversations_data = conversations_request.data

    if not conversations_data:
        raise HTTPException(status_code=404, detail="Conversations not found")

    conversations = conversations_request.data

    return {"is_successful": True, "data": conversations}

# Get all messages in a conversation
@app.get("/conversation/{conversation_id}/messages")
async def get_conversation_history(conversation_id):
    # Sort messages based on the its created_at attribute
    messages_request = supabase.table("message").select("*").eq("conversation", conversation_id).order("created_at.asc").execute()
    
    messages_data = messages_request.data

    if not messages_data:
        raise HTTPException(status_code=404, detail="Messages not found")

    messages = messages_request.data

    return {"is_successful": True, "data": messages}

# Create conversation
@app.post("/conversation/create")
async def create_new_conversation():
    new_conversation = supabase.table("conversation").insert({}).execute()
    
    conversation_id = new_conversation.data[0]['id']

    return {"is_successful": True, "data": conversation_id}

#### Send outgoing message, get response and add both messages to a conversation
@app.post("/conversation/{conversation_id}/message/send")
async def send_message(conversation_id, message: Message):

    # Outgoing message (user -> GPT)
    await add_new_message_to_conversation(conversation_id, message.message_text, False)

    # OPENAI GPT CALL FOR REPSONSE
    completions_response = await get_gpt_completions_response(conversation_id)

    # Incoming message (GPT -> user)
    await add_new_message_to_conversation(conversation_id, completions_response, True)

    return {"is_successful": True, "data": completions_response}

# Helper functions
async def add_new_message_to_conversation(converation_id, message_text, is_incoming):
    supabase.table("message").insert({"message_text": message_text, "is_incoming": is_incoming, "conversation": converation_id}).execute()
    supabase.table("conversation").update({"last_message": message_text}).eq("id", converation_id).execute()
    
async def get_gpt_completions_response(conversation_id):
    raw_messages = await get_conversation_history(conversation_id)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    for message in raw_messages['data']:
        role = "user"
        content = message['message_text']

        if message['is_incoming']:
            role = "assistant"

        messages.append({'role': role, 'content': content})

    print(messages)

    try:
        response = gpt_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=gpt_tools
        )

        # Logic for using scheduler.py based on GPT Response
        if response.choices[0].finish_reason == "tool_calls":
            fn_arguments = response.choices[0].message.tool_calls[0].function.arguments
            scheduler_response = schedule_appointment(fn_arguments)

            gpt_response = "There was a conflict and your appointment could not scheduled."
            if scheduler_response:
                gpt_response = "Succesfully scheduled your appointment!"

            return gpt_response
        else:
            return response.choices[0].message.content
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API returned an API Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
