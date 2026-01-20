from apps.interviews.models import InterviewQuestion
from apps.interviews.services.ai_question_generation.generator import QuestionGenerator
from apps.reference.models import AnswerStatus


class InterviewPreparationService:

    def __init__(self, question_generator: QuestionGenerator):
        self.question_generator = question_generator

    def prepare_interview(self, *,
                          interview,
                          questions_count: int) -> None:
        candidate = interview.candidate
        vacancy = interview.vacancy

        questions = self.question_generator.generate(
            vacancy_title=vacancy.title,
            vacancy_description=vacancy.vacancy_description or "",
            candidate_resume=candidate.resume_text or "",
            questions_count=questions_count,
        )

        default_status = AnswerStatus.objects.default()
        if default_status is None:
            raise RuntimeError("Не найден активный статус ответа по умолчанию")

        for q in questions:
            InterviewQuestion.objects.create(
                interview=interview,
                question_text=q.text,
                order=q.order,
                status=default_status,
            )
