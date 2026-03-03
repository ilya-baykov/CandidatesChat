from .ai_question_generation.dto import GeneratedQuestion
from .constants import CONSENT_POSITIVE, CONSENT_NEGATIVE
# from .interviews import InterviewService
from ..models import Interview, InterviewQuestion
from ...reference.models import AnswerStatus
from ..collections import AnswerCodes, AnswerCodeLiteral, InterviewCodes


class QuestionService:
    """Сервис для работы с вопросами интервью."""

    CONSENT_ORDER = -1

    @staticmethod
    def get_next(interview: Interview) -> InterviewQuestion | None:
        """Возвращает следующий pending вопрос."""
        code_value = AnswerCodes.PENDING.value
        questions = interview.questions.filter(status__code=code_value)  # noqa
        question = questions.order_by('order').first()
        return question

    @staticmethod
    def get_current(interview: Interview) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения: pending или repeat."""
        codes_values = [AnswerCodes.PENDING.value, AnswerCodes.REPEAT.value, AnswerCodes.VALIDATING.value]
        questions = interview.questions.filter(status__code__in=codes_values)  # noqa
        question = questions.order_by('order').first()
        return question

    @staticmethod
    def mark_status(question: InterviewQuestion, code: AnswerCodeLiteral) -> InterviewQuestion | None:
        """Отмечает вопрос с нужным статусом."""
        code_value = code.value  # Получаем строковое значение кода
        question.status = AnswerStatus.objects.get(code=code_value)
        question.save(update_fields=["status"])



    @staticmethod
    def is_consent_question(question: InterviewQuestion) -> bool:
        """Вопрос о согласии определяется исключительно по порядку."""
        return question.order == QuestionService.CONSENT_ORDER

    @staticmethod
    def check_consent_answer(answer_text: str) -> bool | None:
        """
        True  — согласие
        False — отказ
        None  — непонятно, повторить вопрос
        """
        normalized = answer_text.lower().strip()
        if any(word in normalized for word in CONSENT_POSITIVE):
            return True
        if any(word in normalized for word in CONSENT_NEGATIVE):
            return False
        return None
