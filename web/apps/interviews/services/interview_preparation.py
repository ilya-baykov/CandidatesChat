from apps.interviews.models import InterviewQuestion, Interview
from apps.interviews.services.ai_question_generation.generator import QuestionGenerator
from apps.reference.models import AnswerStatus


class InterviewPreparationService:

    def __init__(self, question_generator: QuestionGenerator):
        self.question_generator = question_generator

    def prepare_interview(self, *,
                          interview,
                          questions_count: int) -> None:

        # Проверка наличия вопросов
        if not self._has_no_questions(interview=interview):
            raise RuntimeError("Вопросы для этого интервью уже сгенерированы. "
                               "Удалите существующие, если нужно перегенерировать.")

        candidate = interview.candidate
        vacancy = interview.vacancy

        questions = self.question_generator.generate(
            vacancy_title=vacancy.title,
            vacancy_description=vacancy.vacancy_description or "",
            candidate_resume=candidate.resume_text or "",
            questions_count=questions_count,
        )

        default_status = AnswerStatus.objects.get_pending()  # Всегда устанавливаем статус по-умолчанию (pending)
        if default_status is None:
            raise RuntimeError("Не найден активный статус ответа по умолчанию")

        for q in questions:
            InterviewQuestion.objects.create(
                interview=interview,
                question_text=q.text,
                order=q.order,
                status=default_status,
            )

    def _has_no_questions(self, interview: Interview) -> bool:
        """Проверяет, можно ли генерировать вопросы для этого интервью."""
        questions_exists = interview.questions.exists()  # noqa
        if questions_exists:
            return False
        return True
