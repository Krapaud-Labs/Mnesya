"""Caregiver Schema module.

This module defines Pydantic schemas for Caregiver entity validation
and serialization.
Includes comprehensive password validation for security.
"""

import re
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from uuid import UUID
from typing import List, Optional
import validators

_NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' \-]+$")


class CaregiverCreate(BaseModel):
    """Schema for creating a new caregiver.

    Validates input data when registering a caregiver via API.

    Attributes:
        first_name (str): Caregiver's first name (1-100 chars)
        last_name (str): Caregiver's last name (1-100 chars)
        email (str): Valid email address (5-255 chars)
        password (str): Strong password (8-255 chars,
            must meet security requirements)
    """
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 100:
            raise ValueError("Name is required and must be <= 100 chars")
        if not _NAME_RE.match(value):
            raise ValueError("Name must contain only letters, spaces, hyphens, or apostrophes")
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate email format.

        Args:
            value (str): The email to validate

        Returns:
            str: Trimmed email

        Raises:
            ValueError: If email format is invalid
        """
        value = value.strip()
        if not validators.email(value):
            raise ValueError("email is required and a valid email")
        return value

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validate password meets security requirements.

        Password must contain:
        - 8-20 characters in length
        - At least one digit (0-9)
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one special character ($@#%*!~&)

        Args:
            value (str): The password to validate

        Returns:
            str: Trimmed password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        value = value.strip()
        SpecialSym = ['$', '@', '#', '%', '*', '!', '~', '&']

        # Length validation
        if len(value) < 8 or len(value) > 72:
            raise ValueError('Password does not meet requirements')

        # Check for required character types
        has_digit = has_upper = has_lower = has_sym = False

        for char in value:
            if 48 <= ord(char) <= 57:  # Digits 0-9
                has_digit = True
            elif 65 <= ord(char) <= 90:  # Uppercase A-Z
                has_upper = True
            elif 97 <= ord(char) <= 122:  # Lowercase a-z
                has_lower = True
            elif char in SpecialSym:
                has_sym = True

        # Validate all requirements
        if not has_digit:
            raise ValueError('Password should have at least one numeral')
        if not has_upper:
            raise ValueError(
                'Password should have at least one uppercase letter')
        if not has_lower:
            raise ValueError(
                'Password should have at least one lowercase letter')
        if not has_sym:
            raise ValueError(
                'Password should have at least one of the symbols $@#%*!~&')
        return value


class CaregiverUpdate(BaseModel):
    """Schema for updating an existing caregiver.

    All fields are optional for partial updates.

    Attributes:
        first_name (Optional[str]): Updated first name (1-100 chars)
        last_name (Optional[str]): Updated last name (1-100 chars)
        email (Optional[str]): Updated email address
        password (Optional[str]): Updated password
            (must meet security requirements)
        current_password (Optional[str]): Current password, required
            when updating the password
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=255)
    current_password: Optional[str] = Field(None, min_length=8, max_length=255)

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if len(value) == 0 or len(value) > 100:
            raise ValueError("Name must be <= 100 chars and not empty")
        if not _NAME_RE.match(value):
            raise ValueError("Name must contain only letters, spaces, hyphens, or apostrophes")
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        """Validate email format if provided.

        Args:
            value (Optional[str]): The email to validate

        Returns:
            Optional[str]: Trimmed email or None

        Raises:
            ValueError: If email format is invalid
        """
        if value is not None and not validators.email(value):
            raise ValueError("Must be a valid email")
        return value.strip() if value else None

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        """Validate password meets security requirements if provided.

        Args:
            value (Optional[str]): The password to validate

        Returns:
            Optional[str]: Trimmed password or None

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if value is None:
            return None

        SpecialSym = ['$', '@', '#', '%', '*', '!', '~', '&']

        # Length validation
        if len(value) < 8 or len(value) > 72:
            raise ValueError('Password does not meet requirements')

        # Check for required character types
        has_digit = has_upper = has_lower = has_sym = False

        for char in value:
            if 48 <= ord(char) <= 57:
                has_digit = True
            elif 65 <= ord(char) <= 90:
                has_upper = True
            elif 97 <= ord(char) <= 122:
                has_lower = True
            elif char in SpecialSym:
                has_sym = True

        # Validate all requirements
        if not has_digit:
            raise ValueError('Password should have at least one numeral')
        if not has_upper:
            raise ValueError(
                'Password should have at least one uppercase letter')
        if not has_lower:
            raise ValueError(
                'Password should have at least one lowercase letter')
        if not has_sym:
            raise ValueError(
                'Password should have at least one of the symbols $@#%*!~&')
        return value.strip()


class CaregiverResponse(BaseModel):
    """Schema for caregiver API responses.

    Used when returning caregiver data from API endpoints.
    Does not include sensitive data like password hash.

    Attributes:
        id (UUID): Caregiver's unique identifier
        first_name (str): Caregiver's first name
        last_name (str): Caregiver's last name
        email (str): Caregiver's email address
        created_at (datetime): Creation timestamp
    """
    id: UUID
    first_name: str
    last_name: str
    email: str
    created_at: datetime

    # Enables ORM model conversion
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for paginated caregiver list responses.

    Attributes:
        caregivers (List[CaregiverResponse]): List of caregiver objects
        total (int): Total count of caregivers
    """
    caregivers: List[CaregiverResponse]
    total: int
