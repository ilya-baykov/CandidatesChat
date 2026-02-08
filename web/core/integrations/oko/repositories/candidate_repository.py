import logging

from core.integrations.oko.enums import CandidateStatusEnum
from core.integrations.oko.db.db_client import OkoDBClient

logger = logging.getLogger(__name__)


class OkoCandidateRepository:
    """
    Репозиторий для работы с таблицей public.candidates (БД ОКО).
    """

    @staticmethod
    def update_status(*, candidate_id: int, status: CandidateStatusEnum) -> None:
        """
        Обновляет статус кандидата в БД ОКО.
        """
        logger.info(
            "Обновление статуса кандидата в ОКО | candidate_id=%s | status=%s",
            candidate_id,
            status.name,
        )

        with OkoDBClient.cursor() as cursor:
            cursor.execute(
                """
                UPDATE public.candidates
                SET status_id = %s
                WHERE id = %s
                """,
                [int(status), candidate_id],
            )

        logger.debug(
            "SQL UPDATE выполнен успешно | candidate_id=%s | status_id=%s",
            candidate_id,
            int(status),
        )

    @staticmethod
    def candidate_exists(candidate_id: int) -> bool:
        logger.info("Проверка существования кандидата в ОКО | candidate_id=%s", candidate_id)

        with OkoDBClient.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM public.candidates
                WHERE id = %s
                LIMIT 1
                """,
                [candidate_id],
            )
            return cursor.fetchone() is not None
