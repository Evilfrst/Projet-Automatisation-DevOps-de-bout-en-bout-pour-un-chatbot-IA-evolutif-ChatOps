from .database import SessionLocal
from .models import Incident

def create_incident(
title,
description,
severity="P3"
):

db = SessionLocal()

try:

    incident = Incident(
        title=title,
        description=description,
        severity=severity,
        status="OPEN"
    )

    db.add(incident)

    db.commit()

    db.refresh(incident)

    return {
        "id": incident.id,
        "status": incident.status
    }

except Exception as e:

    db.rollback()

    return {
        "error": str(e)
    }

finally:

    db.close()

def get_incidents():

db = SessionLocal()

try:

    incidents = db.query(
        Incident
    ).all()

    return [
        {
            "id": i.id,
            "title": i.title,
            "severity": i.severity,
            "status": i.status
        }
        for i in incidents
    ]

finally:

    db.close()
