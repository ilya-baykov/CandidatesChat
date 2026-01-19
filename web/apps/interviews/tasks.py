from celery import shared_task
from django.db import transaction

from .models import Interview, InterviewQuestion
from .services.answer_processing import InterviewAnswerProcessingService


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
)
def run_ai_validation_task(
    self,
    *,
    interview_id: int,
    question_id: int,
    answer_text: str,
) -> None:
    """
    Celery-task — транспорт для async use-case.
    """

    interview = (
        Interview.objects
        .select_related("vacancy")
        .get(id=interview_id)
    )

    question = InterviewQuestion.objects.get(id=question_id)

    processor = InterviewAnswerProcessingService(interview=interview)

    # Одна бизнес-операция — одна транзакция
    with transaction.atomic():
        processor.process(
            question=question,
            answer_text=answer_text,
        )
