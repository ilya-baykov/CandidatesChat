import logging

from django.utils import timezone
from django.db import models

from ..collections import InterviewCodes
from ..models import Interview, InterviewAnswer
from ..services.questions import QuestionService
from ...reference.models import InterviewStatus

logger = logging.getLogger(__name__)


class InterviewService:
    """Сервис для работы с интервью."""

    @staticmethod
    def complete_if_done(interview: Interview) -> bool:
        """Завершает интервью, если все вопросы answered."""
        if not QuestionService.get_current(interview):
            interview.total_score = InterviewService._calculate_total_score(interview)
            interview.status = InterviewStatus.objects.get(code=InterviewCodes.COMPLETED)
            interview.completed_at = timezone.now()
            interview.save(update_fields=["status", "completed_at", "total_score"])
            return True
        return False

    @staticmethod
    def get_by_candidate_and_vacancy(candidate_id, vacancy_id):
        """Возвращает интервью по паре candidate_id + vacancy_id."""
        interview = Interview.objects.get(candidate_id=candidate_id, vacancy_id=vacancy_id)
        return interview

    @staticmethod
    def mark_as_failed_precondition(interview: Interview) -> None:
        """Помечает интервью как невалидное"""
        failed_status = InterviewStatus.objects.get(code=InterviewCodes.FAILED_PRECONDITION)
        interview.status = failed_status
        interview.save(update_fields=["status"])

    @staticmethod
    def set_status(interview: Interview, status_code: str) -> None:
        """
        Универсальный метод для установки статуса интервью.

        Пример использования:
            InterviewService.set_status(interview, InterviewCodes.IN_PROGRESS)
        """
        status_obj = InterviewStatus.objects.get(code=status_code)
        interview.status = status_obj
        interview.save(update_fields=["status"])

    @staticmethod
    def _calculate_total_score(interview: Interview) -> float:
        """Вычисляет средний score всех ответов интервью."""
        answers = InterviewAnswer.objects.filter(interview_question__interview=interview, score__isnull=False)
        avg_score = answers.aggregate(avg_score=models.Avg('score'))['avg_score']
        logger.debug(f"Для interview={interview.pk}; Количество ответов-{answers.count()} avg_score={avg_score}")
        return avg_score or 0.0
