# mitm_addon.py
import json
from pathlib import Path
from mitmproxy import http
import requests

CACHE_FILE = Path("domain_cache.json")
SCRAPER_URL = "http://localhost:5001/scrape"

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def send_to_scraper(domain_data):
    try:
        requests.post(SCRAPER_URL, json=domain_data, timeout=1)  # fire-and-forget
    except Exception as e:
        print(f"[!] Failed to notify scraper for {domain_data['url']} - {e}")

class MITMAddon:
    def request(self, flow: http.HTTPFlow):
        host = flow.request.pretty_host.lower()

        domain_cache = load_cache()

        if host not in domain_cache:
            domain_cache[host] = {"url": host, "access": "allowed"}
            save_cache(domain_cache)
            send_to_scraper({"url": host})

        if domain_cache[host]["access"] == "blocked":
            flow.response = http.Response.make(
                403,
                b"<html><body><h1>Blocked by Admin</h1></body></html>",
                {"Content-Type": "text/html"}
            )

# Correct: Register class instance here
addons = [MITMAddon()]
