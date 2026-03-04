import base64
from email.mime.multipart import MIMEMultipart


class GmailSender:
    """Отправляет письмо через Gmail API."""

    def __init__(self, service):
        self._service = service

    def send(self, message: MIMEMultipart) -> str:
        """Возвращает Message ID отправленного письма."""
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        result = (
            self._service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return result["id"]
