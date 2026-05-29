import re
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import date
from uuid import UUID
from typing import List, Optional

_HTML_RE = re.compile(r"[<>\"'&]")

VALID_MOMENTS = {
    "BEFORE_BREAKFAST", "DURING_BREAKFAST", "AFTER_BREAKFAST",
    "BEFORE_LUNCH", "DURING_LUNCH", "AFTER_LUNCH",
    "BEFORE_DINNER", "DURING_DINNER", "AFTER_DINNER",
    "BEDTIME",
}


class MedicationCreate(BaseModel):
    user_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    dosage: Optional[str] = Field(None, max_length=200)
    moments: List[str] = Field(..., min_length=1)
    frequency: str
    recurrence_days: Optional[List[int]] = None
    start_date: date
    end_date: Optional[date] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 200:
            raise ValueError("name is required and must be <= 200 chars")
        if _HTML_RE.search(value):
            raise ValueError("name must not contain HTML characters")
        return value

    @field_validator('dosage')
    @classmethod
    def validate_dosage(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if _HTML_RE.search(value):
            raise ValueError("dosage must not contain HTML characters")
        return value

    @field_validator('moments')
    @classmethod
    def validate_moments(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("moments must not be empty")
        for m in value:
            if m not in VALID_MOMENTS:
                raise ValueError(f"Invalid moment: {m}")
        return value

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, value: str) -> str:
        if value not in ("DAILY", "WEEKLY"):
            raise ValueError("frequency must be DAILY or WEEKLY")
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
    def validate_consistency(self) -> 'MedicationCreate':
        if self.frequency == "WEEKLY" and not self.recurrence_days:
            raise ValueError("recurrence_days is required for WEEKLY frequency")
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class MedicationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    dosage: Optional[str] = Field(None, max_length=200)
    moments: Optional[List[str]] = None
    frequency: Optional[str] = None
    recurrence_days: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if _HTML_RE.search(value):
            raise ValueError("name must not contain HTML characters")
        return value

    @field_validator('moments')
    @classmethod
    def validate_moments(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        for m in value:
            if m not in VALID_MOMENTS:
                raise ValueError(f"Invalid moment: {m}")
        return value

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ("DAILY", "WEEKLY"):
            raise ValueError("frequency must be DAILY or WEEKLY")
        return value


class MedicationResponse(BaseModel):
    id: UUID
    caregiver_id: UUID
    user_id: UUID
    name: str
    dosage: Optional[str]
    moments: List[str]
    frequency: str
    recurrence_days: Optional[List[int]]
    start_date: date
    end_date: Optional[date]

    model_config = ConfigDict(from_attributes=True)


class WeekEntryResponse(BaseModel):
    medication_id: UUID
    name: str
    dosage: Optional[str]
    moment: str
    reminder_id: Optional[UUID]
    status: Optional[str]


class WeekDayResponse(BaseModel):
    date: str
    entries: List[WeekEntryResponse]


class WeekResponse(BaseModel):
    week_start: str
    days: List[WeekDayResponse]
