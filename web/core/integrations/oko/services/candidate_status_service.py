import logging

from core.integrations.oko.enums import CandidateStatusEnum
from core.integrations.oko.repositories.candidate_repository import OkoCandidateRepository

logger = logging.getLogger(__name__)


class OkoCandidateStatusService:
    """
    Сервис изменения статуса кандидата в системе ОКО.

    Это уровень use-case'ов интеграции:
    - инкапсулирует сценарии
    - скрывает SQL
    - служит единственной точкой входа
      для изменения состояния кандидата во внешней системе
    """

    @staticmethod
    def mark_interview_passed(candidate_id: int) -> None:
        """Помечает интервью кандидата как успешно пройденное."""
        OkoCandidateRepository.update_status(
            candidate_id=candidate_id,
            status=CandidateStatusEnum.INTERVIEW_PASSED,
        )

    @staticmethod
    def mark_interview_error(candidate_id: int) -> None:
        """Помечает техническую ошибку при прохождении интервью."""
        OkoCandidateRepository.update_status(
            candidate_id=candidate_id,
            status=CandidateStatusEnum.INTERVIEW_ERROR,
        )

    @staticmethod
    def mark_interview_refusal(candidate_id: int) -> None:
        """Помечает интервью кандидат как 'отказ'."""
        OkoCandidateRepository.update_status(
            candidate_id=candidate_id,
            status=CandidateStatusEnum.REFUSAL_ERROR,
        )
