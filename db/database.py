import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id TEXT PRIMARY KEY,
        title TEXT,
        url TEXT,
        source TEXT,
        sentiment TEXT,
        impact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def save_news(item):
    try:
        cur.execute("""
        INSERT INTO news (id, title, url, source, sentiment, impact)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """, (
            item["id"],
            item["title"],
            item["url"],
            item.get("source"),
            item.get("sentiment"),
            item.get("impact")
        ))
        conn.commit()
    except Exception as e:
        print("DB ERROR:", e)

def get_news():
    cur.execute("""
    SELECT id, title, url, source, sentiment, impact, created_at
    FROM news
    ORDER BY created_at DESC
    LIMIT 50
    """)
    return cur.fetchall()
