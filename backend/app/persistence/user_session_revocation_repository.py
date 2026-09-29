"""Repository for per-user session revocation."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user_session_revocation import UserSessionRevocationModel


class UserSessionRevocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def revoke_all_for_user(self, sub: str) -> None:
        """Upsert a revocation record: any token issued before now is invalid."""
        now = datetime.now(timezone.utc)
        record = self.db.query(UserSessionRevocationModel).filter(
            UserSessionRevocationModel._sub == sub
        ).first()
        if record:
            record._revoked_before = now
        else:
            record = UserSessionRevocationModel()
            record._sub = sub
            record._revoked_before = now
            self.db.add(record)
        self.db.commit()

    def get_revoked_before(self, sub: str) -> datetime | None:
        """Return the revocation timestamp for this sub, or None."""
        record = self.db.query(UserSessionRevocationModel).filter(
            UserSessionRevocationModel._sub == sub
        ).first()
        return record._revoked_before if record else None
