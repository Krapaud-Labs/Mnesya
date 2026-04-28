"""User Schema module.

This module defines Pydantic schemas for User entity validation and serialization.
Schemas are used for API request/response validation and data transformation.
"""

import re
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from uuid import UUID
from typing import List, Optional
from app.schemas.pairing_code_schema import PairingCodeResponse

_NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' \-]+$")


class UserCreate(BaseModel):
    """Schema for creating a new user.

    Validates input data when creating a user via API.

    Attributes:
        first_name (str): User's first name (1-100 chars)
        last_name (str): User's last name (1-100 chars)
        birthday (date): User's date of birth
    """
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    birthday: date

    @field_validator('first_name', 'last_name')
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 100:
            raise ValueError("Name is required and must be <= 100 chars")
        if not _NAME_RE.match(value):
            raise ValueError("Name must contain only letters, spaces, hyphens, or apostrophes")
        return value


class UserUpdate(BaseModel):
    """Schema for updating an existing user.

    All fields are optional for partial updates.

    Attributes:
        first_name (Optional[str]): Updated first name (1-100 chars)
        last_name (Optional[str]): Updated last name (1-100 chars)
        birthday (Optional[date]): Updated date of birth
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birthday: Optional[date] = None

    @field_validator('first_name', 'last_name')
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if len(value) == 0 or len(value) > 100:
            raise ValueError("Name must be <= 100 chars and not empty")
        if not _NAME_RE.match(value):
            raise ValueError("Name must contain only letters, spaces, hyphens, or apostrophes")
        return value


class UserResponse(BaseModel):
    """Schema for user API responses.

    Used when returning user data from API endpoints.

    Attributes:
        id (UUID): User's unique identifier
        first_name (str): User's first name
        last_name (str): User's last name
        birthday (date): User's date of birth
        caregiver_ids (List[UUID]): List of associated caregiver IDs
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    id: UUID
    first_name: str
    last_name: str
    birthday: date
    caregiver_ids: List[UUID]
    created_at: datetime
    updated_at: datetime

    # Enables ORM model conversion
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for paginated user list responses.

    Attributes:
        users (List[UserResponse]): List of user objects
        total (int): Total count of users
    """
    users: List[UserResponse]
    total: int


class UserWithPairingCodeResponse(BaseModel):
    """Schema for user creation response with pairing code.

    Returned when creating a new user, includes both user data
    and the generated pairing code for app pairing.

    Attributes:
        user (UserResponse): Created user data
        pairing_code (PairingCodeResponse): Generated pairing code
    """
    user: UserResponse
    pairing_code: PairingCodeResponse
