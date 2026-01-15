from abc import ABC, abstractmethod

from apps.interviews.models import InterviewQuestion
from apps.interviews.services.ai_answer_validation.dto import AnswerValidationResult
from apps.interviews.services.ai_answer_validation.prompts import PromptGenerator
from core.ai_service.clients import NeuralGatewayClient, gpt_4_model
from core.utilities.json_extractor import JsonExtractor


class AnswerValidator(ABC):
    """
    Интерфейс сервиса проверки ответа кандидата.
    """

    @abstractmethod
    def validate(self, *,
                 question: InterviewQuestion, answer_text: str, vacancy_title: str, vacancy_description: str,
                 question_history: str | None = None) -> AnswerValidationResult:
        """
        Проверяет ответ кандидата и возвращает результат проверки.
        """
        raise NotImplementedError


class AIAnswerValidator(AnswerValidator):
    """Валидатор ответа кандидата через ИИ."""

    def __init__(self, client: NeuralGatewayClient, max_attempts: int = 3):
        self.client = client
        self.max_attempts = max_attempts

    def validate(self, *, question: InterviewQuestion, answer_text: str,
                 vacancy_title: str, vacancy_description: str,
                 question_history: str | None = None) -> AnswerValidationResult:

        prompt = PromptGenerator.validate_answer(
            vacancy_title=vacancy_title,
            vacancy_description=vacancy_description,
            question_text=question.question_text,
            user_answer=answer_text,
            question_history=question_history,
        )

        for _ in range(self.max_attempts):
            raw_text = self.client.get_answer(prompt)
            verdict = JsonExtractor.extract_json(raw_text)

            if verdict:
                result = AnswerValidationResult(score=int(verdict.get("score")),
                                                is_correct=bool(verdict.get("is_correct")),
                                                reply_message=verdict.get("reply_message"),
                                                justification=verdict.get("justification"))
                return result

        # fail-safe: если ИИ сломался — просим повторить
        result = AnswerValidationResult(score=0,
                                        is_correct=False,
                                        reply_message="Пожалуйста, уточните или переформулируйте ответ.",
                                        justification="Ошибка запроса к ИИ-агенту")
        return result


class FakeAnswerValidator(AnswerValidator):
    """
    MVP-валидатор:
    всегда считает ответ корректным.
    """

    def validate(self, *,
                 question: InterviewQuestion,
                 answer_text: str,
                 vacancy_title: str, vacancy_description: str,
                 question_history: str | None = None) -> AnswerValidationResult:
        result = AnswerValidationResult(is_correct=True, reply_message=None)
        return result


ai_answer_validator = AIAnswerValidator(client=gpt_4_model, max_attempts=3)