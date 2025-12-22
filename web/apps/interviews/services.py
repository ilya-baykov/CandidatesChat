from django.utils import timezone

from apps.interviews.collections import AnswerCodes, InterviewCodes
from apps.interviews.models import InterviewQuestion, Interview, InterviewAnswer
from apps.reference.models import AnswerStatus, InterviewStatus


class QuestionService:
    """Сервис для работы с вопросами интервью."""

    @staticmethod
    def get_next(interview: Interview) -> InterviewQuestion | None:
        """
        Возвращает следующий вопрос со статусом 'pending'.
        Если вопросов больше нет — возвращает None.
        """
        return interview.questions.filter(status__code=AnswerCodes.PENDING).order_by("order").first()  # noqa

    @staticmethod
    def mark_answered(question: InterviewQuestion):
        """
        Меняет статус вопроса на 'answered'.
        """
        answered_status = AnswerStatus.objects.get(code=AnswerCodes.ANSWERED)
        question.status = answered_status
        question.save()


class AnswerService:
    """Сервис для работы с ответами кандидата."""

    @staticmethod
    def save(question: InterviewQuestion, answer_text: str, score: float = None) -> InterviewAnswer:
        """
        Сохраняет или обновляет ответ на вопрос.
        Score можно указать вручную (имитация ИИ на текущем этапе).
        """
        answer, created = InterviewAnswer.objects.get_or_create(
            interview_question=question,
            defaults={"answer_text": answer_text, "score": score, "answered_at": timezone.now()}
        )
        if not created:
            # если ответ уже существует, обновляем его
            answer.answer_text = answer_text
            answer.score = score
            answer.answered_at = timezone.now()
            answer.save()
        return answer


class InterviewService:
    """Сервис для работы с интервью."""

    @staticmethod
    def complete_if_done(interview: Interview):
        """
        Проверяет, остались ли pending вопросы.
        Если вопросов больше нет, помечает интервью как COMPLETED и ставит время завершения.
        """
        if not QuestionService.get_next(interview):
            completed_status = InterviewStatus.objects.get(code=InterviewCodes.COMPLETED)
            interview.status = completed_status
            interview.completed_at = timezone.now()
            interview.save()


class InterviewFlowService:
    """
    Оркестратор flow интервью:
    - Сохраняет ответы кандидата
    - Меняет статус вопросов
    - Завершает интервью при необходимости
    """

    def __init__(self, interview: Interview):
        self.interview = interview

    def submit_answer(self, question: InterviewQuestion, answer_text: str,
                      score: float = None) -> InterviewQuestion | None:
        """
        Основной метод для отправки ответа кандидатом.
        1. Сохраняет ответ через AnswerService
        2. Меняет статус вопроса через QuestionService
        3. Завершает интервью через InterviewService, если вопросов больше нет
        Возвращает следующий pending вопрос или None, если интервью завершено.
        """
        AnswerService.save(question, answer_text, score)
        QuestionService.mark_answered(question)
        InterviewService.complete_if_done(self.interview)
        return QuestionService.get_next(self.interview)
