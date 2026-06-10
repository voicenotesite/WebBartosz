import urllib.request
import urllib.parse
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

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
    data = urllib.parse.urlencode({
        "chat_id": YOUR_TELEGRAM_CHAT_ID,
        "text": f"Test: {msg.message}"
    }).encode()
    
    req = urllib.request.Request(
        f"{TELEGRAM_API}/sendMessage",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

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