import sqlite3

DB_NAME = "points.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS points (
            user_id TEXT PRIMARY KEY,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_points(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT score FROM points WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    conn.close()
    return result[0] if result else 0

def update_points(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    current = get_points(user_id)
    new_score = current + amount

    c.execute("""
        INSERT INTO points (user_id, score)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET score = ?
    """, (user_id, new_score, new_score))

    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT user_id, score
        FROM points
        ORDER BY score DESC
        LIMIT ?
    """, (limit,))

    results = c.fetchall()
    conn.close()
    return results
