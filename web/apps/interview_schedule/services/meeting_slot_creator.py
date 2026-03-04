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
            default_location: str = "Outlook",
            default_summary: str = "Интервью",
            slot_duration_minutes: int = SLOT_DURATION_MINUTES,
    ) -> None:
        self._tz = pytz.timezone(TIME_ZONE)
        self._default_location = default_location
        self._default_summary = default_summary
        self._slot_duration_minutes = slot_duration_minutes
        self._invite_service = CalendarInviteService()

    def create(self, *,
               candidate_email: str,
               candidate_name: str,
               recruiter_email: str,
               start: datetime,
               location: str | None = None,
               summary: str | None = None,
               duration_minutes: int | None = None,
               comment: str = "") -> bool:

        location = location or self._default_location
        summary = summary or self._default_summary
        duration_minutes = duration_minutes or self._slot_duration_minutes

        try:
            recruiter_msg_id = self._invite_service.send_invite(
                EventParams(
                    recipient_email=recruiter_email,
                    start=start,
                    summary=f"{summary} — {candidate_name} ({candidate_email})",
                    location=location,
                    duration_minutes=duration_minutes,
                )
            )
            logger.info("Инвайт рекрутеру отправлен | to=%s | message_id=%s", recruiter_email, recruiter_msg_id)

            candidate_msg_id = self._invite_service.send_invite(
                EventParams(
                    recipient_email=candidate_email,
                    start=start,
                    summary=f"{summary} — {candidate_name}",
                    location=location,
                    duration_minutes=duration_minutes,
                )
            )
            logger.info("Инвайт кандидату отправлен | to=%s | message_id=%s", candidate_email, candidate_msg_id)

            return bool(recruiter_msg_id and candidate_msg_id)

        except Exception as e:
            logger.exception("Failed to create meeting slot:%s", e)
            return False
