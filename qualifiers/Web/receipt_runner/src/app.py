import os
import sqlite3
import base64
import requests
import jwt

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate a transient RSA key pair for JWT signing/verification
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_KEY = PRIVATE_KEY.public_key()
PUBLIC_PEM = PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

FLAG = "ASRCTF{Jwk5_s5Rf_T0k3n_F0rG3ry_v4uLt_g4T3_v2}"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="receipt-runner-secret",
        DATABASE=os.path.join(app.root_path, "receipt_runner.db"),
        FLAG=FLAG,
        AUDIT_RECEIPT_ID=8421,
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
                password TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount TEXT NOT NULL,
                internal_note TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
            """
        )

        admin = db.execute(
            "SELECT id FROM users WHERE username = ?",
            ("ops-admin",),
        ).fetchone()
        if admin is None:
            cursor = db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("ops-admin", "ledger-only"),
            )
            admin_id = cursor.lastrowid
        else:
            admin_id = admin["id"]

        seeded = db.execute(
            "SELECT id FROM receipts WHERE id = ?",
            (app.config["AUDIT_RECEIPT_ID"],),
        ).fetchone()
        if seeded is None:
            db.execute(
                """
                INSERT INTO receipts (id, owner_id, title, amount, internal_note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    app.config["AUDIT_RECEIPT_ID"],
                    admin_id,
                    "Command Manifest Reimbursement",
                    "$1,337.00",
                    "Flag stored for audit sync: {0}".format(app.config["FLAG"]),
                ),
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
    def add_orbital_decoys(response):
        response.headers["X-Orrery-Audit-Trail"] = "ASRCTF{cargo_chit_zero_g}"
        response.headers["X-Relay-Checksum"] = "ASRCTF{manifest_cache_8421}"
        return response

    @app.before_request
    def organizer_middleware_gate():
        if not request.path.startswith("/organizer/"):
            return None

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return "Missing or invalid Authorization header. Must be a Bearer JWT.", 401
        
        token = auth_header.split(" ")[1]
        try:
            # Decode JWT header without verifying to inspect alg, jku, kid
            unverified_header = jwt.get_unverified_header(token)
            alg = unverified_header.get("alg")
            jku = unverified_header.get("jku")
            kid = unverified_header.get("kid")
            
            # 1. JWKS Injection check
            if jku:
                # SSRF! Fetch the JWKS from the user-controlled URL
                try:
                    response = requests.get(jku, timeout=3)
                    jwks = response.json()
                    # Find matching key
                    key_data = None
                    for key in jwks.get("keys", []):
                        if not kid or key.get("kid") == kid:
                            key_data = key
                            break
                    if key_data:
                        # Extract the key to verify (could be RSA or HMAC based on their JWK)
                        if key_data.get("kty") == "RSA":
                            # Decode RSA JWK
                            from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
                            def int_from_base64(s):
                                s += '=' * (4 - len(s) % 4)
                                return int.from_bytes(base64.urlsafe_b64decode(s), 'big')
                            n = int_from_base64(key_data["n"])
                            e = int_from_base64(key_data["e"])
                            pub_key = RSAPublicNumbers(e, n).public_key()
                            decoded = jwt.decode(token, pub_key, algorithms=["RS256"])
                        else:
                            # Fallback HMAC or raw key verification
                            k = key_data.get("k")
                            decoded = jwt.decode(token, k, algorithms=[alg])
                    else:
                        return "Key ID not found in JWKS.", 401
                except Exception as exc:
                    return f"JWKS Injection verification failed: {str(exc)}", 401
            
            # 2. Key Confusion (HS256 vs RS256) check
            elif alg == "HS256":
                # VULNERABILITY: Verify HS256 signature using the RS256 PUBLIC_PEM as the secret key!
                # To bypass PyJWT's safety check against asymmetric keys as HMAC secrets, we strip the PEM headers.
                key_secret = PUBLIC_PEM.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").strip()
                decoded = jwt.decode(token, key_secret, algorithms=["HS256"])
            
            # 3. Standard RS256 validation
            else:
                decoded = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            
            # Verify user role is administrator/ops-admin
            if decoded.get("role") == "admin" or decoded.get("user") == "ops-admin":
                return None
            
            return "Unauthorized role.", 403
            
        except jwt.ExpiredSignatureError:
            return "Token expired.", 401
        except jwt.InvalidTokenError as exc:
            return f"Invalid Token: {str(exc)}", 401

    @app.route("/")
    def index():
        if "user_id" not in session:
            return render_template("landing.html")

        receipts = get_db().execute(
            "SELECT id, title, amount FROM receipts WHERE owner_id = ? ORDER BY id",
            (session["user_id"],),
        ).fetchall()
        return render_template(
            "dashboard.html",
            receipts=receipts,
            audit_receipt_id=app.config["AUDIT_RECEIPT_ID"],
        )

    @app.route("/public_key")
    def get_public_key():
        return PUBLIC_PEM, 200, {"Content-Type": "text/plain"}

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
                db.execute(
                    """
                    INSERT INTO receipts (owner_id, title, amount, internal_note)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        "Docking Welcome Pack",
                        "$12.50",
                        "Starter receipt for {0}".format(username),
                    ),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That username is already taken.")
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

    @app.route("/receipts/<int:receipt_id>")
    def receipt_detail(receipt_id):
        if "user_id" not in session:
            return redirect(url_for("login"))

        receipt = get_db().execute(
            """
            SELECT receipts.id, receipts.title, receipts.amount, receipts.internal_note,
                   users.username AS owner_name
            FROM receipts
            JOIN users ON users.id = receipts.owner_id
            WHERE receipts.id = ? AND receipts.owner_id = ?
            """,
            (receipt_id, session["user_id"]),
        ).fetchone()

        if receipt is None:
            return "Receipt not found.", 404

        return render_template("receipt.html", receipt=receipt)

    @app.route("/organizer/receipts/<int:receipt_id>")
    def organizer_receipt(receipt_id):
        receipt = get_db().execute(
            """
            SELECT receipts.id, receipts.title, receipts.amount, receipts.internal_note,
                   users.username AS owner_name
            FROM receipts
            JOIN users ON users.id = receipts.owner_id
            WHERE receipts.id = ?
            """,
            (receipt_id,),
        ).fetchone()

        if receipt is None:
            return "Receipt not found.", 404

        return render_template("receipt.html", receipt=receipt)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
