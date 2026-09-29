"""Reminder Schema module.

This module defines Pydantic schemas for Reminder entity validation and
serialization.
"""

import re
from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    description: str | None = Field(None, max_length=2000)
    scheduled_at: datetime
    user_id: UUID

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
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if len(value) > 2000:
            raise ValueError("Description must be <= 2000 chars")
        if _HTML_RE.search(value):
            raise ValueError("Description must not contain HTML characters")
        return value

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
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    scheduled_at: datetime | None = None
    caregiver_id: UUID | None = None
    user_id: UUID | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
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
    def validate_description(cls, value: str | None) -> str | None:
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
    description: str | None
    scheduled_at: datetime
    caregiver_id: UUID
    user_id: UUID
    user_first_name: str | None = None
    user_last_name: str | None = None
    current_status: str | None = None
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
    reminders: list[ReminderResponse]
    total: int
