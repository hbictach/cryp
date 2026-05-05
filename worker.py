import time
from core.scraper import fetch_all_news
from services.telegram import send_message
from core.ai import analyze_news
from core.alerts import is_alert
from db.database import save_news, init_db

init_db()

MAX_PER_CYCLE = 5

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

            # 🧠 تخزين AI data
            item["sentiment"] = ai.get("sentiment", "neutral")
            item["impact"] = ai.get("impact", "MEDIUM")
            item["source"] = item.get("source", "Crypto News")

            save_news(item)

            # 📢 Telegram
            msg = f"""
🚨 BREAKING

{item['title']}

🧠 {ai.get('summary','')}
📊 Impact: {item['impact']}
📈 Sentiment: {item['sentiment']}

🔗 {item['url']}
"""

            send_message(msg)

            seen.add(item["id"])
            count += 1

        print("⏱ Sleeping...")
        time.sleep(60)

if __name__ == "__main__":
    run()
