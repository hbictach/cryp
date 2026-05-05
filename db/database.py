import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS news (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT
)
""")

def save_news(item):
    try:
        conn.execute(
            "INSERT OR IGNORE INTO news VALUES (?,?,?)",
            (item["id"], item["title"], item["url"])
        )
        conn.commit()
    except:
        pass

def get_news(limit=50):
    cur = conn.execute(
        "SELECT * FROM news ORDER BY rowid DESC LIMIT ?", (limit,)
    )
    return cur.fetchall()
