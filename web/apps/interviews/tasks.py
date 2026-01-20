from celery import shared_task
from django.db import transaction

from .models import Interview, InterviewQuestion
from .services.ai_question_generation.generator import ai_question_generator
from .services.answer_processing import InterviewAnswerProcessingService
from .services.interview_preparation import InterviewPreparationService


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
    print("Celery-task была взята в работу")
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


@shared_task
def generate_questions_for_interview(interview_id: int, questions_count: int) -> None:
    interview = Interview.objects.select_related("candidate", "vacancy").get(id=interview_id)
    service = InterviewPreparationService(question_generator=ai_question_generator)
    service.prepare_interview(interview=interview, questions_count=questions_count)
