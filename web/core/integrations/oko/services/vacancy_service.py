import logging

from core.integrations.oko.repositories.vacancy_repository import OkoVacancyRepository, OkoVacancyRow

logger = logging.getLogger(__name__)


class OkoVacancyService:
    """
    Сервис получения данных вакансии из БД ОКО.

    """

    @staticmethod
    def get_vacancy(vacancy_id: int) -> OkoVacancyRow | None:
        return OkoVacancyRepository.get_by_id(vacancy_id)
