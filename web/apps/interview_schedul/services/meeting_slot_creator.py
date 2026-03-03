from __future__ import annotations
import sys
import os
from datetime import datetime, time, timedelta

import pytz

TIMEZONE = "Europe/Moscow"
SLOT_DURATION_MINUTES = 60

WORK_START = time(10, 0)
WORK_END = time(18, 0)
WORK_DAYS = {0, 1, 2, 3, 4}  # Пн–Пт


def generate_slots(weeks: int = 2) -> list[datetime]:
    """Возвращает все доступные слоты на ближайшие weeks недель."""
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    today = now.date()

    slots: list[datetime] = []
    current = today
    end_date = today + timedelta(weeks=weeks)

    while current < end_date:
        if current.weekday() in WORK_DAYS:
            slot_time = WORK_START
            while slot_time < WORK_END:
                slot_dt = tz.localize(datetime.combine(current, slot_time))
                if slot_dt > now + timedelta(hours=1):
                    slots.append(slot_dt)
                slot_dt_next = slot_dt + timedelta(minutes=SLOT_DURATION_MINUTES)
                slot_time = slot_dt_next.astimezone(tz).time()
        current += timedelta(days=1)

    return slots


def slots_by_week(slots: list[datetime]) -> dict[str, dict[str, list[datetime]]]:
    tz = pytz.timezone(TIMEZONE)
    grouped: dict[str, dict[str, list[datetime]]] = {}
    for slot in slots:
        local = slot.astimezone(tz)
        week_key = f"Неделя {local.date().isocalendar()[1]}"
        day_key = local.strftime("%Y-%m-%d")
        grouped.setdefault(week_key, {}).setdefault(day_key, []).append(slot)
    return grouped


def send_calendar_invite(
        *,
        candidate_email: str,
        candidate_name: str,
        recruiter_email: str,
        start: datetime,
        location: str = "Google Meet",
        duration_minutes: int = 60,
        summary: str = "Tech Interview",
) -> str | None:
    """
    Отправляет calendar-инвайт РЕКРУТЕРУ, чтобы событие появилось в его календаре.
    Кандидат получает отдельное текстовое письмо (без ICS).
    """
    try:
        calendar_invite_path = os.environ.get(
            "CALENDAR_INVITE_MODULE_PATH",
            os.path.join(os.path.dirname(__file__), "..", "..", "calendar_invite"),
        )
        if calendar_invite_path not in sys.path:
            sys.path.insert(0, os.path.abspath(calendar_invite_path))

        from calendar_invite import CalendarInviteService, EventParams  # type: ignore

        os.environ.setdefault("GMAIL_SENDER", recruiter_email)

        service = CalendarInviteService()
        message_id = service.send_invite(
            EventParams(
                # ← инвайт летит РЕКРУТЕРУ
                recipient_email=recruiter_email,
                start=start,
                summary=f"{summary} — {candidate_name} ({candidate_email})",
                location=location,
                duration_minutes=duration_minutes,
            )
        )

        # Отдельное текстовое письмо кандидату
        _send_candidate_confirmation(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=recruiter_email,
            start=start,
            location=location,
            duration_minutes=duration_minutes,
        )

        return message_id

    except Exception as exc:
        import logging
        logging.getLogger(__name__).exception("Failed to send calendar invite: %s", exc)
        return None


def _send_candidate_confirmation(
        *,
        candidate_email: str,
        candidate_name: str,
        recruiter_email: str,
        start: datetime,
        location: str,
        duration_minutes: int,
) -> None:
    """Простое текстовое письмо кандидату: где и когда."""
    from django.core.mail import send_mail

    tz = pytz.timezone(TIMEZONE)
    local_start = start.astimezone(tz)
    local_end   = (start + timedelta(minutes=duration_minutes)).astimezone(tz)

    body = (
        f"Привет, {candidate_name}!\n\n"
        f"Ваше интервью подтверждено:\n\n"
        f"  📅 Дата:   {local_start:%d.%m.%Y}\n"
        f"  🕐 Время:  {local_start:%H:%M} – {local_end:%H:%M} МСК\n"
        f"  📍 Место:  {location}\n\n"
        f"Если возникнут вопросы — напишите рекрутеру: {recruiter_email}\n\n"
        f"Удачи! 🚀"
    )

    send_mail(
        subject="Ваше интервью подтверждено",
        message=body,
        from_email=recruiter_email,
        recipient_list=[candidate_email],
        fail_silently=True,
    )