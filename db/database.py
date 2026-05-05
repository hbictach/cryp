import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("DB connection error:", e)
        return None

def init_db():
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id TEXT PRIMARY KEY,
        title TEXT,
        url TEXT
    )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_news(item):
    conn = get_conn()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO news (id, title, url) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            (item["id"], item["title"], item["url"])
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB save error:", e)

def get_news(limit=50):
    conn = get_conn()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, url FROM news ORDER BY id DESC LIMIT %s",
            (limit,)
        )
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print("DB fetch error:", e)
        return []
