from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>CryptoAlertAlpha</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                background: #0f172a;
                color: white;
                padding: 50px;
            }
            h1 {
                font-size: 48px;
            }
            p {
                font-size: 20px;
                color: #94a3b8;
            }
            .btn {
                display: inline-block;
                margin-top: 20px;
                padding: 15px 25px;
                font-size: 18px;
                background: #22c55e;
                color: black;
                text-decoration: none;
                border-radius: 10px;
            }
            .box {
                margin-top: 40px;
            }
        </style>
    </head>

    <body>

        <h1>🚀 CryptoAlertAlpha</h1>
        <p>Real-time Crypto Alerts & AI Signals</p>

        <a class="btn" href="https://t.me/CryptoAlertAlpha">
            🔥 Join Telegram Now
        </a>

        <div class="box">
            <h2>⚡ What you get:</h2>
            <p>🚨 Breaking Alerts</p>
            <p>🧠 AI Insights</p>
            <p>📈 Market Impact</p>
        </div>

    </body>
    </html>
    """

@app.route("/health")
def health():
    return {"status": "ok"}
