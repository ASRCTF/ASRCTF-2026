import atexit
import ipaddress
import re
import threading
import time
from collections import defaultdict, deque
from functools import wraps

from flask import (
    Flask,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.runtime import ChallengeBusyError, ChallengeManager


class SlidingWindowRateLimiter(object):
    def __init__(self, limit, window_seconds):
        self.limit = max(1, int(limit))
        self.window_seconds = max(1, int(window_seconds))
        self.events = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key):
        now = time.time()
        with self.lock:
            bucket = self.events[key]
            boundary = now - self.window_seconds
            while bucket and bucket[0] < boundary:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return False
            bucket.append(now)
            return True


def get_manager():
    return current_app.extensions["challenge_manager"]


def _config():
    return current_app.config["ASRCTF_CONFIG"]


def _admin_config():
    return _config()["admin"]


def _security_config():
    return _config()["security"]


def _admin_mount():
    return _admin_config()["mount_path"]


def _admin_api_base():
    return _admin_mount() + "/api"


def _creative_filter_config():
    return _config()["challenge"].get("creative_prompt_filter", {})


_FILTER_TRANSLATION = str.maketrans(
    {
        "@": "a",
        "4": "a",
        "3": "e",
        "1": "i",
        "!": "i",
        "|": "i",
        "0": "o",
        "$": "s",
        "5": "s",
        "7": "t",
        "+": "t",
    }
)


def _normalize_filter_text(text):
    lowered = (text or "").lower().translate(_FILTER_TRANSLATION)
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    normalized = " ".join(lowered.split())
    compact = normalized.replace(" ", "")
    return normalized, compact


def _creative_filter_message(prompt):
    filter_config = _creative_filter_config()
    if not filter_config.get("enabled", False):
        return None

    normalized_prompt, compact_prompt = _normalize_filter_text(prompt)
    for phrase in filter_config.get("blocked_phrases", []):
        normalized_phrase, compact_phrase = _normalize_filter_text(phrase)
        if normalized_phrase and normalized_phrase in normalized_prompt:
            return filter_config.get(
                "message",
                "Basic prompt-injection phrases are filtered here. Use a more creative angle.",
            )
        if compact_phrase and compact_phrase in compact_prompt:
            return filter_config.get(
                "message",
                "Basic prompt-injection phrases are filtered here. Use a more creative angle.",
            )
    return None


def _client_ip():
    config = _config()
    if config["security"].get("trust_proxy_headers"):
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _is_loopback(ip_value):
    try:
        return ipaddress.ip_address(ip_value).is_loopback
    except ValueError:
        return False


def _ip_allowed(ip_value, rules):
    if not rules:
        return True
    try:
        client_ip = ipaddress.ip_address(ip_value)
    except ValueError:
        return False

    for rule in rules:
        entry = (rule or "").strip()
        if not entry:
            continue
        try:
            if "/" in entry:
                if client_ip in ipaddress.ip_network(entry, strict=False):
                    return True
            elif client_ip == ipaddress.ip_address(entry):
                return True
        except ValueError:
            continue
    return False


def _admin_origin_allowed():
    config = _admin_config()
    client_ip = _client_ip()
    if not _ip_allowed(client_ip, config.get("allowed_ips", [])):
        return False

    if config.get("token"):
        return True

    return bool(config.get("allow_localhost_without_token", True)) and _is_loopback(client_ip)


def _admin_authenticated():
    token = _admin_config().get("token")
    if not _admin_origin_allowed():
        return False
    if not token:
        return True
    return bool(session.get("asrctf_admin_authenticated"))


def _hide_admin():
    abort(404)


def _json_error(message, status_code):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


def _rate_limit_response(message):
    if request.path.startswith("/api/") or request.path.startswith(_admin_api_base()):
        return _json_error(message, 429)
    return message, 429


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not _admin_authenticated():
            return _hide_admin()
        return view(*args, **kwargs)

    return wrapped


