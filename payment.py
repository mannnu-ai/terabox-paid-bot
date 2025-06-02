import sqlite3

def is_premium_user(user_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT premium FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1
