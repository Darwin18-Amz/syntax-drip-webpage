import os
import json
from flask import Flask, request, render_template, jsonify
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
from datetime import datetime, timezone

app = Flask(__name__)

# Load service account credentials from env
with open("serviceAccountKey.json") as f:
    service_account_info = json.load(f)
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/datastore"]
)

auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)

project_id = service_account_info["project_id"]
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/leads"

headers = {
    "Authorization": f"Bearer {creds.token}",
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    country_code = data.get("countryCode", "+91")

    if not name or not phone:
        return jsonify(success=False, message="Missing fields")

    payload = {
        "fields": {
            "name": {"stringValue": name},
            "phoneNumber": {"stringValue": f"{country_code}{phone}"},
            "timestamp": {"timestampValue": datetime.now(timezone.utc).isoformat()}
        }
    }

    creds.refresh(auth_req)
    headers["Authorization"] = f"Bearer {creds.token}"

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return jsonify(success=True)
    else:
        print("Error:", response.text)
        return jsonify(success=False, message="Failed to write to Firestore")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)