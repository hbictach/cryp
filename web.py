from flask import Flask, render_template
from db.database import get_news
import requests

app = Flask(__name__)

# 💰 جلب الأسعار الحقيقية
def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,ripple&vs_currencies=usd"
        data = requests.get(url).json()

        return {
            "BTC": data["bitcoin"]["usd"],
            "ETH": data["ethereum"]["usd"],
            "SOL": data["solana"]["usd"],
            "BNB": data["binancecoin"]["usd"],
            "XRP": data["ripple"]["usd"]
        }
    except:
        return {}

@app.route("/")
def home():
    raw_news = get_news()
    prices = get_prices()

    # 🧠 تحويل البيانات للـ template
    news = []
    for n in raw_news:
        news.append({
            "id": n[0],
            "title": n[1],
            "url": n[2],
            "source": "Crypto News",
            "impact": "MEDIUM",
            "sentiment": "neutral",
            "posted_at": "now"
        })

    return render_template("index.html", news=news, prices=prices)

@app.route("/health")
def health():
    return {"status": "ok"}
