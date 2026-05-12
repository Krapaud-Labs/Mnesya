import re
import uuid
from datetime import datetime, timezone, date
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app import database


class MedicationModel(database):
    __tablename__ = 'medication'

    _id: uuid.UUID = Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _caregiver_id: uuid.UUID = Column(
        'caregiver_id', UUID(as_uuid=True), ForeignKey('caregiver.id', ondelete='CASCADE'), nullable=False
    )
    _user_id: uuid.UUID = Column(
        'user_id', UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    _name: str = Column('name', String(200), nullable=False)
    _dosage: Optional[str] = Column('dosage', String(200), nullable=True)
    _times: List[str] = Column('times', ARRAY(String(5)), nullable=False)
    _frequency: str = Column('frequency', String(10), nullable=False)
    _recurrence_days: Optional[List[int]] = Column('recurrence_days', ARRAY(Integer()), nullable=True)
    _start_date: date = Column('start_date', Date(), nullable=False)
    _end_date: Optional[date] = Column('end_date', Date(), nullable=True)
    _created_at: datetime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    _updated_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ==================== Properties ====================

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def caregiver_id(self) -> uuid.UUID:
        return self._caregiver_id

    @caregiver_id.setter
    def caregiver_id(self, value: uuid.UUID) -> None:
        self._caregiver_id = value

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @user_id.setter
    def user_id(self, value: uuid.UUID) -> None:
        self._user_id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        value = value.strip()
        if not value or len(value) > 200:
            raise ValueError("name is required and must be <= 200 chars")
        self._name = value

    @property
    def dosage(self) -> Optional[str]:
        return self._dosage

    @dosage.setter
    def dosage(self, value: Optional[str]) -> None:
        if value is not None:
            value = value.strip()
            if len(value) > 200:
                raise ValueError("dosage must be <= 200 chars")
        self._dosage = value

    @property
    def times(self) -> List[str]:
        return self._times

    @times.setter
    def times(self, value: List[str]) -> None:
        if not value:
            raise ValueError("times must not be empty")
        for t in value:
            if not re.match(r'^\d{2}:\d{2}$', t):
                raise ValueError(f"Invalid time format: {t}. Expected HH:MM")
        self._times = value

    @property
    def frequency(self) -> str:
        return self._frequency

    @frequency.setter
    def frequency(self, value: str) -> None:
        if value not in ("DAILY", "WEEKLY"):
            raise ValueError("frequency must be DAILY or WEEKLY")
        self._frequency = value

    @property
    def recurrence_days(self) -> Optional[List[int]]:
        return self._recurrence_days

    @recurrence_days.setter
    def recurrence_days(self, value: Optional[List[int]]) -> None:
        if value is not None:
            if not all(isinstance(d, int) and 0 <= d <= 6 for d in value):
                raise ValueError("recurrence_days must be integers between 0 (Mon) and 6 (Sun)")
        self._recurrence_days = value

    @property
    def start_date(self) -> date:
        return self._start_date

    @start_date.setter
    def start_date(self, value: date) -> None:
        self._start_date = value

    @property
    def end_date(self) -> Optional[date]:
        return self._end_date

    @end_date.setter
    def end_date(self, value: Optional[date]) -> None:
        self._end_date = value

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at
