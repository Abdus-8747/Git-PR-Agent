import requests
import os
from dotenv import load_dotenv

# This physically loads the variables from your .env file into os.environ
load_dotenv() 

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(message: str):
    # Sanity check: Ensure the variables actually loaded
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
    
    # Check if Telegram accepted the message
    if response.status_code == 200:
        print("Message sent successfully!")
        return True
    else:
        # If it fails, print the exact error Telegram gives us
        print(f"Failed to send message. Telegram responded with: {response.status_code}")
        print(response.json())
        return False