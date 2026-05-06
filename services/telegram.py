import os

import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    if not TOKEN or not CHAT_ID:
        print("Telegram is not configured")
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print("TELEGRAM SEND ERROR:", e)
        return False
