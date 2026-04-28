"""Authentication Schema module.

This module defines Pydantic schemas for authentication operations.
"""

import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import validators

_NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' \-]+$")


class LoginRequest(BaseModel):
    """Schema for user login request.

    Attributes:
        email (str): Caregiver's email address
        password (str): Caregiver's password
    """
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate email format."""
        value = value.strip()
        if not validators.email(value):
            raise ValueError("Invalid email format")
        return value


class RegisterRequest(BaseModel):
    """Schema for caregiver registration.

    Attributes:
        first_name (str): Caregiver's first name
        last_name (str): Caregiver's last name
        email (str): Caregiver's email address
        password (str): Caregiver's password
    """
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        if not _NAME_RE.match(value):
            raise ValueError("Name must contain only letters, spaces, hyphens, or apostrophes")
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate email format."""
        value = value.strip()
        if not validators.email(value):
            raise ValueError("Invalid email format")
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validate password strength."""
        value = value.strip()
        SpecialSym = ['$', '@', '#', '%', '*', '!', '~', '&']

        if len(value) < 8 or len(value) > 72:
            raise ValueError('Password does not meet requirements')

        has_digit = has_upper = has_lower = has_sym = False

        for char in value:
            if char.isdigit():
                has_digit = True
            elif char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif char in SpecialSym:
                has_sym = True

        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        if not has_upper:
            raise ValueError(
                'Password must contain at least one uppercase letter')
        if not has_lower:
            raise ValueError(
                'Password must contain at least one lowercase letter')
        if not has_sym:
            raise ValueError(
                f'Password must contain at least one special character: {
                    ", ".join(SpecialSym)}')

        return value


class TokenResponse(BaseModel):
    """Schema for authentication token response.

    Attributes:
        access_token (str): JWT access token
        token_type (str): Type of token (Bearer)
        expires_in (int): Token expiration time in seconds
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class CaregiverProfile(BaseModel):
    """Schema for caregiver profile response.

    Attributes:
        id (str): Caregiver's unique identifier
        first_name (str): Caregiver's first name
        last_name (str): Caregiver's last name
        email (str): Caregiver's email
        created_at (datetime): Account creation timestamp
    """
    id: str
    first_name: str
    last_name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
