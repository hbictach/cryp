from flask import Flask, render_template, request
from db.database import get_news

app = Flask(__name__)

@app.route("/")
def home():
    tab = request.args.get("tab", "all")
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))

    raw = get_news(tab, search, page)

    news = []
    for n in raw:
        news.append({
            "id": n[0],
            "title": n[1],
            "url": n[2],
            "source": n[3],
            "sentiment": n[4],
            "impact": n[5],
            "category": n[6],
            "time": str(n[7])[:16]
        })

    return render_template(
        "index.html",
        news=news,
        tab=tab,
        search=search,
        page=page
    )
