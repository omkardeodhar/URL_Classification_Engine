from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path

app = Flask(__name__, template_folder="templates", static_folder="static")
CACHE_FILE = Path("domain_cache.json")

def load_data():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", dns_config=data)

@app.route("/toggle", methods=["POST"])
def toggle():
    domain = request.form.get("domain")
    access = request.form.get("access")
    data = load_data()
    if domain in data and access in ["allowed", "blocked"]:
        data[domain]["access"] = access
        save_data(data)
    return redirect(url_for("index"))

if __name__ == "__main__":
    print("Starting Admin Panel. Visit: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
