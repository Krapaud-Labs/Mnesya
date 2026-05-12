"""Add medication table and medication_id to reminder

Revision ID: 007
Revises: 006
Create Date: 2026-05-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
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
    op.create_index('ix_medication_user_id', 'medication', ['user_id'])
    op.create_index('ix_medication_caregiver_id', 'medication', ['caregiver_id'])

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
