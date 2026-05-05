from flask import Flask
from db.database import get_news
import requests

app = Flask(__name__)

# 💰 جلب الأسعار الحقيقية
def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        data = requests.get(url).json()

        return {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"],
            "SOL": data["solana"]["usd"]
        }
    except:
        return {"BTC": "-", "ETH": "-", "SOL": "-"}


@app.route("/")
def home():
    news = get_news()
    prices = get_prices()

    html = f"""
    <html>
    <head>
        <title>CryptoAlertAlpha</title>

        <style>
            body {{
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0f172a, #020617);
                color: white;
            }}

            .header {{
                display: flex;
                justify-content: space-between;
                padding: 20px 40px;
                background: rgba(255,255,255,0.03);
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }}

            .logo {{
                font-size: 22px;
                font-weight: bold;
            }}

            .container {{
                display: grid;
                grid-template-columns: 3fr 1fr;
                gap: 20px;
                padding: 30px;
            }}

            .card {{
                background: linear-gradient(145deg, #1e293b, #0f172a);
                padding: 20px;
                border-radius: 16px;
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.08);
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                transition: 0.2s;
            }}

            .card:hover {{
                transform: translateY(-4px);
                border-color: #38bdf8;
            }}

            .title {{
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 10px;
            }}

            .meta {{
                font-size: 12px;
                color: #94a3b8;
                margin-bottom: 10px;
            }}

            .btn {{
                padding: 6px 12px;
                background: #38bdf8;
                border-radius: 8px;
                color: black;
                text-decoration: none;
                font-size: 13px;
            }}

            .sidebar {{
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 12px;
            }}

            .price {{
                margin-bottom: 10px;
                padding: 10px;
                background: #020617;
                border-radius: 10px;
            }}

            h3 {{
                margin-top: 0;
            }}
        </style>

    </head>

    <body>

        <div class="header">
            <div class="logo">🚀 CryptoAlertAlpha</div>
            <div>Real-time Crypto Intelligence</div>
        </div>

        <div class="container">

            <div>
    """

    for i, n in enumerate(news):
        badge = "🚨 BREAKING" if i < 2 else "📰 NEWS"

        html += f"""
        <div class="card">
            <div class="meta">{badge}</div>
            <div class="title">{n[1]}</div>
            <div class="meta">Source: Crypto News</div>
            <a class="btn" href="{n[2]}" target="_blank">Read more</a>
        </div>
        """

    html += f"""
            </div>

            <div class="sidebar">
                <h3>📊 Market</h3>

                <div class="price">BTC: ${prices['BTC']}</div>
                <div class="price">ETH: ${prices['ETH']}</div>
                <div class="price">SOL: ${prices['SOL']}</div>

                <h3>🔥 Trending</h3>
                <p>#Bitcoin</p>
                <p>#Ethereum</p>
                <p>#ETF</p>
            </div>

        </div>

    </body>
    </html>
    """

    return html


@app.route("/health")
def health():
    return {"status": "ok"}
