import psycopg2
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS news (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT
)
""")
conn.commit()

def save_news(item):
    try:
        cur.execute(
            "INSERT INTO news (id,title,url) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            (item["id"], item["title"], item["url"])
        )
        conn.commit()
    except:
        pass

def get_news(limit=50):
    cur.execute("SELECT * FROM news ORDER BY id DESC LIMIT %s", (limit,))
    return cur.fetchall()
