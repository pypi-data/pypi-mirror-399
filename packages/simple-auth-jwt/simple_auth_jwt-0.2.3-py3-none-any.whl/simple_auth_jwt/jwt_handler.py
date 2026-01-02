from datetime import datetime, timedelta
from jose import jwt
from simple_auth_jwt.config import AuthConfig

def create_access(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=AuthConfig.access_expire_min)
    payload = data.copy()
    payload["exp"] = expire
    return jwt.encode(payload, AuthConfig.secret_key, algorithm="HS256")

def create_refresh(data: dict):
    expire = datetime.utcnow() + timedelta(days=AuthConfig.refresh_expire_days)
    payload = data.copy()
    payload["exp"] = expire
    return jwt.encode(payload, AuthConfig.secret_key, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, AuthConfig.secret_key, algorithms=["HS256"])
