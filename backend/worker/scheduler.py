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
        send_caregiver_escalations,
        CronTrigger(minute="*", second=0),
        id="send_caregiver_escalations",
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
