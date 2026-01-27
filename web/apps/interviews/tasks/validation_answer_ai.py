from celery import shared_task
from django.db import transaction

from ..models import Interview, InterviewQuestion
from ..services.answer_processing import InterviewAnswerProcessingService


@shared_task
def run_ai_validation_task(*,
                           interview_id: int,
                           question_id: int,
                           answer_text: str) -> None:
    """Проверка ответа пользователя"""

    interview = Interview.objects.get(id=interview_id)
    question = InterviewQuestion.objects.get(id=question_id)
    processor = InterviewAnswerProcessingService(interview=interview)

    with transaction.atomic():
        processor.process(
            question=question,
            answer_text=answer_text,
        )
