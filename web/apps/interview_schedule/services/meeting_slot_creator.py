"""
apps/interview_schedule/services/meeting_slot_creator.py

Классы для генерации слотов и отправки приглашений на интервью.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import pytz
from django.core.mail import send_mail

from config.settings.base import TIME_ZONE
from .calendar_invite_service import CalendarInviteService
from .dto import EventParams
from ..constants import SLOT_DURATION_MINUTES, EMAIL_ACCEPT_BODY_TEMPLATE

logger = logging.getLogger(__name__)


class MeetingSlotCreator:
    """
    Отправляет calendar-инвайт рекрутеру и письмо-подтверждение кандидату.

    Пример:
        creator = MeetingSlotCreator()
        creator.create(
            candidate_email="ivan@example.com",
            candidate_name="Иван Иванов",
            recruiter_email="hr@company.com",
            start=slot_datetime,
        )
    """

    def __init__(
            self,
            default_location: str = "Google Meet",
            default_summary: str = "Tech Interview",
            slot_duration_minutes: int = SLOT_DURATION_MINUTES,
    ) -> None:
        self._tz = pytz.timezone(TIME_ZONE)
        self._default_location = default_location
        self._default_summary = default_summary
        self._slot_duration_minutes = slot_duration_minutes
        self._invite_service = CalendarInviteService()

    def create(
            self,
            *,
            candidate_email: str,
            candidate_name: str,
            recruiter_email: str,
            start: datetime,
            location: str | None = None,
            summary: str | None = None,
            duration_minutes: int | None = None,
    ) -> str | None:
        """
        Отправляет инвайт рекрутеру и подтверждение кандидату.
        Возвращает Gmail Message ID или None при ошибке.
        """
        location = location or self._default_location
        summary = summary or self._default_summary
        duration_minutes = duration_minutes or self._slot_duration_minutes

        try:
            message_id = self._invite_service.send_invite(
                EventParams(
                    recipient_email=recruiter_email,
                    start=start,
                    summary=f"{summary} — {candidate_name} ({candidate_email})",
                    location=location,
                    duration_minutes=duration_minutes,
                )
            )
            self._send_candidate_confirmation(
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                recruiter_email=recruiter_email,
                start=start,
                location=location,
                duration_minutes=duration_minutes,
            )
            return message_id

        except Exception:
            logger.exception("Failed to create meeting slot")
            return None

    def _send_candidate_confirmation(
            self,
            *,
            candidate_email: str,
            candidate_name: str,
            recruiter_email: str,
            start: datetime,
            location: str,
            duration_minutes: int,
    ) -> None:
        local_start = start.astimezone(self._tz)
        local_end = (start + timedelta(minutes=duration_minutes)).astimezone(self._tz)

        body = EMAIL_ACCEPT_BODY_TEMPLATE.format(
            candidate_name=candidate_name,
            local_start=local_start,
            local_end=local_end,
            location=location,
            recruiter_email=recruiter_email
        )

        send_mail(
            subject="Ваше интервью подтверждено",
            message=body,
            from_email=recruiter_email,
            recipient_list=[candidate_email],
            fail_silently=True,
        )
