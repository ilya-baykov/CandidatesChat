from __future__ import annotations

import logging
from datetime import datetime

from celery import shared_task

from apps.interview_schedule.models import InterviewSlot
from apps.interview_schedule.services.meeting_slot_creator import MeetingSlotCreator

logger = logging.getLogger(__name__)

_meeting_creator = MeetingSlotCreator()


@shared_task(name="apps.interview_schedule.tasks.send_calendar_invite_task")
def send_calendar_invite_task(
        *,
        interview_id: int,
        candidate_email: str,
        candidate_name: str,
        recruiter_email: str,
        start_iso: str,
) -> None:
    """
    Отправляет calendar-инвайт рекрутеру и подтверждение кандидату.
    При ошибке повторяет попытку до 3 раз с интервалом 60 сек.
    """
    start = datetime.fromisoformat(start_iso)

    try:
        msg_id = _meeting_creator.create(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            recruiter_email=recruiter_email,
            start=start
        )
        if msg_id:
            InterviewSlot.objects.filter(pk=interview_id).update(
                gmail_message_id=msg_id,
                status=InterviewSlot.STATUS_CONFIRMED,
            )
            logger.info("Interview %s Отправлено. Message ID: %s", interview_id, msg_id)
        else:
            logger.warning("Interview %s: Приглашение не отправлено (msg_id is None)", interview_id)
    except Exception as exc:
        logger.exception("send_calendar_invite_task failed : %s", exc)
