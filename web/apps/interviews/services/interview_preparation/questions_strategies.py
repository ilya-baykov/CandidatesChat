from abc import ABC, abstractmethod

from django.db import transaction

from apps.interviews.models import Interview
from apps.interviews.services.ai_question_generation.dto import GeneratedQuestion
from apps.interviews.services.questions import QuestionService
from apps.interviews.tasks.triggers import start_generate_questions


class QuestionProvisionStrategy(ABC):
    """Стратегия наполнения интервью вопросами."""

    @abstractmethod
    def provision(self, interview: Interview) -> None:
        raise NotImplementedError


class AIQuestionProvisionStrategy(QuestionProvisionStrategy):
    """Генерирует вопросы через AI (асинхронно через Celery)."""

    def __init__(self, questions_count: int = 5):
        self.questions_count = questions_count

    def provision(self, interview: Interview) -> None:
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

    def provision(self, interview: Interview) -> None:
        transaction.on_commit(
            lambda: QuestionService.save_predefined(
                interview_id=interview.pk,
                questions=self.questions,
            )
        )
