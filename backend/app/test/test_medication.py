"""Unit tests for the medication (pillulier) feature.

Tests cover:
- _first_occurrence: DAILY and WEEKLY scheduling logic
- _is_scheduled_on: active-day filtering
- MedicationCreate schema: validation rules
- MedicationModel: property setters validation
- MedicationFacade: CRUD + reminder generation + semainier
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List
from unittest.mock import MagicMock, patch, call
from pydantic import ValidationError

from app.services.medication_facade import (
    MedicationFacade,
    _first_occurrence,
    _is_scheduled_on,
)
from app.models.medication import MedicationModel
from app.schemas.medication_schema import MedicationCreate


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_medication(
    frequency: str = "DAILY",
    times: Optional[List[str]] = None,
    recurrence_days: Optional[List[int]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> MedicationModel:
    m = MedicationModel()
    m.name = "Doliprane"
    m.dosage = "500mg"
    m.frequency = frequency
    m.times = times or ["08:00"]
    m.recurrence_days = recurrence_days
    m.start_date = start_date or date(2026, 1, 1)
    m.end_date = end_date
    return m


def make_facade() -> tuple[MedicationFacade, MagicMock, MagicMock, MagicMock]:
    """Return (facade, med_repo, rem_repo, status_repo) all mocked."""
    db = MagicMock()
    facade = MedicationFacade.__new__(MedicationFacade)
    facade.db = db
    facade.medication_repo = MagicMock()
    facade.reminder_repo = MagicMock()
    facade.reminder_status_repo = MagicMock()
    return facade, facade.medication_repo, facade.reminder_repo, facade.reminder_status_repo


# ─── _first_occurrence ──────────────────────────────────────────────────────

class TestFirstOccurrence:

    def _freeze(self, mock_dt, now: datetime):
        mock_dt.now.return_value = now
        mock_dt.combine.side_effect = datetime.combine

    def test_daily_future_start_returns_start(self):
        now = datetime(2026, 5, 12, 7, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as m:
            self._freeze(m, now)
            result = _first_occurrence(date(2026, 5, 12), "08:00", "DAILY", None)
        assert result == datetime(2026, 5, 12, 8, 0, tzinfo=timezone.utc)

    def test_daily_past_start_advances_to_tomorrow(self):
        now = datetime(2026, 5, 12, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as m:
            self._freeze(m, now)
            result = _first_occurrence(date(2026, 1, 1), "08:00", "DAILY", None)
        assert result.date() == date(2026, 5, 13)
        assert result.hour == 8

    def test_daily_result_is_always_future(self):
        now = datetime(2026, 5, 12, 9, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as m:
            self._freeze(m, now)
            result = _first_occurrence(date(2026, 1, 1), "08:00", "DAILY", None)
        assert result > now

    def test_weekly_lands_on_valid_weekday(self):
        # now = Tuesday (weekday=1), recurrence on Wednesday (2) and Friday (4)
        now = datetime(2026, 5, 12, 9, 0, tzinfo=timezone.utc)  # Tuesday
        with patch("app.services.medication_facade.datetime") as m:
            self._freeze(m, now)
            result = _first_occurrence(date(2026, 1, 1), "09:00", "WEEKLY", [2, 4])
        assert result.weekday() in [2, 4]
        assert result > now

    def test_weekly_no_days_returns_candidate(self):
        now = datetime(2026, 5, 12, 9, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as m:
            self._freeze(m, now)
            result = _first_occurrence(date(2026, 1, 1), "09:00", "WEEKLY", [])
        # Falls through to return candidate (no valid day to advance to)
        assert result is not None


# ─── _is_scheduled_on ───────────────────────────────────────────────────────

class TestIsScheduledOn:

    def test_daily_before_start_returns_false(self):
        med = make_medication(start_date=date(2026, 5, 15))
        assert _is_scheduled_on(med, date(2026, 5, 14)) is False

    def test_daily_on_start_returns_true(self):
        med = make_medication(start_date=date(2026, 5, 12))
        assert _is_scheduled_on(med, date(2026, 5, 12)) is True

    def test_daily_after_end_returns_false(self):
        med = make_medication(start_date=date(2026, 5, 1), end_date=date(2026, 5, 10))
        assert _is_scheduled_on(med, date(2026, 5, 11)) is False

    def test_daily_no_end_always_active(self):
        med = make_medication(start_date=date(2026, 1, 1), end_date=None)
        assert _is_scheduled_on(med, date(2030, 1, 1)) is True

    def test_weekly_matching_day_true(self):
        # date(2026, 5, 13) = Wednesday = weekday 2
        med = make_medication(frequency="WEEKLY", recurrence_days=[2, 4])
        assert _is_scheduled_on(med, date(2026, 5, 13)) is True

    def test_weekly_non_matching_day_false(self):
        # date(2026, 5, 12) = Tuesday = weekday 1
        med = make_medication(frequency="WEEKLY", recurrence_days=[2, 4])
        assert _is_scheduled_on(med, date(2026, 5, 12)) is False

    def test_weekly_empty_days_false(self):
        med = make_medication(frequency="WEEKLY", recurrence_days=[])
        assert _is_scheduled_on(med, date(2026, 5, 13)) is False


# ─── MedicationCreate schema ─────────────────────────────────────────────────

class TestMedicationCreateSchema:

    base: dict = {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "name": "Doliprane",
        "times": ["08:00", "20:00"],
        "frequency": "DAILY",
        "start_date": "2026-05-12",
    }

    def test_valid_daily(self):
        data = MedicationCreate.model_validate(self.base)
        assert data.frequency == "DAILY"
        assert data.times == ["08:00", "20:00"]

    def test_valid_weekly_with_days(self):
        data = MedicationCreate.model_validate({
            **self.base,
            "frequency": "WEEKLY",
            "recurrence_days": [0, 2, 4],
        })
        assert data.recurrence_days == [0, 2, 4]

    def test_weekly_without_days_raises(self):
        with pytest.raises(ValidationError) as exc:
            MedicationCreate.model_validate({**self.base, "frequency": "WEEKLY"})
        assert "recurrence_days" in str(exc.value)

    def test_invalid_frequency_raises(self):
        with pytest.raises(ValidationError):
            MedicationCreate.model_validate({**self.base, "frequency": "MONTHLY"})

    def test_invalid_time_format_raises(self):
        with pytest.raises(ValidationError):
            MedicationCreate.model_validate({**self.base, "times": ["8:00"]})

    def test_empty_times_raises(self):
        with pytest.raises(ValidationError):
            MedicationCreate.model_validate({**self.base, "times": []})

    def test_end_before_start_raises(self):
        with pytest.raises(ValidationError):
            MedicationCreate.model_validate({
                **self.base,
                "start_date": "2026-05-12",
                "end_date": "2026-05-10",
            })

    def test_name_with_html_raises(self):
        with pytest.raises(ValidationError):
            MedicationCreate.model_validate({**self.base, "name": "<script>xss</script>"})

    def test_dosage_optional(self):
        data = MedicationCreate.model_validate(self.base)
        assert data.dosage is None

    def test_end_date_optional(self):
        data = MedicationCreate.model_validate(self.base)
        assert data.end_date is None

    def test_recurrence_days_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            MedicationCreate.model_validate({
                **self.base,
                "frequency": "WEEKLY",
                "recurrence_days": [0, 7],
            })


# ─── MedicationModel property validation ────────────────────────────────────

class TestMedicationModelValidation:

    def test_name_empty_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError, match="name is required"):
            m.name = "   "

    def test_name_too_long_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError):
            m.name = "x" * 201

    def test_name_strips_whitespace(self):
        m = MedicationModel()
        m.name = "  Doliprane  "
        assert m.name == "Doliprane"

    def test_times_invalid_format_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError, match="Invalid time format"):
            m.times = ["8:00"]

    def test_times_empty_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError, match="times must not be empty"):
            m.times = []

    def test_frequency_invalid_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError, match="frequency must be DAILY or WEEKLY"):
            m.frequency = "MONTHLY"

    def test_recurrence_days_invalid_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError, match="recurrence_days must be integers"):
            m.recurrence_days = [0, 7]

    def test_recurrence_days_none_accepted(self):
        m = MedicationModel()
        m.recurrence_days = None
        assert m.recurrence_days is None

    def test_dosage_too_long_raises(self):
        m = MedicationModel()
        with pytest.raises(ValueError, match="dosage must be"):
            m.dosage = "x" * 201


# ─── MedicationFacade ────────────────────────────────────────────────────────

class TestMedicationFacadeCreate:

    def _make_med_with_id(self, med_id="aaaaaaaa-0000-0000-0000-000000000001") -> MedicationModel:
        import uuid
        med = make_medication(times=["08:00", "20:00"])
        med._id = uuid.UUID(med_id)
        med._caregiver_id = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")
        med._user_id = uuid.UUID("cccccccc-0000-0000-0000-000000000001")
        return med

    def test_creates_one_reminder_per_time(self):
        facade, med_repo, rem_repo, status_repo = make_facade()
        import uuid

        med = self._make_med_with_id()
        med_repo.add.return_value = med

        now = datetime(2026, 5, 12, 7, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.combine.side_effect = datetime.combine
            facade.create_medication(
                {
                    "user_id": uuid.UUID("cccccccc-0000-0000-0000-000000000001"),
                    "name": "Doliprane",
                    "dosage": "500mg",
                    "times": ["08:00", "20:00"],
                    "frequency": "DAILY",
                    "start_date": date(2026, 5, 12),
                    "end_date": None,
                    "recurrence_days": None,
                },
                uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001"),
            )

        # One reminder per time slot → rem_repo.add called twice
        assert rem_repo.add.call_count == 2
        # One PENDING status per reminder → status_repo.add called twice
        assert status_repo.add.call_count == 2

    def test_daily_reminder_is_recurring(self):
        facade, med_repo, rem_repo, status_repo = make_facade()
        import uuid

        med = self._make_med_with_id()
        med_repo.add.return_value = med

        added_reminders = []
        rem_repo.add.side_effect = lambda r: added_reminders.append(r)

        now = datetime(2026, 5, 12, 7, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.combine.side_effect = datetime.combine
            facade.create_medication(
                {
                    "user_id": uuid.UUID("cccccccc-0000-0000-0000-000000000001"),
                    "name": "Doliprane",
                    "dosage": "500mg",
                    "times": ["08:00"],
                    "frequency": "DAILY",
                    "start_date": date(2026, 5, 12),
                    "end_date": date(2026, 12, 31),
                    "recurrence_days": None,
                },
                uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001"),
            )

        assert len(added_reminders) == 1
        r = added_reminders[0]
        assert r.is_recurring is True
        assert r.recurrence_type == "DAILY"
        assert r.recurrence_end_date == date(2026, 12, 31)

    def test_weekly_reminder_sets_recurrence_days(self):
        facade, med_repo, rem_repo, status_repo = make_facade()
        import uuid

        med = make_medication(frequency="WEEKLY", recurrence_days=[1, 3])
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med._caregiver_id = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")
        med._user_id = uuid.UUID("cccccccc-0000-0000-0000-000000000001")
        med_repo.add.return_value = med

        added_reminders = []
        rem_repo.add.side_effect = lambda r: added_reminders.append(r)

        now = datetime(2026, 5, 12, 7, 0, tzinfo=timezone.utc)  # Tuesday
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.combine.side_effect = datetime.combine
            facade.create_medication(
                {
                    "user_id": uuid.UUID("cccccccc-0000-0000-0000-000000000001"),
                    "name": "Aspirine",
                    "dosage": None,
                    "times": ["08:00"],
                    "frequency": "WEEKLY",
                    "start_date": date(2026, 5, 12),
                    "end_date": None,
                    "recurrence_days": [1, 3],
                },
                uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001"),
            )

        assert len(added_reminders) == 1
        r = added_reminders[0]
        assert r.recurrence_type == "WEEKLY"
        assert r.recurrence_days == [1, 3]
        assert r.scheduled_at.weekday() in [1, 3]


class TestMedicationFacadeDelete:

    def test_delete_removes_statuses_then_reminders(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()

        med = make_medication()
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med_repo.get.return_value = med

        import uuid as _uuid
        rem1 = MagicMock()
        rem1.id = _uuid.uuid4()
        med_repo.get_reminders_for_medication.return_value = [rem1]

        s1 = MagicMock()
        s1.id = _uuid.uuid4()
        status_repo.get_statuses_by_reminder.return_value = [s1]

        result = facade.delete_medication(med._id)

        assert result is True
        status_repo.delete.assert_called_once_with(s1.id)
        rem_repo.delete.assert_called_once_with(rem1.id)
        med_repo.delete.assert_called_once_with(med._id)

    def test_delete_returns_false_when_not_found(self):
        facade, med_repo, _, _ = make_facade()
        med_repo.get.return_value = None
        import uuid
        assert facade.delete_medication(uuid.uuid4()) is False


class TestMedicationFacadeUpdate:

    def test_schedule_change_regenerates_reminders(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()

        med = make_medication(times=["08:00"])
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med._caregiver_id = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")
        med._user_id = uuid.UUID("cccccccc-0000-0000-0000-000000000001")
        med_repo.get.return_value = med
        med_repo.update.return_value = med

        old_rem = MagicMock()
        old_rem.id = uuid.uuid4()
        med_repo.get_reminders_for_medication.return_value = [old_rem]
        status_repo.get_statuses_by_reminder.return_value = []

        now = datetime(2026, 5, 12, 7, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.combine.side_effect = datetime.combine
            facade.update_medication(med._id, {"times": ["09:00"]})

        # Old reminder deleted, new one added
        rem_repo.delete.assert_called_once_with(old_rem.id)
        assert rem_repo.add.call_count == 1

    def test_non_schedule_change_keeps_reminders(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()

        med = make_medication()
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med_repo.get.return_value = med
        med_repo.update.return_value = med

        facade.update_medication(med._id, {"name": "Paracetamol"})

        # No schedule field changed → reminders untouched
        rem_repo.delete.assert_not_called()
        rem_repo.add.assert_not_called()


class TestMedicationFacadeGetWeek:

    def test_returns_7_days(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()
        med_repo.get_active_by_user.return_value = []

        result = facade.get_week(uuid.uuid4(), date(2026, 5, 11))

        assert len(result.days) == 7

    def test_week_starts_on_correct_date(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()
        med_repo.get_active_by_user.return_value = []

        result = facade.get_week(uuid.uuid4(), date(2026, 5, 11))  # Monday

        assert result.week_start == "2026-05-11"
        assert result.days[0].date == "2026-05-11"
        assert result.days[6].date == "2026-05-17"

    def test_daily_medication_appears_every_day(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()

        med = make_medication(frequency="DAILY", times=["08:00"],
                              start_date=date(2026, 1, 1))
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med_repo.get_active_by_user.return_value = [med]

        reminder = MagicMock()
        reminder.id = uuid.uuid4()
        reminder.scheduled_at = datetime(2026, 5, 12, 8, 0, tzinfo=timezone.utc)
        med_repo.get_reminders_for_medication.return_value = [reminder]

        status_mock = MagicMock()
        status_mock.status = "PENDING"
        status_mock.created_at = datetime(2026, 5, 12, 7, 0, tzinfo=timezone.utc)
        status_repo.get_statuses_by_reminder.return_value = [status_mock]

        now = datetime(2026, 5, 12, 9, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now

            result = facade.get_week(uuid.uuid4(), date(2026, 5, 11))

        # All 7 days should have 1 entry
        for day in result.days:
            assert len(day.entries) == 1
            assert day.entries[0].name == "Doliprane"

    def test_weekly_medication_appears_only_on_correct_days(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()

        # WEEKLY on Wednesday (2) and Friday (4) only
        med = make_medication(frequency="WEEKLY", recurrence_days=[2, 4],
                              start_date=date(2026, 1, 1))
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med_repo.get_active_by_user.return_value = [med]

        reminder = MagicMock()
        reminder.id = uuid.uuid4()
        reminder.scheduled_at = datetime(2026, 5, 13, 8, 0, tzinfo=timezone.utc)
        med_repo.get_reminders_for_medication.return_value = [reminder]
        status_repo.get_statuses_by_reminder.return_value = []

        now = datetime(2026, 5, 12, 9, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now

            # Week: Mon 11 → Sun 17
            result = facade.get_week(uuid.uuid4(), date(2026, 5, 11))

        days_with_entries = [d for d in result.days if d.entries]
        # Only Wed (index 2) and Fri (index 4) should have entries
        assert len(days_with_entries) == 2
        active_dates = [d.date for d in days_with_entries]
        assert "2026-05-13" in active_dates  # Wednesday
        assert "2026-05-15" in active_dates  # Friday

    def test_entries_sorted_by_time(self):
        import uuid
        facade, med_repo, rem_repo, status_repo = make_facade()

        med = make_medication(frequency="DAILY", times=["20:00", "08:00"],
                              start_date=date(2026, 1, 1))
        med._id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        med_repo.get_active_by_user.return_value = [med]

        rem_morning = MagicMock()
        rem_morning.id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000002")
        rem_morning.scheduled_at = datetime(2026, 5, 12, 8, 0, tzinfo=timezone.utc)

        rem_evening = MagicMock()
        rem_evening.id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000003")
        rem_evening.scheduled_at = datetime(2026, 5, 12, 20, 0, tzinfo=timezone.utc)

        med_repo.get_reminders_for_medication.return_value = [rem_evening, rem_morning]
        status_repo.get_statuses_by_reminder.return_value = []

        now = datetime(2026, 5, 12, 9, 0, tzinfo=timezone.utc)
        with patch("app.services.medication_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            result = facade.get_week(uuid.uuid4(), date(2026, 5, 12))

        today = result.days[0]
        assert len(today.entries) == 2
        assert today.entries[0].time == "08:00"
        assert today.entries[1].time == "20:00"
