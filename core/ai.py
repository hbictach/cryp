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
                font-family: Arial;
                background: #0f172a;
                color: white;
            }

            .header {
                padding: 20px;
                background: #020617;
                font-size: 24px;
                font-weight: bold;
                border-bottom: 1px solid #1e293b;
            }

            .container {
                padding: 20px;
            }

            .prices {
                display: flex;
                gap: 15px;
                margin-bottom: 25px;
            }

            .price-card {
                background: #1e293b;
                padding: 15px;
                border-radius: 10px;
                flex: 1;
            }

            .news-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
            }

            .card {
                background: #1e293b;
                padding: 15px;
                border-radius: 10px;
                transition: 0.2s;
            }

            .card:hover {
                transform: scale(1.02);
            }

            a {
                color: #38bdf8;
                text-decoration: none;
            }

            .category {
                font-size: 12px;
                color: #94a3b8;
                margin-bottom: 5px;
            }
        </style>
    </head>

    <body>

        <div class="header">
            🚀 CryptoAlertAlpha
        </div>

        <div class="container">

            <!-- 💰 Prices (mock) -->
            <div class="prices">
                <div class="price-card">BTC: $68,200</div>
                <div class="price-card">ETH: $3,450</div>
                <div class="price-card">SOL: $155</div>
            </div>

            <!-- 📰 News -->
            <div class="news-grid">
    """

    for n in news:
        html += f"""
        <div class="card">
            <div class="category">Crypto News</div>
            <b>{n[1]}</b><br><br>
            <a href="{n[2]}" target="_blank">Read more →</a>
        </div>
        """

    html += """
            </div>

        </div>
    </body>
    </html>
    """

    return html


@app.route("/health")
def health():
    return {"status": "ok"}
