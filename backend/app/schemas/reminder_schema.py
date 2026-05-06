"""Reminder Schema module.

This module defines Pydantic schemas for Reminder entity validation and
serialization.
"""

import re
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime, timezone, date
from uuid import UUID
from typing import List, Optional

_HTML_RE = re.compile(r"[<>\"'&]")


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder.

    Validates input data when creating a reminder via API.

    Attributes:
        title (str): Brief description (1-200 chars)
        description (Optional[str]): Detailed description (optional)
        scheduled_at (datetime): When the reminder should trigger
        caregiver_id (UUID): ID of caregiver creating the reminder
        user_id (UUID): ID of user this reminder is for
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    scheduled_at: datetime
    user_id: UUID
    is_recurring: bool = False
    recurrence_type: Optional[str] = None
    recurrence_days: Optional[List[int]] = None
    recurrence_end_date: Optional[date] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 200:
            raise ValueError("Title is required and must be <= 200 chars")
        if _HTML_RE.search(value):
            raise ValueError("Title must not contain HTML characters")
        return value

    @field_validator('description')
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if len(value) > 2000:
            raise ValueError("Description must be <= 2000 chars")
        if _HTML_RE.search(value):
            raise ValueError("Description must not contain HTML characters")
        return value

    @field_validator('recurrence_type')
    @classmethod
    def validate_recurrence_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ("DAILY", "WEEKLY", "MONTHLY"):
            raise ValueError("recurrence_type must be DAILY, WEEKLY or MONTHLY")
        return value

    @field_validator('recurrence_days')
    @classmethod
    def validate_recurrence_days(cls, value: Optional[List[int]]) -> Optional[List[int]]:
        if value is not None:
            if not value:
                raise ValueError("recurrence_days must not be empty")
            if not all(isinstance(d, int) and 0 <= d <= 6 for d in value):
                raise ValueError("recurrence_days must be integers between 0 (Mon) and 6 (Sun)")
        return value

    @model_validator(mode='after')
    def validate_recurrence_consistency(self) -> 'ReminderCreate':
        if self.is_recurring:
            if not self.recurrence_type:
                raise ValueError("recurrence_type is required when is_recurring is true")
            if self.recurrence_type == "WEEKLY" and not self.recurrence_days:
                raise ValueError("recurrence_days is required for WEEKLY recurrence")
        else:
            self.recurrence_type = None
            self.recurrence_days = None
            self.recurrence_end_date = None
        return self

    @field_validator('scheduled_at')
    @classmethod
    def validate_scheduled_at(cls, value: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value <= now:
            raise ValueError("scheduled_at must be in the future")
        max_future = now.replace(year=now.year + 2)
        if value > max_future:
            raise ValueError("scheduled_at must be within the next 2 years")
        return value


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder.

    All fields are optional for partial updates.

    Attributes:
        title (Optional[str]): Updated title (1-200 chars)
        description (Optional[str]): Updated description
        scheduled_at (Optional[datetime]): Updated scheduled time
        caregiver_id (Optional[UUID]): Updated caregiver ID
        user_id (Optional[UUID]): Updated user ID
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    scheduled_at: Optional[datetime] = None
    caregiver_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[str] = None
    recurrence_days: Optional[List[int]] = None
    recurrence_end_date: Optional[date] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if len(value) == 0 or len(value) > 200:
            raise ValueError("Title must be <= 200 chars and not empty")
        if _HTML_RE.search(value):
            raise ValueError("Title must not contain HTML characters")
        return value

    @field_validator('description')
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if len(value) > 2000:
            raise ValueError("Description must be <= 2000 chars")
        if _HTML_RE.search(value):
            raise ValueError("Description must not contain HTML characters")
        return value


class ReminderResponse(BaseModel):
    """Schema for reminder API responses.

    Used when returning reminder data from API endpoints.

    Attributes:
        id (UUID): Reminder's unique identifier
        title (str): Reminder title
        description (Optional[str]): Detailed description (may be None)
        scheduled_at (datetime): Scheduled trigger time
        caregiver_id (UUID): ID of caregiver who created it
        user_id (UUID): ID of user it's for
        user_first_name (Optional[str]): First name of the user
            this reminder is for
        user_last_name (Optional[str]): Last name of the user
            this reminder is for
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    id: UUID
    title: str
    description: Optional[str]
    scheduled_at: datetime
    caregiver_id: UUID
    user_id: UUID
    user_first_name: Optional[str] = None
    user_last_name: Optional[str] = None
    current_status: Optional[str] = None
    is_recurring: bool = False
    recurrence_type: Optional[str] = None
    recurrence_days: Optional[List[int]] = None
    recurrence_end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    # Enables ORM model conversion
    model_config = ConfigDict(from_attributes=True)


class ReminderListResponse(BaseModel):
    """Schema for paginated reminder list responses.

    Attributes:
        reminders (List[ReminderResponse]): List of reminder objects
        total (int): Total count of reminders
    """
    reminders: List[ReminderResponse]
    total: int
