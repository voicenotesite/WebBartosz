from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from typing import Optional

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
YOUR_TELEGRAM_CHAT_ID = os.getenv("YOUR_TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
TELEGRAM_API = "https://api.telegram.org/botest8444958704:AAGkwFMh5IApceI61uipnmXjXWbvQWbDgXc"

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
    resp = requests.post(f"{TELEGRAM_API}/sendMessage", data={
        "chat_id": YOUR_TELEGRAM_CHAT_ID,
        "text": f"Test: {msg.message}"
    }, timeout=10)
    return {"status": resp.status_code, "ok": resp.json().get("ok", False)}

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