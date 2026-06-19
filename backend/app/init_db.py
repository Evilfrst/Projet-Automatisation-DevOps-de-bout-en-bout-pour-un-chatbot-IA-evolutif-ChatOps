from .database import engine
from .migrations import migrate_legacy_schema
from .models import Base

Base.metadata.create_all(bind=engine)
migrate_legacy_schema(engine)
