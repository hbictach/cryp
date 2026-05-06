from datetime import datetime, timezone
from threading import Lock
import time
from xml.sax.saxutils import escape

from flask import Flask, Response, jsonify, render_template, request, url_for

from core.ai import analyze_news, detect_category
from core.scraper import fetch_all_news
from db.database import get_news, init_db, is_database_configured, save_news

app = Flask(__name__)

FALLBACK_CACHE_SECONDS = 300
_fallback_cache = {
    "expires_at": 0,
    "items": [],
}
_fallback_cache_lock = Lock()

SEO_KEYWORDS = [
    "crypto news",
    "bitcoin news today",
    "ethereum news",
    "solana news",
    "xrp news",
    "bnb news",
    "cryptocurrency market analysis",
    "blockchain news",
    "defi news",
    "nft news",
    "memecoin news",
    "crypto regulation news",
    "crypto security news",
    "bitcoin ETF news",
    "altcoin market updates",
]

CATEGORY_TABS = [
    ("all", "All"),
    ("bitcoin", "Bitcoin"),
    ("ethereum", "Ethereum"),
    ("solana", "Solana"),
    ("xrp", "XRP"),
    ("binance", "BNB"),
    ("defi", "DeFi"),
    ("nft", "NFT"),
    ("memecoins", "Memecoins"),
    ("regulation", "Regulation"),
    ("security", "Security"),
    ("ai", "AI + DePIN"),
    ("general", "General"),
]


def _parse_page(value):
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return 1


def _format_db_rows(rows):
    news = []
    for n in rows:
        news.append({
            "id": n[0],
            "title": n[1],
            "url": n[2],
            "source": n[3],
            "sentiment": n[4],
            "impact": n[5],
            "category": n[6],
            "time": str(n[7])[:16],
        })
    return news


def _format_live_item(item):
    ai = analyze_news(item["title"])
    category = detect_category(item["title"])

    enriched = {
        **item,
        "sentiment": ai["sentiment"],
        "impact": ai["impact"],
        "category": category,
    }

    # Best effort: if the DB is configured but empty/stale, populate it while
    # still rendering live RSS news immediately for users.
    if is_database_configured():
        save_news(enriched)

    return {
        "id": enriched["id"],
        "title": enriched["title"],
        "url": enriched["url"],
        "source": enriched.get("source", "Crypto News"),
        "sentiment": enriched["sentiment"],
        "impact": enriched["impact"],
        "category": enriched["category"],
        "time": enriched.get("published") or "Live RSS",
    }


def _live_rss_news(tab="all", search="", page=1):
    now = time.time()
    if now >= _fallback_cache["expires_at"]:
        with _fallback_cache_lock:
            now = time.time()
            if now >= _fallback_cache["expires_at"]:
                live_items = [_format_live_item(item) for item in fetch_all_news()]
                _fallback_cache["items"] = live_items
                _fallback_cache["expires_at"] = now + (FALLBACK_CACHE_SECONDS if live_items else 60)

    items = _fallback_cache["items"]
    if tab and tab != "all":
        items = [item for item in items if item["category"] == tab]

    if search:
        needle = search.lower()
        items = [item for item in items if needle in item["title"].lower()]

    limit = 10
    offset = (page - 1) * limit
    return items[offset:offset + limit]


def _structured_news(news):
    return [{
        "@type": "NewsArticle",
        "headline": item["title"],
        "url": item["url"],
        "articleSection": item["category"],
        "publisher": {
            "@type": "Organization",
            "name": item.get("source") or "CryptositNews",
        },
    } for item in news[:10]]


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "database_configured": is_database_configured(),
    })


@app.route("/robots.txt")
def robots_txt():
    sitemap_url = url_for("sitemap_xml", _external=True)
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n",
        mimetype="text/plain",
    )


@app.route("/sitemap.xml")
def sitemap_xml():
    today = datetime.now(timezone.utc).date().isoformat()
    urls = [url_for("home", _external=True)] + [
        url_for("home", tab=tab, _external=True)
        for tab, _label in CATEGORY_TABS
        if tab != "all"
    ]
    body = "".join(
        f"<url><loc>{escape(url)}</loc><lastmod>{today}</lastmod><changefreq>hourly</changefreq></url>"
        for url in urls
    )
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
        mimetype="application/xml",
    )


@app.route("/")
def home():
    tab = request.args.get("tab", "all")
    valid_tabs = {value for value, _label in CATEGORY_TABS}
    if tab not in valid_tabs:
        tab = "all"

    search = request.args.get("search", "").strip()
    page = _parse_page(request.args.get("page", 1))

    init_db()
    news = _format_db_rows(get_news(tab, search, page))
    using_live_fallback = False

    if not news:
        news = _live_rss_news(tab, search, page)
        using_live_fallback = bool(news)

    seo_title = "Live Crypto News, Bitcoin, Ethereum & DeFi Market Updates | CryptositNews"
    seo_description = (
        "Real-time cryptocurrency news covering Bitcoin, Ethereum, DeFi, NFTs, "
        "crypto regulation, ETF headlines and blockchain market sentiment."
    )

    return render_template(
        "index.html",
        canonical_url=request.base_url,
        category_tabs=CATEGORY_TABS,
        news=news,
        page=page,
        search=search,
        selected_tab=tab,
        seo_description=seo_description,
        seo_keywords=SEO_KEYWORDS,
        seo_title=seo_title,
        structured_news=_structured_news(news),
        using_live_fallback=using_live_fallback,
    )
