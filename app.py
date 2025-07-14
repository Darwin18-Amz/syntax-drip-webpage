from flask import Flask, request, render_template, jsonify
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
from datetime import datetime, timezone

app = Flask(__name__)

# Firestore setup
project_id = "syntax-drip-webpage-a9c99"
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/leads"

# Load service account and refresh token
creds = service_account.Credentials.from_service_account_file(
    "serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/datastore"]
)
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
token = creds.token

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
    country_code = data.get("countryCode", "+91")

    if not name or not phone:
        return jsonify(success=False, message="Missing fields")

    # Build Firestore payload
    payload = {
        "fields": {
            "name": {"stringValue": name},
            "phoneNumber": {"stringValue": f"{country_code}{phone}"},
            "timestamp": {"timestampValue": datetime.now(timezone.utc).isoformat()}
        }
    }

    print("Submitting payload to Firestore:")
    print(payload)

    # Refresh token before request (important)
    creds.refresh(auth_req)
    headers["Authorization"] = f"Bearer {creds.token}"

    response = requests.post(url, headers=headers, json=payload)

    print("Firestore API Response:")
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 200:
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Failed to write to Firestore")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5004)