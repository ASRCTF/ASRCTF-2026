import argparse
import json
import os
import shutil

from app.config import load_config


def remove_children(path):
    if not os.path.exists(path):
        return
    for name in os.listdir(path):
        target = os.path.join(path, name)
        if os.path.isdir(target):
            shutil.rmtree(target, ignore_errors=True)
        else:
            os.remove(target)


def reset_solution_files(config):
    json_path = config["paths"]["solution_json"]
    markdown_path = config["paths"]["solution_md"]
    solution_dir = config["paths"]["solution_dir"]
    if not os.path.exists(solution_dir):
        os.makedirs(solution_dir)

    with open(json_path, "w") as handle:
        json.dump({"successful_payloads": [], "updated_at": None}, handle, indent=2, sort_keys=True)

    with open(markdown_path, "w") as handle:
        handle.write(
            "# Successful payloads\n\n"
            "| Timestamp (UTC) | Backend version | Prompt | Response |\n"
            "| --- | --- | --- | --- |\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Reset ASRCTF runtime artifacts to the base model state.")
    parser.add_argument(
        "--config",
        default=os.path.join("config", "challenge.json"),
        help="Path to the JSON challenge config.",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    for path in [config["paths"]["event_log"], config["paths"]["leak_log"], config["paths"].get("prompt_log")]:
        if path and os.path.exists(path):
            os.remove(path)

    reset_solution_files(config)

    print("Reset complete.")
    print("Logs cleared.")
    print("Solution payload tracker reset.")


if __name__ == "__main__":
    main()
