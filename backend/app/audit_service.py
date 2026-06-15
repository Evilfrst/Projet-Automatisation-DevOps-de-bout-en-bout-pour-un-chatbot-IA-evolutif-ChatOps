from .database import SessionLocal
from .models import AuditLog
import logging

logger = logging.getLogger(__name__)


def save_audit_log(username: str, action: str, target: str = None):
    db = SessionLocal()

    try:
        log = AuditLog(
            username=username,
            action=action,
            target=target
        )

        db.add(log)
        db.commit()

        logger.info(
            f"Audit log saved: {username} - {action}"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Audit log error: {e}")

    finally:
        db.close()
