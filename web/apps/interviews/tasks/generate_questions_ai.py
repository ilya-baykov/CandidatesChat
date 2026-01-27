from celery import shared_task

from ..models import Interview
from ..services.ai_question_generation.generator import ai_question_generator
from ..services.interview_preparation.context_factory import InterviewContextFactory
from ..services.interview_preparation.preparer import InterviewPreparationService


@shared_task(name="apps.interviews.tasks.generate_questions_for_interview")
def generate_questions_for_interview(interview_id: int, questions_count: int) -> None:
    """Генерирует вопросы для интервью"""
    interview = Interview.objects.get(id=interview_id)

    candidate = InterviewContextFactory.build_candidate(interview.candidate_id)
    vacancy = InterviewContextFactory.build_vacancy(interview.vacancy_id)

    service = InterviewPreparationService(question_generator=ai_question_generator)
    service.prepare_interview(
        interview=interview,
        candidate=candidate,
        vacancy=vacancy,
        questions_count=questions_count
    )
