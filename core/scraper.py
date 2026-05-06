from concurrent.futures import ThreadPoolExecutor, as_completed
from time import mktime

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
    "User-Agent": "Mozilla/5.0 (compatible; CryptositNewsBot/1.0; +https://cryptositnews.com)",
    "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7",
}

REQUEST_TIMEOUT_SECONDS = 6
MAX_WORKERS = 8
DEFAULT_MAX_ITEMS = 80


def _published_timestamp(entry):
    parsed_date = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed_date:
        return 0
    return int(mktime(parsed_date))


def _parse_feed(feed_config):
    url = feed_config["url"]
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return feed_config, feedparser.parse(response.content)
    except requests.RequestException as e:
        print("RSS FETCH ERROR:", url, e)
        return feed_config, feedparser.parse("")


def _entry_to_item(feed_config, feed, entry):
    link = entry.get("link")
    title = entry.get("title")

    if not link or not title:
        return None

    return {
        "id": link,
        "title": title.strip(),
        "url": link,
        "source": feed.feed.get("title") or feed_config["source"],
        "published": entry.get("published") or entry.get("updated") or "",
        "published_ts": _published_timestamp(entry),
    }


def fetch_all_news(max_items=DEFAULT_MAX_ITEMS):
    news = []
    seen_links = set()

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(FEEDS))) as executor:
        futures = [executor.submit(_parse_feed, feed_config) for feed_config in FEEDS]

        for future in as_completed(futures):
            try:
                feed_config, feed = future.result()
            except Exception as e:
                print("RSS WORKER ERROR:", e)
                continue

            url = feed_config["url"]
            if getattr(feed, "bozo", False):
                print(
                    "RSS PARSE ERROR:",
                    url,
                    getattr(feed, "bozo_exception", "unknown error"),
                )

            for entry in feed.entries:
                item = _entry_to_item(feed_config, feed, entry)
                if not item or item["url"] in seen_links:
                    continue

                seen_links.add(item["url"])
                news.append(item)

    sorted_news = sorted(news, key=lambda item: item.get("published_ts", 0), reverse=True)
    if max_items is None:
        return sorted_news
    return sorted_news[:max_items]
