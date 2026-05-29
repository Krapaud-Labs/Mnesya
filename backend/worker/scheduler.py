"""Scheduler module for automated push notification delivery.

This module defines background jobs that run every 60 seconds to:
- Send initial push notifications to users when a reminder is due (T+0)
- Retry notifications if the user has not responded (T+5)
- Escalate to the caregiver if still no response after 10 minutes (T+10)

The scheduler uses APScheduler's BackgroundScheduler with IntervalTrigger.
Each job opens its own database session to avoid circular import issues.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.persistence.reminder_repository import ReminderRepository
from app.persistence.push_token_repository import PushTokenRepository
from app.persistence.reminder_status_repository import ReminderStatusRepository
from app.persistence.escalation_log_repository import EscalationLogRepository
from app.services.notification_services import NotificationService
from app.persistence.revoked_token_repository import RevokedTokenRepository
from app.services.reminder_facade import schedule_next_occurrence
from app.services.medication_facade import TIME_TO_MOMENT

logger = logging.getLogger(__name__)


def send_user_notifications() -> None:
    """Send initial push notifications for reminders due now (T+0).

    Queries reminders scheduled within the last 55 seconds and sends
    a push notification to the user's registered devices.
    The 90s window provides a 30s buffer against scheduler jitter.
    Skips reminders with a terminal status (DONE, UNABLE, MISSED).
    POSTPONED is intentionally not skipped: the reminder's scheduled_at has
    been moved forward, so it must fire again at the new time.
    """
    from app import SessionLocal

    db: Session = SessionLocal()
    try:
        reminder_repo = ReminderRepository(db)
        push_token_repo = PushTokenRepository(db)
        notification_service = NotificationService()

        reminders = reminder_repo.get_reminders_due_now(window_seconds=55)
        logger.info(
            f"[Scheduler] send_user_notifications: {len(reminders)} reminders due"
        )

        for reminder in reminders:
            # Medication reminders are handled via direct UI interaction — no push notification
            if reminder.medication_id is not None:
                continue
            tokens = [
                t.token
                for t in push_token_repo.get_active_tokens_by_user(reminder.user_id)
            ]
            logger.info(
                f"[Scheduler] reminder {reminder.id}: {len(tokens)} user token(s)"
            )
            if not tokens:
                continue
            notification_service.send_reminder_notification(
                tokens=tokens,
                reminder_title=reminder.title,
                reminder_description=reminder.description,
                reminder_id=str(reminder.id),
                extra_data={"isUserNotification": True},
            )
    except Exception as e:
        logger.error(f"[Scheduler] Error in send_user_notifications: {e}")
    finally:
        db.close()


def send_user_retry(offset_minutes: int) -> None:
    """Retry push notification for reminders that have not been confirmed.

    Called at T+5 minutes after the original scheduled time.

    Args:
        offset_minutes (int): Number of minutes after scheduled_at to target.
    """
    from app import SessionLocal

    db: Session = SessionLocal()
    try:
        reminder_repo = ReminderRepository(db)
        push_token_repo = PushTokenRepository(db)
        notification_service = NotificationService()

        reminders = reminder_repo.get_reminders_at_offset(offset_minutes=offset_minutes)

        for reminder in reminders:
            # Medication reminders are handled via direct UI interaction — no push notification
            if reminder.medication_id is not None:
                continue
            tokens = [
                t.token
                for t in push_token_repo.get_active_tokens_by_user(reminder.user_id)
            ]
            if not tokens:
                continue
            notification_service.send_reminder_notification(
                tokens=tokens,
                reminder_title=reminder.title,
                reminder_description=reminder.description,
                reminder_id=str(reminder.id),
                extra_data={"isUserNotification": True, "retry": offset_minutes},
            )
    except Exception as e:
        logger.error(f"[Scheduler] Error in send_user_retry: {e}")
    finally:
        db.close()


def _build_meal_message(moment: str, med_names: list, locale: str) -> tuple:
    """Return (title, body) for a meal-moment medication reminder."""
    MESSAGES_FR = {
        "BEFORE_BREAKFAST":  ("🌅 Petit-déjeuner", "Pensez à prendre {meds} avant de petit-déjeuner"),
        "DURING_BREAKFAST":  ("🌅 Pendant le petit-déjeuner", "Pensez à prendre {meds} pendant le petit-déjeuner"),
        "AFTER_BREAKFAST":   ("🌅 Après le petit-déjeuner", "N'oubliez pas {meds} après le petit-déjeuner"),
        "BEFORE_LUNCH":      ("🍽️ Bientôt l'heure du midi", "Pensez à prendre {meds} avant le déjeuner"),
        "DURING_LUNCH":      ("🍽️ Pendant le déjeuner", "Pensez à prendre {meds} pendant le déjeuner"),
        "AFTER_LUNCH":       ("🍽️ Après le déjeuner", "N'oubliez pas {meds} après le déjeuner"),
        "BEFORE_DINNER":     ("🌆 Repas du soir", "Pensez à prendre {meds} avant le dîner"),
        "DURING_DINNER":     ("🌆 Pendant le dîner", "Pensez à prendre {meds} pendant le dîner"),
        "AFTER_DINNER":      ("🌆 Après le dîner", "N'oubliez pas {meds} après le dîner"),
        "BEDTIME":           ("🌙 Avant de dormir", "N'oubliez pas {meds} avant de vous coucher"),
    }
    MESSAGES_EN = {
        "BEFORE_BREAKFAST":  ("🌅 Breakfast soon", "Remember to take {meds} before breakfast"),
        "DURING_BREAKFAST":  ("🌅 During breakfast", "Remember to take {meds} during breakfast"),
        "AFTER_BREAKFAST":   ("🌅 After breakfast", "Don't forget {meds} after breakfast"),
        "BEFORE_LUNCH":      ("🍽️ Lunchtime soon", "Remember to take {meds} before lunch"),
        "DURING_LUNCH":      ("🍽️ During lunch", "Remember to take {meds} during lunch"),
        "AFTER_LUNCH":       ("🍽️ After lunch", "Don't forget {meds} after lunch"),
        "BEFORE_DINNER":     ("🌆 Dinner soon", "Remember to take {meds} before dinner"),
        "DURING_DINNER":     ("🌆 During dinner", "Remember to take {meds} during dinner"),
        "AFTER_DINNER":      ("🌆 After dinner", "Don't forget {meds} after dinner"),
        "BEDTIME":           ("🌙 Bedtime soon", "Don't forget {meds} before bed"),
    }
    messages = MESSAGES_FR if locale == "fr" else MESSAGES_EN
    title, body_tpl = messages.get(moment, ("💊 Traitement", "Pensez à prendre {meds}"))

    if len(med_names) == 1:
        meds_str = med_names[0]
    elif len(med_names) == 2:
        sep = " et " if locale == "fr" else " and "
        meds_str = sep.join(med_names)
    else:
        others = f" et {len(med_names) - 2} autre(s)" if locale == "fr" else f" and {len(med_names) - 2} more"
        meds_str = f"{med_names[0]}, {med_names[1]}{others}"

    return title, body_tpl.format(meds=meds_str)


def send_medication_moment_notifications() -> None:
    """Send meal-context notifications for medication reminders due now (T+0).

    Groups medication reminders by (user_id, moment) so each user receives
    one contextual notification per meal slot, listing all relevant medications.
    Only fires when at least one unresolved medication reminder exists for that slot.
    """
    from app import SessionLocal
    from collections import defaultdict
    from datetime import timezone

    db: Session = SessionLocal()
    try:
        reminder_repo = ReminderRepository(db)
        push_token_repo = PushTokenRepository(db)
        notification_service = NotificationService()

        reminders = reminder_repo.get_reminders_due_now(window_seconds=55)
        medication_reminders = [r for r in reminders if r.medication_id is not None]

        if not medication_reminders:
            return

        logger.info(
            f"[Scheduler] send_medication_moment_notifications: {len(medication_reminders)} med reminder(s)"
        )

        # Group by (user_id, moment key)
        groups: dict = defaultdict(list)
        for reminder in medication_reminders:
            time_str = reminder.scheduled_at.astimezone(timezone.utc).strftime("%H:%M")
            moment = TIME_TO_MOMENT.get(time_str)
            if moment:
                groups[(reminder.user_id, moment)].append(reminder.title)

        for (user_id, moment), med_names in groups.items():
            tokens = push_token_repo.get_active_tokens_by_user(user_id)
            if not tokens:
                continue
            token_strings = [t.token for t in tokens]
            locale = tokens[0].locale if tokens else "fr"
            title, body = _build_meal_message(moment, med_names, locale)
            notification_service.send_notification(
                tokens=token_strings,
                title=title,
                body=body,
                data={"type": "medication_moment", "moment": moment},
            )
            logger.info(
                f"[Scheduler] Meal notification sent to user {user_id} for {moment} ({len(med_names)} med(s))"
            )
    except Exception as e:
        logger.error(f"[Scheduler] Error in send_medication_moment_notifications: {e}")
    finally:
        db.close()


def send_caregiver_escalations():
    """Escalate unconfirmed reminders to the caregiver (T+10).

    Reminders are grouped by (caregiver_id, user_id) so the caregiver receives
    one notification per user per tick instead of one per reminder.
    A 30-minute cooldown per (caregiver_id, user_id) pair prevents spam across
    successive scheduler ticks (e.g. retry cycles or multiple simultaneous reminders).
    All reminders in the batch are always marked MISSED regardless of the cooldown.
    """
    from app import SessionLocal
    from collections import defaultdict
    from app.models.reminder_status import ReminderStatusModel

    db: Session = SessionLocal()
    try:
        reminder_repo = ReminderRepository(db)
        push_token_repo = PushTokenRepository(db)
        reminder_status_repo = ReminderStatusRepository(db)
        escalation_log_repo = EscalationLogRepository(db)
        notification_service = NotificationService()

        reminders = reminder_repo.get_reminders_to_escalate()
        logger.info(
            f"[Scheduler] send_caregiver_escalations: {len(reminders)} reminders to escalate"
        )

        # Group by (caregiver_id, user_id) — one notification per user per tick
        groups: dict = defaultdict(list)
        for reminder in reminders:
            groups[(reminder.caregiver_id, reminder.user_id)].append(reminder)

        for (caregiver_id, user_id), group_reminders in groups.items():
            # Snapshot reminder IDs and attributes before any commit expires the session objects
            reminder_snapshots = [
                {
                    "id": r.id,
                    "title": r.title,
                    "is_recurring": r.is_recurring,
                    "reminder_obj": r,
                    "user_first_name": getattr(r, "user_first_name", ""),
                    "user_last_name": getattr(r, "user_last_name", ""),
                }
                for r in group_reminders
            ]

            token_objects = push_token_repo.get_active_tokens_by_caregiver(caregiver_id)

            try:
                in_cooldown = escalation_log_repo.was_recently_escalated(
                    caregiver_id, user_id, cooldown_minutes=30
                )
            except Exception as e:
                logger.error(f"[Scheduler] Failed to check cooldown for user {user_id}: {e}")
                in_cooldown = False

            if token_objects and not in_cooldown:
                token_strings = [t.token for t in token_objects]
                locale = token_objects[0].locale if token_objects else "fr"
                user_name = (
                    f"{reminder_snapshots[0]['user_first_name']} "
                    f"{reminder_snapshots[0]['user_last_name']}"
                ).strip()
                count = len(reminder_snapshots)

                if locale == "fr":
                    title = "⚠️ Alerte Mnesya"
                    if count == 1:
                        body = f"{user_name} n'a pas répondu à : {reminder_snapshots[0]['title']}"
                    else:
                        titles = ", ".join(s["title"] for s in reminder_snapshots[:3])
                        suffix = f" et {count - 3} autre(s)" if count > 3 else ""
                        body = f"{user_name} n'a pas répondu à {count} rappels : {titles}{suffix}"
                else:
                    title = "⚠️ Mnesya Alert"
                    if count == 1:
                        body = f"{user_name} has not responded to: {reminder_snapshots[0]['title']}"
                    else:
                        titles = ", ".join(s["title"] for s in reminder_snapshots[:3])
                        suffix = f" and {count - 3} other(s)" if count > 3 else ""
                        body = f"{user_name} has not responded to {count} reminders: {titles}{suffix}"

                notification_service.send_notification(
                    tokens=token_strings,
                    title=title,
                    body=body,
                    data={"type": "caregiver_alert", "profile_id": str(user_id)},
                )
                logger.info(
                    f"[Scheduler] Escalation sent for user {user_id} ({count} reminder(s))"
                )

                # Log cooldown entry independently — must not block MISSED status saves
                try:
                    escalation_log_repo.log_escalation(caregiver_id, user_id, count)
                except Exception as e:
                    logger.error(f"[Scheduler] Failed to log escalation for user {user_id}: {e}")
                    try:
                        db.rollback()
                    except Exception:
                        pass

            elif in_cooldown:
                logger.info(
                    f"[Scheduler] Cooldown active for user {user_id}, skipping notification"
                )

            # Always mark all reminders as MISSED — isolated per reminder
            for snap in reminder_snapshots:
                try:
                    missed_status = ReminderStatusModel()
                    missed_status._status = "MISSED"
                    missed_status._reminder_id = snap["id"]
                    db.add(missed_status)
                    db.commit()
                    logger.info(f"[Scheduler] MISSED status saved for reminder {snap['id']}")

                    if snap["is_recurring"]:
                        scheduled = schedule_next_occurrence(snap["reminder_obj"], db)
                        logger.info(f"[Scheduler] Next occurrence scheduled: {scheduled}")
                except Exception as e:
                    logger.error(
                        f"[Scheduler] Failed to mark reminder {snap['id']} as MISSED: {e}"
                    )
                    try:
                        db.rollback()
                    except Exception:
                        pass

    except Exception as e:
        import traceback
        logger.error(
            f"[Scheduler] Error in send_caregiver_escalations: {e}\n{traceback.format_exc()}"
        )
    finally:
        db.close()


def send_medication_daily_summary() -> None:
    """Send a daily medication summary to caregivers at 20:00 UTC.

    For each caregiver/user pair that has medication reminders today, sends
    one notification listing each medication with its status icon:
      ✓ taken  ✗ missed/unable  ↪ postponed  ⏳ pending
    """
    from app import SessionLocal
    from collections import defaultdict

    db: Session = SessionLocal()
    try:
        reminder_repo = ReminderRepository(db)
        push_token_repo = PushTokenRepository(db)
        notification_service = NotificationService()

        reminders = reminder_repo.get_medication_reminders_today()
        logger.info(f"[Scheduler] send_medication_daily_summary: {len(reminders)} med reminders today")

        if not reminders:
            return

        # Group by (caregiver_id, user_id)
        groups: dict = defaultdict(list)
        for r in reminders:
            groups[(r.caregiver_id, r.user_id)].append(r)

        for (caregiver_id, user_id), group in groups.items():
            token_objects = push_token_repo.get_active_tokens_by_caregiver(caregiver_id)
            if not token_objects:
                continue

            token_strings = [t.token for t in token_objects]
            locale = token_objects[0].locale if token_objects else "fr"
            user_name = (
                f"{getattr(group[0], 'user_first_name', '')} "
                f"{getattr(group[0], 'user_last_name', '')}"
            ).strip()

            def status_icon(status: str | None) -> str:
                if status in ("DONE",):
                    return "✓"
                if status in ("MISSED", "UNABLE"):
                    return "✗"
                if status == "POSTPONED":
                    return "↪"
                return "⏳"

            lines = []
            for r in group:
                time_str = r.scheduled_at.astimezone(timezone.utc).strftime("%H:%M")
                icon = status_icon(getattr(r, "current_status", None))
                lines.append(f"{icon} {r.title} {time_str}")

            if locale == "fr":
                title = f"Bilan médicaments — {user_name}"
                body = "  ·  ".join(lines)
            else:
                title = f"Medication summary — {user_name}"
                body = "  ·  ".join(lines)

            notification_service.send_notification(
                tokens=token_strings,
                title=title,
                body=body,
                data={"type": "medication_summary", "profile_id": str(user_id)},
            )
            logger.info(
                f"[Scheduler] Medication summary sent for user {user_id} ({len(group)} med(s))"
            )

    except Exception as e:
        import traceback
        logger.error(
            f"[Scheduler] Error in send_medication_daily_summary: {e}\n{traceback.format_exc()}"
        )
    finally:
        db.close()


def cleanup_revoked_tokens() -> None:
    """Delete revoked tokens older than 60 minutes (they are already expired)."""
    from app import SessionLocal
    from datetime import datetime, timezone, timedelta

    db: Session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
        deleted = RevokedTokenRepository(db).delete_expired(cutoff)
        logger.info(f"[Scheduler] cleanup_revoked_tokens: {deleted} token(s) deleted")
    except Exception as e:
        logger.error(f"[Scheduler] Error in cleanup_revoked_tokens: {e}")
    finally:
        db.close()


def start_scheduler():
    """Initialize and start the APScheduler background scheduler.

    Registers 3 jobs, all running every 60 seconds:
    - send_user_notifications: initial notification at T+0
    - send_user_retry(5): retry at T+5 minutes
    - send_caregiver_escalations: caregiver alert at T+10 minutes
    """
    my_scheduler = BackgroundScheduler()

    my_scheduler.add_job(
        send_user_notifications,
        CronTrigger(minute="*", second=0),
        id="send_user_notifications",
    )

    my_scheduler.add_job(
        lambda: send_user_retry(5),
        CronTrigger(minute="*", second=0),
        id="send_user_retry_5min",
    )

    my_scheduler.add_job(
        send_medication_moment_notifications,
        CronTrigger(minute="*", second=0),
        id="send_medication_moment_notifications",
    )

    my_scheduler.add_job(
        send_caregiver_escalations,
        CronTrigger(minute="*", second=0),
        id="send_caregiver_escalations",
    )

    my_scheduler.add_job(
        send_medication_daily_summary,
        CronTrigger(hour=20, minute=0),
        id="send_medication_daily_summary",
    )

    my_scheduler.add_job(
        cleanup_revoked_tokens,
        CronTrigger(minute=0),
        id="cleanup_revoked_tokens",
    )

    my_scheduler.start()
    logger.info("[Scheduler] Started")
    return my_scheduler


if __name__ == "__main__":
    import time
    import os
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    from app import init_app

    init_app(os.environ["DATABASE_URL"])
    scheduler = start_scheduler()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("[Scheduler] Stopped")
