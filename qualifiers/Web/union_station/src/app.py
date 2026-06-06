import os
import sqlite3
import json

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for

FLAG = "ASRCTF{53c0nd_0rd3r_j50n_3x7r4c710n_1nj3c710n_v2}"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="union-station-secret",
        DATABASE=os.path.join(app.root_path, "union_station.db"),
        FLAG=FLAG,
    )

    if test_config:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                profile_json TEXT DEFAULT '{"connector": "OR"}'
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                value TEXT NOT NULL
            )
            """
        )

        note_count = db.execute("SELECT COUNT(*) AS count FROM notes").fetchone()["count"]
        if note_count == 0:
            db.executemany(
                "INSERT INTO notes (title, body) VALUES (?, ?)",
                [
                    ("Relay Schedule", "Archive reindex runs every Tuesday during low orbit."),
                    ("Operator Checklist", "Remember to proofread dispatches before broadcast."),
                    ("Maintenance Draft", "Draft answers for the robotics bay captain."),
                ],
            )

        secret_count = db.execute("SELECT COUNT(*) AS count FROM secrets").fetchone()["count"]
        if secret_count == 0:
            db.execute(
                "INSERT INTO secrets (label, value) VALUES (?, ?)",
                ("production_flag", app.config["FLAG"]),
            )

        db.commit()
        db.close()

    app.teardown_appcontext(close_db)
    app.get_db = get_db
    app.init_db = init_db

    with app.app_context():
        init_db()

    @app.context_processor
    def inject_user():
        return {"current_username": session.get("username")}

    @app.after_request
    def add_signal_decoys(response):
        response.headers["X-Dead-Air-Flag"] = "ASRCTF{union_select_off_the_tracks}"
        response.headers["X-Archive-Beacon"] = "ASRCTF{dispatch_filter_quote_break}"
        return response

    @app.route("/")
    def index():
        if "user_id" not in session:
            return render_template("landing.html")
        return redirect(url_for("search"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            if not username or not password:
                flash("Username and password are required.")
                return redirect(url_for("register"))

            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO users (username, password, profile_json) VALUES (?, ?, ?)",
                    (username, password, '{"connector": "OR"}'),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That username already exists.")
                return redirect(url_for("register"))

            session["user_id"] = cursor.lastrowid
            session["username"] = username
            return redirect(url_for("search"))

        return render_template("auth.html", action="Register")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            user = get_db().execute(
                "SELECT id, username FROM users WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()
            if user is None:
                flash("Invalid credentials.")
                return redirect(url_for("login"))

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("search"))

        return render_template("auth.html", action="Login")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/search")
    def search():
        if "user_id" not in session:
            return redirect(url_for("login"))

        query = request.args.get("q", "")
        rows = []
        error = None
        raw_sql = None

        db = get_db()
        user = db.execute("SELECT profile_json FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        profile_json = user["profile_json"] if user else '{"connector": "OR"}'

        if query:
            raw_sql = "SELECT id, title, body FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id LIMIT 10"
            like_query = "%{0}%".format(query)
            try:
                rows = db.execute(raw_sql, (like_query, like_query)).fetchall()
            except sqlite3.Error as exc:
                error = str(exc)

        return render_template(
            "search.html",
            query=query,
            rows=rows,
            error=error,
            raw_sql=raw_sql,
            profile_json=profile_json,
        )

    @app.route("/update_profile", methods=["POST"])
    def update_profile():
        if "user_id" not in session:
            return redirect(url_for("login"))

        profile_json = request.form.get("profile_json", "").strip()
        try:
            json.loads(profile_json)
            db = get_db()
            db.execute(
                "UPDATE users SET profile_json = ? WHERE id = ?",
                (profile_json, session["user_id"]),
            )
            db.commit()
            flash("Search preferences updated!")
        except Exception as exc:
            flash(f"Invalid JSON: {str(exc)}")

        return redirect(url_for("search"))

    @app.route("/api/search", methods=["POST"])
    def api_search():
        if "user_id" not in session:
            return jsonify({"error": "login required"}), 401

        payload = request.get_json(silent=True) or {}
        term = str(payload.get("term", ""))
        
        db = get_db()
        user = db.execute("SELECT profile_json FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        profile_json = user["profile_json"] if user else '{"connector": "OR"}'
        
        try:
            row = db.execute(
                "SELECT json_extract(?, '$.connector') AS connector",
                (profile_json,)
            ).fetchone()
            connector = row["connector"] if row["connector"] else "OR"
        except Exception as exc:
            return jsonify({"error": f"JSON extract error: {str(exc)}"}), 400

        # Second-order injection vulnerability!
        raw_sql = (
            "SELECT id, title, body FROM notes "
            "WHERE title LIKE :term {0} body LIKE :term "
            "ORDER BY id LIMIT 10"
        ).format(connector)

        try:
            rows = db.execute(raw_sql, {"term": "%{0}%".format(term)}).fetchall()
            return jsonify(
                {
                    "query": raw_sql,
                    "rows": [
                        {"id": row["id"], "title": row["title"], "body": row["body"]}
                        for row in rows
                    ],
                }
            )
        except sqlite3.Error as exc:
            return jsonify({"query": raw_sql, "error": str(exc)}), 400

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
