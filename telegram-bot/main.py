from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from typing import Optional

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
YOUR_TELEGRAM_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
TELEGRAM_API = "https://api.telegram.org/bottesttelegramchatbotbot"

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
    gender = detect_gender(msg.name)
    if gender == "male":
        greeting = f"👨 Ghost Dev połączył się z Panem <b>{msg.name}</b>"
    elif gender == "female":
        greeting = f"👩 Ghost Dev połączyła się z Panią <b>{msg.name}</b>"
    else:
        greeting = f"✨ Ghost Dev: <b>{msg.name}</b>"
    
    text = f"{greeting}\n\n📝 {msg.message}"
    
    resp = requests.post(f"{TELEGRAM_API}/sendMessage", data={
        "chat_id": YOUR_TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })
    
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Telegram send failed")
    
    return {"status": "sent"}

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