"""Escalation Log model module."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from app import database


class EscalationLogModel(database):
    """Tracks caregiver escalation notifications to enforce cooldown and batching."""

    __tablename__ = 'escalation_log'

    _id = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _caregiver_id = Column(
        'caregiver_id', UUID(as_uuid=True),
        ForeignKey('caregiver.id', ondelete='CASCADE'), nullable=False
    )
    _user_id = Column(
        'user_id', UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    _sent_at = Column(
        'sent_at', DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    _reminder_count = Column('reminder_count', Integer, nullable=False, default=1)

    @property
    def id(self):
        return self._id

    @property
    def caregiver_id(self):
        return self._caregiver_id

    @caregiver_id.setter
    def caregiver_id(self, value):
        self._caregiver_id = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def sent_at(self):
        return self._sent_at

    @property
    def reminder_count(self):
        return self._reminder_count

    @reminder_count.setter
    def reminder_count(self, value):
        self._reminder_count = value
