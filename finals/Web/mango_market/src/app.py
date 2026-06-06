from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
from urllib.parse import quote_plus
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex

username = "ROOT"
password = "X5y<5X*`tW1%"

uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@localhost:27017/admin"

client = MongoClient(uri)
db = client["main"]
logins = db["logins"]

logged_in_users = {}

@app.route("/")
def home():
	if session:
		if session["user_id"] in logged_in_users:
			return render_template(
				"index.html", 
				username=logged_in_users.get(session["user_id"])
			)
		else:
			session.pop("user_id", None)
			return render_template("redirect.html")
	else:
		session.pop("user_id", None)
		return render_template("redirect.html")


@app.route("/logout", methods=['GET'])
def logout():
	if session["user_id"]:
		session.pop("user_id", None)
		logged_in_users.pop("user_id", None)
		return redirect(url_for("login"))
	else:
		return "Error logging out", 503

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		username = request.form.get("username", "")
		password = request.form.get("password", "")
			
		if len(username) == 0 or len(password) == 0:
			return "Empty fields", 500

		password_hash = hashlib.md5(password.encode()).hexdigest()
		user = logins.find_one({
			"username": username,
			"password_hash": password_hash,
		})

		if user is None:
			return "User does not exist or Wrong Password", 501

		uid = session["user_id"] = uuid.uuid4().hex
		logged_in_users.update({uid: username})

		return redirect(url_for("home"))
	return render_template("login.html")

@app.route("/admin", methods=['GET'])
def admin():
	if session:
		if logged_in_users[session["user_id"]] == "johnmango": # To be censored
			return render_template("admin.html")
		else:
			return "You are not a mango admin", 504
	return "You are not a mango admin", 504

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3000)