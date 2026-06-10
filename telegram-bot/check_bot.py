#!/usr/bin/env python3
import requests
import time

# Twórz nowego bota przez BotFather
print("Który bot chcesz użyć?")
print("1. Stwórz nowego bota w @BotFather")
print("2. Wyślij /newbot")
print("3. Nazwij: GhostChatBot2") 
print("4. Username: ghost_chat_bot_demo")
print("5. Otrzymasz token")
print("")
print("Aktualny test:")

TOKEN = "8804329666:AAFxbbommutsghDDaDJHOZQhaCTQI0SaowU"
BOT_NAME = "telegtamchatbotbot"

# Test czy bot istnieje
resp = requests.get(f"https://api.telegram.org/bottest{BOT_NAME}/getMe")
print(f"Bot {BOT_NAME} exists: {resp.status_code == 200}")
print(resp.text)