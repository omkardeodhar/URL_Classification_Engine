#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import threading
import json
from pathlib import Path
import subprocess
from bs4 import BeautifulSoup

app = Flask(__name__)

# Files
OUTPUT_FILE = Path("scraper_output.json")   # Metadata output
CACHE_FILE  = Path("domain_cache.json")     # Shared domain cache

# External services
FRIEND_URL = "http://172.31.254.247:5005/predict"

file_lock = threading.Lock()


def fetch_metadata(domain):
    for scheme in ["https://", "http://"]:
        url = f"{scheme}{domain}"
        try:
            result = subprocess.run(
                ["wget", "-q", "-O", "-", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
            html = result.stdout.decode("utf-8", errors="ignore")
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            title = (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else "No Title"
            )
            desc_tag = soup.find("meta", attrs={"name": "description"})
            description = (
                desc_tag["content"].strip()
                if desc_tag and "content" in desc_tag.attrs
                else "No Description"
            )
            return title, description

        except Exception:
            continue

    return "Fetch Failed", "Could not retrieve metadata"


def process_domain(domain):
    title, description = fetch_metadata(domain)
    result = {"domain": domain, "title": title, "description": description}

    # Send metadata to model for prediction
    if title not in ["Fetch Failed", "No Title"] and title.strip():
        try:
            requests.post(FRIEND_URL, json=result, timeout=2)
        except Exception:
            pass

        with file_lock:
            with open(OUTPUT_FILE, "a") as f:
                f.write(json.dumps(result) + "\n")


@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    domain = data.get("url")
    if not domain:
        return jsonify({"error": "No URL provided"}), 400

    threading.Thread(target=process_domain, args=(domain,), daemon=True).start()
    return jsonify({"queued": domain}), 200


# New: handle model callback to update access in domain cache
def update_cache_entry(url: str, access: str):
    with file_lock:
        if CACHE_FILE.exists():
            try:
                cache = json.loads(CACHE_FILE.read_text())
            except Exception:
                cache = {}
        else:
            cache = {}

        # Update entry
        entry = cache.get(url, {"url": url, "access": "allowed"})
        entry["access"] = access
        cache[url] = entry

        # Persist cache
        CACHE_FILE.write_text(json.dumps(cache, indent=4))
        #print(f"[+] Updated cache: {url} -> {access}")


@app.route("/update_access", methods=["POST"])
def update_access():
    data = request.get_json()
    url = data.get("url")
    access = data.get("access")
    if not url or access not in ["allowed", "blocked"]:
        return jsonify({"error": "Invalid payload"}), 400

    # Spawn thread to update cache without blocking
    threading.Thread(
        target=update_cache_entry,
        args=(url, access),
        daemon=True
    ).start()
    return jsonify({"status": "queued", "url": url, "access": access}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
