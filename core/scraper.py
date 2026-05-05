import feedparser

RSS_FEEDS = [
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
    {"name": "CoinTelegraph", "url": "https://cointelegraph.com/rss"},
]

def fetch_all_news():
    news = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries[:15]:
            news.append({
                "id": entry.get("link"),
                "title": entry.get("title"),
                "url": entry.get("link")
            })
    return news
