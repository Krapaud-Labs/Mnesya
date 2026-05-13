"""Add escalation_log table

Revision ID: 008
Revises: 007
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    insp = inspect(conn)
    existing_tables = insp.get_table_names()

    if 'escalation_log' not in existing_tables:
        op.create_table(
            'escalation_log',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('caregiver_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('caregiver.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
            sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('reminder_count', sa.Integer, nullable=False, default=1),
        )

    existing_indexes = {idx['name'] for idx in insp.get_indexes('escalation_log')} \
        if 'escalation_log' in insp.get_table_names() else set()

    if 'ix_escalation_log_caregiver_user' not in existing_indexes:
        op.create_index(
            'ix_escalation_log_caregiver_user',
            'escalation_log',
            ['caregiver_id', 'user_id']
        )


def downgrade():
    op.drop_table('escalation_log')
