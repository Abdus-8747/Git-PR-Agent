import requests
import os
from dotenv import load_dotenv

load_dotenv() 

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: Missing Telegram credentials! Check your .env file.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
    )
    
    if response.status_code == 200:
        print("Message sent successfully!")
        return True
    else:
        print(f"Failed to send message. Telegram responded with: {response.status_code}")
        print(response.json())
        return False