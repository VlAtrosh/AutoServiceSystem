from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import db

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"[AUTH] Received token: {token}")
    print(f"[AUTH] Current tokens: {list(db.tokens.keys())}")

    user_id = db.tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
