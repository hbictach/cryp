from flask import Flask, jsonify, request, Response
from db.database import get_news, init_db
import time
import os

app = Flask(__name__)
init_db()

SITE_NAME = "CryptoAlertAlpha"
SITE_URL  = os.getenv("SITE_URL", "https://cryp-production.up.railway.app")

# =========================
# Cache
# =========================
_cache = {}
CACHE_TTL = 60

def cache_get(key):
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _cache[key]
    return None

def cache_set(key, value):
    _cache[key] = (value, time.time())

# =========================
# Categories
# =========================
def get_category(title):
    t = title.lower()
    if "bitcoin" in t: return "bitcoin"
    if "ethereum" in t: return "ethereum"
    if "sec" in t or "regulation" in t: return "regulation"
    if "hack" in t or "exploit" in t: return "breaking"
    return "market"

# =========================
# Home
# =========================
@app.route("/")
def home():
    tab = request.args.get("tab", "all")
    cache_key = f"home_{tab}"

    cached = cache_get(cache_key)
    if cached:
        return cached

    news = get_news()

    # filter
    if tab != "all":
        news = [n for n in news if get_category(n[1]) == tab]

    html = f"""
    <html>
    <head>
        <title>{SITE_NAME}</title>
        <style>
            body {{
                background:#0f172a;
                color:white;
                font-family:Arial;
                padding:20px;
            }}
            .nav a {{
                margin-right:10px;
                color:#38bdf8;
                text-decoration:none;
            }}
            .card {{
                background:#1e293b;
                padding:15px;
                margin:10px 0;
                border-radius:12px;
            }}
            .title {{
                font-weight:bold;
                font-size:18px;
            }}
            .btn {{
                margin-top:8px;
                display:inline-block;
                background:#38bdf8;
                color:black;
                padding:6px 12px;
                border-radius:6px;
                text-decoration:none;
            }}
        </style>
    </head>
    <body>

    <h1>🚀 {SITE_NAME}</h1>

    <div class="nav">
        <a href="/">All</a>
        <a href="/?tab=bitcoin">BTC</a>
        <a href="/?tab=ethereum">ETH</a>
        <a href="/?tab=regulation">Regulation</a>
        <a href="/?tab=breaking">Breaking</a>
    </div>
    """

    for n in news[:50]:
        html += f"""
        <div class="card">
            <div class="title">🚨 {n[1]}</div>
            <a class="btn" href="{n[2]}" target="_blank">Read more</a>
        </div>
        """

    html += "</body></html>"

    cache_set(cache_key, html)
    return html

# =========================
# API
# =========================
@app.route("/api/news")
def api_news():
    news = get_news()
    return jsonify(news)

# =========================
# RSS
# =========================
@app.route("/rss.xml")
def rss():
    news = get_news()
    items = ""

    for n in news[:20]:
        items += f"""
        <item>
            <title>{n[1]}</title>
            <link>{n[2]}</link>
        </item>
        """

    xml = f"""<?xml version="1.0"?>
    <rss><channel>
    <title>{SITE_NAME}</title>
    {items}
    </channel></rss>"""

    return Response(xml, mimetype="application/xml")

# =========================
# Health
# =========================
@app.route("/health")
def health():
    return {"status":"ok"}
