from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
import requests

FEEDS = [
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "source": "CoinDesk"},
    {"url": "https://cointelegraph.com/rss", "source": "Cointelegraph"},
    {"url": "https://decrypt.co/feed", "source": "Decrypt"},
    {"url": "https://www.theblock.co/rss.xml", "source": "The Block"},
    {"url": "https://cryptoslate.com/feed/", "source": "CryptoSlate"},
    {"url": "https://www.newsbtc.com/feed/", "source": "NewsBTC"},
    {"url": "https://beincrypto.com/feed/", "source": "BeInCrypto"},
    {"url": "https://u.today/rss", "source": "U.Today"},
    {"url": "https://ambcrypto.com/feed/", "source": "AMBCrypto"},
    {"url": "https://dailyhodl.com/feed/", "source": "The Daily Hodl"},
    {"url": "https://bitcoinmagazine.com/.rss/full/", "source": "Bitcoin Magazine"},
]

HEADERS = {
    "User-Agent": "CryptositNewsBot/1.0 (+https://cryptositnews.com)",
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}


def _parse_feed(feed_config):
    url = feed_config["url"]
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()
        return feed_config, feedparser.parse(response.content)
    except requests.RequestException as e:
        print("RSS FETCH ERROR:", url, e)
        return feed_config, feedparser.parse("")


def fetch_all_news():
    news = []
    seen_links = set()

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_parse_feed, feed_config) for feed_config in FEEDS]

        for future in as_completed(futures):
            feed_config, feed = future.result()
            url = feed_config["url"]

            if getattr(feed, "bozo", False):
                print(
                    "RSS PARSE ERROR:",
                    url,
                    getattr(feed, "bozo_exception", "unknown error"),
                )

            for entry in feed.entries:
                link = entry.get("link")
                title = entry.get("title")

                if not link or not title or link in seen_links:
                    continue

                seen_links.add(link)
                news.append({
                    "id": link,
                    "title": title,
                    "url": link,
                    "source": feed.feed.get("title") or feed_config["source"],
                    "published": entry.get("published", ""),
                })

    return news
