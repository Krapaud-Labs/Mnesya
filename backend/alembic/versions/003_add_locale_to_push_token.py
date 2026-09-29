"""Add locale column to push_token table

Revision ID: 003
Revises: 121727de92d3
Create Date: 2026-02-28 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: str | None = '121727de92d3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('push_token', sa.Column('locale', sa.String(length=5), nullable=True, server_default='fr'))


def downgrade() -> None:
    op.drop_column('push_token', 'locale')
