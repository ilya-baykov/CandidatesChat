"""
Фасад: оркестрирует сборку ICS, письма и отправку через Gmail.
Бизнес-логика приложения — здесь.
Низкоуровневая работа с Gmail — в core/utilities/gmail/.
"""

import logging

from django.conf import settings

from core.utilities.gmail import EmailBuilder, GmailAuth, GmailSender, ICSBuilder

from .dto import EventParams

logger = logging.getLogger(__name__)


class CalendarInviteService:
    """
    Отправляет calendar-инвайт через Gmail API.

    Пример:
        service = CalendarInviteService()
        message_id = service.send_invite(EventParams(
            recipient_email="recruiter@company.com",
            start=datetime(2025, 6, 1, 14, 0, tzinfo=...),
            summary="Tech Interview — Ivan Ivanov",
            location="Google Meet",
        ))
    """

    def __init__(self) -> None:
        self._sender_email: str = settings.GMAIL_SENDER
        self._ics_builder = ICSBuilder()
        self._email_builder = EmailBuilder()
        self._auth = GmailAuth()

    def send_invite(self, params: EventParams) -> str:
        """Собирает ICS, письмо и отправляет. Возвращает Gmail Message ID."""
        ics_bytes = self._ics_builder.build(params, self._sender_email)
        message = self._email_builder.build(self._sender_email, params, ics_bytes)
        service = self._auth.get_service()
        message_id = GmailSender(service).send(message)
        logger.info("Calendar invite sent. Message ID: %s", message_id)
        return message_id
