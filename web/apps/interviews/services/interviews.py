from django.utils import timezone
from django.db import transaction

from ..collections import InterviewCodes
from ..models import Interview
from ..services.questions import QuestionService
from ...reference.models import InterviewStatus
from ...interviews.tasks import generate_questions_for_interview


class InterviewService:
    """Сервис для работы с интервью."""

    @staticmethod
    def complete_if_done(interview: Interview) -> bool:
        """Завершает интервью, если все вопросы answered."""
        if not QuestionService.get_current(interview):
            interview.status = InterviewStatus.objects.get(code=InterviewCodes.COMPLETED)
            interview.completed_at = timezone.now()
            interview.save(update_fields=["status", "completed_at"])
            return True
        return False

    @staticmethod
    def get_by_candidate_and_vacancy(candidate_id, vacancy_id):
        """Возвращает интервью по паре candidate_id + vacancy_id."""
        interview = Interview.objects.get(candidate_id=candidate_id, vacancy_id=vacancy_id)
        return interview

    @staticmethod
    def create_or_get_interview(candidate_id, vacancy_id, questions_count=5):
        """Создает новое интервью и ставит задачу по генерации вопросов в очередь"""
        with transaction.atomic():
            interview, created = Interview.objects.get_or_create(
                candidate_id=candidate_id,
                vacancy_id=vacancy_id,
                defaults={"status": InterviewStatus.objects.get(code="in_progress"), },
            )

            if created:
                transaction.on_commit(
                    lambda: generate_questions_for_interview.delay(
                        interview_id=interview.pk,
                        questions_count=questions_count,
                    )
                )

            return interview, created
