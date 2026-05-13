"""rename medication.times to moments

Revision ID: 009
Revises: 008
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('medication', 'times', new_column_name='moments')


def downgrade() -> None:
    op.alter_column('medication', 'moments', new_column_name='times')
