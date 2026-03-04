"""
core/utilities/gmail/gmail_auth.py

OAuth2-авторизация для Gmail API.
Читает пути к credentials/token из Django settings.
"""

import os

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from apps.interview_schedule.constants import SCOPES


class GmailAuth:
    """
    Управляет OAuth2-токеном для Gmail API.

    Берёт пути из settings:
        GMAIL_CREDENTIALS_PATH  — путь к credentials.json
        GMAIL_TOKEN_PATH        — путь к token.json
    """

    def get_service(self):
        creds = self._load_credentials()
        if not creds or not creds.valid:
            creds = self._refresh_or_authorize(creds)
            self._save_credentials(creds)
        return build("gmail", "v1", credentials=creds)

    # ── private ──────────────────────────────────────────────────────────────

    @staticmethod
    def _load_credentials() -> Credentials | None:
        path = settings.GMAIL_TOKEN_PATH
        if os.path.exists(path):
            return Credentials.from_authorized_user_file(path, SCOPES)
        return None

    @staticmethod
    def _refresh_or_authorize(creds: Credentials | None) -> Credentials:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GMAIL_CREDENTIALS_PATH, SCOPES
        )
        return flow.run_local_server(port=0)

    @staticmethod
    def _save_credentials(creds: Credentials) -> None:
        with open(settings.GMAIL_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
