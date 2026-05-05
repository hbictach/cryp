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
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # 🔥 هذا هو الحل
    try:
        cur.execute("ALTER TABLE news ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        conn.commit()
    except:
        pass

def save_news(item):
    try:
        cur.execute("""
        INSERT INTO news (id, title, url, source, sentiment, impact, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """, (
            item["id"],
            item["title"],
            item["url"],
            item.get("source"),
            item.get("sentiment"),
            item.get("impact"),
            item.get("category")
        ))
        conn.commit()
    except Exception as e:
        print("DB ERROR:", e)

def get_news(tab=None, search=None, page=1):
    limit = 10
    offset = (page - 1) * limit

    query = "SELECT * FROM news ORDER BY created_at DESC LIMIT %s OFFSET %s"
    cur.execute(query, (limit, offset))
    return cur.fetchall()
