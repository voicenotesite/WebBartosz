import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()

CHAT_FILE = Path("chats.json")
if not CHAT_FILE.exists():
    CHAT_FILE.write_text("[]")

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
    return {"status": "saved", "chat_id": len(chats)}

@app.get("/chats")
async def get_chats():
    return json.loads(CHAT_FILE.read_text())

@app.get("/")
async def root():
    return {"status": "Telegram Chat Bot is running"}