import logging
from typing import TypedDict

from core.integrations.oko.db.db_client import OkoDBClient

logger = logging.getLogger(__name__)


class OkoVacancyRow(TypedDict):
    id: int
    vacancy: str
    city: str
    job_title: str
    main_responsibilities: str
    required_experience: str
    software_knowledge: str
    wishes_prompt: str


class OkoVacancyRepository:
    """
    Репозиторий для работы с вакансиями в БД ОКО.

    Пока пустой — добавляется заранее,
    чтобы при появлении новых требований
    не нарушать структуру.

    Взаимодействие с OkoVacancyService !
    """

    @staticmethod
    def get_by_id(vacancy_id: int) -> OkoVacancyRow | None:
        logger.info("Получение вакансии из БД ОКО | vacancy_id=%s", vacancy_id)

        select_query = """
            SELECT id, vacancy, city, job_title, main_responsibilities, 
                   required_experience, software_knowledge, wishes_prompt 
            FROM public.candidate_search 
            WHERE id = %s
        """
        with OkoDBClient.cursor() as cursor:
            cursor.execute(select_query, [vacancy_id])
            row = cursor.fetchone()

        if not row:
            logger.warning("Вакансия не найдена в БД ОКО | vacancy_id=%s", vacancy_id)
            return None

        columns = ("id", "vacancy", "city", "job_title",
                   "main_responsibilities", "required_experience", "software_knowledge", "wishes_prompt")

        return OkoVacancyRow(**dict(zip(columns, row)))
