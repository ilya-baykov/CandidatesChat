from abc import ABC, abstractmethod

from django.db import transaction

from apps.interviews.models import Interview, InterviewQuestion
from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.constants import CONSENT_QUESTION_TEXT
from apps.interviews.services.questions import QuestionService
from apps.interviews.tasks.triggers import start_generate_questions
from apps.reference.models import AnswerStatus


class QuestionProvisionStrategy(ABC):
    """Стратегия наполнения интервью вопросами."""

    def provision(self, interview: Interview) -> None:
        """Создаёт consent-вопрос, затем делегирует конкретной стратегии."""
        self._create_consent_question(interview)
        self._provision(interview)

    @abstractmethod
    def _provision(self, interview: Interview) -> None:
        raise NotImplementedError

    @staticmethod
    def _create_consent_question(interview: Interview) -> None:
        default_status = AnswerStatus.objects.get_pending()
        InterviewQuestion.objects.create(
            interview=interview,
            question_text=CONSENT_QUESTION_TEXT,
            order=QuestionService.CONSENT_ORDER,
            status=default_status,
        )


class AIQuestionProvisionStrategy(QuestionProvisionStrategy):
    """Генерирует вопросы через AI (асинхронно через Celery)."""

    def __init__(self, questions_count: int = 5):
        self.questions_count = questions_count

    def _provision(self, interview: Interview) -> None:
        transaction.on_commit(
            lambda: start_generate_questions(
                interview_id=interview.pk,
                questions_count=self.questions_count,
            )
        )


class PredefinedQuestionProvisionStrategy(QuestionProvisionStrategy):
    """Сохраняет заранее подготовленные вопросы."""

    def __init__(self, questions: list[GeneratedQuestion]):
        self.questions = questions

    def _provision(self, interview: Interview) -> None:
        transaction.on_commit(
            lambda: QuestionService.save_predefined(
                interview_id=interview.pk,
                questions=self.questions,
            )
        )
