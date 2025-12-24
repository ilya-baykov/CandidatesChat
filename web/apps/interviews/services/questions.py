from ..collections import AnswerCodes
from ..models import Interview, InterviewQuestion
from ...reference.models import AnswerStatus


class QuestionService:
    """Сервис для работы с вопросами интервью."""

    @staticmethod
    def get_next(interview: Interview) -> InterviewQuestion | None:
        """Возвращает следующий pending вопрос."""
        questions = interview.questions.filter(status__code=AnswerCodes.PENDING)  # noqa
        question = questions.order_by('order').first()
        return question

    @staticmethod
    def get_current(interview: Interview) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения: pending или repeat."""
        questions = interview.questions.filter(status__code__in=[AnswerCodes.PENDING, AnswerCodes.REPEAT])  # noqa
        question = questions.order_by('order').first()
        return question

    @staticmethod
    def mark_answered(question: InterviewQuestion):
        """Отмечает вопрос как answered."""
        question.status = AnswerStatus.objects.get(code=AnswerCodes.ANSWERED)
        question.save(update_fields=["status"])

    @staticmethod
    def mark_repeat(question: InterviewQuestion):
        """Отмечает вопрос как повторяемый."""
        question.status = AnswerStatus.objects.get(code=AnswerCodes.REPEAT)
        question.save(update_fields=["status"])
