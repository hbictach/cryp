import time
import random
from core.scraper import fetch_all_news
from services.telegram import send_message
from core.ai import analyze_news
from core.alerts import is_alert
from services.twitter import format_tweet
from db.database import save_news

MAX_PER_CYCLE = 3

def is_premium():
    return random.random() < 0.3

def run():
    seen = set()

    while True:
        news = fetch_all_news()
        count = 0

        for item in news:
            if count >= MAX_PER_CYCLE:
                break

            if item["id"] in seen:
                continue

            ai = analyze_news(item["title"])

            if not is_alert(item["title"]) and ai["impact"] != "HIGH":
                continue

            if is_premium():
                premium = "🔒 Premium insight: breakout possible soon"
            else:
                premium = "🔒 Unlock premium signals 👉 DM @CryptositNews"

            msg = f"""
🚨 BREAKING — @CryptositNews

💥 {item['title']}

🧠 {ai['summary']}

📈 Impact: {ai['impact']}
📊 Sentiment: {ai['sentiment']}

{premium}

🔗 {item['url']}
"""

            # send telegram
            send_message(msg)

            # save to database 🔥
            save_news(item)

            # twitter mock
            tweet = format_tweet(item["title"], ai)
            print("TWEET:", tweet)

            seen.add(item["id"])
            count += 1

        time.sleep(60)

if __name__ == "__main__":
    run()
