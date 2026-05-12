"""Unit tests for recurrence logic.

Tests cover:
- calculate_next_occurrence: DAILY, WEEKLY, MONTHLY, end_date cutoff
- schedule_next_occurrence: updates scheduled_at + creates PENDING status
- ReminderCreate schema: recurrence validation rules
"""

import pytest
from datetime import datetime, date, timezone
from typing import Optional
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.services.reminder_facade import calculate_next_occurrence, schedule_next_occurrence
from app.models.reminder import ReminderModel
from app.schemas.reminder_schema import ReminderCreate


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_reminder(
    recurrence_type: str,
    recurrence_days: Optional[list] = None,
    recurrence_end_date: Optional[date] = None,
    scheduled_at: Optional[datetime] = None,
) -> ReminderModel:
    r = ReminderModel()
    r.title = "Test"
    r.is_recurring = True
    r.recurrence_type = recurrence_type
    r.recurrence_days = recurrence_days
    r.recurrence_end_date = recurrence_end_date
    r.scheduled_at = scheduled_at or datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc)  # Monday
    return r


# ─── calculate_next_occurrence ───────────────────────────────────────────────

class TestCalculateNextOccurrenceDaily:

    def test_returns_next_day(self):
        r = make_reminder("DAILY", scheduled_at=datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc))
        # Freeze 'now' just after scheduled_at so +1 day is in the future
        future_now = datetime(2026, 1, 6, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = future_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result == datetime(2026, 1, 7, 9, 0, tzinfo=timezone.utc)

    def test_skips_past_occurrences(self):
        r = make_reminder("DAILY", scheduled_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc))
        now = datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is not None
        assert result > now

    def test_respects_end_date(self):
        r = make_reminder(
            "DAILY",
            scheduled_at=datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc),
            recurrence_end_date=date(2026, 1, 6),
        )
        now = datetime(2026, 1, 6, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is None

    def test_not_recurring_returns_none(self):
        r = ReminderModel()
        r.is_recurring = False
        r.recurrence_type = None
        r.scheduled_at = datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence(r)
        assert result is None


class TestCalculateNextOccurrenceWeekly:

    def test_next_selected_weekday(self):
        # scheduled_at is Monday (weekday=0), recurrence on Wednesday (2) and Friday (4)
        r = make_reminder(
            "WEEKLY",
            recurrence_days=[2, 4],
            scheduled_at=datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),  # Monday
        )
        now = datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        # Next occurrence should be Wednesday Jan 7
        assert result is not None
        assert result.weekday() == 2
        assert result > now

    def test_single_day_same_week(self):
        # Monday, recurrence every Friday
        r = make_reminder(
            "WEEKLY",
            recurrence_days=[4],
            scheduled_at=datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),
        )
        now = datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is not None
        assert result.weekday() == 4

    def test_wraps_to_next_week(self):
        # Friday, recurrence only Monday
        r = make_reminder(
            "WEEKLY",
            recurrence_days=[0],
            scheduled_at=datetime(2026, 1, 9, 9, 0, tzinfo=timezone.utc),  # Friday
        )
        now = datetime(2026, 1, 9, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is not None
        assert result.weekday() == 0
        assert result.day == 12  # Next Monday

    def test_empty_days_returns_none(self):
        r = make_reminder("WEEKLY", recurrence_days=[])
        result = calculate_next_occurrence(r)
        assert result is None

    def test_respects_end_date(self):
        r = make_reminder(
            "WEEKLY",
            recurrence_days=[2],
            scheduled_at=datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),  # Monday
            recurrence_end_date=date(2026, 1, 6),  # End before next Wednesday
        )
        now = datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is None


