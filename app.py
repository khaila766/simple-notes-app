import os
import time
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppass"),
    "database": os.getenv("DB_NAME", "notesdb"),
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_conn(retries=10, delay=3):
    last_err = None
    for _ in range(retries):
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.MySQLError as err:
            last_err = err
            time.sleep(delay)
    raise last_err


def init_db():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS notes (
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   content VARCHAR(255) NOT NULL,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )"""
        )
    conn.close()


@app.route("/")
def hello():
    return "Halo dari Flask + MySQL + Docker + Jenkins!"


@app.route("/health")
def health():
    try:
        conn = get_conn(retries=1)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            cur.fetchone()
        conn.close()
        return jsonify(status="ok", database="connected")
    except Exception as err:
        return jsonify(status="error", detail=str(err)), 500


@app.route("/notes", methods=["GET"])
def list_notes():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        rows = cur.fetchall()
    conn.close()
    for r in rows:
        r["created_at"] = str(r["created_at"])
    return jsonify(rows)


@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify(error="field 'content' wajib diisi"), 400
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
        new_id = cur.lastrowid
    conn.close()
    return jsonify(id=new_id, content=content), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
