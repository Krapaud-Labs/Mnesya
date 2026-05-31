"""Reminder Facade module.

This module implements the Facade pattern for Reminder business logic.
It provides a simplified interface for reminder operations.
"""

import calendar
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.reminder import ReminderModel
from app.models.reminder_status import ReminderStatusModel
from app.models.reminder_status_enum import ReminderStatusEnum
from app.persistence.reminder_repository import ReminderRepository
from app.persistence.reminder_status_repository import ReminderStatusRepository
from uuid import UUID


def _add_one_month(dt: datetime) -> datetime:
    month = dt.month + 1
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def calculate_next_occurrence(reminder: ReminderModel) -> Optional[datetime]:
    """Return the next scheduled_at for a recurring reminder, or None if exhausted."""
    if not reminder.is_recurring or not reminder.recurrence_type:
        return None

    current = reminder.scheduled_at
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if reminder.recurrence_type == "DAILY":
        next_dt = current + timedelta(days=1)
        while next_dt <= now:
            next_dt += timedelta(days=1)

    elif reminder.recurrence_type == "WEEKLY":
        days = sorted(reminder.recurrence_days or [])
        if not days:
            return None
        current_weekday = current.weekday()
        next_dt = None
        for day in days:
            diff = (day - current_weekday) % 7 or 7
            candidate = current + timedelta(days=diff)
            if next_dt is None or candidate < next_dt:
                next_dt = candidate
        while next_dt <= now:
            next_weekday = next_dt.weekday()
            min_diff = min(((d - next_weekday) % 7 or 7) for d in days)
            next_dt += timedelta(days=min_diff)

    elif reminder.recurrence_type == "MONTHLY":
        next_dt = _add_one_month(current)
        while next_dt <= now:
            next_dt = _add_one_month(next_dt)

    else:
        return None

    if reminder.recurrence_end_date and next_dt.date() > reminder.recurrence_end_date:
        return None

    return next_dt


def schedule_next_occurrence(reminder: ReminderModel, db: Session) -> bool:
    """Update scheduled_at to next occurrence and create a PENDING status.

    Returns True if a next occurrence was scheduled, False if recurrence is exhausted.
    """
    next_dt = calculate_next_occurrence(reminder)
    if next_dt is None:
        return False

    reminder.scheduled_at = next_dt
    db.add(reminder)

    pending = ReminderStatusModel()
    pending.status = "PENDING"
    pending.reminder_id = reminder.id
    db.add(pending)
    db.commit()
    return True


class ReminderFacade:
    """Facade for Reminder business logic operations.

    This class implements the Facade pattern to provide a clean interface
    for reminder-related operations. It handles business logic and coordinates
    between the model and repository layers.

    Attributes:
        reminder_repo (ReminderRepository): Repository for reminder data access
        reminder_status_repo (ReminderStatusRepository): Repository for
            status data access
    """

    def __init__(self, db: Session):
        """Initialize the facade with reminder and status repositories."""
        self.reminder_repo = ReminderRepository(db)
        self.reminder_status_repo = ReminderStatusRepository(db)

    # ==================== REMINDER BUSINESS LOGIC ====================

    def create_reminder(self, reminder_data: dict) -> object:
        """Create a new reminder with an initial PENDING status.

        Business logic for reminder creation. Validates data through the
        model's property setters, persists to the database, and automatically
        creates a PENDING status entry.

        Args:
            reminder_data (dict): Dictionary containing reminder fields
                (title, description, scheduled_at, caregiver_id, user_id)

        Returns:
            ReminderModel: The created reminder with generated ID and
                timestamps

        Raises:
            ValueError: If validation fails (from model setters)
            Exception: If database operation fails
        """
        # Create the reminder
        reminder = ReminderModel(**reminder_data)
        self.reminder_repo.add(reminder)

        # Automatically create initial PENDING status
        initial_status = ReminderStatusModel()
        initial_status.status = ReminderStatusEnum.PENDING.value
        initial_status.reminder_id = reminder.id
        self.reminder_status_repo.add(initial_status)

        return reminder

    def get_reminder(self, reminder_id: str) -> object:
        """Retrieve a reminder by ID.

        Args:
            reminder_id (str): The reminder's unique identifier

        Returns:
            ReminderModel: The reminder if found, None otherwise
        """
        return self.reminder_repo.get(UUID(reminder_id))

    def get_all_reminders(self) -> list:
        """Retrieve all reminders.

        Returns:
            list[ReminderModel]: List of all reminders in the system

        Warning:
            Use with caution on large datasets - consider pagination
            or use specific query methods (by_caregiver, by_user)
        """
        return self.reminder_repo.get_all()

    def get_reminder_by_caregiver(self, caregiver_id: UUID) -> list:
        return self.reminder_repo.get_reminders_by_caregiver(caregiver_id)

    def get_reminder_by_user(self, user_id: UUID) -> list:
        return self.reminder_repo.get_reminders_by_user(user_id)

    def update_reminder(self, reminder_id: str, reminder_data: dict) -> object:
        """Update an existing reminder.

        Business logic for reminder updates. Only updates provided fields.

        Args:
            reminder_id (str): The reminder's unique identifier
            reminder_data (dict): Dictionary of fields to update

        Returns:
            ReminderModel: The updated reminder if found, None otherwise

        Raises:
            ValueError: If validation fails (from model setters)
            Exception: If database operation fails
        """
        self.reminder_repo.update(UUID(reminder_id), reminder_data)
        return self.reminder_repo.get(UUID(reminder_id))

    def postpone_reminder(self, reminder_id: str, delay_minutes: int = 5) -> object:
        """Postpone a reminder by a given number of minutes.

        Updates the reminder's scheduled_at to now + delay_minutes
        and creates a POSTPONED status entry.

        Args:
            reminder_id (str): The reminder's unique identifier
            delay_minutes (int): Number of minutes to postpone. Defaults to 5.

        Returns:
            ReminderModel: The updated reminder, or None if not found
        """
        from datetime import datetime, timedelta, timezone

        reminder = self.reminder_repo.get(UUID(reminder_id))
        if not reminder:
            return None

        new_scheduled_at = (
            datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
        ).replace(second=0, microsecond=0)
        self.reminder_repo.update(UUID(reminder_id), {"scheduled_at": new_scheduled_at})

        postponed_status = ReminderStatusModel()
        postponed_status.status = ReminderStatusEnum.POSTPONED.value
        postponed_status.reminder_id = reminder.id
        self.reminder_status_repo.add(postponed_status)

        return self.reminder_repo.get(UUID(reminder_id))

    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder and its associated statuses.

        Args:
            reminder_id (str): The reminder's unique identifier

        Returns:
            bool: True if reminder was found and deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        reminder = self.reminder_repo.get(UUID(reminder_id))
        if reminder:
            # Delete associated statuses first to avoid FK constraint violation
            statuses = self.reminder_status_repo.get_statuses_by_reminder(reminder.id)
            for status in statuses:
                self.reminder_status_repo.delete(status.id)
            self.reminder_repo.delete(UUID(reminder_id))
            return True
        return False
