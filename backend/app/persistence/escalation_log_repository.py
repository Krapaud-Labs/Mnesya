"""Escalation Log Repository module."""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.escalation_log import EscalationLogModel
from app.persistence.base_repository import BaseRepository


class EscalationLogRepository(BaseRepository[EscalationLogModel]):

    def __init__(self, db: Session):
        super().__init__(EscalationLogModel, db)

    def get_last_escalation(self, caregiver_id: UUID, user_id: UUID) -> Optional[EscalationLogModel]:
        return (
            self.db.query(self.model)
            .filter(
                self.model._caregiver_id == caregiver_id,
                self.model._user_id == user_id,
            )
            .order_by(self.model._sent_at.desc())
            .first()
        )

    def was_recently_escalated(self, caregiver_id: UUID, user_id: UUID, cooldown_minutes: int = 30) -> bool:
        last = self.get_last_escalation(caregiver_id, user_id)
        if not last:
            return False
        sent_at = last.sent_at
        if sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)
        return sent_at > datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)

    def log_escalation(self, caregiver_id: UUID, user_id: UUID, reminder_count: int) -> EscalationLogModel:
        entry = EscalationLogModel()
        entry.caregiver_id = caregiver_id
        entry.user_id = user_id
        entry.reminder_count = reminder_count
        return self.add(entry)
