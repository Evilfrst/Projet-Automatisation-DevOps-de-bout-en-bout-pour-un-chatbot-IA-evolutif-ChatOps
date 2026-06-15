from .database import SessionLocal
from .models import AuditLog

def save_audit_log(
username: str,
action: str,
target: str = ""
):

```
db = SessionLocal()

try:

    audit = AuditLog(
        username=username,
        action=action,
        target=target
    )

    db.add(audit)
    db.commit()

except Exception as e:

    db.rollback()

    print(
        f"Audit error: {e}"
    )

finally:

    db.close()
```
