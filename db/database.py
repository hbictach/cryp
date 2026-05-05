import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# create table
cur.execute("""
CREATE TABLE IF NOT EXISTS news (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT
)
""")

def save_news(item):
    try:
        cur.execute(
            "INSERT INTO news (id, title, url) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (item["id"], item["title"], item["url"])
        )
    except Exception as e:
        print("DB save error:", e)

def get_news(limit=50):
    try:
        cur.execute(
            "SELECT id, title, url FROM news ORDER BY id DESC LIMIT %s",
            (limit,)
        )
        return cur.fetchall()
    except Exception as e:
        print("DB fetch error:", e)
        return []
