import sqlite3

DB_FILE = "seen_posts.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS posts (id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

def is_seen(post_id: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM posts WHERE id = ?", (post_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def mark_seen(post_id: str):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT OR REPLACE INTO posts (id) VALUES (?)", (post_id,))
    conn.commit()
    conn.close()