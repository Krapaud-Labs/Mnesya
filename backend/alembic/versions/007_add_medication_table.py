"""Add medication table and medication_id to reminder

Revision ID: 007
Revises: 006
Create Date: 2026-05-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    insp = inspect(conn)
    existing_tables = insp.get_table_names()

    if 'medication' not in existing_tables:
        op.create_table(
            'medication',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('caregiver_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('caregiver.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True),
                      sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('dosage', sa.String(200), nullable=True),
            sa.Column('times', postgresql.ARRAY(sa.String(5)), nullable=False),
            sa.Column('frequency', sa.String(10), nullable=False),
            sa.Column('recurrence_days', postgresql.ARRAY(sa.Integer()), nullable=True),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        )

    existing_indexes = {idx['name'] for idx in insp.get_indexes('medication')} \
        if 'medication' in existing_tables else set()

    if 'ix_medication_user_id' not in existing_indexes:
        op.create_index('ix_medication_user_id', 'medication', ['user_id'])
    if 'ix_medication_caregiver_id' not in existing_indexes:
        op.create_index('ix_medication_caregiver_id', 'medication', ['caregiver_id'])

    reminder_cols = {col['name'] for col in insp.get_columns('reminder')}
    if 'medication_id' not in reminder_cols:
        op.add_column('reminder', sa.Column(
            'medication_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('medication.id', ondelete='SET NULL'),
            nullable=True,
        ))


def downgrade():
    op.drop_column('reminder', 'medication_id')
    op.drop_index('ix_medication_caregiver_id', 'medication')
    op.drop_index('ix_medication_user_id', 'medication')
    op.drop_table('medication')
