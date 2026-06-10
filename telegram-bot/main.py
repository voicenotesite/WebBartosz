import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()

CHAT_FILE = Path("chats.json")
if not CHAT_FILE.exists():
    CHAT_FILE.write_text("[]")

TELEGRAM_BOT_TOKEN = "8444958704:AAGkwFMh5IApceI61uipnmXjXWbvQWbDgXc"
YOUR_TELEGRAM_CHAT_ID = "8444958704"
TELEGRAM_API = f"https://api.telegram.org/botest{TELEGRAM_BOT_TOKEN}"

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

@app.post("/telegram-webhook")
async def telegram_webhook(update: dict):
    if "message" in update and "text" in update["message"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        
        resp = requests.post(f"{TELEGRAM_API}/sendMessage", data={
            "chat_id": chat_id,
            "text": f"🤖 Odpowiedziałeś: {text}"
        })
    
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "Telegram Chat Bot is running"}