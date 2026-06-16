from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import SessionLocal
from .models import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(
                User.username == payload["sub"]
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Utilisateur introuvable"
            )

        return user

    finally:
        db.close()
