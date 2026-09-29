"""Pairing Facade module.

This module implements the Facade pattern for pairing code business logic.
It provides a simplified interface for pairing operations, coordinating
between the model layer and repository layer.
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.pairing_code import PairingCodeModel
from app.models.user import UserModel
from app.persistence.pairing_code_repository import PairingCodeRepository
from app.persistence.user_repository import UserRepository

PAIRING_CODE_EXPIRE_MINUTES = 5


class PairingFacade:
    """Facade for pairing code business logic operations.

    Attributes:
        pairing_code_repo (PairingCodeRepository): Repository for pairing code data access
        user_repo (UserRepository): Repository for user data access
    """

    def __init__(self, db: Session):
        self.pairing_code_repo = PairingCodeRepository(db)
        self.user_repo = UserRepository(db)

    def _generate_unique_code(self) -> str:
        """Generate a unique 6-character alphanumeric pairing code."""
        chars = string.ascii_uppercase + string.digits
        code = "".join(secrets.choice(chars) for _ in range(6))
        while self.pairing_code_repo.find_by_code(code):
            code = "".join(secrets.choice(chars) for _ in range(6))
        return code

    def get_or_create_pairing_code(
        self, user_id: UUID, caregiver_id: UUID
    ) -> PairingCodeModel:
        """Return the active pairing code for a user, or create a new one.

        Args:
            user_id (UUID): The user to generate the code for
            caregiver_id (UUID): The caregiver generating the code

        Returns:
            PairingCodeModel: An active pairing code (existing or newly created)
        """
        existing = self.pairing_code_repo.find_active_by_user_id(user_id)
        if existing:
            return existing

        pairing_code = PairingCodeModel()
        pairing_code.code = self._generate_unique_code()
        pairing_code.user_id = user_id
        pairing_code.caregiver_id = caregiver_id
        pairing_code.expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=PAIRING_CODE_EXPIRE_MINUTES
        )
        self.pairing_code_repo.add(pairing_code)
        return pairing_code

    def find_pairing_code(self, code: str) -> PairingCodeModel | None:
        """Find a pairing code by its string value.

        Args:
            code (str): The code to look up

        Returns:
            PairingCodeModel or None if not found
        """
        return self.pairing_code_repo.find_by_code(code)

    def consume_pairing_code(self, pairing_code: PairingCodeModel) -> UserModel:
        """Mark a pairing code as used and return the associated user.

        Args:
            pairing_code (PairingCodeModel): A valid pairing code to consume

        Returns:
            UserModel: The user associated with the pairing code
        """
        pairing_code.is_used = True
        self.pairing_code_repo.add(pairing_code)
        return self.user_repo.get(pairing_code.user_id)
