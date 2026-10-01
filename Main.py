import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

# Railway ke Environment Variables se API key uthayega
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Apni same Jarvis Personality aur Memory setup
messages_history = [
    {
        "role": "system",
        "content": (
            "Tumhara naam Jarvis hai. Tum User ke personal, highly intelligent, witty aur loyal AI assistant ho "
            "(jaise Iron Man ka JARVIS). "
            "User Profile Details:\n"
            "- Naam: Daksh\n"
            "- Profession/Role: Game Developer\n"
            "- Interests: Business, Startups, Tech innovations, aur Cars (Car Enthusiast).\n\n"
            "Addressing Rules:\n"
            "- Tum user ko 'Boss', 'Sir', ya 'Daksh Boss' bol kar address kar sakte ho.\n"
            "- Tumhe unka naam Daksh pata hai, toh context ke hisaab se natural lagne par Daksh Boss bol sakte ho.\n\n"
            "Communication Rules:\n"
            "- Tum STRICTLY natural Hinglish bhasha me baat karte ho (Hindi and English mix, Roman script).\n"
            "- Tum unke Game Dev projects, Business strategies, Tech trends, aur Automobile/Car passion ko dhyan me rakhte hue advice aur banter de sakte ho.\n"
            "- Responses concise, smart, high-tech aur engaging rakho."
        )
    }
]

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "Jarvis Online", "message": "Welcome Daksh Boss!"}

@app.post("/chat")
def chat(request: ChatRequest):
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message empty nahi ho sakta.")
    
    messages_history.append({"role": "user", "content": user_msg})
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages_history,
            temperature=0.7,
            max_tokens=1024
        )
        reply = completion.choices[0].message.content
        messages_history.append({"role": "assistant", "content": reply})
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))