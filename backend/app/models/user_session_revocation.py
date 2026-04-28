"""UserSessionRevocation model — tracks per-user logout timestamps."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app import database


class UserSessionRevocationModel(database):
    """Records the last logout timestamp per user (sub).

    Any token with iat <= revoked_before for the same sub is considered
    invalid, even if its JTI was never individually blacklisted.
    """

    __tablename__ = "user_session_revocation"

    _sub = Column("sub", String(36), primary_key=True)
    _revoked_before = Column(
        "revoked_before",
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def sub(self) -> str:
        return self._sub

    @property
    def revoked_before(self) -> datetime:
        return self._revoked_before
