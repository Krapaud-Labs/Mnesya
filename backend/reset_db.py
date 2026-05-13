"""Reset database script — truncates all data while preserving the schema.

Usage (on VPS):
    python reset_db.py
"""

import os
import sys
from sqlalchemy import create_engine, text

TABLES = [
    "reminder_status",
    "escalation_log",
    "reminder",
    "medication",
    "pairing_code",
    "push_token",
    "revoked_token",
    "user_session_revocation",
    '"user"',
    "caregiver",
]


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(database_url)

    confirm = input("This will DELETE ALL DATA in the database. Type 'yes' to confirm: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        sys.exit(0)

    with engine.begin() as conn:
        tables_sql = ", ".join(TABLES)
        conn.execute(text(f"TRUNCATE {tables_sql} RESTART IDENTITY CASCADE"))

    print("Database reset complete. Schema preserved, all data deleted.")


if __name__ == "__main__":
    main()
