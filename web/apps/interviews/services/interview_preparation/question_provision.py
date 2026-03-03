import logging

from apps.interviews.collections import InterviewCodes
from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.interviews import InterviewService
from apps.reference.models import AnswerStatus

logger = logging.getLogger(__name__)


class QuestionProvisionService:
    """
    Сервис выполнения стратегий наполнения вопросами.
    Отвечает за статусы интервью по результату — IN_PROGRESS или FAILED.
    """

    @staticmethod
    def run_predefined(interview_id: int, questions: list[GeneratedQuestion]) -> None:
        """Сохраняет готовые вопросы и переводит интервью в нужный статус."""
        interview = Interview.objects.get(id=interview_id)
        try:
            default_status = AnswerStatus.objects.get_pending()
            InterviewQuestion.objects.bulk_create([
                InterviewQuestion(
                    interview=interview,
                    question_text=q.text,
                    order=q.order,
                    status=default_status,
                )
                for q in questions
            ])
            InterviewService.set_status(interview=interview, status_code=InterviewCodes.IN_PROGRESS)

        except Exception as e:
            logger.critical(f"Не удалось сохранить predefined вопросы для интервью {interview.pk}: {e}")
            InterviewService.mark_as_failed_precondition(interview)
