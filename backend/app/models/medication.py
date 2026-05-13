import uuid
from datetime import datetime, timezone, date
from typing import Any, List, Optional
from sqlalchemy import String, DateTime, Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app import database


class MedicationModel(database):
    __tablename__ = 'medication'

    _id: Mapped[uuid.UUID] = mapped_column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _caregiver_id: Mapped[uuid.UUID] = mapped_column(
        'caregiver_id', UUID(as_uuid=True), ForeignKey('caregiver.id', ondelete='CASCADE')
    )
    _user_id: Mapped[uuid.UUID] = mapped_column(
        'user_id', UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE')
    )
    _name: Mapped[str] = mapped_column('name', String(200))
    _dosage: Mapped[Optional[str]] = mapped_column('dosage', String(200), nullable=True)
    _moments: Mapped[Any] = mapped_column('moments', ARRAY(String(20)))
    _frequency: Mapped[str] = mapped_column('frequency', String(10))
    _recurrence_days: Mapped[Any] = mapped_column('recurrence_days', ARRAY(Integer()), nullable=True)
    _start_date: Mapped[date] = mapped_column('start_date', Date())
    _end_date: Mapped[Optional[date]] = mapped_column('end_date', Date(), nullable=True)
    _created_at: Mapped[datetime] = mapped_column(
        'created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    _updated_at: Mapped[datetime] = mapped_column(
        'updated_at',
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
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

    VALID_MOMENTS = {
        "BEFORE_BREAKFAST", "AFTER_BREAKFAST",
        "BEFORE_LUNCH", "AFTER_LUNCH",
        "BEFORE_DINNER", "AFTER_DINNER",
        "BEDTIME",
    }

    @property
    def moments(self) -> List[str]:
        return self._moments

    @moments.setter
    def moments(self, value: List[str]) -> None:
        if not value:
            raise ValueError("moments must not be empty")
        for m in value:
            if m not in self.VALID_MOMENTS:
                raise ValueError(f"Invalid moment: {m}. Must be one of {self.VALID_MOMENTS}")
        self._moments = value

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
