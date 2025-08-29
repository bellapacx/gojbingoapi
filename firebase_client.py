import firebase_admin # type: ignore
from firebase_admin import credentials, firestore # type: ignore

print(">>> firebase_admin_setup.py loaded")  # Optional debug

cred = credentials.Certificate("/etc/secrets/service.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
