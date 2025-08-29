from fastapi import APIRouter
from auth import authenticate_user, register_user
from utils.token import create_access_token

router = APIRouter()

@router.post("/login")
def login(data: dict):
    user = authenticate_user(data['username'], data['password'])
    token = create_access_token({"sub": user['username'], "role": user['role']})
    return {"token": token}

@router.post("/register")
def register(data: dict):
    return register_user(data['username'], data['password'], data.get('role', 'admin'))