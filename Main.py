import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI()

# Credentials from Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

SYSTEM_PROMPT = """Tumhara naam Jarvis hai. Tum User ke personal, highly intelligent, witty aur loyal AI assistant ho (jaise Iron Man ka JARVIS).
User Profile Details:
- Naam: Daksh
- Profession/Role: Game Developer
- Interests: Business, Startups, Tech innovations, aur Cars (Car Enthusiast).

Addressing Rules:
- Tum user ko 'Boss', 'Sir', ya 'Daksh Boss' bol kar address kar sakte ho.

Communication Rules:
- Tum STRICTLY natural Hinglish bhasha me baat karte ho (Hindi and English mix, Roman script).
- Responses concise, smart, high-tech aur engaging rakho."""

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "Jarvis Online", "memory": "Supabase Connected"}

@app.post("/chat")
def chat(request: ChatRequest):
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message empty nahi ho sakta.")

    try:
        # Fetch last 10 messages from Supabase
        history_res = supabase.table("chat_history").select("role, content").order("created_at", desc=False).limit(10).execute()
        db_history = history_res.data if history_res.data else []

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for item in db_history:
            messages.append({"role": item["role"], "content": item["content"]})
        
        messages.append({"role": "user", "content": user_msg})

        # Generate AI response
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        reply = completion.choices[0].message.content

        # Save to database
        supabase.table("chat_history").insert([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": reply}
        ]).execute()

        return {"response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))