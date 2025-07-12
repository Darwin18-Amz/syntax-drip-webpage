from flask import Flask, render_template, request, jsonify
from datetime import datetime
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import os
import json

app = Flask(__name__)

# Load service account from environment variable (NOT from file)
try:
    service_account_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
except KeyError:
    raise Exception("❌ Missing environment variable: GOOGLE_APPLICATION_CREDENTIALS_JSON")

creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/datastore"]
)

# Refresh to get access token
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
token = creds.token

# Replace with your actual Firebase project ID
PROJECT_ID = "syntax-drip-webpage"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/callbacks"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit-phone", methods=["POST"])
def submit_phone():
    try:
        data = request.get_json()
        print("📩 Received data:", data)

        phone_number = data.get("phoneNumber")
        country_code = data.get("countryCode")

        if not phone_number or not country_code:
            return jsonify({"success": False, "message": "Missing phone number or country code."}), 400

        full_number = country_code + phone_number

        payload = {
            "fields": {
                "phoneNumber": {"stringValue": full_number},
                "timestamp": {"timestampValue": datetime.utcnow().isoformat() + "Z"}
            }
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(FIRESTORE_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({"success": True, "message": "Saved to Firestore via REST."})
        else:
            print("❌ Firestore error:", response.text)
            return jsonify({"success": False, "message": "Failed to write to Firestore."}), 500

    except Exception as e:
        print("❌ Error in /submit-phone:", str(e))
        return jsonify({"success": False, "message": "Internal Server Error."}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5004)