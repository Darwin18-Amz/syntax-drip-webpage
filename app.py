from flask import Flask, request, render_template, jsonify
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import os
import json

app = Flask(__name__)

# Load service account credentials from environment variable
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if not SERVICE_ACCOUNT_JSON:
    raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable")

creds = service_account.Credentials.from_service_account_info(
    json.loads(SERVICE_ACCOUNT_JSON),
    scopes=["https://www.googleapis.com/auth/datastore"]
)

auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
token = creds.token

# Firestore API setup
project_id = json.loads(SERVICE_ACCOUNT_JSON).get("project_id")
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/leads"
headers = {
    "Authorization": f"Bearer {token}",
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
    country_code = data.get("countryCode", "+91")  # used if needed, not stored

    if not name or not phone:
        return jsonify(success=False, message="Name and phone are required.")

    print(f"📤 Incoming data: {data}")
    print(f"✅ Name: {name}")
    print(f"✅ Phone: {phone}")

    # Refresh token
    creds.refresh(auth_req)
    token = creds.token
    headers["Authorization"] = f"Bearer {token}"

    # Prepare Firestore payload (without countryCode)
    payload = {
        "fields": {
            "name": {"stringValue": name},
            "phone": {"stringValue": phone}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📥 Firestore response:", response.text)

    if response.status_code == 200:
        return jsonify(success=True, message="Data submitted successfully!")
    else:
        return jsonify(success=False, message="Failed to submit data.", details=response.text)

# ✅ PRODUCTION RUNNER (required for Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # Render sets $PORT automatically
    app.run(host="0.0.0.0", port=port)
