"""
core/utilities/gmail/email_builder.py

Сборка MIME-письма с ICS-вложением.
Не зависит от Django.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apps.interview_schedule.services.dto import EventParams

_EMAIL_SUBJECT = "Calendar Invitation"

_EMAIL_BODY_TEMPLATE = (
    "Вы получили приглашение на встречу.\n\n"
    "Тема: {summary}\n"
    "Время: {start:%d.%m.%Y %H:%M} МСК\n"
    "Место: {location}\n\n"
    "Если приглашение не добавилось автоматически — "
    "откройте вложение invite.ics вручную."
)


class EmailBuilder:
    """Собирает MIME-письмо с ICS-вложением."""

    def build(self, sender: str, params: EventParams, ics_bytes: bytes) -> MIMEMultipart:
        msg = MIMEMultipart("mixed")
        msg["Subject"] = _EMAIL_SUBJECT
        msg["From"] = sender
        msg["To"] = params.recipient_email

        msg.attach(self._text_part(params))
        msg.attach(self._calendar_part(ics_bytes))
        return msg

    @staticmethod
    def _text_part(params: EventParams) -> MIMEText:
        body = _EMAIL_BODY_TEMPLATE.format(
            summary=params.summary,
            start=params.start,
            location=params.location,
        )
        return MIMEText(body, "plain", "utf-8")

    @staticmethod
    def _calendar_part(ics_bytes: bytes) -> MIMEText:
        part = MIMEText(ics_bytes.decode("utf-8"), "calendar", "utf-8")
        part.replace_header(
            "Content-Type",
            'text/calendar; charset="utf-8"; method=REQUEST; name="invite.ics"',
        )
        part.add_header("Content-Disposition", "attachment", filename="invite.ics")
        return part