def create_app(config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["ASRCTF_CONFIG"] = config
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.secret_key = config["security"]["session_secret"]
    app.config["MAX_CONTENT_LENGTH"] = int(config["security"]["max_request_bytes"])
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = bool(
        config["security"].get("session_cookie_secure", False)
    )
    app.extensions["challenge_manager"] = ChallengeManager(config)
    app.extensions["rate_limiters"] = {
        "public": SlidingWindowRateLimiter(
            config["security"]["public_rate_limit_count"],
            config["security"]["public_rate_limit_window_seconds"],
        ),
        "admin": SlidingWindowRateLimiter(
            config["security"]["admin_rate_limit_count"],
            config["security"]["admin_rate_limit_window_seconds"],
        ),
    }

    admin_mount = config["admin"]["mount_path"]
    admin_api_base = admin_mount + "/api"

    @app.before_request
    def apply_rate_limits():
        client_ip = _client_ip()
        if request.path == "/api/chat":
            if not app.extensions["rate_limiters"]["public"].allow("public:{0}".format(client_ip)):
                return _rate_limit_response("Too many chat requests. Slow down and try again.")
        elif request.path.startswith(admin_mount):
            if not app.extensions["rate_limiters"]["admin"].allow("admin:{0}".format(client_ip)):
                return _rate_limit_response("Too many organizer requests. Try again shortly.")

    @app.after_request
    def apply_security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.errorhandler(413)
    def payload_too_large(error):
        del error
        return _json_error("Request body too large.", 413)

    @app.route("/")
    def challenge():
        public_state = get_manager().public_status()
        if not public_state["available"]:
            response = render_template(
                "model_down.html",
                page_name="challenge_down",
                config=config,
                public_state=public_state,
            )
            return response, 503
        return render_template(
            "play.html",
            page_name="challenge",
            config=config,
            creative_filter=_creative_filter_config(),
        )

    @app.route(admin_mount, methods=["GET", "POST"])
    def dashboard():
        if not _admin_origin_allowed():
            return _hide_admin()

        expected_token = _admin_config().get("token")
        if expected_token and request.method == "POST":
            submitted = (request.form.get("token") or "").strip()
            if submitted == expected_token:
                session["asrctf_admin_authenticated"] = True
                return redirect(url_for("dashboard"))

        if not _admin_authenticated():
            return render_template(
                "organizer_login.html",
                page_name="organizer_login",
                config=config,
            )

        return render_template(
            "dashboard.html",
            page_name="dashboard",
            config=config,
            admin_api_base=admin_api_base,
        )

    @app.route(admin_mount + "/events")
    @admin_required
    def events():
        return render_template(
            "events.html",
            page_name="events",
            config=config,
            admin_api_base=admin_api_base,
        )

    @app.route(admin_mount + "/logout", methods=["POST"])
    @admin_required
    def organizer_logout():
        session.pop("asrctf_admin_authenticated", None)
        return redirect(url_for("challenge"))

    @app.route("/healthz")
    def healthz():
        return jsonify({"ok": True})

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        payload = request.get_json(force=True, silent=True) or {}
        prompt = payload.get("prompt") or ""
        if not isinstance(prompt, str):
            return _json_error("Prompt must be a string.", 400)

        prompt = prompt.strip()
        if not prompt:
            return _json_error("Prompt is required.", 400)

        filter_message = _creative_filter_message(prompt)
        if filter_message:
            return _json_error(filter_message, 400)

        max_prompt_chars = int(config["security"]["max_prompt_chars"])
        if len(prompt) > max_prompt_chars:
            return _json_error(
                "Prompt exceeds the {0}-character limit.".format(max_prompt_chars), 413
            )

        try:
            result = get_manager().chat(prompt)
        except ChallengeBusyError as exc:
            return _json_error(str(exc), 503)

        return jsonify({"response": result["response"], "leaked": result["leaked"], "status": "ok"})

    @app.route(admin_api_base + "/status")
    @admin_required
    def api_status():
        return jsonify(get_manager().status_snapshot())

    @app.route(admin_api_base + "/events")
    @admin_required
    def api_events():
        return jsonify({"events": get_manager().list_events()})

    @app.route(admin_api_base + "/payloads")
    @admin_required
    def api_payloads():
        return jsonify({"payloads": get_manager().list_solutions()})

    @app.route(admin_api_base + "/reset", methods=["POST"])
    @admin_required
    def api_reset():
        expected_token = _admin_config().get("token")
        payload = request.get_json(force=True, silent=True) or {}
        provided_token = payload.get("token")
        if expected_token and provided_token != expected_token:
            return _json_error("Invalid admin token.", 403)
        return jsonify(get_manager().reset_to_base())

    @app.route(admin_api_base + "/block", methods=["POST"])
    @admin_required
    def api_block():
        payload = request.get_json(force=True, silent=True) or {}
        prompt = payload.get("prompt") or ""
        return jsonify(get_manager().block_payload(prompt))



    def shutdown_manager():
        manager = app.extensions.get("challenge_manager")
        if manager:
            manager.shutdown()

    atexit.register(shutdown_manager)
    return app


def serve_app(app, config):
    host = config["server"]["host"]
    port = int(config["server"]["port"])
    threads = int(config["server"].get("threads", 8))
    prefer_waitress = bool(config["server"].get("prefer_waitress"))

    if prefer_waitress:
        try:
            from waitress import serve
        except ImportError:
            prefer_waitress = False
        else:
            serve(app, host=host, port=port, threads=threads)
            return

    app.run(
        host=host,
        port=port,
        threaded=bool(config["server"].get("threaded", True)),
        debug=False,
        use_reloader=False,
    )
