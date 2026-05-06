"""Add recurrence fields to reminder table

Revision ID: 006
Revises: 005
Create Date: 2026-05-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reminder', sa.Column(
        'is_recurring', sa.Boolean(), nullable=False, server_default='false'
    ))
    op.add_column('reminder', sa.Column('recurrence_type', sa.String(10), nullable=True))
    op.add_column('reminder', sa.Column(
        'recurrence_days', postgresql.ARRAY(sa.Integer()), nullable=True
    ))
    op.add_column('reminder', sa.Column('recurrence_end_date', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('reminder', 'recurrence_end_date')
    op.drop_column('reminder', 'recurrence_days')
    op.drop_column('reminder', 'recurrence_type')
    op.drop_column('reminder', 'is_recurring')
