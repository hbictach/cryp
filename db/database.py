import os

import psycopg2
from psycopg2 import OperationalError

_conn = None
_cur = None


NEWS_COLUMNS = "id, title, url, source, sentiment, impact, category, created_at"


def _database_url():
    return os.getenv("DATABASE_URL")


def is_database_configured():
    return bool(_database_url())


def _get_cursor():
    """Return a live database cursor, or None when the DB is not configured."""
    global _conn, _cur

    database_url = _database_url()
    if not database_url:
        print("DATABASE_URL is not configured")
        return None

    try:
        if _conn is None or _conn.closed:
            _conn = psycopg2.connect(database_url)
            _cur = _conn.cursor()
        return _cur
    except OperationalError as e:
        print("DB CONNECTION ERROR:", e)
        _conn = None
        _cur = None
        return None


def _rollback():
    if _conn is not None and not _conn.closed:
        _conn.rollback()


# ✅ إنشاء / تحديث table
def init_db():
    cur = _get_cursor()
    if cur is None:
        return False

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT,
            sentiment TEXT,
            impact TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _conn.commit()

        # 🔥 إصلاح column إذا ما كانش
        cur.execute("""
        ALTER TABLE news
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """)
        _conn.commit()
        return True

    except Exception as e:
        print("INIT DB ERROR:", e)
        _rollback()
        return False


# ✅ حفظ الأخبار
def save_news(item):
    cur = _get_cursor()
    if cur is None:
        return False

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
            item.get("category"),
        ))
        _conn.commit()
        return True

    except Exception as e:
        print("SAVE NEWS ERROR:", e)
        _rollback()
        return False


# ✅ جلب الأخبار (بدون crash)
def get_news(tab=None, search=None, page=1):
    cur = _get_cursor()
    if cur is None:
        return []

    try:
        _rollback()  # 🔥 مهم بزاف

        limit = 10
        page = max(int(page or 1), 1)
        offset = (page - 1) * limit

        query = f"SELECT {NEWS_COLUMNS} FROM news WHERE 1=1"
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
        _rollback()
        return []


def get_recent_news(limit=100):
    cur = _get_cursor()
    if cur is None:
        return []

    try:
        _rollback()
        limit = max(min(int(limit or 100), 500), 1)
        cur.execute(f"SELECT {NEWS_COLUMNS} FROM news ORDER BY created_at DESC LIMIT %s", (limit,))
        return cur.fetchall()

    except Exception as e:
        print("GET RECENT NEWS ERROR:", e)
        _rollback()
        return []
