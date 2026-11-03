import sqlite3
from flask import Flask, request, abort, g

app = Flask(__name__)


def db():
    return sqlite3.connect("notes.db")


@app.get("/notes/<int:note_id>")
def get_note(note_id: int):
    conn = db()
    row = conn.execute(
        "SELECT id, owner_id, title FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    if row is None:
        abort(404)
    if row[1] != g.user_id:
        abort(403)
    return {"id": row[0], "title": row[2]}
