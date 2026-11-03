import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


def db():
    return sqlite3.connect("library.db")


@app.get("/books")
def search_books():
    title = request.args.get("title", "")
    order = request.args.get("sort", "title")
    conn = db()
    rows = conn.execute(
        "SELECT id, title, author FROM books WHERE title LIKE '%" + title + "%' ORDER BY " + order
    ).fetchall()
    return jsonify(rows)
