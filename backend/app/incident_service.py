from .database import SessionLocal
from .models import Incident


def create_incident(
    title: str,
    description: str | None,
    severity: str = "P3",
) -> dict:
    db = SessionLocal()
    try:
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            status="OPEN",
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return {
            "id": incident.id,
            "status": incident.status,
        }
    except Exception as exc:
        db.rollback()
        return {"error": str(exc)}
    finally:
        db.close()


def get_incidents() -> list[dict]:
    db = SessionLocal()
    try:
        incidents = db.query(Incident).order_by(Incident.id.desc()).all()
        return [
            {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "created_at": incident.created_at,
            }
            for incident in incidents
        ]
    finally:
        db.close()
