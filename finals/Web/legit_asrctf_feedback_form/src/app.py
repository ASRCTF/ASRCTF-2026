import os

from flask import *
from jinja2 import *
from jinja2.sandbox import *

from threading import Thread
from uuid import uuid4
from bot import bot_visit

app = Flask(__name__)
app.secret_key = os.urandom(32)

os.makedirs('/tmp/jinja_cache/', exist_ok=True)
os.makedirs('/tmp/feedback_logs/', exist_ok=True)

feedback_db = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/feedback")
def feedback():
    page_id = request.args.get("id")

    if not page_id or page_id not in feedback_db:
        return "Feedback not found", 404

    if "id" not in session:
        session["id"] = str(uuid4())
    session_id = session["id"]

    cache_dir = f'/tmp/jinja_cache/{session_id}/'
    os.makedirs(cache_dir, exist_ok=True)

    player_env = SandboxedEnvironment(
        loader=FileSystemLoader("templates/"),
        bytecode_cache=FileSystemBytecodeCache(cache_dir),
        autoescape=False
    )

    entry = feedback_db[page_id]
    template = player_env.get_template("feedback.html")

    return template.render(
        name=entry["name"],
        email=entry["email"],
        rating=entry["rating"],
        feedback=entry["feedback"]
    )


@app.route("/submit", methods=["POST"])
def submit():
    name     = request.form.get("name", "")
    email    = request.form.get("email", "")
    rating   = request.form.get("rating", "")
    feedback = request.form.get("feedback", "")

    page_id = str(uuid4())
    feedback_db[page_id] = {
        "name": name, "email": email,
        "rating": rating, "feedback": feedback
    }

    log_path = f"/tmp/feedback_logs/{name}.log"
    with open(log_path, "wb") as f:
        f.write(email.encode("latin-1"))

    player_session = request.cookies.get("session")
    Thread(target=bot_visit, args=(page_id, player_session)).start()

    return jsonify({"redirect": f"/feedback?id={page_id}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, threaded=True, debug=True)