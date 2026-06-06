import os
import secrets
import sqlite3
import time

from flask import Flask, flash, g, redirect, render_template, request, session, url_for


_FLAG_KEY = 0x2D
_FLAG_CIPHERTEXT = bytes.fromhex(
    "6c7e7f6e796b565e1e18181c1d43724e41191c4018725f194e1e7259451e72411e494a1e5f725f19591c1d431b5d58415e1e50"
)


def decrypt_flag():
    return "".join(chr(byte ^ _FLAG_KEY) for byte in _FLAG_CIPHERTEXT)


FLAG = decrypt_flag()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="coupon-clash-secret",
        DATABASE=os.path.join(app.root_path, "coupon_clash.db"),
        FLAG=FLAG,
        FLAG_COST=600,
        COUPON_VALUE=75,
        REDEEM_DELAY=0.20,
        CLAIM_WINDOW=3.0,
    )

    if test_config:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"], check_same_thread=False)
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = sqlite3.connect(app.config["DATABASE"], check_same_thread=False)
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code TEXT UNIQUE NOT NULL,
                value INTEGER NOT NULL,
                redeemed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        db.commit()
        db.close()

    def issue_coupon(db, user_id):
        code = "WELCOME-" + secrets.token_hex(4).upper()
        db.execute(
            "INSERT INTO coupons (user_id, code, value, redeemed) VALUES (?, ?, ?, 0)",
            (user_id, code, app.config["COUPON_VALUE"]),
        )
        return code

    def current_coupons():
        return get_db().execute(
            "SELECT code, value, redeemed FROM coupons WHERE user_id = ? ORDER BY id",
            (session["user_id"],),
        ).fetchall()

    def current_balance():
        row = get_db().execute(
            "SELECT balance FROM users WHERE id = ?",
            (session["user_id"],),
        ).fetchone()
        return row["balance"]

    app.teardown_appcontext(close_db)
    app.get_db = get_db
    app.init_db = init_db

    with app.app_context():
        init_db()

    @app.context_processor
    def inject_user():
        return {"current_username": session.get("username")}

    def pending_claim_view():
        claim = session.get("pending_claim")
        if not claim:
            return None

        seconds_left = max(0, int(claim.get("deadline", 0) - time.time()))
        if seconds_left <= 0:
            return None

        token = claim.get("token", "")
        return {
            "token": token,
            "short_token": token[:10],
            "seconds_left": seconds_left,
        }

    @app.after_request
    def add_canteen_headers(response):
        response.headers["X-Canteen-Receipt"] = "ASRCTF{legacy_redeem_batch_wins}"
        response.headers["X-Ration-Ledger"] = "redeem-lock-compatibility-mode"
        return response

    @app.route("/")
    def index():
        if "user_id" not in session:
            return render_template("landing.html", flag_cost=app.config["FLAG_COST"])
        return render_template(
            "dashboard.html",
            balance=current_balance(),
            coupons=current_coupons(),
            flag_cost=app.config["FLAG_COST"],
            pending_claim=pending_claim_view(),
        )

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
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password),
                )
                user_id = cursor.lastrowid
                issue_coupon(db, user_id)
                db.commit()
            except sqlite3.IntegrityError:
                flash("That username already exists.")
                return redirect(url_for("register"))

            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("index"))

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
            return redirect(url_for("index"))

        return render_template("auth.html", action="Login")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/redeem", methods=["POST"])
    def redeem():
        if "user_id" not in session:
            return redirect(url_for("login"))

        code = request.form.get("code", "").strip()
        if not code:
            flash("Legacy kiosk rejected an empty coupon scan.")
            return redirect(url_for("index"))

        flash("Legacy redeem kiosk is read-only. Reserve a settlement slip at the live desk.")
        return redirect(url_for("index"))

    @app.route("/reserve", methods=["POST"])
    def reserve():
        if "user_id" not in session:
            return redirect(url_for("login"))

        code = request.form.get("code", "").strip()
        db = get_db()
        coupon = db.execute(
            "SELECT id, value, redeemed FROM coupons WHERE user_id = ? AND code = ?",
            (session["user_id"], code),
        ).fetchone()
        if coupon is None:
            flash("Coupon not found.")
            return redirect(url_for("index"))
        if coupon["redeemed"]:
            flash("Coupon already redeemed.")
            return redirect(url_for("index"))

        token = secrets.token_urlsafe(16)
        session["pending_claim"] = {
            "code": code,
            "token": token,
            "deadline": time.time() + app.config["CLAIM_WINDOW"],
        }
        flash("Settlement slip issued. Settle it before the ledger window closes.")
        return redirect(url_for("index"))

    @app.route("/claim", methods=["POST"])
    def claim_without_token():
        if "user_id" not in session:
            return redirect(url_for("login"))

        flash("Settlement now requires a slip identifier.")
        return redirect(url_for("index"))

    @app.route("/claim/<claim_id>", methods=["POST"])
    def claim(claim_id):
        if "user_id" not in session:
            return redirect(url_for("login"))

        pending_claim = session.get("pending_claim") or {}
        code = pending_claim.get("code", "")
        if not code:
            flash("Reserve a coupon first.")
            return redirect(url_for("index"))
        if not secrets.compare_digest(claim_id, pending_claim.get("token", "")):
            flash("Settlement slip not recognized.")
            return redirect(url_for("index"))
        if time.time() > pending_claim.get("deadline", 0):
            session.pop("pending_claim", None)
            flash("Settlement window expired. Reserve the coupon again.")
            return redirect(url_for("index"))

        db = get_db()
        coupon = db.execute(
            "SELECT id, value, redeemed FROM coupons WHERE user_id = ? AND code = ?",
            (session["user_id"], code),
        ).fetchone()
        if coupon is None:
            flash("Coupon not found.")
            return redirect(url_for("index"))
        if coupon["redeemed"]:
            session.pop("pending_claim", None)
            flash("Coupon already redeemed.")
            return redirect(url_for("index"))

        time.sleep(app.config["REDEEM_DELAY"])
        db.execute(
            "UPDATE users SET balance = balance + ? WHERE id = ?",
            (coupon["value"], session["user_id"]),
        )
        db.commit()

        time.sleep(app.config["REDEEM_DELAY"])
        db.execute(
            "UPDATE coupons SET redeemed = 1 WHERE id = ?",
            (coupon["id"],),
        )
        db.commit()

        session.pop("pending_claim", None)
        flash("Coupon accepted for {0} credits.".format(coupon["value"]))
        return redirect(url_for("index"))

    @app.route("/store/buy/flag", methods=["POST"])
    def buy_flag():
        if "user_id" not in session:
            return redirect(url_for("login"))

        balance = current_balance()
        if balance < app.config["FLAG_COST"]:
            flash("Not enough credits yet.")
            return redirect(url_for("index"))

        db = get_db()
        db.execute(
            "UPDATE users SET balance = balance - ? WHERE id = ?",
            (app.config["FLAG_COST"], session["user_id"]),
        )
        db.commit()
        return render_template("purchased.html", flag=app.config["FLAG"])

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        threaded=True,
    )
