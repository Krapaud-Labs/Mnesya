"""Add performance indexes for auto-refresh queries

Revision ID: 005
Revises: 004
Create Date: 2026-03-18 00:00:00.000000

Indexes added:
- reminder.caregiver_id  — used by GET /api/reminder/caregiver (RemindersListScreen, DashboardScreen)
- reminder.user_id       — used by GET /api/reminder/user (UserHomeScreen)
- reminder.scheduled_at  — ORDER BY on all reminder list queries
- reminder_status.reminder_id  — JOIN reminder_status → reminder
- reminder_status.created_at   — WHERE clause in activity log (last 48h)
- user.caregiver_ids (GIN)     — ARRAY contains filter in GET /api/users
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_reminder_caregiver_id", "reminder", ["caregiver_id"])
    op.create_index("ix_reminder_user_id", "reminder", ["user_id"])
    op.create_index("ix_reminder_scheduled_at", "reminder", ["scheduled_at"])
    op.create_index("ix_reminder_status_reminder_id", "reminder_status", ["reminder_id"])
    op.create_index("ix_reminder_status_created_at", "reminder_status", ["_created_at"])
    op.create_index(
        "ix_user_caregiver_ids_gin",
        "user",
        ["caregiver_ids"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_user_caregiver_ids_gin", table_name="user")
    op.drop_index("ix_reminder_status_created_at", table_name="reminder_status")
    op.drop_index("ix_reminder_status_reminder_id", table_name="reminder_status")
    op.drop_index("ix_reminder_scheduled_at", table_name="reminder")
    op.drop_index("ix_reminder_user_id", table_name="reminder")
    op.drop_index("ix_reminder_caregiver_id", table_name="reminder")
