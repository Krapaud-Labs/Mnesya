from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.medication import MedicationModel
from app.models.reminder import ReminderModel
from app.persistence.base_repository import BaseRepository
from datetime import date


class MedicationRepository(BaseRepository[MedicationModel]):

    def __init__(self, db: Session):
        super().__init__(MedicationModel, db)

    def get_by_user(self, user_id: UUID) -> List[MedicationModel]:
        return (
            self.db.query(self.model)
            .filter(self.model._user_id == user_id)
            .order_by(self.model._name)
            .all()
        )

    def get_by_caregiver(self, caregiver_id: UUID) -> List[MedicationModel]:
        return (
            self.db.query(self.model)
            .filter(self.model._caregiver_id == caregiver_id)
            .order_by(self.model._name)
            .all()
        )

    def get_active_by_user(self, user_id: UUID, on_date: date) -> List[MedicationModel]:
        """Return medications active on a given date (start_date <= on_date <= end_date or no end_date)."""
        return (
            self.db.query(self.model)
            .filter(
                self.model._user_id == user_id,
                self.model._start_date <= on_date,
                (self.model._end_date.is_(None)) | (self.model._end_date >= on_date),
            )
            .all()
        )

    def get_reminders_for_medication(self, medication_id: UUID) -> List[ReminderModel]:
        return (
            self.db.query(ReminderModel)
            .filter(ReminderModel._medication_id == medication_id)
            .all()
        )

    def delete_by_user_id(self, user_id: UUID) -> None:
        self.db.query(self.model).filter(
            self.model._user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()
