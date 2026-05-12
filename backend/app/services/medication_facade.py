from datetime import datetime, timezone, timedelta, time as dt_time, date
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.medication import MedicationModel
from app.models.reminder import ReminderModel
from app.models.reminder_status import ReminderStatusModel
from app.models.reminder_status_enum import ReminderStatusEnum
from app.persistence.medication_repository import MedicationRepository
from app.persistence.reminder_repository import ReminderRepository
from app.persistence.reminder_status_repository import ReminderStatusRepository
from app.schemas.medication_schema import WeekResponse, WeekDayResponse, WeekEntryResponse


def _first_occurrence(start_date: date, time_str: str, frequency: str,
                      recurrence_days: Optional[List[int]]) -> datetime:
    """Compute the first scheduled_at for a medication occurrence on or after today."""
    hour, minute = map(int, time_str.split(':'))
    now = datetime.now(timezone.utc)

    candidate = datetime.combine(start_date, dt_time(hour, minute)).replace(tzinfo=timezone.utc)

    if frequency == "DAILY":
        while candidate <= now:
            candidate += timedelta(days=1)
        return candidate

    # WEEKLY: advance until we land on a valid weekday
    days = sorted(recurrence_days or [])
    if not days:
        return candidate
    while candidate <= now or candidate.weekday() not in days:
        candidate += timedelta(days=1)
    return candidate


def _is_scheduled_on(medication: MedicationModel, target_date: date) -> bool:
    """Return True if the medication is active and scheduled on target_date."""
    if target_date < medication.start_date:
        return False
    if medication.end_date and target_date > medication.end_date:
        return False
    if medication.frequency == "DAILY":
        return True
    if medication.frequency == "WEEKLY":
        days = medication.recurrence_days or []
        return target_date.weekday() in days
    return False


class MedicationFacade:

    def __init__(self, db: Session):
        self.medication_repo = MedicationRepository(db)
        self.reminder_repo = ReminderRepository(db)
        self.reminder_status_repo = ReminderStatusRepository(db)
        self.db = db

    # ==================== CRUD ====================

    def create_medication(self, data: dict, caregiver_id: UUID) -> MedicationModel:
        medication = MedicationModel()
        medication.caregiver_id = caregiver_id
        medication.user_id = data['user_id']
        medication.name = data['name']
        medication.dosage = data.get('dosage')
        medication.times = data['times']
        medication.frequency = data['frequency']
        medication.recurrence_days = data.get('recurrence_days')
        medication.start_date = data['start_date']
        medication.end_date = data.get('end_date')
        self.medication_repo.add(medication)
        self._generate_reminders(medication)
        return medication

    def get_medication(self, medication_id: UUID) -> Optional[MedicationModel]:
        return self.medication_repo.get(medication_id)

    def get_by_user(self, user_id: UUID) -> List[MedicationModel]:
        return self.medication_repo.get_by_user(user_id)

    def get_by_caregiver(self, caregiver_id: UUID) -> List[MedicationModel]:
        return self.medication_repo.get_by_caregiver(caregiver_id)

    def update_medication(self, medication_id: UUID, data: dict) -> Optional[MedicationModel]:
        medication = self.medication_repo.get(medication_id)
        if not medication:
            return None

        schedule_fields = {'times', 'frequency', 'recurrence_days', 'start_date', 'end_date'}
        schedule_changed = bool(schedule_fields & set(data.keys()))

        self.medication_repo.update(medication_id, data)
        medication = self.medication_repo.get(medication_id)
        if not medication:
            return None

        if schedule_changed:
            self._delete_reminders(medication)
            self._generate_reminders(medication)

        return medication

    def delete_medication(self, medication_id: UUID) -> bool:
        medication = self.medication_repo.get(medication_id)
        if not medication:
            return False
        self._delete_reminders(medication)
        self.medication_repo.delete(medication_id)
        return True

    # ==================== SEMAINIER ====================

    def get_week(self, user_id: UUID, week_start: date) -> WeekResponse:
        """Build the 7-day semainier for a user starting from week_start (Monday)."""
        days: List[WeekDayResponse] = []

        for offset in range(7):
            target = week_start + timedelta(days=offset)
            entries: List[WeekEntryResponse] = []

            medications = self.medication_repo.get_active_by_user(user_id, target)
            for med in medications:
                if not _is_scheduled_on(med, target):
                    continue
                reminders = self.medication_repo.get_reminders_for_medication(med.id)
                for reminder in reminders:
                    time_str = reminder.scheduled_at.astimezone(timezone.utc).strftime('%H:%M')
                    status = self._resolve_status(reminder, target)
                    entries.append(WeekEntryResponse(
                        medication_id=med.id,
                        name=med.name,
                        dosage=med.dosage,
                        time=time_str,
                        reminder_id=reminder.id,
                        status=status,
                    ))

            entries.sort(key=lambda e: e.time)
            days.append(WeekDayResponse(date=target.isoformat(), entries=entries))

        return WeekResponse(week_start=week_start.isoformat(), days=days)

    # ==================== PRIVATE ====================

    def _generate_reminders(self, medication: MedicationModel) -> None:
        for time_str in medication.times:
            scheduled_at = _first_occurrence(
                medication.start_date, time_str,
                medication.frequency, medication.recurrence_days
            )
            reminder = ReminderModel()
            reminder.title = medication.name
            reminder.description = medication.dosage
            reminder.scheduled_at = scheduled_at
            reminder.caregiver_id = medication.caregiver_id
            reminder.user_id = medication.user_id
            reminder.is_recurring = True
            reminder.recurrence_type = medication.frequency
            reminder.recurrence_days = medication.recurrence_days
            reminder.recurrence_end_date = medication.end_date
            reminder.medication_id = medication.id
            self.reminder_repo.add(reminder)

            pending = ReminderStatusModel()
            pending.status = ReminderStatusEnum.PENDING.value
            pending.reminder_id = reminder.id
            self.reminder_status_repo.add(pending)

    def _delete_reminders(self, medication: MedicationModel) -> None:
        reminders = self.medication_repo.get_reminders_for_medication(medication.id)
        for reminder in reminders:
            statuses = self.reminder_status_repo.get_statuses_by_reminder(reminder.id)
            for s in statuses:
                self.reminder_status_repo.delete(s.id)
            self.reminder_repo.delete(reminder.id)

    def _resolve_status(self, reminder: ReminderModel, target_date: date) -> Optional[str]:
        """Return the most relevant status for a reminder on a given date."""
        statuses = self.reminder_status_repo.get_statuses_by_reminder(reminder.id)
        if not statuses:
            return None

        # For past days: look for a terminal status created on target_date
        today = datetime.now(timezone.utc).date()
        if target_date < today:
            day_statuses = [
                s for s in statuses
                if s.created_at.astimezone(timezone.utc).date() == target_date
                and s.status != ReminderStatusEnum.PENDING.value
            ]
            if day_statuses:
                day_statuses.sort(key=lambda s: s.created_at, reverse=True)
                return day_statuses[0].status
            return None

        # For today or future: return the latest status
        statuses.sort(key=lambda s: s.created_at, reverse=True)
        return statuses[0].status
