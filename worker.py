import time
from core.scraper import fetch_all_news
from core.ai import analyze_news, detect_category
from db.database import save_news, init_db

init_db()

def run():
    seen = set()

    while True:
        news = fetch_all_news()

        for item in news:
            if item["id"] in seen:
                continue

            ai = analyze_news(item["title"])

            item["sentiment"] = ai["sentiment"]
            item["impact"] = ai["impact"]
            item["category"] = detect_category(item["title"])

            save_news(item)
            seen.add(item["id"])

        print("⏱ cycle done")
        time.sleep(60)

if __name__ == "__main__":
    run()
