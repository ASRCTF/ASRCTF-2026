
import os
import json
import hmac
import hashlib
import base64

from flask import Flask, request, jsonify, send_from_directory, abort

ROOT_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "keys.json")

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Keys file not found: {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    KEYS = json.load(f)

print(f"[+] Keys loaded from {CONFIG_PATH}")

app = Flask(__name__, static_folder=ROOT_DIR)



def _b64url_enc(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_dec(s):
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def _jwt_signature(header_b64, payload_b64, secret):
    """Compute HMAC-SHA256 signature for a JWT header.payload string."""
    message = f"{header_b64}.{payload_b64}".encode()
    sig = hmac.new(secret.encode(), message, hashlib.sha256).digest()
    return _b64url_enc(sig)


def generate_cadet_jwt():
    """Generate a signed cadet-role JWT using the secret from keys.json."""
    header  = json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":"))
    payload = json.dumps({"username": "cadet_12",  "role": "cadet"},   separators=(",", ":"))
    h = _b64url_enc(header)
    p = _b64url_enc(payload)
    s = _jwt_signature(h, p, KEYS["jwt_secret"])
    return f"{h}.{p}.{s}"


def verify_jwt(token):
    """
    Verify a JWT token against the stored secret.
    Returns (payload_dict, None) on success or (None, error_reason) on failure.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return None, "malformed"

    h_b64, p_b64, submitted_sig = parts

    expected_sig = _jwt_signature(h_b64, p_b64, KEYS["jwt_secret"])

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(submitted_sig, expected_sig):
        return None, "invalid_signature"

    try:
        payload = json.loads(_b64url_dec(p_b64))
        return payload, None
    except Exception:
        return None, "invalid_payload"



@app.route("/config/", defaults={"path": ""})
@app.route("/config/<path:path>")
def block_config(path):
    """Never serve the config directory."""
    abort(403)


@app.route("/server.py")
def block_server_script():
    """Never serve this script itself."""
    abort(403)



@app.route("/api/session", methods=["GET"])
def api_session():
    """
    Returns a freshly signed cadet JWT for the player's session.
    The secret is never exposed — only the signed token is returned.
    """
    token = generate_cadet_jwt()
    return jsonify({"token": token})


@app.route("/api/archive", methods=["POST"])
def api_archive():
    """
    Check if the queried domain matches the known archive and return the
    appropriate HTML fragment. The target domain never appears in client code.
    """
    data  = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip().lower()
    # Normalise — strip protocol and trailing slash
    query = query.replace("https://", "").replace("http://", "")
    query = query.lstrip("www.").rstrip("/")

    TARGET = "leosterling.astro.old"
    TARGET_FULL = "archive.cosmoconnect.net/archive/" + TARGET

    if query in (TARGET, TARGET_FULL):
        return jsonify({"found": True})
    return jsonify({"found": False})


@app.route("/api/check-key", methods=["POST"])
def api_check_key():
    """
    Validate a single key and return a hint pointing to the next step.

    Request body (JSON):
        { "step": 1|2|3, "value": str }

    Response (JSON):
        { "correct": bool, "hint": str | null }

    Hints are only revealed on a correct answer to avoid leaking structure.
    """
    data  = request.get_json(silent=True) or {}
    step  = data.get("step")
    value = (data.get("value") or "").strip()

    hints = {
        1: (
            "Signal decoded. A Git commit diff references a legacy intranet domain. "
            "Search for it in the AstroArchive. The archived page contains a classified reference document."
        ),
        2: (
            "Document authenticated. Inspect Commander Leo Sterling's profile avatar closely. "
            "It contains mission-critical EXIF metadata — the image properties may hold encoded telemetry data."
        ),
        3: (
            "Spacecraft identified. Your current session token grants insufficient privileges. "
            "Decode it, elevate the role to COMMANDER, and re-sign it. "
            "The HMAC secret is the lowercase name of the Node-01 primary installation site — "
            "cross-reference the telemetry table in the handbook."
        ),
    }

    if step == 1:
        correct = (value.upper() == KEYS["key1"].upper())
    elif step == 2:
        correct = (value.upper() == KEYS["key2"].upper())
    elif step == 3:
        correct = (value.upper() in [k.upper() for k in KEYS["key3"]])
    else:
        return jsonify({"correct": False, "hint": None}), 400

    return jsonify({
        "correct": correct,
        "hint":    hints[step] if correct else None,
    })


@app.route("/api/validate", methods=["POST"])
def api_validate():
    """
    Validate submitted keys + JWT entirely server-side.

    Request body (JSON):
        { "key1": str, "key2": str, "key3": str, "jwt": str }

    Response (JSON):
        { "success": bool, "errors": [str], "hint": str | null }
    """
    data = request.get_json(silent=True) or {}

    key1      = (data.get("key1") or "").strip().upper()
    key2      = (data.get("key2") or "").strip().upper()
    key3      = (data.get("key3") or "").strip()
    jwt_token = (data.get("jwt")  or "").strip()

    errors = []

    k1_ok = (key1 == KEYS["key1"].upper())
    k2_ok = (key2 == KEYS["key2"].upper())
    k3_ok = (key3.upper() in [k.upper() for k in KEYS["key3"]])

    if not k1_ok:
        errors.append("Key [1] Telemetry Decoupler signature invalid.")
    if not k2_ok:
        errors.append("Key [2] Handbook Decryptor signature invalid.")
    if not k3_ok:
        errors.append("Key [3] Spacecraft International Designator mismatched.")

    payload, jwt_err = verify_jwt(jwt_token)
    jwt_role = (payload or {}).get("role", "none")
    jwt_ok   = (jwt_err is None and jwt_role == KEYS["required_role"])

    if not jwt_ok:
        if jwt_err == "malformed":
            errors.append("JWT Authentication: TOKEN MALFORMED OR MISSING.")
        elif jwt_err == "invalid_signature":
            errors.append("JWT Authentication: SIGNATURE VERIFICATION FAILED.")
        else:
            errors.append(
                f"JWT Authentication: Access denied for role [{jwt_role.upper()}]. "
                "COMMANDER privileges required."
            )

    hint = None
    if k1_ok and k2_ok and k3_ok and not jwt_ok:
        hint = (
            "📡 SYSTEM NOTE: All mission keys verified. "
            "Authentication token signature mismatch detected.\n"
            "HMAC secret is derived from the installation site of Node-01 — "
            "the primary telescope array referenced in telemetry table 2.1. "
            "Cross-reference with observatory coordinates."
        )

    success = k1_ok and k2_ok and k3_ok and jwt_ok
    return jsonify({
        "success": success,
        "errors":  errors,
        "hint":    hint,
        "flag":    KEYS["flag"] if success else None,
    })



@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    if not path:
        path = "index.html"

    # Extra safety — block anything inside config/
    if path.startswith("config/") or path == "server.py":
        abort(403)

    full_path = os.path.join(ROOT_DIR, path)
    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(ROOT_DIR, path)



if __name__ == "__main__":
    port = 8000
    print(f"\n🚀  Challenge server starting on http://localhost:{port}")
    print(f"    Serving files from : {ROOT_DIR}")
    print(f"    Keys file          : {CONFIG_PATH}")
    print(f"    Blocked paths      : /config/*  /server.py\n")
    app.run(host="0.0.0.0", port=port, debug=False)
