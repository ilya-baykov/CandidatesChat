from django.utils import timezone

from apps.interviews.models import Interview, InterviewQuestion, InterviewAnswer
from apps.reference.models import AnswerStatus, InterviewStatus
from apps.interviews.collections import AnswerCodes, InterviewCodes


class QuestionService:
    """Сервис для работы с вопросами интервью."""

    @staticmethod
    def get_next(interview: Interview) -> InterviewQuestion | None:
        """Возвращает следующий pending вопрос."""
        questions = interview.questions.filter(status__code=AnswerCodes.PENDING)  # noqa
        question = questions.order_by("order").first()
        return question

    @staticmethod
    def get_current(interview: Interview) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения: pending или repeat."""
        questions = interview.questions.filter(status__code__in=[AnswerCodes.PENDING, AnswerCodes.REPEAT])  # noqa
        question = questions.order_by("order").first()
        return question

    @staticmethod
    def mark_answered(question: InterviewQuestion):
        """Отмечает вопрос как answered."""
        question.status = AnswerStatus.objects.get(code=AnswerCodes.ANSWERED)
        question.save()

    @staticmethod
    def mark_repeat(question: InterviewQuestion):
        """Отмечает вопрос как повторяемый (непонятный ответ)."""
        question.status = AnswerStatus.objects.get(code=AnswerCodes.REPEAT)
        question.save()


class AnswerService:
    """Сервис для работы с ответами кандидата."""

    @staticmethod
    def save(question: InterviewQuestion, answer_text: str, score: float = None) -> InterviewAnswer:
        """Сохраняет или обновляет ответ на вопрос."""
        answer, created = InterviewAnswer.objects.get_or_create(
            interview_question=question,
            defaults={"answer_text": answer_text, "score": score, "answered_at": timezone.now()}
        )
        if not created:
            answer.answer_text = answer_text
            answer.score = score
            answer.answered_at = timezone.now()
            answer.save()
        return answer


class InterviewService:
    """Сервис для работы с интервью."""

    @staticmethod
    def complete_if_done(interview: Interview):
        """Завершает интервью, если все вопросы answered."""
        if not QuestionService.get_current(interview):
            interview.status = InterviewStatus.objects.get(code=InterviewCodes.COMPLETED)
            interview.completed_at = timezone.now()
            interview.save()


class InterviewFlowService:
    """
    Оркестратор flow интервью:
    - Сохраняет ответы кандидата
    - Меняет статус вопросов (answered/repeat)
    - Завершает интервью при необходимости
    """

    def __init__(self, interview: Interview):
        self.interview = interview

    def get_current_question(self) -> InterviewQuestion | None:
        """Возвращает текущий вопрос для отображения кандидату."""
        return QuestionService.get_current(self.interview)

    def submit_answer(self, question: InterviewQuestion, answer_text: str,
                      is_correct: bool) -> InterviewQuestion | None:
        """
        Сохраняет ответ и управляет статусом вопроса.
        - is_correct=True → question.mark_answered()
        - is_correct=False → question.mark_repeat()
        """
        AnswerService.save(question, answer_text)

        if is_correct:
            QuestionService.mark_answered(question)
        else:
            QuestionService.mark_repeat(question)

        InterviewService.complete_if_done(self.interview)

        return self.get_current_question()
