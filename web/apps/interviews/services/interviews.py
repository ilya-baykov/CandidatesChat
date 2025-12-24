from django.utils import timezone

from ..collections import InterviewCodes
from ..models import Interview
from ..services import QuestionService
from ...reference.models import InterviewStatus


class InterviewService:
    """Сервис для работы с интервью."""

    @staticmethod
    def complete_if_done(interview: Interview):
        """Завершает интервью, если все вопросы answered."""
        if not QuestionService.get_current(interview):
            interview.status = InterviewStatus.objects.get(code=InterviewCodes.COMPLETED)
            interview.completed_at = timezone.now()
            interview.save(update_fields=["status", "completed_at"])
