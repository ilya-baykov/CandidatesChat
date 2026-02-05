from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AnswerValidationResult:
    """
    Результат проверки ответа кандидата.
    Используется для управления flow (без сохранения в БД).
    """

    is_correct: bool  # Корректность ответа
    reply_message: Optional[str]  # Ответное сообщение
    score: Optional[float] = None  # Оценка ответа
    justification: Optional[str] = None  # Описание
