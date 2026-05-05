import time
import feedparser
import requests
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": msg
    })

def fetch():
    feed = feedparser.parse("https://cointelegraph.com/rss")
    return feed.entries[:5]

def run():
    seen = set()
    while True:
        news = fetch()
        for n in news:
            if n.link in seen:
                continue
            msg = f"📰 {n.title}\n\n🔗 {n.link}"
            send(msg)
            seen.add(n.link)
        time.sleep(60)

if __name__ == "__main__":
    run()
