from __future__ import annotations

from datetime import datetime

from .send_invite_task import send_calendar_invite_task


def start_send_calendar_invite(
        *,
        interview_id: int,
        candidate_email: str,
        candidate_name: str,
        recruiter_email: str,
        start: datetime,
) -> None:
    """Запускает асинхронную отправку calendar-инвайта."""
    send_calendar_invite_task.delay(
        interview_id=interview_id,
        candidate_email=candidate_email,
        candidate_name=candidate_name,
        recruiter_email=recruiter_email,
        start_iso=start.isoformat(),  # datetime → строка, Celery не сериализует datetime
    )
