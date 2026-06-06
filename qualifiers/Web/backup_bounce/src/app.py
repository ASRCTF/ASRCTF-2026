import base64
import io
import json
import os
import sqlite3

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)


_FLAG_KEY = 0x2D
_FLAG_CIPHERTEXT = bytes.fromhex(
    "6c7e7f6e796b564e1d405d1d431e435972591d461e431872195f1e724919591972591d1d724e5f5442185b1958415950"
)


def decrypt_flag():
    return "".join(chr(byte ^ _FLAG_KEY) for byte in _FLAG_CIPHERTEXT)


FLAG = decrypt_flag()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="backup-bounce-secret",
        DATABASE=os.path.join(app.root_path, "backup_bounce.db"),
        FLAG=FLAG,
        COMPONENT_PREVIEW_KEY="volunteer-preview",
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
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                display_name TEXT NOT NULL,
                favorite_quote TEXT NOT NULL,
                favorite_snack TEXT NOT NULL
            )
            """
        )
        db.commit()
        db.close()

    def current_profile():
        if "user_id" not in session:
            return None
        return get_db().execute(
            """
            SELECT id, username, display_name, favorite_quote, favorite_snack
            FROM users WHERE id = ?
            """,
            (session["user_id"],),
        ).fetchone()

    def encode_backup(payload):
        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return base64.urlsafe_b64encode(raw)

    def decode_backup(raw):
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            padded = raw + b"=" * (-len(raw) % 4)
            return json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))

    def render_component(component):
        name = component.get("name")
        props = component.get("props", {})
        field = props.get("field", "favorite_quote")
        if field not in ("display_name", "favorite_quote", "favorite_snack"):
            return {}

        if name == "profile.note":
            return {field: str(props.get("text", ""))}

        if name == "internal.flag-preview" and props.get("preview_key") == app.config["COMPONENT_PREVIEW_KEY"]:
            return {field: app.config["FLAG"]}

        return {}

    app.teardown_appcontext(close_db)
    app.get_db = get_db
    app.init_db = init_db
    app.current_profile = current_profile
    app.decode_backup = decode_backup
    app.render_component = render_component

    @app.after_request
    def add_backup_decoys(response):
        response.headers["X-Backup-Parser"] = "ASRCTF{yaml_anchor_airlock}"
        response.headers["X-Cryo-Manifest"] = "ASRCTF{pickle_imports_are_code_exec}"
        return response

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("profile"))
        return render_template("landing.html")

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
                    """
                    INSERT INTO users (
                        username, password, display_name, favorite_quote, favorite_snack
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        password,
                        username.title(),
                        "Imports should be harmless, right?",
                        "vacuum-packed kelp",
                    ),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That username already exists.")
                return redirect(url_for("register"))

            session["user_id"] = cursor.lastrowid
            session["username"] = username
            return redirect(url_for("profile"))

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
            return redirect(url_for("profile"))

        return render_template("auth.html", action="Login")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/profile")
    def profile():
        if "user_id" not in session:
            return redirect(url_for("login"))

        profile_row = current_profile()
        return render_template("profile.html", profile=profile_row)

    @app.route("/export")
    def export_profile():
        if "user_id" not in session:
            return redirect(url_for("login"))

        profile_row = current_profile()
        payload = {
            "format": "BBSC/1",
            "fields": {
                "display_name": profile_row["display_name"],
                "favorite_quote": profile_row["favorite_quote"],
                "favorite_snack": profile_row["favorite_snack"],
            },
            "components": [
                {
                    "name": "profile.note",
                    "props": {
                        "field": "favorite_quote",
                        "text": profile_row["favorite_quote"],
                    },
                }
            ],
        }
        return send_file(
            io.BytesIO(encode_backup(payload)),
            as_attachment=True,
            download_name="profile_backup.bbsc",
            mimetype="application/octet-stream",
        )

    @app.route("/import", methods=["POST"])
    def import_profile():
        if "user_id" not in session:
            return redirect(url_for("login"))

        uploaded = request.files.get("backup")
        if uploaded is None or uploaded.filename == "":
            flash("Choose a backup file first.")
            return redirect(url_for("profile"))

        try:
            restored = decode_backup(uploaded.read())
        except Exception as exc:
            flash("Import failed: {0}".format(exc))
            return redirect(url_for("profile"))

        if not isinstance(restored, dict):
            flash("Backup format not recognized.")
            return redirect(url_for("profile"))

        profile_row = current_profile()
        merged = {
            "display_name": profile_row["display_name"],
            "favorite_quote": profile_row["favorite_quote"],
            "favorite_snack": profile_row["favorite_snack"],
        }
        fields = restored.get("fields", {})
        if isinstance(fields, dict):
            for key in ("display_name", "favorite_quote", "favorite_snack"):
                if key in fields:
                    merged[key] = str(fields[key])

        components = restored.get("components", [])
        if isinstance(components, list):
            for component in components:
                if isinstance(component, dict):
                    merged.update(render_component(component))

        db = get_db()
        db.execute(
            """
            UPDATE users
            SET display_name = ?, favorite_quote = ?, favorite_snack = ?
            WHERE id = ?
            """,
            (
                merged["display_name"],
                merged["favorite_quote"],
                merged["favorite_snack"],
                session["user_id"],
            ),
        )
        db.commit()
        flash("Profile restored from backup.")
        return redirect(url_for("profile"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
