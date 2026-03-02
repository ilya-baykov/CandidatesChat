import logging

from celery import shared_task
from django.db import transaction

from core.integrations.oko.services.candidate_status_service import OkoCandidateStatusService
from ..collections import AnswerCodes
from ..models import Interview, InterviewQuestion
from ..services.answer_processing import InterviewAnswerProcessingService
from ..services.consent_processing_service import ConsentProcessingService
from ..services.interview_preparation.context_factory import InterviewContextFactory
from ..services.questions import QuestionService

logger = logging.getLogger(__name__)


@shared_task(name="apps.interviews.tasks.run_ai_validation_task")
def run_ai_validation_task(*,
                           interview_id: int,
                           question_id: int,
                           answer_text: str) -> None:
    """Проверка ответа пользователя"""

    logger.info(f"Запуск задачи run_ai_validation_task для "
                f"Интервью:{interview_id}; Вопрос:{question_id}")

    interview = Interview.objects.get(id=interview_id)
    question = InterviewQuestion.objects.get(id=question_id)

    # Проверка согласия на обработку
    if QuestionService.is_consent_question(question):
        ConsentProcessingService(interview=interview, question=question).process(answer_text)
        return

    vacancy = InterviewContextFactory.build_vacancy(interview.vacancy_id)
    processor = InterviewAnswerProcessingService(interview=interview, question=question, vacancy=vacancy)

    try:
        with transaction.atomic():
            logger.info(f"Начало обработки ответа для Интервью:{interview_id}, Вопрос:{question_id}")
            processor.process(answer_text=answer_text)
            logger.info(f"Успешно обработан ответ для Интервью:{interview_id}, Вопрос:{question_id}")



    except Exception as e:
        QuestionService.mark_status(question=question, code=AnswerCodes.FAILED_VALIDATION)
        OkoCandidateStatusService.mark_interview_error(candidate_id=interview.candidate_id)
        logger.error(f"Ошибка:{e} при выполнении задачи run_ai_validation_task для "
                     f"Интервью:{interview_id}; Вопос:{question_id}")
