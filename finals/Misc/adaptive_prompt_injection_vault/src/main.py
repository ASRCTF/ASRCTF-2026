import argparse
import os

from app import create_app, load_config, serve_app


def parse_args():
    parser = argparse.ArgumentParser(
        description="ASRCTF adaptive prompt injection web challenge"
    )
    parser.add_argument(
        "--config",
        default=os.path.join("config", "challenge.json"),
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host interface to bind to. Overrides the config file when provided.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to. Overrides the config file when provided.",
    )
    parser.add_argument(
        "--backend",
        choices=["mock", "ollama", "transformers"],
        default=None,
        help="Override the configured backend for quick testing.",
    )
    parser.add_argument(
        "--waitress",
        action="store_true",
        help="Prefer Waitress if it is installed.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)

    if args.host:
        config["server"]["host"] = args.host
    if args.port:
        config["server"]["port"] = args.port
    if args.backend:
        config["challenge"]["backend"] = args.backend
    if args.waitress:
        config["server"]["prefer_waitress"] = True

    host = config["server"]["host"]
    port = int(config["server"]["port"])
    display_host = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    print("ASRCTF challenge server starting")
    print("Public challenge: http://{0}:{1}/".format(display_host, port))
    print(
        "Organizer dashboard: http://{0}:{1}{2}".format(
            display_host, port, config["admin"]["mount_path"]
        )
    )
    print("Backend: {0}".format(config["challenge"]["backend"]))
    if config["challenge"]["backend"] == "ollama":
        print(
            "Ollama target: {0} via {1}".format(
                config["challenge"]["base_model"],
                config["challenge"]["ollama_base_url"],
            )
        )
    if not config["admin"].get("token"):
        print("Local dev mode: no ASRCTF_ADMIN_TOKEN set; organizer dashboard is localhost-only.")
    else:
        print("Organizer token is enabled; use the configured token on the organizer dashboard.")

    app = create_app(config)
    serve_app(app, config)


if __name__ == "__main__":
    main()
