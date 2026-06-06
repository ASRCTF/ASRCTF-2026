from flask import Flask, render_template, render_template_string, request
import re

app = Flask(__name__)
pattern = re.compile(
    r"(__|import|os|sys|subprocess|popen|system|eval|exec|builtins|globals|locals|class|mro|base|getitem|setitem|delitem|read|write|open|config|request|self|join|format|map|select|reject|list|dict|tuple|chr|ord|range|cycler|namespace|lipsum|url_for|get_flashed_messages|\+|\-|\*)"
)

def filter(input):
    if pattern.search(input):
        return "Error: Intercepted Malicious Payload"    
    return "Received: " + input

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send_signal", methods=["POST"])
def signal():
    input = request.form.get("payload")
    print(input)
    reply = render_template_string(filter(input))
    return render_template("index.html", reply=reply)

if __name__ == "__main__":
    app.run('0.0.0.0', 3000)
