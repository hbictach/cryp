import feedparser

URLS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss"
]

def fetch_all_news():
    news = []

    for url in URLS:
        feed = feedparser.parse(url)

        if getattr(feed, "bozo", False):
            print(
                "RSS PARSE ERROR:",
                url,
                getattr(feed, "bozo_exception", "unknown error"),
            )

        for entry in feed.entries:
            link = entry.get("link")
            title = entry.get("title")

            if not link or not title:
                continue

            news.append({
                "id": link,
                "title": title,
                "url": link,
                "source": feed.feed.get("title", "Crypto News"),
                "published": entry.get("published", "")
            })

    return news
