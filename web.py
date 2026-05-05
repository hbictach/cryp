from flask import Flask
from db.database import get_news

app = Flask(__name__)

@app.route("/")
def home():
    try:
        news = get_news()

        html = "<h1>🚀 Crypto Alerts</h1>"

        for n in news:
            html += f"""
            <div style="margin-bottom:20px;">
                <b>{n[1]}</b><br>
                <a href="{n[2]}" target="_blank">Read</a>
            </div>
            """

        return html

    except Exception as e:
        return f"Error loading page: {e}"


@app.route("/health")
def health():
    return {"status": "ok"}
