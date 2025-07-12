from google.oauth2 import service_account
import google.auth.transport.requests
import requests
from datetime import datetime

# Load credentials and get access token
creds = service_account.Credentials.from_service_account_file(
    "serviceAccountKey.json",
    scopes=["https://www.googleapis.com/auth/datastore"]
)
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
token = creds.token

# Replace with your actual project ID from Firebase Console
project_id = "syntax-drip-webpage"  # <--- CHANGE THIS

# REST API endpoint
url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/test"

# Payload
data = {
    "fields": {
        "test": { "stringValue": "hello from REST" },
        "timestamp": { "timestampValue": datetime.utcnow().isoformat() + "Z" }
    }
}

# Request headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# POST to Firestore
response = requests.post(url, headers=headers, json=data)
print("Status:", response.status_code)
print("Response:", response.json())