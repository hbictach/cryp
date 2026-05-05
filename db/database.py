import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


# ✅ إنشاء / تحديث table
def init_db():
    try:
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

        # 🔥 إصلاح column إذا ما كانش
        try:
            cur.execute("ALTER TABLE news ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            conn.commit()
        except:
            conn.rollback()

    except Exception as e:
        print("INIT DB ERROR:", e)
        conn.rollback()


# ✅ حفظ الأخبار
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
        print("SAVE NEWS ERROR:", e)
        conn.rollback()


# ✅ جلب الأخبار (بدون crash)
def get_news(tab=None, search=None, page=1):
    try:
        conn.rollback()  # 🔥 مهم بزاف

        limit = 10
        offset = (page - 1) * limit

        query = "SELECT * FROM news WHERE 1=1"
        params = []

        if tab and tab != "all":
            query += " AND category = %s"
            params.append(tab)

        if search:
            query += " AND LOWER(title) LIKE %s"
            params.append(f"%{search.lower()}%")

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, params)
        return cur.fetchall()

    except Exception as e:
        print("GET NEWS ERROR:", e)
        conn.rollback()
        return []
