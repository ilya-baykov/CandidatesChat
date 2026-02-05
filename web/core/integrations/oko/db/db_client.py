import logging
from contextlib import contextmanager
from django.db import connection

logger = logging.getLogger(__name__)


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
        """Контекстный менеджер для cursor'а БД ОКО."""
        logger.debug("Открытие cursor для БД ОКО")

        try:
            with connection.cursor() as cursor:
                yield cursor
        except Exception:
            logger.exception("Ошибка при работе с cursor БД ОКО")
            raise
        finally:
            logger.debug("Закрытие cursor БД ОКО")
