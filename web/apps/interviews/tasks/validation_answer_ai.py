import logging

from celery import shared_task
from django.db import transaction

from ..collections import AnswerCodes
from ..models import Interview, InterviewQuestion
from ..services.answer_processing import InterviewAnswerProcessingService
from ..services.interview_preparation.context_factory import InterviewContextFactory
from ..services.questions import QuestionService

logger = logging.getLogger(__name__)


@shared_task(name="apps.interviews.tasks.run_ai_validation_task")
def run_ai_validation_task(*,
                           interview_id: int,
                           question_id: int,
                           answer_text: str) -> None:
    """Проверка ответа пользователя"""

    interview = Interview.objects.get(id=interview_id)
    vacancy = InterviewContextFactory.build_vacancy(interview.vacancy_id)
    question = InterviewQuestion.objects.get(id=question_id)
    processor = InterviewAnswerProcessingService(interview=interview, question=question, vacancy=vacancy)

    try:
        with transaction.atomic():
            processor.process(answer_text=answer_text)


    except Exception as e:
        QuestionService.mark_status(question=question, code=AnswerCodes.FAILED_VALIDATION)
        logger.error(f"Ошибка:{e} при выполнении задачи run_ai_validation_task для "
                     f"Интервью:{interview_id}; Вопос:{question_id}")
