"""Seed test data for manual QA of the activity log and new features.

Creates:
  - 1 caregiver   : marie@test.com / Test1234!
  - 1 user        : Jessica Martin (born 1945-03-12)
  - 2 medications : Doliprane 500mg (AFTER_BREAKFAST) + Metformine 850mg (AFTER_LUNCH & AFTER_DINNER)
  - 3 manual reminders : Sieste, Appel famille, Promenade
  - ~9 reminder_status spread over the last 5 days (DONE / POSTPONED / UNABLE / MISSED)

Usage (inside the Docker container):
    python /app/seed_test_data.py
"""

import os, sys, uuid
from datetime import datetime, timedelta, date, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set.", file=sys.stderr)
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Import models after engine is ready (app.__init__ needs to be initialised)
from app import init_app
init_app(DATABASE_URL)

from app.models.caregiver import CaregiverModel
from app.models.user import UserModel
from app.models.reminder import ReminderModel
from app.models.reminder_status import ReminderStatusModel
from app.models.medication import MedicationModel

# ─── Helpers ─────────────────────────────────────────────────────────────────

def ago(days: float = 0, hours: float = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days, hours=hours)


def make_status(reminder_id: uuid.UUID, status: str, days_ago: float) -> ReminderStatusModel:
    s = ReminderStatusModel()
    s._id = uuid.uuid4()
    s._reminder_id = reminder_id
    s._status = status
    s._created_at = ago(days_ago)
    s._updated_at = ago(days_ago)
    return s


def make_reminder(
    title: str,
    caregiver_id: uuid.UUID,
    user_id: uuid.UUID,
    days_ago: float,
    medication_id: uuid.UUID | None = None,
) -> ReminderModel:
    r = ReminderModel()
    r._id = uuid.uuid4()
    r._title = title
    r._description = None
    r._scheduled_at = ago(days_ago)
    r._caregiver_id = caregiver_id
    r._user_id = user_id
    r._is_recurring = False
    r._medication_id = medication_id
    r._created_at = ago(days_ago + 0.1)
    r._updated_at = ago(days_ago + 0.1)
    return r


# ─── Seed ────────────────────────────────────────────────────────────────────

def seed() -> None:
    with Session() as db:
        # ── Caregiver ──
        caregiver = CaregiverModel()
        caregiver._id = uuid.uuid4()
        caregiver._first_name = "Marie"
        caregiver._last_name = "Dupont"
        caregiver._email = "marie@test.com"
        caregiver.password = "Test1234!"   # hashed via setter
        caregiver._user_ids = []
        db.add(caregiver)
        db.flush()

        # ── User ──
        user = UserModel()
        user._id = uuid.uuid4()
        user._first_name = "Jessica"
        user._last_name = "Martin"
        user._birthday = date(1945, 3, 12)
        user._caregiver_ids = [caregiver._id]
        db.add(user)
        db.flush()

        caregiver._user_ids = [user._id]

        # ── Medications ──
        doliprane = MedicationModel()
        doliprane._id = uuid.uuid4()
        doliprane._caregiver_id = caregiver._id
        doliprane._user_id = user._id
        doliprane._name = "Doliprane"
        doliprane._dosage = "500mg"
        doliprane._moments = ["AFTER_BREAKFAST"]
        doliprane._frequency = "DAILY"
        doliprane._recurrence_days = None
        doliprane._start_date = date.today() - timedelta(days=10)
        db.add(doliprane)

        metformine = MedicationModel()
        metformine._id = uuid.uuid4()
        metformine._caregiver_id = caregiver._id
        metformine._user_id = user._id
        metformine._name = "Metformine"
        metformine._dosage = "850mg"
        metformine._moments = ["AFTER_LUNCH", "AFTER_DINNER"]
        metformine._frequency = "DAILY"
        metformine._recurrence_days = None
        metformine._start_date = date.today() - timedelta(days=10)
        db.add(metformine)
        db.flush()

        # ── Reminders (manual) ──
        r_sieste    = make_reminder("Sieste", caregiver._id, user._id, days_ago=0.3)
        r_appel     = make_reminder("Appel famille", caregiver._id, user._id, days_ago=1.2)
        r_promenade = make_reminder("Promenade", caregiver._id, user._id, days_ago=3.5)

        # ── Reminders (medication-generated) ──
        r_doli_1 = make_reminder("Doliprane", caregiver._id, user._id, days_ago=0.4, medication_id=doliprane._id)
        r_doli_2 = make_reminder("Doliprane", caregiver._id, user._id, days_ago=1.4, medication_id=doliprane._id)
        r_doli_3 = make_reminder("Doliprane", caregiver._id, user._id, days_ago=2.4, medication_id=doliprane._id)
        r_met_1  = make_reminder("Metformine", caregiver._id, user._id, days_ago=0.5, medication_id=metformine._id)
        r_met_2  = make_reminder("Metformine", caregiver._id, user._id, days_ago=1.5, medication_id=metformine._id)
        r_met_3  = make_reminder("Metformine", caregiver._id, user._id, days_ago=4.5, medication_id=metformine._id)

        for r in [r_sieste, r_appel, r_promenade, r_doli_1, r_doli_2, r_doli_3, r_met_1, r_met_2, r_met_3]:
            db.add(r)
        db.flush()

        # ── Statuses ──
        statuses = [
            # Aujourd'hui
            make_status(r_sieste._id,    "DONE",      0.3),
            make_status(r_doli_1._id,    "DONE",      0.4),
            make_status(r_met_1._id,     "POSTPONED", 0.5),
            # Hier
            make_status(r_appel._id,     "UNABLE",    1.2),
            make_status(r_doli_2._id,    "MISSED",    1.4),
            make_status(r_met_2._id,     "DONE",      1.5),
            # Il y a 2 jours
            make_status(r_doli_3._id,    "DONE",      2.4),
            # Il y a 3 jours
            make_status(r_promenade._id, "POSTPONED", 3.5),
            # Il y a 4 jours
            make_status(r_met_3._id,     "MISSED",    4.5),
        ]

        for s in statuses:
            db.add(s)

        db.commit()

    print("Seed complete!")
    print("  Caregiver : marie@test.com / Test1234!")
    print("  User      : Jessica Martin")
    print("  Rappels   : Sieste, Appel famille, Promenade")
    print("  Médicaments: Doliprane 500mg (après petit-déj.), Metformine 850mg (après déj. & dîner)")
    print("  Statuts   : 9 entrées sur 5 jours différents")


if __name__ == "__main__":
    seed()
