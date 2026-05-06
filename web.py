from datetime import datetime, timezone
from hashlib import sha1
import re
from threading import Lock
import time
from xml.sax.saxutils import escape

from flask import Flask, Response, abort, jsonify, render_template, request, url_for

from core.ai import analyze_news, detect_category
from core.scraper import fetch_all_news
from db.database import get_news, get_recent_news, init_db, is_database_configured, save_news

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
VALID_TABS = {value for value, _label in CATEGORY_TABS}

STATIC_PAGES = {
    "about": {
        "title": "About CryptositNews",
        "heading": "Independent crypto news monitoring for traders and builders",
        "description": "CryptositNews tracks public crypto news sources, market data and high-impact headlines so readers can react faster and research smarter.",
        "bullets": [
            "We monitor Bitcoin, Ethereum, Solana, DeFi, NFTs, regulation, security and broader Web3 markets.",
            "News items include lightweight sentiment, impact and category labels to make scanning faster.",
            "Market widgets are for educational monitoring only and are not financial advice.",
        ],
    },
    "editorial-policy": {
        "title": "Editorial Policy | CryptositNews",
        "heading": "Editorial policy and transparency",
        "description": "Our goal is to make crypto headlines easier to discover, verify and contextualize while clearly linking back to original sources.",
        "bullets": [
            "Every aggregated headline links to the original publisher for attribution and full context.",
            "Automated labels are informational signals, not trading recommendations.",
            "High-impact topics such as regulation, hacks and exchange news are highlighted for faster review.",
        ],
    },
    "learn": {
        "title": "Learn Crypto Trading & Blockchain Basics | CryptositNews",
        "heading": "Learn crypto, blockchain and trading basics",
        "description": "Start with evergreen explainers that help new readers understand market structure, risk and common crypto terms.",
        "bullets": [
            "Bitcoin ETF: why spot ETFs can affect market liquidity and sentiment.",
            "Funding rates: how perpetual futures can reveal crowded long or short trades.",
            "Risk management: position sizing, stop losses and avoiding over-leverage.",
            "Wallet security: seed phrase safety, approvals and common phishing risks.",
        ],
    },
}


def _parse_page(value):
    try:
        return max(int(value), 1)
    except (TypeError, ValueError):
        return 1


def _slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "crypto-news"


def _article_slug(item):
    digest = sha1((item.get("url") or item.get("id") or item["title"]).encode("utf-8")).hexdigest()[:10]
    return f"{_slugify(item['title'])}-{digest}"


def _enhance_news_item(item):
    item["slug"] = _article_slug(item)
    item["detail_url"] = url_for("article_detail", slug=item["slug"])
    item["external_url"] = item["url"]
    return item


def _format_db_rows(rows):
    news = []
    for n in rows:
        news.append(_enhance_news_item({
            "id": n[0],
            "title": n[1],
            "url": n[2],
            "source": n[3],
            "sentiment": n[4],
            "impact": n[5],
            "category": n[6],
            "time": str(n[7])[:16],
        }))
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

    return _enhance_news_item({
        "id": enriched["id"],
        "title": enriched["title"],
        "url": enriched["url"],
        "source": enriched.get("source", "Crypto News"),
        "sentiment": enriched["sentiment"],
        "impact": enriched["impact"],
        "category": enriched["category"],
        "time": enriched.get("published") or "Live RSS",
    })


def _live_rss_news(tab="all", search="", page=1):
    now = time.time()
    if now >= _fallback_cache["expires_at"]:
        with _fallback_cache_lock:
            now = time.time()
            if now >= _fallback_cache["expires_at"]:
                live_items = [_format_live_item(item) for item in fetch_all_news(max_items=60)]
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


def _recent_articles(limit=100):
    init_db()
    articles = _format_db_rows(get_recent_news(limit))
    if articles:
        return articles

    now = time.time()
    if now >= _fallback_cache["expires_at"] or not _fallback_cache["items"]:
        _live_rss_news()
    return _fallback_cache["items"][:limit]


def _find_article(slug):
    for item in _recent_articles(limit=120):
        if item["slug"] == slug:
            return item
    return None


def _structured_news(news):
    return [{
        "@type": "NewsArticle",
        "headline": item["title"],
        "url": url_for("article_detail", slug=item["slug"], _external=True),
        "mainEntityOfPage": url_for("article_detail", slug=item["slug"], _external=True),
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
    news_sitemap_url = url_for("news_sitemap_xml", _external=True)
    return Response(
        f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\nSitemap: {news_sitemap_url}\n",
        mimetype="text/plain",
    )


@app.route("/sitemap.xml")
def sitemap_xml():
    today = datetime.now(timezone.utc).date().isoformat()
    urls = [
        url_for("home", _external=True),
        url_for("static_page", page="about", _external=True),
        url_for("static_page", page="editorial-policy", _external=True),
        url_for("static_page", page="learn", _external=True),
    ] + [
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


@app.route("/news-sitemap.xml")
def news_sitemap_xml():
    articles = _recent_articles(limit=50)
    body = "".join(
        "<url>"
        f"<loc>{escape(url_for('article_detail', slug=item['slug'], _external=True))}</loc>"
        "<news:news>"
        "<news:publication><news:name>CryptositNews</news:name><news:language>en</news:language></news:publication>"
        f"<news:publication_date>{escape(item.get('time') or datetime.now(timezone.utc).isoformat())}</news:publication_date>"
        f"<news:title>{escape(item['title'])}</news:title>"
        "</news:news>"
        "</url>"
        for item in articles
    )
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">{body}</urlset>',
        mimetype="application/xml",
    )


@app.route("/news/<slug>")
def article_detail(slug):
    article = _find_article(slug)
    if article is None:
        abort(404)

    related = [
        item for item in _recent_articles(limit=80)
        if item["slug"] != slug and item["category"] == article["category"]
    ][:4]
    if len(related) < 4:
        related.extend([
            item for item in _recent_articles(limit=80)
            if item["slug"] != slug and item not in related
        ][:4 - len(related)])

    seo_title = f"{article['title']} | CryptositNews"
    seo_description = (
        f"Latest {article['category']} crypto news from {article.get('source') or 'trusted crypto sources'} "
        f"with sentiment {article['sentiment']} and {article['impact']} impact label."
    )
    return render_template(
        "article.html",
        article=article,
        canonical_url=request.base_url,
        related=related,
        seo_description=seo_description,
        seo_keywords=SEO_KEYWORDS,
        seo_title=seo_title,
        structured_article={
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": article["title"],
            "url": request.base_url,
            "mainEntityOfPage": request.base_url,
            "articleSection": article["category"],
            "datePublished": article["time"],
            "publisher": {"@type": "Organization", "name": "CryptositNews"},
        },
    )


@app.route("/<page>")
def static_page(page):
    content = STATIC_PAGES.get(page)
    if content is None:
        abort(404)
    return render_template(
        "page.html",
        canonical_url=request.base_url,
        content=content,
        seo_description=content["description"],
        seo_keywords=SEO_KEYWORDS,
        seo_title=content["title"],
    )


@app.route("/")
def home():
    tab = request.args.get("tab", "all")
    if tab not in VALID_TABS:
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
