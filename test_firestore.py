from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timezone
import socket

# Test DNS resolution (manual debug)
print("🔍 Testing DNS...")
print("firestore.googleapis.com resolves to:", socket.gethostbyname("firestore.googleapis.com"))

# Firebase init
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
print("✅ Firebase initialized")

# Firestore client
db = firestore.client()

print("📤 Writing to Firestore...")
doc_ref = db.collection("test").add({
    "test": "hello",
    "timestamp": datetime.now(timezone.utc)
})
print("✅ Successfully wrote with ID:", doc_ref[1].id)