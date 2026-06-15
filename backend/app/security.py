from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv(
"JWT_SECRET",
"CHANGE_ME_IN_PRODUCTION"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 24

def create_access_token(data: dict):

```
payload = data.copy()

payload.update(
    {
        "exp":
        datetime.utcnow()
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
```

def verify_token(token: str):

```
try:

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload

except Exception:

    return None
```
