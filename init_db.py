import sqlite3

# --- データベース接続 ---
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# --- テーブル作成 ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS Book (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE,
    status TEXT DEFAULT 'available'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    registered_at TEXT DEFAULT (datetime('now'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Loan (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    loan_date TEXT DEFAULT (date('now')),
    return_date TEXT,
    FOREIGN KEY (book_id) REFERENCES Book(book_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
)
""")

conn.commit()
conn.close()

print("📚 データベースを初期化しました。")
