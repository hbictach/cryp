import os
import time

from core.ai import analyze_news, detect_category
from core.scraper import fetch_all_news
from db.database import init_db, save_news


def _sleep_seconds():
    try:
        return max(int(os.getenv("WORKER_SLEEP_SECONDS", "60")), 10)
    except ValueError:
        return 60


def run():
    seen = set()

    while True:
        if not init_db():
            print("Database is not ready; worker will retry")
            time.sleep(_sleep_seconds())
            continue

        news = fetch_all_news()

        for item in news:
            if item["id"] in seen:
                continue

            ai = analyze_news(item["title"])

            item["sentiment"] = ai["sentiment"]
            item["impact"] = ai["impact"]
            item["category"] = detect_category(item["title"])

            if save_news(item):
                seen.add(item["id"])

        print("⏱ cycle done")
        time.sleep(_sleep_seconds())


if __name__ == "__main__":
    run()
