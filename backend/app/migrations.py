import logging

from sqlalchemy import Engine, inspect, text

logger = logging.getLogger(__name__)


def migrate_legacy_schema(engine: Engine) -> None:
    """Apply small, idempotent migrations needed by older project archives.

    Older ChatOps databases created the ``conversations`` table without a
    ``user_id`` column. SQLAlchemy's ``create_all`` does not alter an existing
    table, so authentication-aware history would otherwise fail at runtime.
    """

    inspector = inspect(engine)
    if not inspector.has_table("conversations"):
        return

    columns = {column["name"] for column in inspector.get_columns("conversations")}

    with engine.begin() as connection:
        if "user_id" not in columns:
            logger.warning(
                "Legacy conversations table detected: adding user_id column"
            )
            connection.execute(
                text("ALTER TABLE conversations ADD COLUMN user_id INTEGER")
            )

        # Preserve existing history by assigning orphaned rows to the first
        # account when one already exists. If there is no user yet, registration
        # will perform the same assignment for the first created account.
        first_user_id = connection.execute(
            text("SELECT id FROM users ORDER BY id ASC LIMIT 1")
        ).scalar()

        if first_user_id is not None:
            connection.execute(
                text(
                    "UPDATE conversations "
                    "SET user_id = :user_id "
                    "WHERE user_id IS NULL"
                ),
                {"user_id": first_user_id},
            )

        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_conversations_user_id "
                "ON conversations (user_id)"
            )
        )
