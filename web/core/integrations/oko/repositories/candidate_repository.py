from core.integrations.oko.enums import CandidateStatusEnum
from core.integrations.oko.db.db_client import OkoDBClient


class OkoCandidateRepository:
    """
    Репозиторий для работы с таблицей public.candidates (БД ОКО).
    """

    @staticmethod
    def update_status(*, candidate_id: int, status: CandidateStatusEnum) -> None:
        with OkoDBClient.cursor() as cursor:
            """
            Обновляет статус кандидата в БД ОКО.

            :param candidate_id: ID кандидата в системе ОКО
            :param status: новый статус кандидата (CandidateStatusEnum)

            :raises DatabaseError: при проблемах с выполнением SQL
            """
            cursor.execute(
                """
                UPDATE public.candidates
                SET status_id = %s
                WHERE id = %s
                """,
                [int(status), candidate_id],
            )
