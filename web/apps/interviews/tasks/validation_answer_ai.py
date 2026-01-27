from celery import shared_task
from django.db import transaction

from ..models import Interview, InterviewQuestion
from ..services.answer_processing import InterviewAnswerProcessingService
from ..services.interview_preparation.context_factory import InterviewContextFactory


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

    with transaction.atomic():
        processor.process(answer_text=answer_text)