class TestCalculateNextOccurrenceMonthly:

    def test_next_month_same_day(self):
        r = make_reminder(
            "MONTHLY",
            scheduled_at=datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
        )
        now = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is not None
        assert result.month == 2
        assert result.day == 15

    def test_day_clamping_for_short_month(self):
        # Jan 31 → Feb should clamp to Feb 28
        r = make_reminder(
            "MONTHLY",
            scheduled_at=datetime(2026, 1, 31, 9, 0, tzinfo=timezone.utc),
        )
        now = datetime(2026, 1, 31, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is not None
        assert result.month == 2
        assert result.day == 28

    def test_december_wraps_to_january(self):
        r = make_reminder(
            "MONTHLY",
            scheduled_at=datetime(2026, 12, 10, 9, 0, tzinfo=timezone.utc),
        )
        now = datetime(2026, 12, 10, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is not None
        assert result.year == 2027
        assert result.month == 1

    def test_respects_end_date(self):
        r = make_reminder(
            "MONTHLY",
            scheduled_at=datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc),
            recurrence_end_date=date(2026, 2, 1),
        )
        now = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = calculate_next_occurrence(r)
        assert result is None


# ─── schedule_next_occurrence ────────────────────────────────────────────────

class TestScheduleNextOccurrence:

    def test_returns_true_and_updates_scheduled_at(self):
        r = make_reminder(
            "DAILY",
            scheduled_at=datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc),
        )
        db = MagicMock()
        now = datetime(2026, 1, 6, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = schedule_next_occurrence(r, db)
        assert result is True
        assert r.scheduled_at == datetime(2026, 1, 7, 9, 0, tzinfo=timezone.utc)
        db.add.assert_called()
        db.commit.assert_called_once()

    def test_returns_false_when_exhausted(self):
        r = make_reminder(
            "DAILY",
            scheduled_at=datetime(2026, 1, 6, 9, 0, tzinfo=timezone.utc),
            recurrence_end_date=date(2026, 1, 6),
        )
        db = MagicMock()
        now = datetime(2026, 1, 6, 10, 0, tzinfo=timezone.utc)
        with patch("app.services.reminder_facade.datetime") as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = schedule_next_occurrence(r, db)
        assert result is False
        db.commit.assert_not_called()


# ─── ReminderCreate schema validation ────────────────────────────────────────

class TestReminderCreateSchema:

    base: dict = {
        "title": "Test",
        "scheduled_at": "2026-06-01T09:00:00Z",
        "user_id": "00000000-0000-0000-0000-000000000001",
    }

    def test_non_recurring_valid(self):
        data = ReminderCreate.model_validate(self.base)
        assert data.is_recurring is False

    def test_recurring_daily_valid(self):
        data = ReminderCreate.model_validate({**self.base, "is_recurring": True, "recurrence_type": "DAILY"})
        assert data.recurrence_type == "DAILY"

    def test_recurring_weekly_with_days_valid(self):
        data = ReminderCreate.model_validate({
            **self.base,
            "is_recurring": True,
            "recurrence_type": "WEEKLY",
            "recurrence_days": [0, 2, 4],
        })
        assert data.recurrence_days == [0, 2, 4]

    def test_recurring_monthly_valid(self):
        data = ReminderCreate.model_validate({**self.base, "is_recurring": True, "recurrence_type": "MONTHLY"})
        assert data.recurrence_type == "MONTHLY"

    def test_recurring_without_type_raises(self):
        with pytest.raises(ValidationError) as exc:
            ReminderCreate.model_validate({**self.base, "is_recurring": True})
        assert "recurrence_type" in str(exc.value)

    def test_invalid_recurrence_type_raises(self):
        with pytest.raises(ValidationError):
            ReminderCreate.model_validate({
                **self.base,
                "is_recurring": True,
                "recurrence_type": "HOURLY",
            })

    def test_weekly_without_days_raises(self):
        with pytest.raises(ValidationError) as exc:
            ReminderCreate.model_validate({
                **self.base,
                "is_recurring": True,
                "recurrence_type": "WEEKLY",
            })
        assert "recurrence_days" in str(exc.value)

    def test_recurrence_day_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            ReminderCreate.model_validate({
                **self.base,
                "is_recurring": True,
                "recurrence_type": "WEEKLY",
                "recurrence_days": [0, 7],  # 7 is invalid
            })

    def test_recurrence_with_end_date_valid(self):
        data = ReminderCreate.model_validate({
            **self.base,
            "is_recurring": True,
            "recurrence_type": "DAILY",
            "recurrence_end_date": "2026-12-31",
        })
        assert data.recurrence_end_date == date(2026, 12, 31)
