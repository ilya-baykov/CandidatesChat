from celery import shared_task

from ..models import Interview
from ..services.ai_question_generation.generator import ai_question_generator
from ..services.interview_preparation.context_factory import InterviewContextFactory
from ..services.interview_preparation.preparer import InterviewPreparationService
from ..services.interviews import InterviewService


@shared_task
def generate_questions_for_interview(interview_id: int, questions_count: int) -> None:
    """Генерирует вопросы для интервью"""
    interview = Interview.objects.get(id=interview_id)

    candidate = InterviewContextFactory.build_candidate(interview.candidate_id)
    vacancy = InterviewContextFactory.build_vacancy(interview.vacancy_id)

    if not candidate or not candidate.resume_text:
        InterviewService.mark_as_failed_precondition(interview)
        return

    if not vacancy:
        InterviewService.mark_as_failed_precondition(interview)
        return

    service = InterviewPreparationService(question_generator=ai_question_generator)
    service.prepare_interview(
        interview=interview,
        candidate=candidate,
        vacancy=vacancy,
        questions_count=questions_count
    )
