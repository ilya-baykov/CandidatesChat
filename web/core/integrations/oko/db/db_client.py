from contextlib import contextmanager
from django.db import connection


class OkoDBClient:
    """
    Low-level клиент для работы с БД ОКО.

    Использует django.db.connection, но:
    - не зависит от ORM
    - всегда работает с явным указанием схем
    - изолирует доступ к внешней БД

    """

    @staticmethod
    @contextmanager
    def cursor():
        """Контекстный менеджер для получения cursor'а"""
        with connection.cursor() as cursor:
            yield cursor
