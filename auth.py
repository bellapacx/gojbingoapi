import bcrypt
from firebase_client import db
from utils.token import create_access_token
from fastapi import HTTPException

def authenticate_user(username: str, password: str):
    docs = db.collection("users").where("username", "==", username).stream()
    user = next((doc.to_dict() for doc in docs), None)
    if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
        return user
    raise HTTPException(status_code=401, detail="Invalid credentials")

def register_user(username: str, password: str, role: str = "admin"):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.collection("users").add({"username": username, "password": hashed, "role": role})
    return {"status": "created"}
