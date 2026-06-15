from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "CHANGE_ME"

ALGORITHM = "HS256"

def create_access_token(data):

    payload = data.copy()

    payload.update({
        "exp": datetime.utcnow() + timedelta(hours=24)
    })

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
