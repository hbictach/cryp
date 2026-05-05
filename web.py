from flask import Flask
from db.database import get_news

app = Flask(__name__)

@app.route("/")
def home():
    news = get_news()

    html = """
    <html>
    <head>
        <title>CryptoAlertAlpha</title>
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI';
                background: linear-gradient(135deg, #0f172a, #020617);
                color: white;
            }

            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 40px;
                background: rgba(255,255,255,0.03);
                backdrop-filter: blur(10px);
            }

            .logo {
                font-size: 22px;
                font-weight: bold;
            }

            .container {
                display: grid;
                grid-template-columns: 3fr 1fr;
                gap: 20px;
                padding: 30px;
            }

            .main {
            }

            .sidebar {
                background: rgba(255,255,255,0.05);
                padding: 15px;
                border-radius: 12px;
            }

            .card {
                background: rgba(255,255,255,0.04);
                padding: 18px;
                border-radius: 14px;
                margin-bottom: 15px;
                transition: 0.2s;
                border: 1px solid rgba(255,255,255,0.05);
            }

            .card:hover {
                transform: translateY(-3px);
                border-color: #38bdf8;
            }

            .title {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 10px;
            }

            .btn {
                display: inline-block;
                padding: 6px 12px;
                background: #38bdf8;
                border-radius: 8px;
                color: black;
                text-decoration: none;
                font-size: 13px;
            }

            .badge {
                background: #ef4444;
                padding: 4px 8px;
                font-size: 11px;
                border-radius: 6px;
                margin-right: 6px;
            }

            .price {
                margin-bottom: 10px;
                padding: 10px;
                background: #020617;
                border-radius: 10px;
            }
        </style>
    </head>

    <body>

        <div class="header">
            <div class="logo">🚀 CryptoAlertAlpha</div>
            <div>Real-time Crypto Intelligence</div>
        </div>

        <div class="container">

            <div class="main">
    """

    for i, n in enumerate(news):
        badge = "🚨" if i < 2 else ""

        html += f"""
        <div class="card">
            <div class="title">{badge} {n[1]}</div>
            <a class="btn" href="{n[2]}" target="_blank">Read more</a>
        </div>
        """

    html += """
            </div>

            <div class="sidebar">
                <h3>📊 Market</h3>

                <div class="price">BTC: $68,200</div>
                <div class="price">ETH: $3,450</div>
                <div class="price">SOL: $155</div>

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
