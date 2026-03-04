import os
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GmailConfig:
    sender_email: str
    credentials_path: str
    token_path: str

    @classmethod
    def from_env(cls) -> "GmailConfig":
        sender = os.environ.get("GMAIL_SENDER")
        if not sender:
            raise EnvironmentError("Переменная GMAIL_SENDER не задана в .env")
        return cls(
            sender_email=sender,
            credentials_path=os.environ.get("GMAIL_CREDENTIALS_PATH", "credentials.json"),
            token_path=os.environ.get("GMAIL_TOKEN_PATH", "token.json"),
        )


# ── Параметры события (передаются при вызове) ─────────────────────────────────

@dataclass(frozen=True)
class EventParams:
    recipient_email: str
    start: datetime
    summary: str
    location: str
    duration_minutes: int = 60