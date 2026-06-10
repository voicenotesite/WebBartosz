import urllib.request
import urllib.parse
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()

CHAT_FILE = Path("chats.json")
if not CHAT_FILE.exists():
    CHAT_FILE.write_text("[]")

CHAT_ID = "8444958704"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    name: str
    message: str

def detect_gender(name: str) -> str:
    import json
    try:
        with open("firstnames.json", "r") as f:
            names = json.load(f)
        return names.get(name.lower(), "unknown")
    except:
        return "unknown"

@app.post("/send-message")
async def send_message(msg: Message):
    chats = json.loads(CHAT_FILE.read_text())
    chats.append({"name": msg.name, "message": msg.message})
    CHAT_FILE.write_text(json.dumps(chats))
    
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": f"✨ Nowa wiadomość od: {msg.name}\n\n{msg.message}",
        "parse_mode": "HTML"
    }).encode()
    
    req = urllib.request.Request(
        f"https://api.telegram.org/botest8444958704:AAGkwFMh5IApceI61uipnmXjWbvQWbDgXc/sendMessage",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    try:
        urllib.request.urlopen(req)
    except:
        pass
    
    return {"status": "saved", "chat_id": len(chats)}

@app.get("/chats")
async def get_chats():
    return json.loads(CHAT_FILE.read_text())

@app.get("/")
async def root():
    return {"status": "Telegram Chat Bot is running"}