from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)
DB_NAME = "library.db"

# -------------------------------
# ホームページ
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------
# 図書一覧ページ
# -------------------------------
@app.route("/books")
def books():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Book テーブルと Loan テーブルを結合して、貸出中の場合は貸しているユーザーIDを取得
    cur.execute("""
        SELECT 
            b.book_id, b.title, b.author, b.isbn, b.status,
            l.user_id
        FROM Book b
        LEFT JOIN Loan l
            ON b.book_id = l.book_id AND l.return_date IS NULL
    """)
    books = cur.fetchall()
    conn.close()
    return render_template("books.html", books=books)

# -------------------------------
# 図書登録ページ（フォーム表示）
# -------------------------------
@app.route("/add_book")
def add_book_form():
    return render_template("add_book.html")

# -------------------------------
# 新しい図書を登録する（POST処理）
# -------------------------------
@app.route("/books/add", methods=["POST"])
def add_book():
    title = request.form["title"]
    author = request.form["author"]
    isbn = request.form["isbn"]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Book (title, author, isbn) VALUES (?, ?, ?)",
        (title, author, isbn)
    )
    conn.commit()
    conn.close()

    return redirect("/books")

# -------------------------------
# 利用者一覧ページ
# -------------------------------
@app.route("/users")
def users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, email FROM User")
    users = cur.fetchall()
    conn.close()
    return render_template("users.html", users=users)

# -------------------------------
# 利用者登録ページ（フォーム表示）
# -------------------------------
@app.route("/add_user")
def add_user_form():
    return render_template("add_user.html")

# -------------------------------
# 新しい利用者を登録する（POST処理）
# -------------------------------
@app.route("/users/add", methods=["POST"])
def add_user():
    name = request.form["name"]
    email = request.form["email"]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO User (name, email) VALUES (?, ?)",
        (name, email)
    )
    conn.commit()
    conn.close()

    return redirect("/users")

# -------------------------------
# 貸出フォームページ
# -------------------------------
@app.route("/loan_book")
def loan_book_form():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT book_id, title FROM Book WHERE status = 'available'")
    books = cur.fetchall()
    cur.execute("SELECT user_id, name FROM User")
    users = cur.fetchall()
    conn.close()
    return render_template("loan_book.html", books=books, users=users)

# -------------------------------
# 貸出処理
# -------------------------------
@app.route("/loan", methods=["POST"])
def loan_book():
    user_id = request.form["user_id"]
    book_id = request.form["book_id"]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # 本の状態を確認
    cur.execute("SELECT status FROM Book WHERE book_id = ?", (book_id,))
    book = cur.fetchone()

    if book and book[0] == "available":
        # 貸出記録を追加
        cur.execute("""
            INSERT INTO Loan (book_id, user_id, loan_date)
            VALUES (?, ?, ?)
        """, (book_id, user_id, date.today().isoformat()))

        # 図書を「貸出中」に更新
        cur.execute("UPDATE Book SET status = 'loaned' WHERE book_id = ?", (book_id,))
        conn.commit()

    conn.close()
    return redirect("/books")

# -------------------------------
# 返却処理
# -------------------------------
@app.route("/return/<int:book_id>")
def return_book(book_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # 貸出記録の返却日を更新
    cur.execute("""
        UPDATE Loan SET return_date = ?
        WHERE book_id = ? AND return_date IS NULL
    """, (date.today().isoformat(), book_id))

    # 図書の状態を「利用可能」に戻す
    cur.execute("UPDATE Book SET status = 'available' WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()

    return redirect("/books")

# -------------------------------
# アプリ起動
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
