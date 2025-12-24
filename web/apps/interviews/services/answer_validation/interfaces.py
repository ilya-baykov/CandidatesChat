from abc import ABC, abstractmethod

from ...models import InterviewQuestion
from .dto import AnswerValidationResult


class AnswerValidator(ABC):
    """
    Интерфейс сервиса проверки ответа кандидата.
    """

    @abstractmethod
    def validate(self, *,
                 question: InterviewQuestion, answer_text: str,
                 question_history: str | None = None) -> AnswerValidationResult:
        """
        Проверяет ответ кандидата и возвращает результат проверки.
        """
        raise NotImplementedError
