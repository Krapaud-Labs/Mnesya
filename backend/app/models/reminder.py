"""Reminder model module.

This module defines the Reminder entity for scheduled care-related tasks.
Reminders are created by caregivers for users and track scheduled activities.
"""

import uuid
from datetime import datetime, timezone, date
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app import database


class ReminderModel(database):
    """Reminder model representing a scheduled care task or event.

    This model stores reminder information including what needs to be done,
    when it should occur, and who is involved.

    Attributes:
        id (UUID): Unique identifier for the reminder
        title (str): Brief description of the reminder (max 200 chars)
        description (str): Detailed description (optional, unlimited length)
        scheduled_at (datetime): When the reminder should trigger
        caregiver_id (UUID): ID of the caregiver who created the reminder
        user_id (UUID): ID of the user this reminder is for
        created_at (datetime): Timestamp of reminder creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = 'reminder'
    _id: uuid.UUID = Column(
        'id',
        UUID(
            as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)
    _title: str = Column('title', String(200), nullable=False)
    _description: str | None = Column('description', Text, nullable=True)
    _scheduled_at: datetime = Column(
        'scheduled_at', DateTime(
            timezone=True), nullable=False)
    _caregiver_id: uuid.UUID = Column(
        'caregiver_id',
        UUID(
            as_uuid=True),
        ForeignKey('caregiver.id'))
    _user_id: uuid.UUID = Column('user_id', UUID(as_uuid=True), ForeignKey('user.id'))
    _is_recurring: bool = Column('is_recurring', Boolean(), nullable=False, default=False)
    _recurrence_type: Optional[str] = Column('recurrence_type', String(10), nullable=True)
    _recurrence_days: Optional[List[int]] = Column(
        'recurrence_days', ARRAY(Integer()), nullable=True
    )
    _recurrence_end_date: Optional[date] = Column('recurrence_end_date', Date(), nullable=True)
    _medication_id: Optional[uuid.UUID] = Column(
        'medication_id', UUID(as_uuid=True),
        ForeignKey('medication.id', ondelete='SET NULL'), nullable=True
    )
    _created_at: datetime = Column(
        DateTime(
            timezone=True), default=lambda: datetime.now(
            timezone.utc), nullable=False)
    _updated_at: datetime = Column(
        DateTime(
            timezone=True), default=lambda: datetime.now(
            timezone.utc), onupdate=lambda: datetime.now(
                timezone.utc), nullable=False)

    # ==================== Getter Setter ====================

    @property
    def id(self) -> uuid.UUID:
        """Get the reminder's unique identifier.

        Returns:
            UUID: The reminder's ID
        """
        return self._id

    @property
    def title(self) -> str:
        """Get the reminder's title.

        Returns:
            str: The reminder's title
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set the reminder's title with validation.

        Args:
            value (str): The title to set

        Raises:
            ValueError: If title is empty, only whitespace, or exceeds 200 characters
        """
        if (not value or len(value) > 200 or len(value.strip()) == 0):
            raise ValueError("Title is required and must be <= 200 chars")
        self._title = value.strip()

    @property
    def description(self) -> str:
        """Get the reminder's detailed description.

        Returns:
            str: The reminder's description (may be None)
        """
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Set the reminder's description.

        Args:
            value (str): The description to set (optional)
        """
        self._description = value

    @property
    def scheduled_at(self) -> datetime:
        """Get the reminder's scheduled datetime.

        Returns:
            datetime: When this reminder is scheduled to trigger
        """
        return self._scheduled_at

    @scheduled_at.setter
    def scheduled_at(self, value: datetime) -> None:
        """Set the reminder's scheduled datetime with validation.

        Args:
            value (datetime or str): Datetime object or ISO format string

        Raises:
            ValueError: If format is invalid or value is not a datetime

        Note:
            Accepts ISO 8601 format strings, including 'Z' suffix for UTC
        """
        # Convert ISO string to datetime if needed
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(
                    "scheduled_at must be a valid ISO datetime format")

        # Validate type
        if not isinstance(value, datetime):
            raise ValueError(
                "scheduled_at must be a datetime object or ISO string")

        self._scheduled_at = value

    @property
    def caregiver_id(self) -> uuid.UUID:
        """Get the ID of the caregiver who created this reminder.

        Returns:
            UUID: The caregiver's ID
        """
        return self._caregiver_id

    @caregiver_id.setter
    def caregiver_id(self, value: uuid.UUID) -> None:
        """Set the caregiver ID.

        Args:
            value (UUID): The caregiver's unique identifier
        """
        self._caregiver_id = value

    @property
    def user_id(self) -> uuid.UUID:
        """Get the ID of the user this reminder is for.

        Returns:
            UUID: The user's ID
        """
        return self._user_id

    @user_id.setter
    def user_id(self, value: uuid.UUID) -> None:
        """Set the user ID.

        Args:
            value (UUID): The user's unique identifier
        """
        self._user_id = value

    @property
    def is_recurring(self) -> bool:
        return self._is_recurring or False

    @is_recurring.setter
    def is_recurring(self, value: bool) -> None:
        self._is_recurring = bool(value)

    @property
    def recurrence_type(self) -> Optional[str]:
        return self._recurrence_type

    @recurrence_type.setter
    def recurrence_type(self, value: Optional[str]) -> None:
        if value is not None and value not in ("DAILY", "WEEKLY", "MONTHLY"):
            raise ValueError("recurrence_type must be DAILY, WEEKLY or MONTHLY")
        self._recurrence_type = value

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
    def recurrence_end_date(self) -> Optional[date]:
        return self._recurrence_end_date

    @recurrence_end_date.setter
    def recurrence_end_date(self, value: Optional[date]) -> None:
        self._recurrence_end_date = value

    @property
    def medication_id(self) -> Optional[uuid.UUID]:
        return self._medication_id

    @medication_id.setter
    def medication_id(self, value: Optional[uuid.UUID]) -> None:
        self._medication_id = value

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp.

        Returns:
            datetime: When this reminder was created
        """
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get the last update timestamp.

        Returns:
            datetime: When this reminder was last updated
        """
        return self._updated_at
