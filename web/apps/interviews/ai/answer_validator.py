from apps.interviews.models import InterviewQuestion, Interview
from apps.interviews.services.answer_validation.ai import ai_answer_validator
from apps.interviews.services.answer_validation.dto import AnswerValidationResult


class AnswerAiValidator:
    """Валидатор ответов кандидата на вопрос"""

    VALIDATOR_CLS = ai_answer_validator

    @staticmethod
    def ai_validate_answer(interview: Interview,
                           question_history: str,
                           question: InterviewQuestion,
                           answer_text: str) -> AnswerValidationResult:
        """
        Медленный шаг (для Celery):
        - валидируем ответ через ИИ
        """
        # Валидация ответа пользователя

        validation_result = AnswerAiValidator.VALIDATOR_CLS.validate(
            vacancy_title=interview.vacancy.title,
            vacancy_description=interview.vacancy.vacancy_description,
            question=question,
            answer_text=answer_text,
            question_history=question_history
        )
        return validation_result
