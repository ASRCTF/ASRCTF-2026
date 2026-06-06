import os
import threading
from urllib.parse import urljoin

import requests
from flask import Flask, render_template, request


_FLAG_KEY = 0x2D
_FLAG_CIPHERTEXT = bytes.fromhex(
    "6c7e7f6e796b56194f181d4158591e72585f4118721c4a431d5f1e724f19181e72585f411872411d1d5d1a5b1d5f591e5550"
)


def decrypt_flag():
    return "".join(chr(byte ^ _FLAG_KEY) for byte in _FLAG_CIPHERTEXT)


FLAG = decrypt_flag()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="loopback-lounge-secret",
        FLAG=FLAG,
        INTERNAL_PORT=5001,
        SPONSOR_BASE_URL="https://sponsor-board.invalid/cards/",
    )

    if test_config:
        app.config.update(test_config)

    def build_preview_target(path):
        return urljoin(app.config["SPONSOR_BASE_URL"], path)

    def is_blocked_target(target):
        lowered = target.lower()
        return "localhost" in lowered or "127.0.0.1" in lowered

    app.build_preview_target = build_preview_target
    app.is_blocked_target = is_blocked_target

    @app.after_request
    def add_preview_decoys(response):
        response.headers["X-Sponsor-Beacon"] = "ASRCTF{numeric_loopback_starport}"
        response.headers["X-Preview-Telemetry"] = "ASRCTF{redirect_chain_to_airlock}"
        return response

    def start_internal_server():
        if app.config.get("_INTERNAL_SERVER_STARTED"):
            return

        port = int(app.config["INTERNAL_PORT"])

        thread = threading.Thread(
            target=app.run,
            kwargs={
                "host": "::1",
                "port": port,
                "threaded": True,
                "use_reloader": False,
            },
            daemon=True,
        )
        thread.start()
        app.config["_INTERNAL_SERVER_STARTED"] = True

    app.start_internal_server = start_internal_server

    @app.route("/")
    def index():
        path = request.args.get("path", request.args.get("url", ""))
        preview = None
        error = None
        status_code = None
        target = None

        if path:
            target = build_preview_target(path)
            if is_blocked_target(target):
                error = "That destination is blocked by policy."
            else:
                try:
                    response = requests.get(target, timeout=3)
                    status_code = response.status_code
                    preview = response.text[:2000]
                except requests.RequestException as exc:
                    error = str(exc)

        return render_template(
            "index.html",
            path=path,
            target=target,
            preview=preview,
            error=error,
            status_code=status_code,
            internal_port=app.config["INTERNAL_PORT"],
            sponsor_base_url=app.config["SPONSOR_BASE_URL"],
        )

    @app.route("/internal/flag")
    def internal_flag():
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return "Loopback access only.", 403
        return app.config["FLAG"]

    return app


app = create_app()


if __name__ == "__main__":
    external_port = int(os.environ.get("PORT", "5000"))
    internal_port = int(os.environ.get("INTERNAL_PORT", str(external_port + 1)))
    app.config["INTERNAL_PORT"] = internal_port
    app.start_internal_server()
    app.run(
        host="0.0.0.0",
        port=external_port,
        threaded=True,
    )
