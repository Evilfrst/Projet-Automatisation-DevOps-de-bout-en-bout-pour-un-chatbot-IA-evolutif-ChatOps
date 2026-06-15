from sqlalchemy import (
Column,
Integer,
String,
Text,
DateTime,
ForeignKey
)

from sqlalchemy.orm import (
declarative_base,
relationship
)

from datetime import datetime

Base = declarative_base()

# ==================================================

# USERS

# ==================================================

class User(Base):

```
__tablename__ = "users"

id = Column(
    Integer,
    primary_key=True,
    index=True
)

username = Column(
    String(100),
    unique=True,
    nullable=False
)

email = Column(
    String(255),
    unique=True,
    nullable=False
)

password_hash = Column(
    String(255),
    nullable=False
)

role = Column(
    String(50),
    default="viewer"
)

created_at = Column(
    DateTime,
    default=datetime.utcnow
)

conversations = relationship(
    "Conversation",
    back_populates="user"
)
```

# ==================================================

# CONVERSATIONS

# ==================================================

class Conversation(Base):

```
__tablename__ = "conversations"

id = Column(
    Integer,
    primary_key=True,
    index=True
)

user_id = Column(
    Integer,
    ForeignKey("users.id")
)

user_message = Column(
    Text,
    nullable=False
)

ai_response = Column(
    Text,
    nullable=False
)

created_at = Column(
    DateTime,
    default=datetime.utcnow,
    nullable=False
)

user = relationship(
    "User",
    back_populates="conversations"
)
```

# ==================================================

# AUDIT LOGS

# ==================================================

class AuditLog(Base):

```
__tablename__ = "audit_logs"

id = Column(
    Integer,
    primary_key=True,
    index=True
)

username = Column(
    String(100),
    nullable=False
)

action = Column(
    String(255),
    nullable=False
)

target = Column(
    String(255),
    nullable=True
)

created_at = Column(
    DateTime,
    default=datetime.utcnow
)
```

# ==================================================

# INCIDENTS

# ==================================================

class Incident(Base):

```
__tablename__ = "incidents"

id = Column(
    Integer,
    primary_key=True,
    index=True
)

title = Column(
    Text,
    nullable=False
)

description = Column(
    Text,
    nullable=True
)

severity = Column(
    String(20),
    nullable=False
)

status = Column(
    String(20),
    default="OPEN"
)

created_at = Column(
    DateTime,
    default=datetime.utcnow
)
```
