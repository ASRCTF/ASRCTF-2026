import os
from flask import Flask, request, render_template, redirect, url_for, abort
import re

app = Flask(__name__)
app.secret_key = "n0t3b00k-s3cr3t-k3y"

NOTES_DIR = os.path.join(os.path.dirname(__file__), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)


def list_notes():
    notes = []
    for fname in sorted(os.listdir(NOTES_DIR)):
        if fname.endswith(".txt"):
            note_id = fname[:-4]
            fpath = os.path.join(NOTES_DIR, fname)
            with open(fpath, "r") as f:
                lines = f.read().splitlines()
            title = lines[0] if lines else "(untitled)"
            notes.append({"id": note_id, "title": title})
    return notes

@app.route("/")
def index():
    return render_template("index.html", notes=list_notes())

@app.route("/note/new", methods=["GET"])
def new_note():
    return render_template("new_note.html")

@app.route("/note/create", methods=["POST"])
def create_note():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if not title:
        abort(400)
    note_id = title.lower().replace(" ", "_")
    fpath = os.path.join(NOTES_DIR, note_id + ".txt")
    with open(fpath, "w") as f:
        f.write(title + "\n" + content)
    return redirect(url_for("index"))

@app.route("/note/<path:note_id>")
def view_note(note_id):
    fpath = os.path.join(NOTES_DIR, note_id)
    print(fpath)
    
    if not os.path.exists(fpath):
        return render_template("404.html"), 404
    
    if (note_id != "flag.txt" and not bool(re.compile(r'^(?!.*flag\.txt).*$').match(fpath))):
        print("asd")
        return render_template("404.html"), 404
    
    with open(fpath, 'r') as f:
        lines = f.read().splitlines()
    
        title = lines[0] if lines else "(untitled)"
        content = "\n".join(lines[1:]) if len(lines) > 1 else ""
        if "ASRCTF{" in content:
            return render_template("404.html"), 404
        
        return render_template("view_note.html", note={"id": note_id, "title": title, "content": content})

if __name__ == "__main__":
    app.run("0.0.0.0", 3000, debug=True)