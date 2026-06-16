from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "CHANGE_ME_IN_PRODUCTION"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):
    payload = data.copy()

    payload.update(
        {
            "exp": datetime.utcnow()
            + timedelta(
                hours=ACCESS_TOKEN_EXPIRE_HOURS
            )
        }
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None
