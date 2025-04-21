import joblib
import pandas as pd
import json
import logging
import requests
from flask import Flask, request, jsonify

# ——— Configuration ———
BLOCKED_CATEGORIES = {"gambling", "adult"} 
PROXY_CALLBACK_URL = "http://127.0.0.1:5001/update_access"

# ——— Logging ———
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s – %(message)s'
)
logger = logging.getLogger(__name__)

# ——— Flask App ———
app = Flask(__name__)

def custom_tokenizer(x):
    return x.replace('.', ' ').replace('/', ' ').replace('-', ' ').split()

# ——— Load Model ———
try:
    model = joblib.load('RF_categorizer.pkl')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise



def process_data(json_data):
    """
    Returns a dict mapping each domain to its {url, access}.
    Also POSTs back to the proxy for each entry.
    """
    if isinstance(json_data, dict):
        df = pd.DataFrame([json_data])
    elif isinstance(json_data, list):
        df = pd.DataFrame(json_data)
    else:
        return {"error": "Invalid JSON format"}

    df['text'] = (
        df['domain'].fillna('') + ' '
        + df['title'].fillna('') + ' '
        + df['description'].fillna('')
    )

    output_map = {}
    for _, row in df.iterrows():
        domain = row['domain']
        pred = model.predict([row['text']])[0]
        access = "blocked" if pred.lower() in BLOCKED_CATEGORIES else "allowed"

        entry = {
            "url": domain,
            "access": access
        }

        output_map[domain] = entry

        # Callback to proxy
        try:
            requests.post(PROXY_CALLBACK_URL, json=entry, timeout=2)
        except Exception as e:
            logger.warning(f"Callback failed for {domain}: {e}")

    return output_map

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result_map = process_data(data)
    return jsonify(result_map)

if __name__ == "__main__":
    logger.info("Starting model server on port 5005")
    app.run(host='192.168.29.109', port=5005, debug=False)
