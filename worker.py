import time
import random
from core.scraper import fetch_all_news
from services.telegram import send_message
from core.ai import analyze_news
from core.alerts import is_alert
from services.twitter import format_tweet
from db.database import save_news

MAX_PER_CYCLE = 5  # زدنا العدد باش نشوفو نتائج

def is_premium():
    return random.random() < 0.3

def run():
    seen = set()

    print("🚀 Worker started...")

    while True:
        try:
            news = fetch_all_news()
            print(f"📰 Fetched {len(news)} news")

            count = 0

            for item in news:
                if count >= MAX_PER_CYCLE:
                    break

                if not item.get("id") or not item.get("title"):
                    continue

                if item["id"] in seen:
                    continue

                ai = analyze_news(item["title"])

                # ❌ عطّلنا الفلترة مؤقتاً
                # if not is_alert(item["title"]) and ai["impact"] != "HIGH":
                #     continue

                # premium logic
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

                # 📢 Telegram
                try:
                    send_message(msg)
                    print("✅ Sent to Telegram")
                except Exception as e:
                    print("❌ Telegram error:", e)

                # 💾 DATABASE (مهم)
                try:
                    print("💾 Saving:", item["title"])
                    save_news(item)
                except Exception as e:
                    print("❌ DB error:", e)

                # 🐦 Twitter mock
                tweet = format_tweet(item["title"], ai)
                print("🐦 TWEET:", tweet)

                seen.add(item["id"])
                count += 1

            print("⏱ Sleeping...\n")
            time.sleep(60)

        except Exception as e:
            print("🔥 Worker crash:", e)
            time.sleep(10)


if __name__ == "__main__":
    run()
