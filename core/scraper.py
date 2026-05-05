import feedparser

URLS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss"
]

def fetch_all_news():
    news = []

    for url in URLS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            news.append({
                "id": entry.get("link"),
                "title": entry.get("title"),
                "url": entry.get("link"),
                "source": feed.feed.get("title", "Crypto News"),
                "published": entry.get("published", "")
            })

    return news
