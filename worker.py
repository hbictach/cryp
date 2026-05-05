import time
from core.scraper import fetch_all_news
from services.telegram import send_message

def run():
    seen = set()

    while True:
        news = fetch_all_news()

        for item in news[:5]:
            if item["id"] in seen:
                continue

            msg = f"🚨 @CryptositNews\n\n📰 {item['title']}\n\n🔗 {item['url']}"
            send_message(msg)

            seen.add(item["id"])

        time.sleep(60)

if __name__ == "__main__":
    run()
