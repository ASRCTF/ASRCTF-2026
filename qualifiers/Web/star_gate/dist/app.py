from flask import *
import sqlite3
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(64)

def init_db():
    conn = sqlite3.connect("stargate.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS commanders (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            sector TEXT NOT NULL,
            status TEXT NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)

    users = [
        {"id": 1, "username": "voss7", "role": "Commander", "sector": "S7", "status": "Active"},
        {"id": 2, "username": "lyra", "role": "Navigator", "sector": "S3", "status": "Standby"},
        {"id": 3, "username": "kael", "role": "Engineer", "sector": "S9", "status": "Inactive"},
        {"id": 4, "username": "orin", "role": "Security", "sector": "S7", "status": "Locked"},
    ]

    for user in users:
        random_password = os.urandom(4).hex()
        password_hash = hashlib.sha256(random_password.encode()).hexdigest()

        cur.execute("""
            INSERT OR REPLACE INTO commanders
            (id, username, role, sector, status, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user["id"],
            user["username"],
            user["role"],
            user["sector"],
            user["status"],
            password_hash
        ))

        print(f'username: {user["username"]:<10} password: {random_password}')

    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        flash('Please login')
        return redirect(url_for('login'))
    return wrap

@app.route("/crew/", defaults={"sort_by": "id"})
@app.route("/crew/<sort_by>")
def crew(sort_by):
    conn = sqlite3.connect("stargate.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(f"""
        SELECT id, username, role, sector, status
        FROM commanders
        ORDER BY {sort_by}
    """)

    rows = cur.fetchall()
    conn.close()

    users = [dict(row) for row in rows]

    return render_template("client_dashboard.html", users=users)


def authenticate(username: str, password: str):
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("stargate.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT username, role, password_hash FROM commanders
        WHERE username = ?
        AND password_hash = ?
    """, (username, password_hash))

    row = cur.fetchone()
    conn.close()

    if row:
        if row[1] == 'Commander':
            session['logged_in'] = True
            return jsonify({"success": True}), 200
        return jsonify({"success": False, "message": "Access denied."}), 401 
    return jsonify({"success": False, "message": "Access denied."}), 401

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.get_json()
        if data:
            username = data.get("username", "")
            password = data.get("password", "")
            return authenticate(username, password)
        else:
            return jsonify({"message": "No credentials provided!"}), 400
    else:
        return render_template("login.html")

if __name__ == "__main__":
    init_db()
    app.run('0.0.0.0', 3000)