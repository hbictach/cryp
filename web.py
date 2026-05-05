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
                background: #0f172a;
                color: white;
                font-family: Arial;
                padding: 20px;
            }
            .card {
                background: #1e293b;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 10px;
            }
            a {
                color: #38bdf8;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Crypto Alerts</h1>
    """

    for n in news:
        html += f"""
        <div class="card">
            <b>{n[1]}</b><br>
            <a href="{n[2]}" target="_blank">Read more</a>
        </div>
        """

    html += "</body></html>"

    return html


@app.route("/health")
def health():
    return {"status": "ok"}
